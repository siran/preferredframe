#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import shutil, os
from zoneinfo import ZoneInfo

# Paths
REPO   = Path(__file__).resolve().parent.parent
SRC    = REPO / "src"
OUTD   = REPO / "site"
PRINTS = REPO / "prints"

# Hardcode base domain
BASE_URL = "https://preferredframe.com"

def now_iso():
    # New York time
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M")

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

    # index.html at root
    md_content = render_markdown_index(items)
    full_page = "\n".join([header, md_content, footer, f"\nupdated: {now_iso()}\n", coda])
    (OUTD/"index.html").write_text(full_page, encoding="utf-8")

    # per-paper pages
    for it in items:
        folder_out = OUTD / "prints" / it["folder"].name
        folder_out.mkdir(parents=True, exist_ok=True)

        md = it["md"]
        rel_md = md.relative_to(PRINTS).as_posix()
        md_site = f"{BASE_URL}/prints/{rel_md}"

        pdf_abs = md.with_suffix(".pdf")
        pdf_part = ""
        if pdf_abs.exists():
            rel_pdf = pdf_abs.relative_to(PRINTS).as_posix()
            pdf_site = f"{BASE_URL}/prints/{rel_pdf}"
            pdf_part = f"- [PDF]({pdf_site})"

        # GitHub blob (still useful)
        GITHUB_USER = os.getenv("GITHUB_USER", "user")
        REPO_NAME   = os.getenv("REPO_NAME", "repo")
        GH_BRANCH   = os.getenv("GH_BRANCH", "main")
        gh_blob = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/blob/{GH_BRANCH}/prints/{rel_md}"

        md_lines = [
            f"# {it['title']}",
            "",
            f"- [Markdown]({md_site})",
            f"- [Markdown (GitHub)]({gh_blob})",
        ]
        if pdf_part:
            md_lines.append(pdf_part)

        md_page = "\n".join(md_lines)
        page = "\n".join([header, md_page, footer, f"\nupdated: {now_iso()}\n", coda])
        (folder_out/"index.html").write_text(page, encoding="utf-8")

if __name__ == "__main__":
    build()
