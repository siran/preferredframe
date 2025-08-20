#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import shutil, os

REPO   = Path(__file__).resolve().parent.parent
SRC    = REPO / "src"
OUTD   = REPO / "site"
PRINTS = REPO / "prints"

# Adjust these three to your repo
GITHUB_USER = os.environ.get("GITHUB_USER", "YourUser")
REPO_NAME   = os.environ.get("REPO_NAME", "PF")
GH_BRANCH   = os.environ.get("GH_BRANCH", "main")

BASE_URL = f"https://{GITHUB_USER}.github.io/{REPO_NAME}"   # site root
GH_URL   = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/blob/{GH_BRANCH}"
RAW_URL  = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{GH_BRANCH}"

def now_iso():
    # New York time
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M DST")

def is_dot(name: str) -> bool:
    return name.startswith(".")

def read_title(md_abs: Path) -> str:
    try:
        with md_abs.open("r", encoding="utf-8") as f:
            first = f.readline().rstrip("\n")
        if first.startswith("% "):
            return first[2:].strip()
    except Exception:
        pass
    return md_abs.stem

def collect_items():
    items = []
    for folder in sorted(PRINTS.iterdir()):
        if not folder.is_dir() or is_dot(folder.name):
            continue
        md_files = [p for p in folder.glob("*.md") if p.name.lower() != "readme.md"]
        if not md_files:
            continue
        md = md_files[0]
        items.append({
            "title": read_title(md),
            "folder": folder,
            "md": md,
        })
    return items

def render_markdown_index(items):
    lines = ["## Latest publications", ""]
    if not items:
        lines.append("> No prints yet.")
        return "\n".join(lines)

    for it in items[:10]:
        title = it["title"]
        folder_url = f"{BASE_URL}/prints/{it['folder'].name}/"
        lines.append(f"- [{title}]({folder_url})")
    return "\n".join(lines)

def copy_static():
    OUTD.mkdir(parents=True, exist_ok=True)
    for p in SRC.iterdir():
        if p.name in ("header.html","footer.html","coda.html"):
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

    header = (SRC/"header.html").read_text(encoding="utf-8") if (SRC/"header.html").exists() else ""
    footer = (SRC/"footer.html").read_text(encoding="utf-8") if (SRC/"footer.html").exists() else ""
    coda   = (SRC/"coda.html").read_text(encoding="utf-8")   if (SRC/"coda.html").exists() else ""

    # index.html for root
    md_content = render_markdown_index(items)
    full_page = "\n".join([header, md_content, footer, f"\n(updated: {now_iso()})\n", coda])
    (OUTD/"index.html").write_text(full_page, encoding="utf-8")

    # per-paper pages
    for it in items:
        folder_out = OUTD / "prints" / it["folder"].name
        folder_out.mkdir(parents=True, exist_ok=True)

        rel_md = it["md"].relative_to(REPO).as_posix()
        md_raw  = f"{RAW_URL}/{rel_md}"
        md_blob = f"{GH_URL}/{rel_md}"
        pdf_file = it["md"].with_suffix(".pdf")
        pdf_link = ""
        if pdf_file.exists():
            rel_pdf = pdf_file.relative_to(REPO).as_posix()
            pdf_link = f"- [PDF]({RAW_URL}/{rel_pdf})"

        md_lines = [
            f"# {it['title']}",
            "",
            f"- [Markdown raw]({md_raw})",
            f"- [GitHub view]({md_blob})",
        ]
        if pdf_link:
            md_lines.append(pdf_link)

        md_page = "\n".join(md_lines)
        page = "\n".join([header, md_page, footer, f"\nupdated: {now_iso()}\n", coda])
        (folder_out/"index.html").write_text(page, encoding="utf-8")

if __name__ == "__main__":
    build()
