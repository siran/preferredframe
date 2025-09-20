#!/usr/bin/env python3
"""
submit_pnpmd.py

Usage:
  python .scripts/src/submit_pnpmd.py 'path/to/My Paper.md' [--use-gh] [--no-preflight]

Behavior:
- Reads local file, extracts Title from first '% ' line (Authors from second).
- Writes to preferredframe/prints/<Title>/<Title>.<ext> with sidecar <Title>/<Title>.sidecar.yml (UTF-8).
- If source is in a git repo, records origin repo/commit/author/email/date.
- Uses a dedicated git worktree per submission branch (no touching your main).
- Always bases the submission branch on upstream/main (clean).
- Pushes the branch; default prints compare URL. With --use-gh, tries GitHub CLI.
- Preflight: runs the PR gate locally (same as CI) unless --no-preflight.
- Idempotent: safe re-runs. Cleans the temporary worktree at the end.

Strictness:
- Title/destination filename are NOT modified.
- Rejects: path separators, NUL, OS-problem chars, and ANY non-ASCII in Title.
- Branch name is derived from Title via safe substitution (invalid ref chars → '-').
"""

import argparse, subprocess, sys, shutil, re, os
from pathlib import Path
import datetime, yaml

ROOT = Path(__file__).resolve().parents[2]
WT_BASE = ROOT / ".tmp" / "submit_worktrees"

