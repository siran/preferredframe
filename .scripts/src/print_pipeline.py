#!/usr/bin/env python3
"""
print_pipeline.py

PR gate:   --pr-check  (diff BASE..HEAD; title from HEAD blob; ASCII-only)
Push build: validate -> pnp.md -> html/pdf (from pnp.md) -> Zenodo -> sidecars -> assets
"""

import os, sys, argparse, subprocess
from pathlib import Path

ZERO = "0000000000000000000000000000000000000000"

# ---------- diagnostics ----------
def echo(msg): sys.stderr.write(msg.rstrip() + "\n")

def run_checked(cmd, *, text=False):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=text, check=True)
    return p.stdout if text else p.stdout

# ---------- repo root detection ----------
def is_git_dir(p: Path) -> bool:
    try:
        subprocess.run(["git", "-C", str(p), "rev-parse", "--is-inside-work-tree"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def candidates_from_env_and_paths() -> list[Path]:
    c = []
    # Current working dir first (what the runner actually has)
    c.append(Path(os.getcwd()).resolve())
    # GitHub defaults
    for envk in ("GITHUB_WORKSPACE",):
        v = os.environ.get(envk)
        if v: c.append(Path(v).resolve())
    # Common GH container mount
    c.append(Path("/github/workspace"))
    # Path derived from this file
    c.append(Path(__file__).resolve().parents[2])
    # Walk up from cwd a few levels (just in case)
    cwd = Path(os.getcwd()).resolve()
    for i in range(5):
        c.append(cwd)
        cwd = cwd.parent
    # De-dup preserving order
    seen, out = set(), []
    for p in c:
        if p not in seen:
            out.append(p); seen.add(p)
    return out

def find_repo_root() -> Path:
    echo("== Repo root detection ==")
    echo(f"pwd: {Path(os.getcwd()).resolve()}")
    echo(f"GITHUB_WORKSPACE: {os.environ.get('GITHUB_WORKSPACE','(unset)')}")
    echo(f"__file__: {Path(__file__).resolve()}")
    for cand in candidates_from_env_and_paths():
        try:
            top = subprocess.run(["git", "-C", str(cand), "rev-parse", "--show-toplevel"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            root = Path(top.stdout.strip()).resolve()
            echo(f"git top OK @ {cand} -> {root}")
            return root
        except subprocess.CalledProcessError:
            continue
    echo("FATAL: could not locate a git worktree. Check that actions/checkout ran in this job.")
    sys.exit(1)

ROOT = find_repo_root()

def git_co(*args) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT)] + list(args))

def git(*args, text=False) -> str | bytes:
    p = subprocess.run(["git", "-C", str(ROOT)] + list(args),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=text, check=True)
    return p.stdout if text else p.stdout

def git_diff_names_z(base: str, head: str) -> list[str]:
    out = git("-c", "core.quotepath=false", "diff",
              "--name-only", "--diff-filter=ACMRT", "-z", f"{base}..{head}")
    parts = [p for p in out.split(b"\x00") if p]
    return [p.decode("utf-8", "strict") for p in parts]

def pick_exactly_one_print_md(paths: list[str]) -> str:
    md = [p for p in paths if p.startswith("preferredframe/prints/") and p.endswith(".md")]
    print("Changed files:"); [print(p) for p in paths]
    print("\nChanged print .md files:"); [print(p) for p in md]
    if len(md) != 1:
        sys.exit(f"Exactly one .md must be changed (got {len(md)}).")
    return md[0]

def read_title_from_blob(head_sha: str, repo_rel_path: str) -> str:
    try:
        data = git_co("show", f"{head_sha}:{repo_rel_path}")
        for raw in data.splitlines():
            s = raw.decode("utf-8", "strict").strip()
            if not s: continue
            if s.startswith("% "): return s[2:].strip()
            break
    except Exception:
        pass
    return Path(repo_rel_path).stem

def read_title_from_fs(p: Path) -> str:
    for ln in p.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s: continue
        if s.startswith("% "): return s[2:].strip()
        break
    return p.stem

def assert_ascii_title(title: str):
    if any(ord(ch) > 127 for ch in title):
        sys.exit("Title must be ASCII-only (replace Unicode like ‘–’ with '-').")

def pr_check():
    base = os.environ.get("BASE_SHA"); head = os.environ.get("HEAD_SHA")
    if not base or not head:
        sys.exit("For --pr-check set BASE_SHA and HEAD_SHA.")
    echo(f"PR check diff: {base}..{head}")
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

    # Extra diagnostics
    echo("== Diagnostics ==")
    try:
        echo("git rev-parse --show-toplevel: " + git("rev-parse", "--show-toplevel", text=True).strip())
    except Exception as e:
        echo(f"git rev-parse failed: {e}")

    if args.pr_check:
        return pr_check()

    before = os.environ.get("GITHUB_BEFORE"); after = os.environ.get("GITHUB_AFTER")
    if not before or not after:
        sys.exit("Set GITHUB_BEFORE and GITHUB_AFTER for push pipeline.")
    if before == ZERO:
        prev = git("rev-list", "-n", "1", f"{after}~1", text=True).strip()
        if not prev:
            sys.exit("Cannot determine base for first commit.")
        before = prev
    echo(f"Push diff: {before}..{after}")

    paths = git_diff_names_z(before, after)
    md_repo_rel = pick_exactly_one_print_md(paths)
    md_path = ROOT / md_repo_rel

    # 1) validate
    run_checked([sys.executable, str(ROOT / ".scripts/src/validate_pnpmd.py"), str(md_path)])

    # 2) .pnp.md (normalize + preprocess) — source of truth for rendering
    pnp_md = md_path.with_suffix(".pnp.md")
    run_checked([sys.executable, str(ROOT / ".scripts/src/make_pnpmd.py"), str(md_path), str(pnp_md)])

    # 3) HTML (from .pnp.md)
    html_path = md_path.with_suffix(".html")
    run_checked([sys.executable, str(ROOT / ".scripts/src/make_html.py"), str(pnp_md), str(html_path)])

    # 4) PDF (from .pnp.md)
    pdf_path = md_path.with_suffix(".pdf")
    run_checked([sys.executable, str(ROOT / ".scripts/src/make_pdf.py"), str(pnp_md), str(pdf_path)])

    # 5) Zenodo: primary = original .md; attach pnp.md/html/pdf
    title = read_title_from_fs(md_path)
    assert_ascii_title(title)
    run_checked([
        sys.executable, str(ROOT / ".scripts/src/zenodo_publish.py"),
        "--primary", str(md_path),
        "--attach",  str(pnp_md),
        "--attach",  str(html_path),
        "--attach",  str(pdf_path),
        "--title",   title
    ])

    # 6) sidecars
    run_checked([sys.executable, str(ROOT / ".scripts/src/write_version_sidecar.py"), str(md_path)])

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
                run_checked(["git", "clone", "--depth=1", clone_url, "assets"])
                repo = tdp / "assets"
                dest = repo / "preferredframe" / title / doi_safe
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(html_path, dest / f"{title}.html")
                shutil.copy2(pdf_path,  dest / f"{title}.pdf")
                src_yml = md_path.parent / "source.yml"
                if src_yml.exists():
                    shutil.copy2(src_yml, dest / "source.yml")
                run_checked(["git", "-C", str(repo), "config", "user.name", "preferredframe-bot"])
                run_checked(["git", "-C", str(repo), "config", "user.email", "bot@preferredframe.com"])
                run_checked(["git", "-C", str(repo), "add", str(dest.relative_to(repo))])
                run_checked(["git", "-C", str(repo), "commit", "-m", f'Add assets for "{title}" — {doi_safe}'])
                run_checked(["git", "-C", str(repo), "push"])

    print("Pipeline finished successfully.")

if __name__ == "__main__":
    main()
