#!/usr/bin/env python3
"""
submit_pnpmd.py

Usage:
  python .scripts/src/submit_pnpmd.py '../path/with spaces/My Paper.md' [--use-gh]

Behavior:
- Reads the given local file path (first arg).
- Extracts Title from the first non-empty line starting with '% ' (2nd such line = authors).
- Stores at: preferredframe/prints/<Title>/<Title><.ext> (sidecar .yml with metadata).
- If the source is in a git repo, records origin repo/commit/author/email/date.
- Uses a dedicated git worktree for the submission branch (no switching in your main tree).
- Pushes the branch. If --use-gh, attempts to open a PR via GitHub CLI; otherwise prints compare URL.

Notes:
- No absolute local paths are stored.
- Title/destination filename are NOT modified except for path-separator checks.
"""

import argparse, subprocess, sys, shutil, re
from pathlib import Path
import datetime, yaml

ROOT = Path(__file__).resolve().parents[2]
TMP  = ROOT / ".tmp" / "submit_worktrees"

def run(cmd, cwd=None, check=True, text=True):
    return subprocess.run(cmd, cwd=cwd, check=check, text=text,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()

def try_run(cmd, cwd=None):
    try:
        return run(cmd, cwd=cwd)
    except Exception:
        return ""

def run_allow_noop_commit(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0 and "nothing to commit" not in (p.stdout + p.stderr).lower():
        raise subprocess.CalledProcessError(p.returncode, cmd, p.stdout, p.stderr)
    return p.stdout.strip()

def in_git_repo(path: Path) -> bool:
    try:
        run(["git","-C", str(path.parent), "rev-parse", "--is-inside-work-tree"])
        return True
    except subprocess.CalledProcessError:
        return False

def git_metadata(path: Path) -> dict:
    md = {}
    try:
        top = run(["git","-C", str(path.parent), "rev-parse", "--show-toplevel"])
        rel = str(path.resolve().relative_to(Path(top)))
        md["origin_repo"]   = run(["git","-C", top, "config","--get","remote.origin.url"])
        md["origin_commit"] = run(["git","-C", top, "log","-n1","--pretty=%H","--", rel])
        md["origin_author"] = run(["git","-C", top, "log","-n1","--pretty=%an","--", rel])
        md["origin_email"]  = run(["git","-C", top, "log","-n1","--pretty=%ae","--", rel])
        md["origin_date"]   = run(["git","-C", top, "log","-n1","--pretty=%aI","--", rel])
    except Exception:
        pass
    return {k:v for k,v in md.items() if v}

def extract_header_fields(md_file: Path):
    title, authors = None, ""
    with md_file.open(encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s: continue
            if not s.startswith("% "): break
            content = s[2:].strip()
            if title is None: title = content
            elif authors == "": authors = content; break
    if not title: title = md_file.stem
    return title, authors

def assert_safe_component(label: str, s: str):
    if any(ch in s for ch in ['/', '\\', '\x00']):
        sys.exit(f"ERROR: {label} contains a path separator or NUL. Value: {s!r}")

def write_sidecar(dest_md: Path, *, title: str, authors: str, original_filename: str, origin: dict):
    side = {
        "title": title,
        "authors": authors or None,
        "filename": dest_md.name,
        "original_filename": original_filename,
        **origin,
        "submitted_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    side = {k:v for k,v in side.items() if v}
    yml = dest_md.with_suffix(".yml")
    yml.write_text(yaml.safe_dump(side, sort_keys=False), encoding="utf-8")
    return yml

def ensure_repo():
    if not (ROOT / ".git").exists():
        sys.exit("ERROR: run from a preferredframe repo clone (root has .git).")
    try:
        run(["git","remote","get-url","upstream"], cwd=ROOT)
    except subprocess.CalledProcessError:
        run(["git","remote","add","upstream","https://github.com/siran/preferredframe"], cwd=ROOT)

def sync_main():
    run(["git","fetch","upstream","main"], cwd=ROOT)
    # Try to fast-forward main without switching your current branch
    try_run(["git","update-ref","refs/heads/main","refs/remotes/upstream/main"], cwd=ROOT)
    # If update-ref isn't allowed, ignore; we don't need to checkout main.

def branch_exists_remote(branch: str) -> bool:
    return bool(try_run(["git","ls-remote","--heads","origin",branch], cwd=ROOT).strip())

def list_worktrees():
    out = try_run(["git","worktree","list","--porcelain"], cwd=ROOT)
    wts, cur = [], {}
    for line in (out.splitlines() if out else []):
        if not line.strip():
            if cur: wts.append(cur); cur={}
            continue
        k, v = line.split(" ", 1)
        cur[k] = v.strip()
    if cur: wts.append(cur)
    return wts

def ensure_worktree(branch: str) -> Path:
    TMP.mkdir(parents=True, exist_ok=True)
    wt = TMP / branch
    wt_posix = wt.as_posix()

    # If registered, reuse it
    for ent in list_worktrees():
        if ent.get("worktree") == wt_posix:
            try_run(["git","fetch","origin"], cwd=ROOT)
            try_run(["git","-C", wt_posix, "pull", "--ff-only"])
            return wt

    # If dir exists but not registered as a worktree, clean it
    if wt.exists():
        shutil.rmtree(wt)

    base = f"origin/{branch}" if branch_exists_remote(branch) else "main"
    run(["git","worktree","add","-B", branch, wt_posix, base], cwd=ROOT)
    return wt

def parse_origin_owner():
    url = try_run(["git","remote","get-url","origin"], cwd=ROOT).strip()
    if not url: return ""
    m = re.match(r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", url)
    if m: return m.group("owner")
    m = re.match(r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", url)
    if m: return m.group("owner")
    return ""

def main():
    if len(sys.argv) < 2:
        print("usage: submit_pnpmd.py path/to/file.md [--use-gh]", file=sys.stderr)
        sys.exit(2)

    ap = argparse.ArgumentParser()
    ap.add_argument("src_path")
    ap.add_argument("--use-gh", action="store_true",
                    help="Use GitHub CLI if available (default: print PR URL)")
    args = ap.parse_args()

    src = Path(args.src_path).resolve()
    if not src.exists():
        print(f"File not found: {src}", file=sys.stderr); sys.exit(1)

    ensure_repo()
    sync_main()

    title, authors = extract_header_fields(src)
    assert_safe_component("Title", title)

    safe_branch = re.sub(r"[^A-Za-z0-9._-]+", "-", f"submit-{title}").strip("-") or "submit-paper"
    wt = ensure_worktree(safe_branch)

    # Write into the worktree
    prints_dir = wt / "preferredframe" / "prints"
    dest_dir   = prints_dir / title
    ext        = src.suffix or ".md"
    dest_md    = dest_dir / f"{title}{ext}"

    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest_md)

    origin = git_metadata(src) if in_git_repo(src) else {}
    sidecar = write_sidecar(dest_md, title=title, authors=authors,
                            original_filename=src.name, origin=origin)

    # Commit & push inside the worktree
    run(["git","add", str(dest_md), str(sidecar)], cwd=wt)
    run_allow_noop_commit(["git","commit","-m", f"Submit {title}"], cwd=wt)

    has_upstream = try_run(["git","rev-parse","--abbrev-ref","--symbolic-full-name","@{u}"], cwd=wt)
    if has_upstream:
        run(["git","push","origin", safe_branch], cwd=wt)
    else:
        run(["git","push","-u","origin", safe_branch], cwd=wt)

    owner = parse_origin_owner()
    compare = f"https://github.com/siran/preferredframe/compare/main...{owner}:{safe_branch}?expand=1" if owner else ""

    if args.use_gh:
        try:
            url = run(["gh","pr","create","--fill","--head", safe_branch], cwd=wt)
            print(f"PR created: {url}")
            _ = try_run(["gh","pr","merge","--squash","--auto"], cwd=wt)
            return
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass  # fall back to URL below

    print("Branch pushed.")
    print("Open this URL to create the PR:" if compare else "Open your fork and click 'Compare & pull request':")
    print(compare or "(unknown origin owner)")

if __name__ == "__main__":
    main()
