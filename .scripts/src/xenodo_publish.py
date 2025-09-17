#!/usr/bin/env python3
"""
Zenodo publisher:
- If --concept supplied: create NEW VERSION under that concept.
- Else: create NEW deposition (first version + concept DOI).
- Attach both files (md + pdf).
- Output JSON: {concept_doi, version_doi, record_url, issued}

Requires: ZENODO_TOKEN env. Optional: ZENODO_API_URL.
"""
from __future__ import annotations
import os, sys, json, argparse
from pathlib import Path
import requests
from datetime import datetime, timezone

API = os.getenv("ZENODO_API_URL", "https://zenodo.org/api")
TOKEN = os.getenv("ZENODO_TOKEN")

def die(msg): print(f"ERROR: {msg}", file=sys.stderr); sys.exit(1)
def headers(): return {"Authorization": f"Bearer {TOKEN}"}

def create_deposition(meta):
    r = requests.post(f"{API}/deposit/depositions", params={"access_token": TOKEN}, json={"metadata": meta})
    r.raise_for_status()
    return r.json()

def new_version(conceptrecid: int):
    r = requests.post(f"{API}/deposit/depositions/{conceptrecid}/actions/newversion",
                      params={"access_token": TOKEN})
    r.raise_for_status()
    latest = requests.get(r.json()["links"]["latest_draft"], params={"access_token": TOKEN})
    latest.raise_for_status()
    return latest.json()

def upload(dep, path: Path):
    with path.open("rb") as fp:
        r = requests.post(dep["links"]["files"], params={"access_token": TOKEN},
                          data={"name": path.name}, files={"file": fp})
    r.raise_for_status()

def publish(dep_id: int):
    r = requests.post(f"{API}/deposit/depositions/{dep_id}/actions/publish",
                      params={"access_token": TOKEN})
    r.raise_for_status()
    return r.json()

def lookup_conceptrecid(concept_doi: str) -> int:
    # Use records search to find concept recid by DOI
    q = requests.get(f"{API}/records", params={"q": f"doi:{concept_doi}"}, headers=headers())
    q.raise_for_status()
    hits = q.json().get("hits", {}).get("hits", [])
    if not hits: die(f"Concept DOI not found: {concept_doi}")
    return hits[0]["conceptrecid"]

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--md", required=True)
    p.add_argument("--pdf", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--creators", nargs="*", default=[])  # "Name|ORCID"
    p.add_argument("--keywords", nargs="*", default=[])
    p.add_argument("--license", default="cc-by-4.0")
    p.add_argument("--concept", default=None)            # concept DOI to version
    return p.parse_args()

def main():
    if not TOKEN: die("ZENODO_TOKEN required")
    a = parse_args()
    md, pdf = Path(a.md), Path(a.pdf)
    if not md.exists() or not pdf.exists(): die("missing input files")

    creators = []
    for c in a.creators:
        if "|" in c:
            n,o = c.split("|",1); creators.append({"name": n.strip(), "orcid": o.strip()})
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

    if a.concept:
        conceptrecid = lookup_conceptrecid(a.concept)
        dep = new_version(conceptrecid)
    else:
        dep = create_deposition(meta)

    dep_id = dep["id"]
    # refresh metadata (title may change)
    r = requests.put(f"{API}/deposit/depositions/{dep_id}",
                     params={"access_token": TOKEN}, json={"metadata": meta})
    r.raise_for_status()

    upload(dep, md)
    upload(dep, pdf)

    pub = publish(dep_id)
    out = {
        "concept_doi": pub.get("conceptdoi"),
        "version_doi": pub.get("doi"),
        "record_url": pub["links"]["html"],
        "issued": datetime.now(timezone.utc).date().isoformat(),
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
