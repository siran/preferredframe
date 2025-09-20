#!/usr/bin/env python3
"""
print_submit.py — MR accept pipeline:
PNPMD validate -> PDF build -> Zenodo publish -> write sidecars -> push assets.

REQUIRED env:
  ZENODO_TOKEN    : Zenodo Personal Access Token (deposit:write + deposit:actions)
  ASSETS_PAT      : GitHub PAT with contents:write for siran/assets

OPTIONAL env:
  ZENODO_API      : https://zenodo.org/api (prod) or https://sandbox.zenodo.org/api
  BASE_URL        : e.g. https://preferredframe.com  (used in sidecar links)
  TAG_NAME        : release tag (for GitHub tag link in sidecar)
  GITHUB_REPOSITORY : owner/repo (auto-present in Actions, used in sidecar)

Usage (must pass --md):
  python3 src/print_submit.py --md prints/<Work>/<Title>.md [--title "Title"] [--concept <concept DOI>]
"""
from __future__ import annotations
import os, sys, json, shutil, subprocess, tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"

def die(msg: str, code: int = 1):
    sys.stderr.write(msg.strip() + "\n")
    sys.exit(code)

def run(cmd, cwd=None, capture=False):
    return subprocess.run(cmd, check=True, text=True, capture_output=capture, cwd=cwd)

def require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        die(f"Error: {name} is not set.")
    return v

def read_title_from_md(md: Path) -> str:
    first = md.read_text(encoding="utf-8").splitlines()[0].strip()
    return first[2:].strip() if first.startswith("% ") else die('Could not extract title')

def main():
    import argparse
    ap = argparse.ArgumentParser()
    args = ap.parse_args()

    ZENODO_TOKEN = require_env("ZENODO_TOKEN")
    ASSETS_PAT   = require_env("ASSETS_PAT")

    ZENODO_API = os.getenv("ZENODO_API", "https://zenodo.org/api")
    os.environ["ZENODO_API"] = ZENODO_API
    sys.stderr.write(f"[zenodo] API: {ZENODO_API}\n")

    md = Path(args.md).resolve()
    if not md.exists():
        die(f"Missing file: {md}")
    title = read_title_from_md(md)

    sys.stderr.write(f"[validate] {md}\n")
    run([sys.executable, str(SRC / "validate_pnpmd.py"), str(md)])


    # PDFs are made out of the pnpmd

    sys.stderr.write(f"[pandoc] -> {pdf}\n")
    run([sys.executable, str(SRC / "make_pdf.py"), str(md), str(pdf)])

    cmd = [
        sys.executable, str(SRC / "zenodo_publish.py"),
        "--primary", str(md),
        "--attach",  str(pdf),
        "--title",   title,
    ]
    if args.concept:
        cmd += ["--concept", args.concept]  # safe to include; ignored if zenodo_publish.py doesn't support
    sys.stderr.write("[zenodo] publishing…\n")
    pub = run(cmd, capture=True)
    try:
        pub_json = json.loads(pub.stdout)
    except Exception as e:
        die(f"Failed to parse zenodo_publish output: {e}\n{pub.stdout}")

    concept_doi = pub_json.get("concept_doi")
    version_doi = pub_json.get("version_doi")
    record_url  = pub_json.get("record_url", "")
    issued      = pub_json.get("issued", "")

    if not (concept_doi and version_doi):
        die(f"Zenodo publish did not return DOIs: {pub.stdout}")

    sys.stderr.write("[sidecar] writing version + latest…\n")
    env = os.environ.copy()
    if issued:
        env["ISSUED_DATE"] = issued
    run([
        sys.executable, str(SRC / "write_version_sidecar.py"),
        str(md), version_doi, concept_doi, record_url
    ], capture=False)

    sys.stderr.write("[assets] pushing PDF + source.yml to siran/assets…\n")
    doi_safe = version_doi.replace("/", "_")
    work_dir = md.parent
    source_yml = work_dir / "source.yml"
    if not source_yml.exists():
        die(f"Expected sidecar not found: {source_yml}")

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        clone_url = f"https://{ASSETS_PAT}@github.com/siran/assets.git"
        run(["git", "clone", "--depth=1", clone_url, "assets"], cwd=td)
        assets_repo = td / "assets"
        dest = assets_repo / "preferredframe" / title / doi_safe
        dest.mkdir(parents=True, exist_ok=True)

        shutil.copy2(pdf,       dest / f"{title}.pdf")
        shutil.copy2(source_yml, dest / "source.yml")

        run(["git", "config", "user.name", "preferredframe-bot"], cwd=assets_repo)
        run(["git", "config", "user.email", "bot@preferredframe.com"], cwd=assets_repo)
        run(["git", "add", str(dest.relative_to(assets_repo))], cwd=assets_repo)
        msg = f'Add PDF for "{title}" — {version_doi}'
        run(["git", "commit", "-m", msg], cwd=assets_repo)
        run(["git", "push"], cwd=assets_repo)

    print(json.dumps({
        "ok": True,
        "md": str(md),
        "pdf": str(pdf),
        "title": title,
        "concept_doi": concept_doi,
        "version_doi": version_doi,
        "record_url": record_url,
        "issued": issued,
        "assets_path": f'preferredframe/{title}/{doi_safe}/',
    }, indent=2))

if __name__ == "__main__":
    main()
