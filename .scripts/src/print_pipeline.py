#!/usr/bin/env python3
"""
print_pipeline.py

Pipeline logic for PNPMD → Zenodo publication.

Modes:
- --pr-check : PR gate (exactly one .md under preferredframe/prints + ASCII Title)
- default    : push build (validate -> pdf -> pnp.md -> html -> Zenodo -> sidecars -> assets)

Env (push mode):
  GITHUB_BEFORE, GITHUB_AFTER  : SHAs for diff
  ASSETS_PAT                   : PAT to push artifacts to siran/assets
  ZENODO_TOKEN, ZENODO_API     : Zenodo credentials
  BASE_URL, GITHUB_REPOSITORY  : optional, for sidecars
"""
import os, subprocess, sys, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run(cmd, cwd=None, check=True, text=False, env=None):
    p = subprocess.run(
        cmd, cwd=cwd, check=check, text=text,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    return p.stdout if text else p.stdout

def have_commit(sha: str) -> bool:
    try:
        run(["git", "cat-file", "-e", f"{sha}^{{commit}}"])
        return True
    except subprocess.CalledProcessError:
        return False

def fetch_commit(sha: str):
    for remote in ("origin", "upstream"):
        try:
            run(["git", "fetch", "--no-tags", "--depth", "1", remote, sha])
            if have_commit(sha):
                return
        except subprocess.CalledProcessError:
            pass
    try:
        run(["git", "fetch", "--no-tags", "--prune", "--progress", "--depth", "0", "origin"])
    except subprocess.CalledProcessError:
        pass

def ensure_commits(base: str, head: str):
    if not have_commit(base): fetch_commit(base)
    if not have_commit(head): fetch_commit(head)

def git_changed_paths(base: str, head: str) -> list[str]:
    ensure_commits(base, head)
    try:
        out = run(["git","-c","core.quotepath=false","diff","--name-only","-z", f"{base}...{head}"])
    except subprocess.CalledProcessError:
        mb = run(["git","merge-base", base, head], text=True).strip()
        out = run(["git","-c","core.quotepath=false","diff","--name-only","-z", f"{mb}..{head}"])
    parts = [p for p in out.split(b"\x00") if p]
    return [p.decode("utf-8","strict") for p in parts]

def pick_one_md_under_prints(base: str, head: str) -> str:
    paths = git_changed_paths(base, head)
    md_files = [p for p in paths if p.startswith("preferredframe/prints/") and p.endswith(".md")]
    print("Changed files:"); [print(p) for p in paths]
    print("\nChanged print .md files:"); [print(p) for p in md_files]
    if len(md_files) != 1:
        sys.exit(f"Exactly one .md must be changed (got {len(md_files)}).")
    return md_files[0]

def read_title(md_path: Path) -> str:
    for ln in md_path.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s: continue
        if s.startswith("% "): return s[2:].strip()
        break
    return md_path.stem

def assert_ascii_title(title: str):
    if any(ord(ch) > 127 for ch in title):
        sys.exit("Title must be ASCII-only (replace Unicode like ‘–’ with '-').")

def pr_check(base: str, head: str):
    md_repo_rel = pick_one_md_under_prints(base, head)
    md_path = ROOT / md_repo_rel
    title = read_title(md_path)
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
        base = os.environ.get("BASE_SHA") or os.environ.get("GITHUB_BEFORE") or ""
        head = os.environ.get("HEAD_SHA") or os.environ.get("GITHUB_AFTER") or ""
        if not base or not head:
            sys.exit("BASE_SHA/HEAD_SHA (or GITHUB_BEFORE/GITHUB_AFTER) must be set for --pr-check.")
        return pr_check(base, head)

    before = os.environ.get("GITHUB_BEFORE")
    after  = os.environ.get("GITHUB_AFTER")
    if not before or not after:
        sys.exit("GITHUB_BEFORE and GITHUB_AFTER must be set.")

    md_repo_rel = pick_one_md_under_prints(before, after)
    md_path = ROOT / md_repo_rel

    # Step 1: validate PNPMD
    run([sys.executable, str(ROOT / ".scripts/src/validate_pnpmd.py"), str(md_path)], check=True)

    # Step 2: build PDF (from original)
    pdf_path = md_path.with_suffix(".pdf")
    run([sys.executable, str(ROOT / ".scripts/src/make_pdf.py"), str(md_path), str(pdf_path)], check=True)

    # Step 3: build normalized .pnp.md
    pnp_md = md_path.with_suffix(".pnp.md")
    run([sys.executable, str(ROOT / ".scripts/src/make_pnpmd.py"), str(md_path), str(pnp_md)], check=True)

    # Step 4: build HTML (from .pnp.md)
    html_path = md_path.with_suffix(".html")
    run([sys.executable, str(ROOT / ".scripts/src/make_html.py"), str(pnp_md), str(html_path)], check=True)

    # Step 5: publish to Zenodo
    title = read_title(md_path)
    assert_ascii_title(title)
    run([
        sys.executable, str(ROOT / ".scripts/src/zenodo_publish.py"),
        "--primary", str(md_path),
        "--attach",  str(pnp_md),
        "--attach",  str(html_path),
        "--attach",  str(pdf_path),
        "--title",   title
    ], check=True)

    # Step 6: write version sidecar
    run([sys.executable, str(ROOT / ".scripts/src/write_version_sidecar.py"), str(md_path)], check=True)

    # Step 7: push .html/.pdf + source.yml to siran/assets (if PAT present)
    assets_pat = os.environ.get("ASSETS_PAT", "")
    if assets_pat:
        import tempfile, shutil
        versions_dir = md_path.parent / "versions"
        if versions_dir.exists():
            latest = sorted(versions_dir.glob("*.yml"))
            if latest:
                doi_safe = latest[-1].stem
                with tempfile.TemporaryDirectory() as td:
                    td = Path(td)
                    clone_url = f"https://{assets_pat}@github.com/siran/assets.git"
                    run(["git","clone","--depth=1", clone_url, "assets"], cwd=td)
                    assets_repo = td / "assets"
                    dest = assets_repo / "preferredframe" / title / doi_safe
                    dest.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(html_path, dest / f"{title}.html")
                    shutil.copy2(pdf_path,  dest / f"{title}.pdf")
                    src_yml = md_path.parent / "source.yml"
                    if src_yml.exists():
                        shutil.copy2(src_yml, dest / "source.yml")
                    run(["git","config","user.name","preferredframe-bot"], cwd=assets_repo)
                    run(["git","config","user.email","bot@preferredframe.com"], cwd=assets_repo)
                    run(["git","add", str(dest.relative_to(assets_repo))], cwd=assets_repo)
                    run(["git","commit","-m", f'Add assets for "{title}" — {doi_safe}'], cwd=assets_repo)
                    run(["git","push"], cwd=assets_repo)

    print("Pipeline finished successfully.")

if __name__ == "__main__":
    main()
