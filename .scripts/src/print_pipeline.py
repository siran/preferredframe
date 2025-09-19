#!/usr/bin/env python3
"""
print_pipeline.py

Modes:
- PR gate (CI):    python print_pipeline.py --pr-check
  * Uses BASE_SHA, HEAD_SHA (env).
  * Ensures exactly one .md changed under preferredframe/prints/**.
  * Enforces ASCII-only Title (first '% ' line or stem). Exit 1 with clear msg if not.

- Push pipeline:   python print_pipeline.py
  * Uses GITHUB_BEFORE, GITHUB_AFTER (env).
  * Detects the one changed .md, validates ASCII Title, calls builders, publishes to Zenodo,
    writes version sidecar, pushes artifacts to siran/assets.

No YAML metaprogramming; all logic here.
"""

from __future__ import annotations
import os, sys, subprocess, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run(cmd, cwd=None, check=True, text=False, env=None):
    p = subprocess.run(cmd, cwd=cwd, check=check, text=text,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    return p.stdout if text else p.stdout

def die(msg: str, code: int = 1):
    print(msg, file=sys.stderr)
    sys.exit(code)

def need(name: str) -> str:
    v = os.environ.get(name, "")
    if not v:
        die(f"ERROR: environment variable {name} is required")
    return v

def git_changed_paths(base: str, head: str) -> list[str]:
    # NUL-separated, no C-quoting → safe UTF-8
    out = run(["git","-c","core.quotepath=false","diff","--name-only","-z", f"{base}...{head}"])
    parts = [p for p in out.split(b"\x00") if p]
    return [p.decode("utf-8", "strict") for p in parts]

def pick_one_md_under_prints(base: str, head: str) -> Path:
    paths = git_changed_paths(base, head)
    print("Changed files:")
    for p in paths: print(p)
    md = [p for p in paths if p.startswith("preferredframe/prints/") and p.endswith(".md")]
    print("\nChanged PNPMD .md files:")
    for p in md: print(p)
    if len(md) != 1:
        die(f"Exactly one .md must be changed (got {len(md)}).")
    return ROOT / md[0]

def extract_title(md_path: Path) -> str:
    with md_path.open("r", encoding="utf-8") as f:
        first = f.readline().strip()
    return first[2:].strip() if first.startswith("% ") else md_path.stem

def enforce_ascii_title(title: str):
    try:
        title.encode("ascii")
    except UnicodeEncodeError:
        die(f"ERROR: Title must be ASCII-only (replace Unicode like ‘–’ with '-'). Found: {title!r}")

def build_and_publish(md_path: Path, title: str):
    pdf_path  = md_path.with_suffix(".pdf")
    pnp_md    = md_path.with_suffix(".pnp.md")
    html_path = md_path.with_suffix(".html")

    print("Validating PNPMD…")
    run(["python",".scripts/src/validate_pnpmd.py", str(md_path)], text=True)

    print("Building PDF…")
    run(["python",".scripts/src/make_pdf.py", str(md_path), str(pdf_path)], text=True)

    print("Building PNPMD normalized (.pnp.md)…")
    run(["python",".scripts/src/make_pnpmd.py", str(md_path), str(pnp_md)], text=True)

    print("Building HTML…")
    run(["python",".scripts/src/make_html.py", str(pnp_md), str(html_path)], text=True)

    print("Publishing to Zenodo…")
    zenodo_token = need("ZENODO_TOKEN")
    zenodo_api   = need("ZENODO_API")
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
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
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
    doi_safe = version_doi.replace("/", "_")
    print(f"Zenodo OK: version={version_doi} concept={concept_doi}")

    print("Writing version sidecar…")
    run(["python",".scripts/src/write_version_sidecar.py",
         str(md_path), version_doi, concept_doi, record_url], text=True)

    print("Pushing artifacts to siran/assets…")
    assets_pat = need("ASSETS_PAT")
    assets_dir = ROOT / "assets"
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
    run(["git","config","--global","user.name","preferredframe-bot"], text=True)
    run(["git","config","--global","user.email","bot@preferredframe.com"], text=True)
    run(["git","clone", f"https://{assets_pat}@github.com/siran/assets.git", str(assets_dir)], text=True)

    dest = assets_dir / "preferredframe" / title / doi_safe
    dest.mkdir(parents=True, exist_ok=True)

    shutil.copy2(pdf_path,  dest / f"{title}.pdf")
    shutil.copy2(html_path, dest / f"{title}.html")
    src_dir = md_path.parent
    shutil.copy2(src_dir / "source.yml",                      dest / "source.yml")
    shutil.copy2(src_dir / "versions" / f"{doi_safe}.yml",    dest / f"{doi_safe}.yml")

    run(["git","-C", str(assets_dir), "add", str(dest.relative_to(assets_dir))], text=True)
    run(["git","-C", str(assets_dir), "commit","-m", f'Publish "{title}" — {version_doi} (primary: .md)'], text=True)
    run(["git","-C", str(assets_dir), "push"], text=True)

def main():
    args = sys.argv[1:]
    if args and args[0] == "--pr-check":
        base = need("BASE_SHA")
        head = need("HEAD_SHA")
        md_path = pick_one_md_under_prints(base, head)
        title = extract_title(md_path)
        enforce_ascii_title(title)
        print("PR gate OK.")
        return

    # push mode
    before = need("GITHUB_BEFORE")
    after  = need("GITHUB_AFTER")
    md_path = pick_one_md_under_prints(before, after)
    title = extract_title(md_path)
    enforce_ascii_title(title)
    build_and_publish(md_path, title)
    print("Push pipeline OK.")

if __name__ == "__main__":
    main()
