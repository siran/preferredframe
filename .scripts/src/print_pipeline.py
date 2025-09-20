#!/usr/bin/env python3
"""
print_pipeline.py

Modes:
  --pr-check : PR gate on exactly one .md under preferredframe/prints/** + ASCII-only Title
               (diff BASE_SHA..HEAD_SHA; title read from HEAD blob).
  default    : Push build: validate -> pnp.md -> html/pdf (from pnp.md) -> Zenodo -> sidecars -> assets
               (diff GITHUB_BEFORE..GITHUB_AFTER, with zero-SHA guard).

Env:
  GITHUB_WORKSPACE (preferred), GITHUB_BEFORE, GITHUB_AFTER,
  ASSETS_PAT (optional), ZENODO_TOKEN, ZENODO_API, BASE_URL, GITHUB_REPOSITORY
"""
import os, subprocess, sys, argparse
from pathlib import Path

# Prefer GitHub's canonical workspace; fallback to path-derived root
_WS = os.environ.get("GITHUB_WORKSPACE")
ROOT = Path(_WS).resolve() if _WS else Path(__file__).resolve().parents[2]
ZERO = "0000000000000000000000000000000000000000"

def ensure_repo_root():
    if not (ROOT / ".git").exists():
        sys.stderr.write(f"ERROR: Not a git repo at {ROOT}\n")
        sys.exit(1)

def sh(cmd, *, text=False):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=text, check=True)
    return p.stdout if text else p.stdout

def git(*args, text=False) -> str | bytes:
    # Always force -C ROOT so git runs in the correct repo
    base = ["git", "-C", str(ROOT)]
    p = subprocess.run(base + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=text, check=True)
    return p.stdout if text else p.stdout

def git_co(*args) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT)] + list(args))

def git_diff_names_z(base: str, head: str) -> list[str]:
    out = git_co("-c", "core.quotepath=false",
                 "diff", "--name-only", "--diff-filter=ACMRT", "-z", f"{base}..{head}")
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
        data = git_co("show", f"{head_sha}:{repo_rel_path}")
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
        prev = git("rev-list", "-n", "1", f"{after}~1", text=True).strip()
        if not prev:
            sys.exit("Cannot determine base for first commit.")
        before = prev

    paths = git_diff_names_z(before, after)
    md_repo_rel = pick_exactly_one_print_md(paths)
    md_path = ROOT / md_repo_rel

    # 1) validate (original .md)
    sh([sys.executable, str(ROOT / ".scripts/src/validate_pnpmd.py"), str(md_path)])

    # 2) .pnp.md (normalize + preprocess) — source of truth for rendering
    pnp_md = md_path.with_suffix(".pnp.md")
    sh([sys.executable, str(ROOT / ".scripts/src/make_pnpmd.py"), str(md_path), str(pnp_md)])

    # 3) HTML (from .pnp.md)
    html_path = md_path.with_suffix(".html")
    sh([sys.executable, str(ROOT / ".scripts/src/make_html.py"), str(pnp_md), str(html_path)])

    # 4) PDF (from .pnp.md)
    pdf_path = md_path.with_suffix(".pdf")
    sh([sys.executable, str(ROOT / ".scripts/src/make_pdf.py"), str(pnp_md), str(pdf_path)])

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
    ])

    # 6) sidecars
    sh([sys.executable, str(ROOT / ".scripts/src/write_version_sidecar.py"), str(md_path)])

    # 7) assets push (optional)
    assets_pat = os.environ.get("ASSETS_PAT", "")
    if assets_pat:
        import tempfile, shutil
        versions_dir = md_path.parent / "versions"
        latest = sorted(versions_dir.glob("*.yml"))
        if latest:
            doi_safe = latest[-1].stem
            with tempfile.TemporaryDirectory() as td:
                tdp = Path(td)
                clone_url = f"https://{assets_pat}@github.com/siran/assets.git"
                sh(["git", "clone", "--depth=1", clone_url, "assets"],)
                repo = tdp / "assets"
                dest = repo / "preferredframe" / title / doi_safe
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(html_path, dest / f"{title}.html")
                shutil.copy2(pdf_path,  dest / f"{title}.pdf")
                src_yml = md_path.parent / "source.yml"
                if src_yml.exists():
                    shutil.copy2(src_yml, dest / "source.yml")
                sh(["git", "-C", str(repo), "config", "user.name", "preferredframe-bot"])
                sh(["git", "-C", str(repo), "config", "user.email", "bot@preferredframe.com"])
                sh(["git", "-C", str(repo), "add", str(dest.relative_to(repo))])
                sh(["git", "-C", str(repo), "commit", "-m", f'Add assets for "{title}" — {doi_safe}'])
                sh(["git", "-C", str(repo), "push"])

    print("Pipeline finished successfully.")

if __name__ == "__main__":
    main()
