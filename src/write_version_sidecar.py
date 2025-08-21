#!/usr/bin/env python3
"""
Write immutable per-version sidecar: prints/<Work>/versions/<doi_safe>.yml
Also refresh mutable prints/<Work>/source.yml (latest pointer).

Inputs via env/args; minimal, deterministic.
"""
from __future__ import annotations
from pathlib import Path
import os, sys, yaml, json, subprocess
from datetime import datetime, timezone

def die(m): print(m, file=sys.stderr); sys.exit(1)

def main():
    if len(sys.argv) < 4:
        die("usage: write_version_sidecar.py <md_path> <version_doi> <concept_doi> [record_url]")

    md_path     = Path(sys.argv[1]).resolve()
    version_doi = sys.argv[2]
    concept_doi = sys.argv[3]
    record_url  = sys.argv[4] if len(sys.argv) > 4 else ""

    work_dir = md_path.parent
    title = md_path.stem
    issued = os.getenv("ISSUED_DATE") or datetime.utcnow().date().isoformat()
    repo   = os.getenv("GITHUB_REPOSITORY", "")
    ref    = subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip()

    # Build human links (PF stubs)
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    rel_md   = md_path.relative_to(Path("prints")).as_posix()
    rel_pdf  = md_path.with_suffix(".pdf").relative_to(Path("prints")).as_posix()
    pf_md    = f"{base_url}/prints/{rel_md}"
    pf_mdui  = f"{base_url}/prints/{rel_md}.github"
    pf_pdf   = f"{base_url}/prints/{rel_pdf}"

    # GitHub tag (optional) from env TAG_NAME
    tag_url = ""
    tag = os.getenv("TAG_NAME", "")
    if tag:
        tag_url = f"https://github.com/{repo}/releases/tag/{tag}"

    # version sidecar (immutable)
    doi_safe = version_doi.replace("/", "_")
    versions_dir = work_dir / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    side = {
        "version_doi": version_doi,
        "concept_doi": concept_doi,
        "title": title,
        "issued": issued,
        "repo_ref": ref,
        "files": {
            "md": pf_md,
            "md_github": pf_mdui,
            "pdf": pf_pdf,
            "github_tag": tag_url or None,
            "zenodo_record": record_url or None,
        }
    }
    side = {k:v for k,v in side.items() if v is not None}
    out_yml = versions_dir / f"{doi_safe}.yml"
    out_yml.write_text(yaml.safe_dump(side, sort_keys=False), encoding="utf-8")

    # latest pointer (mutable)
    latest = {
        "concept_doi": concept_doi,
        "latest_version_doi": version_doi,
        "repo": repo,
        "path": str(md_path),
        "ref": ref,
        "imported_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "title": title,
    }
    (work_dir / "source.yml").write_text(yaml.safe_dump(latest, sort_keys=False), encoding="utf-8")

    print(str(out_yml))

if __name__ == "__main__":
    main()
