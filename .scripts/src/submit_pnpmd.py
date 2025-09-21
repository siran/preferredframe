#!/usr/bin/env python3
"""
submit_pnpmd.py — minimal PR submitter (commit only the .md).

Flow:
  1) Read local .md (argv[1])
  2) Title = first '% ' line (fallback: stem); enforce ASCII-only
  3) Create branch submit-<slug> from origin/main
  4) Copy .md → preferredframe/prints/<Title>/<Title>.md
  5) Git add ONLY the .md; commit; push
  6) Print PR creation URL (/pull/new/<branch>)
"""

from __future__ import annotations
import argparse, re, sys, subprocess, shutil
from pathlib import Path

# repo root = <repo>/.scripts/src/submit_pnpmd.py -> parents[2]
ROOT = Path(__file__).resolve().parents[2]

# --- shell helpers ------------------------------------------------------------

def sh(args, cwd=ROOT):
    """Passthrough runner: stream child stdout/stderr; raise on error."""
    subprocess.run(args, cwd=cwd, check=True)

def sh_co(args, cwd=ROOT) -> str:
    """Capture stdout (stderr merged), for things like remote URLs."""
    p = subprocess.run(args, cwd=cwd, check=True, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.stdout or ""

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

    # Ensure we start from origin/main
    sh(["git", "fetch", "origin", "main"])
    sh(["git", "checkout", "-B", branch, "origin/main"])

    # Copy ONLY the .md into repo
    dest_dir = ROOT / "preferredframe" / "prints" / title
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_md = dest_dir / f"{title}.md"
    shutil.copy2(src, dest_md)

    # Stage and commit ONLY the .md
    sh(["git", "add", str(dest_md)])
    sh(["git", "commit", "-m", f"Add print: {title}"])
    sh(["git", "push", "-u", "origin", branch])

    # Direct "new PR" URL
    pr_url = f"https://github.com/siran/preferredframe/pull/new/{branch}"
    print("\nBranch pushed.")
    print("Open this URL to create the PR:")
    print(pr_url)

if __name__ == "__main__":
    main()
