#!/usr/bin/env python3
"""
zenodo_publish.py

Create a Zenodo deposition, upload the primary artifact (the original .md),
attach additional files (.pnp.md, .html, .pdf, etc.), publish, and print a JSON
summary to stdout.

ENV:
  ZENODO_API   (e.g., https://sandbox.zenodo.org/api or https://zenodo.org/api)
  ZENODO_TOKEN (required)
"""
from __future__ import annotations
import os, sys, json, argparse
from pathlib import Path
from datetime import datetime, timezone
import requests

API   = os.getenv("ZENODO_API", "https://zenodo.org/api").rstrip("/")
TOKEN = os.getenv("ZENODO_TOKEN")

def die(msg: str):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)

def auth_params():
    return {"access_token": TOKEN}

def create_deposition(meta: dict) -> dict:
    r = requests.post(f"{API}/deposit/depositions",
                      params=auth_params(),
                      json={"metadata": meta})
    r.raise_for_status()
    return r.json()

def upload_file(dep: dict, path: Path):
    with path.open("rb") as fp:
        r = requests.post(dep["links"]["files"],
                          params=auth_params(),
                          data={"name": path.name},
                          files={"file": fp})
    r.raise_for_status()

def publish(dep_id: int) -> dict:
    r = requests.post(f"{API}/deposit/depositions/{dep_id}/actions/publish",
                      params=auth_params())
    r.raise_for_status()
    return r.json()

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--primary", required=True, help="Primary artifact (original .md)")
    p.add_argument("--attach",  action="append", default=[], help="Extra files to attach (.pnp.md, .html, .pdf, etc.)")
    p.add_argument("--title",   required=True)
    p.add_argument("--description", default="")
    p.add_argument("--creators", nargs="*", default=[], help='Authors: "Name|ORCID" or "Name"')
    p.add_argument("--keywords", nargs="*", default=[])
    p.add_argument("--license",  default="cc-by-4.0")
    return p.parse_args()

def main():
    if not TOKEN:
        die("ZENODO_TOKEN is required")

    a = parse_args()
    primary = Path(a.primary)
    if not primary.exists():
        die(f"missing primary file: {primary}")

    attaches = [Path(x) for x in a.attach]
    for f in attaches:
        if not f.exists():
            die(f"missing attachment: {f}")

    creators = []
    for c in a.creators:
        if "|" in c:
            name, orcid = c.split("|", 1)
            creators.append({"name": name.strip(), "orcid": orcid.strip()})
        else:
            creators.append({"name": c.strip()})

    meta = {
        "title": a.title,
        "upload_type": "publication",
        "publication_type": "article",
        "description": a.description or a.title,
        "creators": creators or [{"name": "Unknown"}],
        "keywords": a.keywords,
        "access_right": "open",
        "license": a.license,
    }

    dep = create_deposition(meta)
    dep_id = dep["id"]

    # upload primary first (the .md truth)
    upload_file(dep, primary)
    # then all formats (pnp.md, html, pdf, etc.)
    for f in attaches:
        upload_file(dep, f)

    pub = publish(dep_id)
    out = {
        "concept_doi": pub.get("conceptdoi"),
        "version_doi": pub.get("doi"),
        "record_url":  pub["links"]["html"],
        "issued":      datetime.now(timezone.utc).date().isoformat(),
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
