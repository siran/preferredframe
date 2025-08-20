#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote
import shutil, os

REPO    = Path(__file__).resolve().parent.parent
SRC     = REPO / "src"
OUTD    = REPO / "site"
PRINTS  = REPO / "prints"

# --- Config (populated by Actions or use defaults locally) ---
GITHUB_USER = os.environ.get("GITHUB_USER", "YourUser")
REPO_NAME   = os.environ.get("REPO_NAME", "PF")
GH_BRANCH   = os.environ.get("GH_BRANCH", "main")

# Custom domain for public links (preferredframe.com)
BASE_URL = os.environ.get("CUSTOM_BASE_URL", "https://preferredframe.com").rstrip("/")

def now_nyc():
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
    if not PRINTS.exists():
        return items
    for folder in sorted(PRINTS.iterdir()):
        if not folder.is_dir() or is_dot(folder.name):
            continue
        md_files = sorted(
            [p for p in folder.glob("*.md") if p.name.lower() != "readme.md"],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
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
        # Absolute URL to folder page on the published site
        folder_url = f"{BASE_URL}/prints/{quote(it['folder'].name, safe='')}/"
        lines.append(f"- [{title}]({folder_url})")
    return "\n".join(lines)

def copy_static():
    OUTD.mkdir(parents=True, exist_ok=True)
    if SRC.exists():
        for p in SRC.iterdir():
            if p.name in ("header.html", "footer.html", "coda.html"):
                continue
            dst = OUTD / p.name
            if p.is_file():
                shutil.copy2(p, dst)
            elif p.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(p, dst)

def copy_prints_into_site():
    """Publish prints/ contents as static files under site/prints/."""
    target = OUTD / "prints"
    if target.exists():
        shutil.rmtree(target)
    if PRINTS.exists():
        shutil.copytree(PRINTS, target)

def sandwich_write(out_html_path: Path, md_content: str):
    header = (SRC / "header.html").read_text(encoding="utf-8") if (SRC / "header.html").exists() else ""
    footer = (SRC / "footer.html").read_text(encoding="utf-8") if (SRC / "footer.html").exists() else ""
    coda   = (SRC / "coda.html").read_text(encoding="utf-8")   if (SRC / "coda.html").exists() else ""

    out_html_path.parent.mkdir(parents=True, exist_ok=True)
    html = f"{header}{md_content}\n{footer}\n\nupdated: {now_nyc()}\n\n{coda}"
    out_html_path.write_text(html, encoding="utf-8")

def build():
    items = collect_items()
    copy_static()
    copy_prints_into_site()

    # Root page (latest 10 only; Markdown list only)
    root_md = render_markdown_index(items)
    sandwich_write(OUTD / "index.html", root_md)

    # Per-folder pages (list all .md files with absolute links)
    for it in items:
        folder = it["folder"]
        folder_out = OUTD / "prints" / folder.name
        mds = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".md" and p.name.lower() != "readme.md"])
        if not mds:
            md_page = "> No markdown files found."
        else:
            lines = [f"# {folder.name}", "", "## Files", ""]
            for md in mds:
                # Absolute site link to the md and optional pdf
                rel_md = md.relative_to(PRINTS).as_posix()  # e.g. "Paper/filename.md"
                md_site = f"{BASE_URL}/prints/{quote(rel_md, safe='/')}"
                pdf_abs = md.with_suffix(".pdf")
                pdf_part = ""
                if pdf_abs.exists():
                    rel_pdf = pdf_abs.relative_to(PRINTS).as_posix()
                    pdf_site = f"{BASE_URL}/prints/{quote(rel_pdf, safe='/')}"
                    pdf_part = f" • [PDF]({pdf_site})"
                # Optional GitHub view (blob) link if you still want it:
                gh_blob = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/blob/{GH_BRANCH}/{quote((REPO / 'prints' / rel_md).relative_to(REPO).as_posix(), safe='/')}"
                lines.append(f"- **{md.stem}** — [Markdown]({md_site}) • [GitHub view]({gh_blob}){pdf_part}")
            md_page = "\n".join(lines)
        sandwich_write(folder_out / "index.html", md_page)

if __name__ == "__main__":
    build()
