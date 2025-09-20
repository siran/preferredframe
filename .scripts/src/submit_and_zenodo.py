#!/usr/bin/env python3
"""
Minimal pipeline:
- Take .md file path (argv[1])
- Clone repo into a temp worktree
- Create branch from main
- Copy .md into prints/<TitleSlug>/
- Commit & push branch
- Call Zenodo API (sandbox or prod)
- Print DOI
"""

import os, sys, subprocess, tempfile, shutil, pathlib, re, json, requests

REPO_URL = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY','siran/preferredframe')}.git"
ZENODO_API = os.environ.get("ZENODO_API","https://sandbox.zenodo.org/api")
ZENODO_TOKEN = os.environ["ZENODO_TOKEN"]  # required

def sh(*cmd, cwd=None):
    print("+", " ".join(cmd))
    return subprocess.check_output(cmd, cwd=cwd).decode()

def slugify(title: str) -> str:
    return re.sub(r'[^A-Za-z0-9]+', '-', title).strip("-")

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: submit_and_zenodo.py path/to/file.md")
    src_md = pathlib.Path(sys.argv[1]).resolve()
    if not src_md.exists():
        sys.exit(f"No such file: {src_md}")

    title = src_md.stem
    slug = slugify(title)
    branch = f"PR_{slug}"

    tmp = tempfile.mkdtemp(prefix="pf_repo_")
    try:
        sh("git","clone",REPO_URL,tmp)
        sh("git","checkout","-b",branch,cwd=tmp)

        dest_dir = pathlib.Path(tmp)/"preferredframe"/"prints"/title
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_md = dest_dir/(title+".md")
        shutil.copy2(src_md, dest_md)

        sh("git","add",".",cwd=tmp)
        sh("git","commit","-m",f"Add {title} via submit_and_zenodo",cwd=tmp)
        sh("git","push","origin",branch,cwd=tmp)

        # Zenodo deposition
        headers = {"Authorization": f"Bearer {ZENODO_TOKEN}"}
        r = requests.post(f"{ZENODO_API}/deposit/depositions",
                          params={"access_token":ZENODO_TOKEN},
                          json={}, headers=headers)
        r.raise_for_status()
        dep = r.json()
        doi = dep["metadata"].get("prereserve_doi",{}).get("doi","(no doi)")
        print("Zenodo deposition created. DOI:", doi)

    finally:
        shutil.rmtree(tmp)

if __name__=="__main__":
    main()
