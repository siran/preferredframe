#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import shutil
import os

REPO = Path(__file__).resolve().parent.parent
SRC  = REPO / "src"
OUTD = REPO / "site"
PRINTS = REPO / "prints"

# set your repo/user here or via env
GITHUB_USER = os.environ.get("GITHUB_USER", "YourUser")
REPO_NAME   = os.environ.get("REPO_NAME", "PF")
BASE_URL    = f"https://{GITHUB_USER}.github.io/{REPO_NAME}"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def collect_items():
    items = []
    for folder in sorted(PRINTS.iterdir()):
        if not folder.is_dir():
            continue
        mds = [p for p in folder.glob("*.md") if p.name.lower() != "readme.md"]
        if not mds:
            continue
        md = mds[0]
        items.append({
            "title": md.stem,
            "folder": folder.name,
            "md_rel": str(md.relative_to(REPO)),
            "folder_rel": str(folder.relative_to(REPO)),
        })
    return items

def render_markdown(items):
    lines = [
        "# Preferred Frame",
        "",
        f"Latest publications as of {now_iso()}:",
        ""
    ]
    if not items:
        lines.append("> No prints yet.")
    else:
        for it in items:
            # full GitHub Pages URL
            url = f"{BASE_URL}/{it['folder_rel']}"
            lines.append(f"- [{it['title']}]({url})")
    return "\n".join(lines)

def copy_static():
    OUTD.mkdir(parents=True, exist_ok=True)
    for p in SRC.iterdir():
        if p.name in ("index.md","index.html"):
            continue
        dst = OUTD / p.name
        if p.is_file():
            shutil.copy2(p, dst)
        elif p.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(p, dst)

def build():
    items = collect_items()
    copy_static()
    md = render_markdown(items)
    html = md + "\n\n---\n\n" + """<meta charset="utf-8">

<style>
* {
    white-space: pre-wrap;
    font-family: monospace;
}
</style>
"""
    (OUTD / "index.html").write_text(html, encoding="utf-8")

if __name__ == "__main__":
    build()
