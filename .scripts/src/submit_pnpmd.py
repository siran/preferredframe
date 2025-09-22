#!/usr/bin/env python3
"""
submit_pnpmd.py — PNPMD PR submitter (commit only the .md).

Flow:
  1) Read local .md (argv[1]); Title = first '% ' line (fallback: stem); enforce ASCII-only.
  2) Branch name = submit-<slug>.
     - If branch exists (local and/or remote), ask whether to delete.
  3) Create clean branch from origin/<default>.
  4) Copy .md → preferredframe/prints/<Title>/<Title>.md
  5) Git add ONLY the .md; commit; push.
  6) Print PR creation URL.
  7) Checkout default branch; delete local topic branch (remote kept, unless --cleanup=remote).
"""

from __future__ import annotations
import argparse, re, sys, subprocess, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# --- shell helpers ------------------------------------------------------------

def sh(args, cwd=ROOT, check=True, capture=False) -> str:
    r = subprocess.run(
        args, cwd=cwd, check=check, text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )
    return (r.stdout or "").strip() if capture else ""

def die(msg: str):
    print(msg, file=sys.stderr); sys.exit(1)

# --- utils --------------------------------------------------------------------

def read_title(md: Path) -> str:
    for ln in md.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s: continue
        if s.startswith("% "): return s[2:].strip()
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
    ref = sh(["git", "rev-parse", "--abbrev-ref", "origin/HEAD"], capture=True)
    if ref and ref.startswith("origin/"):
        return ref.split("/", 1)[1]
    for cand in ("main", "master"):
        code = subprocess.run(["git", "ls-remote", "--heads", "origin", cand], cwd=ROOT,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        if code == 0: return cand
    die("Could not determine default branch on origin.")

def origin_https_url() -> str:
    url = sh(["git", "remote", "get-url", "origin"], capture=True).strip()
    if not url: die("No 'origin' remote configured.")
    if url.startswith("git@github.com:"):
        path = url[len("git@github.com:"):]
        if path.endswith(".git"): path = path[:-4]
        return f"https://github.com/{path}"
    if url.startswith("https://github.com/"):
        path = url[len("https://github.com/"):]
        if path.endswith(".git"): path = path[:-4]
        return f"https://github.com/{path}"
    return url[:-4] if url.endswith(".git") else url

def branch_exists_local(name: str) -> bool:
    code = subprocess.run(["git", "show-ref", "--verify", f"refs/heads/{name}"], cwd=ROOT,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    return code == 0

def branch_exists_remote(name: str) -> bool:
    out = sh(["git", "ls-remote", "--heads", "origin", name], capture=True)
    return bool(out.strip())

def prompt_yn(q: str, default_no: bool = True) -> bool:
    yn = " [y/N]: " if default_no else " [Y/n]: "
    ans = input(q + yn).strip().lower()
    if not ans: return not default_no
    return ans.startswith("y")

# --- main ---------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src_md", help="Path to local PNPMD .md")
    ap.add_argument("--cleanup", choices=["local", "remote", "none"], default="local",
                    help="Post-push cleanup: delete local topic branch (default), also delete remote, or none.")
    args = ap.parse_args()

    src = Path(args.src_md).resolve()
    if not src.exists(): die(f"File not found: {src}")

    title = read_title(src); assert_ascii(title)
    slug  = slugify(title)
    branch = f"submit-{slug}"

    # Ensure fresh remote refs
    sh(["git", "fetch", "origin", "--prune"])

    # Handle pre-existing branch
    exists_local  = branch_exists_local(branch)
    exists_remote = branch_exists_remote(branch)
    if exists_local or exists_remote:
        print(f"Found existing branch '{branch}' "
              f"(local={exists_local}, remote={exists_remote}).")
        if prompt_yn("Delete existing branch before proceeding?"):
            if exists_local:
                # Move off branch if currently checked out
                cur = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)
                if cur == branch:
                    default = origin_default_branch()
                    sh(["git", "checkout", default])
                sh(["git", "branch", "-D", branch])
                print(" - deleted local branch")
            if exists_remote:
                # Ignore if remote not found at delete time
                subprocess.run(["git", "push", "origin", "--delete", branch],
                               cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                print(" - deleted remote branch (if existed)")
        else:
            die("Aborting per user choice (branch exists).")

    # Create clean topic branch from origin/<default>
    default = origin_default_branch()
    sh(["git", "checkout", "-B", branch, f"origin/{default}"])

    # Copy ONLY the .md into repo
    dest_dir = ROOT / "preferredframe" / "prints" / title
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_md = dest_dir / f"{title}.md"
    shutil.copy2(src, dest_md)

    # Stage and commit ONLY the .md
    sh(["git", "add", str(dest_md)])
    # Allow no-change commit to be skipped gracefully
    committed = True
    try:
        sh(["git", "commit", "-m", f"Add print: {title}"])
    except subprocess.CalledProcessError:
        committed = False
        print("No changes to commit (identical content?). Continuing to push...")

    # Push branch
    sh(["git", "push", "-u", "origin", branch])

    # PR URL
    pr_url = f"{origin_https_url()}/pull/new/{branch}"
    print("\nBranch pushed.")
    print("Open this URL to create the PR:")
    print(pr_url)

    # Post-push: checkout default, delete local topic branch (default behavior)
    sh(["git", "checkout", default])
    if args.cleanup in ("local", "remote"):
        # best-effort local delete
        subprocess.run(["git", "branch", "-D", branch], cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(f"Local branch '{branch}' deleted.")
    if args.cleanup == "remote":
        subprocess.run(["git", "push", "origin", "--delete", branch], cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(f"Remote branch '{branch}' deleted (PR would close).")

if __name__ == "__main__":
    main()
