#!/usr/bin/env python3
"""
submit_pnpmd.py — minimal PR submitter (commit only the .md).

Flow:
  1) Read local .md (argv[1])
  2) Title = first '% ' line (fallback: stem); enforce ASCII-only
  3) Create branch submit-<slug> from origin/<default>
  4) Copy .md → preferredframe/prints/<Title>/<Title>.md
  5) Git add ONLY the .md; commit; push
  6) Print PR creation URL for origin (/pull/new/<branch>)
"""

from __future__ import annotations
import argparse, re, sys, subprocess, shutil
from pathlib import Path

# repo root = <repo>/.scripts/src/submit_pnpmd.py -> parents[2]
ROOT = Path(__file__).resolve().parents[2]

# --- shell helpers ------------------------------------------------------------

def sh(args, cwd=ROOT, check=True):
    """Passthrough runner: stream child stdout/stderr; raise on error."""
    subprocess.run(args, cwd=cwd, check=check)

def sh_co(args, cwd=ROOT, check=True) -> str:
    """Capture stdout (stderr merged)."""
    p = subprocess.run(args, cwd=cwd, check=check, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return (p.stdout or "").strip()

def die(msg: str):
    print(msg, file=sys.stderr)
    sys.exit(1)

# --- small utils --------------------------------------------------------------

def read_title(md: Path) -> str:
    """Title = first non-empty line starting with '% ' ; else stem."""
    for ln in md.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("% "):
            return s[2:].strip()
        break
    return md.stem

def assert_ascii(s: str):
    if any(ord(ch) > 127 for ch in s):
        die("Title must be ASCII-only (replace Unicode punctuation).")

def slugify(title: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", title)
    safe = re.sub(r"-{2,}", "-", safe).strip("-")
    return safe or "untitled"

def origin_default_branch() -> str:
    """
    Get default branch name from origin.
    Uses: git rev-parse --abbrev-ref origin/HEAD => origin/main
    """
    ref = sh_co(["git", "rev-parse", "--abbrev-ref", "origin/HEAD"])
    if ref and ref.startswith("origin/"):
        return ref.split("/", 1)[1]
    # Fallbacks
    for cand in ("main", "master"):
        try:
            sh(["git", "ls-remote", "--exit-code", "--heads", "origin", cand])
            return cand
        except subprocess.CalledProcessError:
            continue
    die("Could not determine default branch on origin.")

def origin_https_url() -> str:
    """
    Return HTTPS URL for origin, normalized, e.g.:
      - git@github.com:org/repo.git -> https://github.com/org/repo
      - https://github.com/org/repo.git -> https://github.com/org/repo
    """
    url = sh_co(["git", "remote", "get-url", "origin"])
    url = url.strip()
    if not url:
        die("No 'origin' remote configured.")
    if url.startswith("git@github.com:"):
        path = url[len("git@github.com:"):]
        if path.endswith(".git"): path = path[:-4]
        return f"https://github.com/{path}"
    if url.startswith("https://github.com/"):
        path = url[len("https://github.com/"):]
        if path.endswith(".git"): path = path[:-4]
        return f"https://github.com/{path}"
    # last resort: strip .git if present; hope it is a browsable https
    if url.endswith(".git"):
        url = url[:-4]
    return url

# --- main ---------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src_md", help="Path to local PNPMD .md")
    args = ap.parse_args()

    src = Path(args.src_md).resolve()
    if not src.exists():
        die(f"File not found: {src}")

    title = read_title(src)
    assert_ascii(title)
    branch = f"submit-{slugify(title)}"

    # Ensure we start from origin/<default>
    sh(["git", "fetch", "origin", "--prune"])
    default = origin_default_branch()
    sh(["git", "checkout", "-B", branch, f"origin/{default}"])

    # Copy ONLY the .md into repo
    dest_dir = ROOT / "preferredframe" / "prints" / title
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_md = dest_dir / f"{title}.md"
    shutil.copy2(src, dest_md)

    # Stage and commit ONLY the .md
    sh(["git", "add", str(dest_md)])
    # Quietly ignore empty commit if identical file already exists
    try:
        sh(["git", "commit", "-m", f"Add print: {title}"])
    except subprocess.CalledProcessError:
        print("No changes to commit (file identical?).")

    # Push branch
    sh(["git", "push", "-u", "origin", branch])

    # Direct "new PR" URL (derived from origin)
    base = origin_https_url()
    pr_url = f"{base}/pull/new/{branch}"
    print("\nBranch pushed.")
    print("Open this URL to create the PR:")
    print(pr_url)

if __name__ == "__main__":
    main()
