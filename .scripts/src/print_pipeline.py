#!/usr/bin/env python3
"""
print_pipeline.py

Purpose:
- Pure-Python CI orchestrator for the PNPMD → Zenodo pipeline.
- Keeps workflow YAML minimal; all logic and I/O lives here.

Behavior:
1) Detect exactly one changed Markdown file under preferredframe/prints/** on push.
2) Enforce ASCII-only Title (first '% ' line or stem).
3) Call existing build scripts:
   - validate_pnpmd.py
   - make_pdf.py
   - make_pnpmd.py
   - make_html.py
4) Publish to Zenodo via zenodo_publish.py; parse JSON for DOIs/URL.
5) Write version sidecar via write_version_sidecar.py.
6) Clone siran/assets and push artifacts+provenance.

Env required (injected by workflow):
- GITHUB_REPOSITORY (owner/repo)
- GITHUB_BEFORE (sha)
- GITHUB_AFTER (sha)
- ASSETS_PAT
- ZENODO_TOKEN
- ZENODO_API
- BASE_URL
"""

from __future__ import annotations
import os, sys, subprocess, json, shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root

def run(cmd, cwd=None, check=True, text=True):
    p = subprocess.run(cmd, cwd=cwd, check=check, text=text,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout

def die(msg: str, code: int = 1):
    print(msg, file=sys.stderr)
    sys.exit(code)

def ensure_env(name: str) -> str:
    v = os.environ.get(name, "")
    if not v:
        die(f"ERROR: environment variable {name} is required")
    return v

def git_changed_md(before: str, after: str) -> list[str]:
    # NUL-separated, no C-quoting; filter to one *.md
    cmd = ["git","-c","core.quotepath=false","diff","--name-only","-z",
           "--diff-filter=ACMRT", before, after,
           "--", "preferredframe/prints/", ":!**/README.md"]
    out = run(cmd)
    files = [p for p in out.split("\0") if p]
    md = [p for p in files if p.endswith(".md") and p.startswith("preferredframe/prints/")]
    return md

def extract_title(md_path: Path) -> str:
    with md_path.open("r", encoding="utf-8") as f:
        first = f.readline().strip()
    return first[2:].strip() if first.startswith("% ") else md_path.stem

def enforce_ascii_title(title: str):
    try:
        title.encode("ascii")
    except UnicodeEncodeError:
        die(f"ERROR: Title must be ASCII-only (replace Unicode like ‘–’ with '-'). Found: {title!r}")

def main():
    # Inputs
    repo = ensure_env("GITHUB_REPOSITORY")
    before = ensure_env("GITHUB_BEFORE")
    after  = ensure_env("GITHUB_AFTER")
    assets_pat = ensure_env("ASSETS_PAT")
    zenodo_token = ensure_env("ZENODO_TOKEN")
    zenodo_api = ensure_env("ZENODO_API")
    _ = ensure_env("BASE_URL")  # reserved if needed by your scripts

    # 1) Detect changed .md
    md_files = git_changed_md(before, after)
    print("Changed files (filtered to .md under prints):")
    for p in md_files: print(p)
    if len(md_files) != 1:
        die(f"Exactly one .md must change per push (got {len(md_files)}).")
    md_rel = md_files[0]
    md_path = ROOT / md_rel

    # 2) Extract + enforce ASCII Title
    title = extract_title(md_path)
    enforce_ascii_title(title)

    # Derived targets
    pdf_path   = md_path.with_suffix(".pdf")
    pnp_md     = md_path.with_suffix(".pnp.md")
    html_path  = md_path.with_suffix(".html")

    # 3) Validate + build artifacts (delegate to your existing scripts)
    print("Validating PNPMD…")
    run(["python",".scripts/src/validate_pnpmd.py", str(md_path)])

    print("Building PDF…")
    run(["python",".scripts/src/make_pdf.py", str(md_path), str(pdf_path)])

    print("Building PNPMD normalized (.pnp.md)…")
    run(["python",".scripts/src/make_pnpmd.py", str(md_path), str(pnp_md)])

    print("Building HTML…")
    run(["python",".scripts/src/make_html.py", str(pnp_md), str(html_path)])

    # 4) Publish to Zenodo
    print("Publishing to Zenodo…")
    env = os.environ.copy()
    env["ZENODO_TOKEN"] = zenodo_token
    env["ZENODO_API"]   = zenodo_api
    p = subprocess.run(
        ["python",".scripts/src/zenodo_publish.py",
         "--primary", str(md_path),
         "--attach",  str(pnp_md),
         "--attach",  str(html_path),
         "--attach",  str(pdf_path),
         "--title",   title],
        env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if p.returncode != 0:
        sys.stderr.write(p.stderr)
        die("zenodo_publish.py failed")
    try:
        z = json.loads(p.stdout)
    except Exception as e:
        print(p.stdout)
        die(f"zenodo_publish.py did not return JSON: {e}")
    concept_doi = z["concept_doi"]
    version_doi = z["version_doi"]
    record_url  = z["record_url"]
    print(f"Zenodo OK: version={version_doi} concept={concept_doi}")
    doi_safe = version_doi.replace("/", "_")

    # 5) Write version sidecar in repo
    print("Writing version sidecar…")
    run(["python",".scripts/src/write_version_sidecar.py",
         str(md_path), version_doi, concept_doi, record_url])

    # 6) Push artifacts+provenance to siran/assets
    print("Pushing artifacts to siran/assets…")
    assets_dir = ROOT / "assets"
    if assets_dir.exists():
        run(["rm","-rf", str(assets_dir)])
    # use HTTPS with PAT
    run(["git","config","--global","user.name","preferredframe-bot"])
    run(["git","config","--global","user.email","bot@preferredframe.com"])
    run(["git","clone", f"https://{assets_pat}@github.com/siran/assets.git", str(assets_dir)])

    dest_dir = assets_dir / "preferredframe" / title / doi_safe
    dest_dir.mkdir(parents=True, exist_ok=True)

    # copy artifacts
    import shutil as _sh
    _sh.copy2(pdf_path,  dest_dir / f"{title}.pdf")
    _sh.copy2(html_path, dest_dir / f"{title}.html")

    src_dir = md_path.parent
    _sh.copy2(src_dir / "source.yml",                 dest_dir / "source.yml")
    _sh.copy2(src_dir / "versions" / f"{doi_safe}.yml", dest_dir / f"{doi_safe}.yml")

    # commit and push
    run(["git","-C", str(assets_dir), "add", str(dest_dir.relative_to(assets_dir))])
    run(["git","-C", str(assets_dir), "commit","-m", f'Publish "{title}" — {versio_]()
