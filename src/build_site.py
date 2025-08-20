#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import os, shutil

# Paths
REPO   = Path(__file__).resolve().parent.parent
SRC    = REPO / "src"
OUTD   = REPO / "site"
PRINTS = REPO / "prints"

# Config
BASE_URL     = "https://preferredframe.com"  # public domain (human-readable)
GITHUB_USER  = os.getenv("GITHUB_USER", "siran")
REPO_NAME    = os.getenv("REPO_NAME", "preferredframe")
GH_BRANCH    = os.getenv("GH_BRANCH", "main")

def now_nyc():
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M")

def is_dot(name: str) -> bool:
    return name.startswith(".")

def is_md(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() == ".md"

def is_pdf(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() == ".pdf"

def read_title(md_abs: Path) -> str:
    try:
        with md_abs.open("r", encoding="utf-8") as f:
            first = f.readline().rstrip("\n")
        if first.startswith("% "):
            return first[2:].strip()
    except Exception:
        pass
    return md_abs.stem

def collect_folders():
    if not PRINTS.exists():
        return []
    return sorted([d for d in PRINTS.iterdir() if d.is_dir() and not is_dot(d.name)])

def collect_items():
    """Pick first non-README.md per folder for root list."""
    items = []
    for folder in collect_folders():
        md_files = sorted([p for p in folder.glob("*.md") if p.name.lower() != "readme.md"],
                          key=lambda p: p.stat().st_mtime, reverse=True)
        if not md_files:
            continue
        md = md_files[0]
        items.append({"title": read_title(md), "folder": folder, "md": md})
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

def render_folder_markdown(folder: Path):
    mds  = sorted([p for p in folder.iterdir() if is_md(p) and p.name.lower() != "readme.md"])
    pdfs = {p.stem: p for p in folder.iterdir() if is_pdf(p)}
    if not mds:
        return "> No markdown files found."
    lines = [f"# {folder.name}", "", "## Files", ""]
    for md in mds:
        rel_md  = md.relative_to(PRINTS).as_posix()
        md_site = f"{BASE_URL}/prints/{rel_md}"  # served via redirect stub
        gh_blob = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/blob/{GH_BRANCH}/prints/{rel_md}"
        pdf_part = ""
        if md.stem in pdfs:
            rel_pdf  = pdfs[md.stem].relative_to(PRINTS).as_posix()
            pdf_site = f"{BASE_URL}/prints/{rel_pdf}"  # served via redirect stub
            pdf_part = f" • [PDF]({pdf_site})"
        lines.append(f"- **{md.stem}** — [Markdown]({md_site}) • [Markdown (GitHub)]({gh_blob}){pdf_part}")
    return "\n".join(lines)

def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""

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

def sandwich_write(out_html_path: Path, md_content: str):
    header = load_text(SRC / "header.html")
    footer = load_text(SRC / "footer.html")
    coda   = load_text(SRC / "coda.html")
    out_html_path.parent.mkdir(parents=True, exist_ok=True)
    html = f"{header}{md_content}\n{footer}\n\nupdated: {now_nyc()}\n\n{coda}"
    out_html_path.write_text(html, encoding="utf-8")

def make_redirect_stub(path: Path, target_url: str):
    """Minimal redirect file: meta refresh + anchor + meta charset. No header/footer/coda."""
    path.parent.mkdir(parents=True, exist_ok=True)
    html = f"""<meta http-equiv="refresh" content="0; url={target_url}" />

<a href="{target_url}">the file</a>

<meta charset="utf-8">
"""
    path.write_text(html, encoding="utf-8")

def build():
    copy_static()

    folders = collect_folders()
    items   = collect_items()

    # Root page
    root_md = render_markdown_index(items)
    sandwich_write(OUTD / "index.html", root_md)

    # Per-folder pages + redirect stubs for each .md/.pdf
    for folder in folders:
        # Folder page
        folder_out = OUTD / "prints" / folder.name / "index.html"
        folder_md  = render_folder_markdown(folder)
        sandwich_write(folder_out, folder_md)

        # Redirect stubs for MD/PDF files
        for f in sorted(folder.iterdir()):
            if is_md(f):
                rel_md = f.relative_to(REPO).as_posix()  # prints/Folder/File.md
                target = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/blob/{GH_BRANCH}/{rel_md}"
                # To serve .../File.md -> create .../File.md/index.html
                make_redirect_stub(OUTD / "prints" / folder.name / f"{f.name}" / "index.html", target)
                # If a sibling PDF exists, add a stub for it too
                pdf = f.with_suffix(".pdf")
                if pdf.exists():
                    rel_pdf = pdf.relative_to(REPO).as_posix()
                    pdf_target = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/raw/{GH_BRANCH}/{rel_pdf}"
                    make_redirect_stub(OUTD / "prints" / folder.name / f"{pdf.name}" / "index.html", pdf_target)
            elif is_pdf(f):
                # If PDF exists without a matching .md, still create a stub
                rel_pdf = f.relative_to(REPO).as_posix()
                pdf_target = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/raw/{GH_BRANCH}/{rel_pdf}"
                make_redirect_stub(OUTD / "prints" / folder.name / f"{f.name}" / "index.html", pdf_target)

if __name__ == "__main__":
    build()
