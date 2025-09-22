#!/usr/bin/env python3
"""
submit_pnpmd.py — PNPMD PR submitter (commit only the .md).

- Detect existing submit-<slug> branch; prompt to delete (local/remote).
- Create fresh branch from origin/<default>.
- Copy ONLY the .md → preferredframe/prints/<Title>/<Title>.md
- Force-add (-f) to bypass .gitignore; commit; push.
- Print PR URL; checkout default; delete local topic branch (remote optional).

Usage:
  submit_pnpmd.py /path/to/file.md [--cleanup {local,remote,none}]
"""

from __future__ import annotations
import argparse, re, sys, subprocess, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def sh(args, *, capture=False, check=True) -> str:
    r = subprocess.run(
        args, cwd=ROOT, text=True, check=check,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )
    return (r.stdout or "").strip() if capture else ""

def die(msg: str):
    print(msg, file=sys.stderr); sys.exit(1)

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
    if ref.startswith("origin/"):
        return ref.split("/", 1)[1]
    for cand in ("main", "master"):
        if subprocess.run(["git", "ls-remote", "--heads", "origin", cand], cwd=ROOT,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            return cand
    die("Could not determine origin default branch.")

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
    return subprocess.run(["git", "show-ref", "--verify", f"refs/heads/{name}"],
                          cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def branch_exists_remote(name: str) -> bool:
    return bool(sh(["git", "ls-remote", "--heads", "origin", name], capture=True))

def prompt_yn(q: str, default_no: bool = True) -> bool:
    yn = " [y/N]: " if default_no else " [Y/n]: "
    try:
        ans = input(q + yn).strip().lower()
    except EOFError:
        return not default_no
    if not ans: return not default_no
    return ans.startswith("y")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src_md", help="Path to local PNPMD .md")
    ap.add_argument("--cleanup", choices=["local", "remote", "none"], default="local",
                    help="After pushing, delete local topic branch (default), also delete remote, or do nothing.")
    args = ap.parse_args()

    src = Path(args.src_md).resolve()
    if not src.exists():
        die(f"File not found: {src}")

    title = read_title(src)
    assert_ascii(title)
    slug  = slugify(title)
    branch = f"submit-{slug}"

    print(f"[submit] Source: {src}")
    print(f"[submit] Title:  {title}")
    print(f"[submit] Slug:   {slug}")
    print(f"[submit] Branch: {branch}")

    sh(["git", "fetch", "origin", "--prune"])
    default = "main"

    exists_local  = branch_exists_local(branch)
    exists_remote = branch_exists_remote(branch)
    if exists_local or exists_remote:
        print(f"[submit] Found existing branch '{branch}' (local={exists_local}, remote={exists_remote})")
        if prompt_yn("Delete existing branch before proceeding?"):
            if exists_local:
                cur = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)
                if cur == branch:
                    sh(["git", "checkout", default])
                sh(["git", "branch", "-D", branch])
                print("[submit] - deleted local branch")
            if exists_remote:
                subprocess.run(["git", "push", "origin", "--delete", branch],
                               cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                print("[submit] - deleted remote branch (if existed)")
        else:
            die("[submit] Aborting per user choice (branch exists).")

    # Fresh topic branch
    sh(["git", "checkout", "-B", branch, f"origin/{default}"])
    print(f"[submit] Switched to clean branch {branch} from origin/{default}")

    # Copy ONLY the .md → prints/<Title>/<Title>.md
    dest_dir = ROOT / "prints" / title
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_md = dest_dir / f"{title}.md"
    print(f"[submit] Copy → {dest_md.relative_to(ROOT)}")
    shutil.copy2(src, dest_md)

    # Assert copy
    if not dest_md.exists() or dest_md.stat().st_size == 0:
        die("[submit] Copy failed or file empty after copy.")

    # Status before add
    print("[submit] git status (before add):")
    print(sh(["git", "status", "--porcelain"], capture=True))

    # Force-add (bypass .gitignore), commit iff changes exist
    sh(["git", "add", "-f", str(dest_md)])  # -f: in case prints/ is ignored
    print("[submit] git status (after add):")
    print(sh(["git", "status", "--porcelain"], capture=True))

    committed = True
    try:
        sh(["git", "commit", "-m", f"Add print: {title}"])
        print("[submit] Commit created.")
    except subprocess.CalledProcessError:
        committed = False
        print("[submit] No changes to commit (file identical?). Proceeding.")

    # Always push the branch (even if no new commit) to open/refresh PR
    sh(["git", "push", "-u", "origin", branch])
    pr_url = f"{origin_https_url()}/pull/new/{branch}"
    print("\n[submit] Branch pushed.")
    print("[submit] Create/refresh PR at:")
    print(pr_url)

    # Cleanup: switch back; delete local topic; optional remote
    sh(["git", "checkout", default])
    if args.cleanup in ("local", "remote"):
        subprocess.run(["git", "branch", "-D", branch], cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(f"[submit] Local branch '{branch}' deleted.")
    if args.cleanup == "remote":
        subprocess.run(["git", "push", "origin", "--delete", branch], cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(f"[submit] Remote branch '{branch}' deleted.")

if __name__ == "__main__":
    main()