def run(cmd, cwd=None, check=True, text=True, env=None):
    return subprocess.run(cmd, cwd=cwd, check=check, text=text, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()

def try_run(cmd, cwd=None):
    try: return run(cmd, cwd=cwd)
    except Exception: return ""

def run_allow_noop_commit(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0 and "nothing to commit" not in (p.stdout + p.stderr).lower():
        raise subprocess.CalledProcessError(p.returncode, cmd, p.stdout, p.stderr)
    return p.stdout.strip()

def in_git_repo(path: Path) -> bool:
    try:
        run(["git","-C", str(path.parent), "rev-parse","--is-inside-work-tree"]); return True
    except subprocess.CalledProcessError: return False

def git_metadata(path: Path) -> dict:
    md = {}
    try:
        top = run(["git","-C", str(path.parent), "rev-parse","--show-toplevel"])
        rel = str(path.resolve().relative_to(Path(top)))
        md["origin_repo"]   = run(["git","-C", top, "config","--get","remote.origin.url"])
        md["origin_commit"] = run(["git","-C", top, "log","-n1","--pretty=%H","--", rel])
        md["origin_author"] = run(["git","-C", top, "log","-n1","--pretty=%an","--", rel])
        md["origin_email"]  = run(["git","-C", top, "log","-n1","--pretty=%ae","--", rel])
        md["origin_date"]   = run(["git","-C", top, "log","-n1","--pretty=%aI","--", rel])
    except Exception: pass
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
    forbidden = set('/\\\x00:*?"<>|')
    if any(ch in forbidden for ch in s):
        sys.exit(f"ERROR: {label} contains forbidden characters. Value: {s!r}")
    if any(ord(ch) > 127 for ch in s):
        sys.exit(f"ERROR: {label} must be ASCII-only (replace Unicode like ‘–’ with '-'). Value: {s!r}")

def write_sidecar(dest_md: Path, *, title: str, authors: str, original_filename: str, origin: dict):
    side = {
        "title": title,
        "authors": authors or None,
        "filename": dest_md.name,          # stored name (Title.ext)
        "original_filename": original_filename,
        **origin,
        "submitted_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    side = {k:v for k,v in side.items() if v}
    yml = dest_md.parent / f"{title}.sidecar.yml"  # <Title>.sidecar.yml
    yml.write_text(yaml.safe_dump(side, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return yml

def ensure_repo():
    if not (ROOT / ".git").exists():
        sys.exit("ERROR: run from a preferredframe repo clone (root has .git).")
    try: run(["git","remote","get-url","upstream"], cwd=ROOT)
    except subprocess.CalledProcessError:
        run(["git","remote","add","upstream","https://github.com/siran/preferredframe"], cwd=ROOT)

def sync_upstream_main():
    run(["git","fetch","upstream","main"], cwd=ROOT)

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
    WT_BASE.mkdir(parents=True, exist_ok=True)
    wt = WT_BASE / branch
    wt_posix = wt.as_posix()
    for ent in list_worktrees():
        if ent.get("worktree") == wt_posix:
            run(["git","fetch","upstream","main"], cwd=ROOT)
            run(["git","-C", wt_posix, "fetch", "upstream", "main"])
            run(["git","-C", wt_posix, "checkout", "-B", branch, "upstream/main"])
            run(["git","-C", wt_posix, "reset", "--hard", "upstream/main"])
            return wt
    if wt.exists(): shutil.rmtree(wt)
    run(["git","fetch","upstream","main"], cwd=ROOT)
    run(["git","worktree","add","-B", branch, wt_posix, "upstream/main"], cwd=ROOT)
    return wt

def cleanup_worktree(wt: Path):
    wt_posix = wt.as_posix()
    _ = try_run(["git","worktree","remove","--force", wt_posix], cwd=ROOT)
    _ = try_run(["git","worktree","prune"], cwd=ROOT)
    if wt.exists(): shutil.rmtree(wt, ignore_errors=True)

def parse_origin_owner():
    url = try_run(["git","remote","get-url","origin"], cwd=ROOT).strip()
    if not url: return ""
    m = re.match(r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", url)
    if m: return m.group("owner")
    m = re.match(r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", url)
    if m: return m.group("owner")
    return ""

def push_with_retry(branch: str, cwd: Path):
    try:
        has_upstream = try_run(["git","rev-parse","--abbrev-ref","--symbolic-full-name","@{u}"], cwd=cwd)
        if has_upstream: run(["git","push","origin", branch], cwd=cwd)
        else:            run(["git","push","-u","origin", branch], cwd=cwd)
    except subprocess.CalledProcessError:
        run(["git","push","--force-with-lease","-u","origin", branch], cwd=cwd)

def pr_preflight(wt: Path):
    base_sha = run(["git","rev-parse","upstream/main"], cwd=ROOT)
    head_sha = run(["git","rev-parse","HEAD"], cwd=wt)
    env = os.environ.copy()
    env["BASE_SHA"] = base_sha
    env["HEAD_SHA"] = head_sha
    p = subprocess.run(
        ["python", ".scripts/src/print_pipeline.py", "--pr-check"],
        cwd=ROOT, env=env, text=True
    )
    if p.returncode != 0:
        sys.exit("Preflight PR-check failed. Fix the issues above and re-run.")

def make_branch_name(title: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", title)
    safe = re.sub(r"-{2,}", "-", safe).strip("-")
    if not safe:
        sys.exit("ERROR: Title produced an empty branch name after sanitization for branch.")
    branch = f"submit-{safe}"
    try:
        run(["git", "check-ref-format", "--branch", branch], cwd=ROOT)
    except subprocess.CalledProcessError:
        sys.exit(
            "ERROR: Branch name derived from Title is not a valid git branch name.\n"
            f"Derived: {branch!r}\n"
            "Please adjust the Title to an ASCII, ref-safe form and re-run."
        )
    return branch

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src_path")
    ap.add_argument("--use-gh", action="store_true",
                    help="Use GitHub CLI if available (default: print PR URL)")
    ap.add_argument("--no-preflight", action="store_true",
                    help="Skip local PR gate preflight (not recommended)")
    args = ap.parse_args()

    src = Path(args.src_path).resolve()
    if not src.exists():
        print(f"File not found: {src}", file=sys.stderr); sys.exit(1)

    ensure_repo()
    sync_upstream_main()

    title, authors = extract_header_fields(src)
    assert_safe_component("Title", title)

    safe_branch = make_branch_name(title)

    wt = ensure_worktree(safe_branch)

    try:
        prints_dir = wt / "preferredframe" / "prints"
        dest_dir   = prints_dir / title
        ext        = src.suffix or ".md"
        dest_md    = dest_dir / f"{title}{ext}"

        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest_md)

        origin = git_metadata(src) if in_git_repo(src) else {}
        sidecar = write_sidecar(dest_md, title=title, authors=authors,
                                original_filename=src.name, origin=origin)

        run(["git","add", str(dest_md), str(sidecar)], cwd=wt)
        run_allow_noop_commit(["git","commit","-m", f"Submit {title}"], cwd=wt)

        push_with_retry(safe_branch, wt)

        if not args.no_preflight:
            pr_preflight(wt)

        owner = parse_origin_owner()
        compare = f"https://github.com/siran/preferredframe/compare/main...{owner}:{safe_branch}?expand=1" if owner else ""

        if args.use_gh:
            try:
                url = run(["gh","pr","create","--fill","--head", safe_branch], cwd=wt)
                print(f"PR created: {url}")
                _ = try_run(["gh","pr","merge","--squash","--auto"], cwd=wt)
            except (FileNotFoundError, subprocess.CalledProcessError):
                print("Branch pushed.\nOpen this URL to create the PR:")
                print(compare or "(unknown origin owner)")
        else:
            print("Branch pushed.\nOpen this URL to create the PR:")
            print(compare or "(unknown origin owner)")
    finally:
        cleanup_worktree(wt)

if __name__ == "__main__":
    main()
