#!/usr/bin/env python3
"""
print_pipeline.py

Pipeline logic for PNPMD → Zenodo publication.

Behavior:
- Detect exactly one changed .md file under preferredframe/prints/.
- Validate it with validate_pnpmd.py.
- Build PDF, normalized .pnp.md, HTML.
- Publish to Zenodo.
- Write version sidecar.
- Push artifacts/provenance to siran/assets.

This script is invoked by GitHub Actions (print.yml) on push.
It can also be run locally by setting GITHUB_BEFORE and GITHUB_AFTER.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(cmd, cwd=None, check=True, text=False, env=None):
    p = subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        text=text,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    return p.stdout if text else p.stdout


def have_commit(sha: str) -> bool:
    try:
        run(["git", "cat-file", "-e", f"{sha}^{{commit}}"])
        return True
    except subprocess.CalledProcessError:
        return False


def fetch_commit(sha: str):
    # Try fetching just that commit
    for remote in ("origin", "upstream"):
        try:
            run(["git", "fetch", "--no-tags", "--depth", "1", remote, sha])
            if have_commit(sha):
                return
        except subprocess.CalledProcessError:
            pass
    # Last resort: unshallow origin
    try:
        run(["git", "fetch", "--no-tags", "--prune", "--progress", "--depth", "0", "origin"])
    except subprocess.CalledProcessError:
        pass


def ensure_commits(base: str, head: str):
    if not have_commit(base):
        fetch_commit(base)
    if not have_commit(head):
        fetch_commit(head)


def git_changed_paths(base: str, head: str) -> list[str]:
    ensure_commits(base, head)
    try:
        out = run(
            ["git", "-c", "core.quotepath=false", "diff", "--name-only", "-z", f"{base}...{head}"]
        )
    except subprocess.CalledProcessError:
        # fallback to merge-base..head
        mb = run(["git", "merge-base", base, head], text=True).strip()
        out = run(
            ["git", "-c", "core.quotepath=false", "diff", "--name-only", "-z", f"{mb}..{head}"]
        )
    parts = [p for p in out.split(b"\x00") if p]
    return [p.decode("utf-8", "strict") for p in parts]


def pick_one_md_under_prints(base: str, head: str) -> str:
    paths = git_changed_paths(base, head)
    md_files = [
        p for p in paths if p.startswith("preferredframe/prints/") and p.endswith(".md")
    ]
    print("Changed files:")
    for p in paths:
        print(p)
    print("\nChanged print .md files:")
    for p in md_files:
        print(p)

    if len(md_files) != 1:
        sys.exit(f"Exactly one .md must be changed (got {len(md_files)}).")

    return md_files[0]


def main():
    before = os.environ.get("GITHUB_BEFORE")
    after = os.environ.get("GITHUB_AFTER")

    if not before or not after:
        sys.exit("GITHUB_BEFORE and GITHUB_AFTER must be set.")

    md_repo_rel = pick_one_md_under_prints(before, after)
    md_path = ROOT / md_repo_rel

    # Step 1: validate PNPMD
    run([sys.executable, str(ROOT / ".scripts/src/validate_pnpmd.py"), str(md_path)], check=True)

    # Step 2: build PDF
    pdf_path = md_path.with_suffix(".pdf")
    run(
        [sys.executable, str(ROOT / ".scripts/src/make_pdf.py"), str(md_path), str(pdf_path)],
        check=True,
    )

    # Step 3: build normalized .pnp.md
    pnp_md = md_path.with_suffix(".pnp.md")
    run(
        [sys.executable, str(ROOT / ".scripts/src/make_pnpmd.py"), str(md_path), str(pnp_md)],
        check=True,
    )

    # Step 4: build HTML
    html_path = md_path.with_suffix(".html")
    run(
        [sys.executable, str(ROOT / ".scripts/src/make_html.py"), str(pnp_md), str(html_path)],
        check=True,
    )

    # Step 5: publish to Zenodo
    run(
        [sys.executable, str(ROOT / ".scripts/src/zenodo_publish.py"), "--primary", str(md_path),
         "--attach", str(pnp_md), "--attach", str(html_path), "--attach", str(pdf_path)],
        check=True,
    )

    # Step 6: write version sidecar
    run(
        [sys.executable, str(ROOT / ".scripts/src/write_version_sidecar.py"), str(md_path)],
        check=True,
    )

    print("Pipeline finished successfully.")


if __name__ == "__main__":
    main()
