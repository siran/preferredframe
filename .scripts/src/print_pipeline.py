#!/usr/bin/env python3
"""
print_pipeline.py

Straightforward pipeline for PNPMD → Zenodo.

Modes:
  --pr-check : Gate on exactly one changed .md under preferredframe/prints/** and ASCII-only Title.
               Diff is ONLY BASE_SHA..HEAD_SHA. Title read from HEAD blob.
  (default)  : Push build:
               validate -> pnp.md -> html/pdf (both from pnp.md) -> Zenodo -> sidecars -> assets.
               Diff is ONLY GITHUB_BEFORE..GITHUB_AFTER (with zero-SHA guard).

Env (push mode):
  GITHUB_BEFORE, GITHUB_AFTER
  ASSETS_PAT (optional): push .html/.pdf + source.yml to siran/assets
  ZENODO_TOKEN, ZENODO_API, BASE_URL, GITHUB_REPOSITORY
"""
import os, subprocess, sys, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZERO = "0000000000000000000000000000000000000000"

def ensure_repo_root():
    # Force working dir to repo root for safety
    os.chdir(ROOT)
    if not (ROOT / ".git").exists():
        sys.exit(f"Not a git repository at {ROOT}. Did checkout run?")

def sh(cmd, *, text=False, cwd=None):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=text, check=True, cwd=cwd or ROOT)
    return p.stdout if text else p.stdout

def sh_co(cmd, *, cwd=None):
    return subprocess.check_output(cmd, cwd=cwd or ROOT)

def git_diff_names_z(base: str, head: str) -> list[str]:
    out = sh_co([
        "git", "-c", "core.quotepath=false",
        "diff", "--name-only", "--diff-filter=ACMRT", "-z", f"{base}..{head}"
    ], cwd=ROOT)
    parts = [p for p in out.split(b"\x00") if p]
    return [p.decode("utf-8", "strict") for p in parts]

def pick_exactly_one_print_md(changed_paths: list[str]) -> str:
    md_files = [p for p in changed_paths
                if p.startswith("preferredframe/prints/") and p.endswith(".md")]
    print("Changed files:"); [print(p) for p in changed_paths]
    print("\nChanged print .md files:"); [print(p) for p in md_files]
    if len(md_files) != 1:
        sys.exit(f"Exactly one .md must be changed (got {len(md_files)}).")
    return md_files[0]

def read_title_from_blob(head_sha: str, repo_rel_path: str) -> str:
    try:
        data = sh_co(["git", "show", f"{head_sha}:{repo_rel_path}"], cwd=ROOT)
        for raw in data.splitlines():
            line = raw.decode("utf-8", "strict").strip()
            if not line: continue
            if line.startswith("% "): return line[2:].strip()
            break
    except Exception:
        pass
    return Path(repo_rel_path).stem

def read_title_from_fs(path: Path) -> str:
    for ln in path.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s: continue
        if s.startswith("% "): return s[2:].strip()
        break
    return path.stem

def assert_ascii_title(title: str):
    if any(ord(ch) > 127 for ch in title):
        sys.exit("Title must be ASCII-only (replace Unicode like ‘–’ with '-').")

def pr_check():
    ensure_repo_root()
    base = os.environ.get("BASE_SHA")
    head = os.environ.get("HEAD_SHA")
    if not base or not head:
        sys.exit("For --pr-check set BASE_SHA and HEAD_SHA.")
    paths = git_diff_names_z(base, head)
    md_repo_rel = pick_exactly_one_print_md(paths)
    title = read_title_from_blob(head, md_repo_rel)
    assert_ascii_title(title)
    print("Check 1: exactly one .md under preferredframe/prints — PASSED")
    print("Check 2: ASCII-only Title — PASSED")
    print("PR gate OK.")
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr-check", action="store_true")
    args = ap.parse_args()

    if args.pr_check:
        return pr_check()

    ensure_repo_root()

    before = os.environ.get("GITHUB_BEFORE")
    after  = os.environ.get("GITHUB_AFTER")
    if not before or not after:
        sys.exit("Set GITHUB_BEFORE and GITHUB_AFTER for push pipeline.")
    if before == ZERO:
        prev = sh(["git", "rev-list", "-n", "1", f"{after}~1"], text=True, cwd=ROOT).strip()
        if not prev:
            sys.exit("Cannot determine base for first commit.")
        before = prev

    paths = git_diff_names_z(before, after)
    md_repo_rel = pick_exactly_one_print_md(paths)
    md_path = ROOT / md_repo_rel

    # 1) validate (original .md)
    sh([sys.executable, str(ROOT / ".scripts/src/validate_pnpmd.py"), str(md_path)], cwd=ROOT)

    # 2) .pnp.md (normalize + preprocess)
    pnp_md = md_path.with_suffix(".pnp.md")
    sh([sys.executable, str(ROOT / ".scripts/src/make_pnpmd.py"), str(md_path), str(pnp_md)], cwd=ROOT)

    # 3) HTML (from .pnp.md)
    html_path = md_path.with_suffix(".html")
    sh([sys.executable, str(ROOT / ".scripts/src/make_html.py"), str(pnp_md), str(html_path)], cwd=ROOT)

    # 4) PDF (from .pnp.md)
    pdf_path = md_path.with_suffix(".pdf")
    sh([sys.executable, str(ROOT / ".scripts/src/make_pdf.py"), str(pnp_md), str(pdf_path)], cwd=ROOT)

    # 5) Zenodo: primary = original .md; attach pnp.md/html/pdf
    title = read_title_from_fs(md_path)
    assert_ascii_title(title)
    sh([
        sys.executable, str(ROOT / ".scripts/src/zenodo_publish.py"),
        "--primary", str(md_path),
        "--attach",  str(pnp_md),
        "--attach",  str(html_path),
        "--attach",  str(pdf_path),
        "--title",   title
    ], cwd=ROOT)

    # 6) sidecars
    sh([sys.executable, str(ROOT / ".scripts/src/write_version_sidecar.py"), str(md_path)], cwd=ROOT)

    # 7) assets push (optional)
    assets_pat = os.environ.get("ASSETS_PAT", "")
    if assets_pat:
        import tempfile, shutil
        versions_dir = md_path.parent / "versions"
        latest = sorted(versions_dir.glob("*.yml"))
        if latest:
            doi_safe = latest[-1].stem
            with tempfile.TemporaryDirectory() as td:
                td = Path(td)
                clone_url = f"https://{assets_pat}@github.com/siran/assets.git"
                sh(["git", "clone", "--depth=1", clone_url, "assets"], cwd=td)
                repo = td / "assets"
                dest = repo / "preferredframe" / title / doi_safe
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(html_path, dest / f"{title}.html")
                shutil.copy2(pdf_path,  dest / f"{title}.pdf")
                src_yml = md_path.parent / "source.yml"
                if src_yml.exists():
                    shutil.copy2(src_yml, dest / "source.yml")
                sh(["git", "config", "user.name", "preferredframe-bot"], cwd=repo)
                sh(["git", "config", "user.email", "bot@preferredframe.com"], cwd=repo)
                sh(["git", "add", str(dest.relative_to(repo))], cwd=repo)
                sh(["git", "commit", "-m", f'Add assets for "{title}" — {doi_safe}'], cwd=repo)
                sh(["git", "push"], cwd=repo)

    print("Pipeline finished successfully.")

if __name__ == "__main__":
    main()
