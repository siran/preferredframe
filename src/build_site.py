#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
import os, shutil

# ---------- Paths ----------
REPO    = Path(__file__).resolve().parent.parent
SRC     = REPO / "src"
OUTD    = REPO / "site"
PRINTS  = REPO / "prints"

# ---------- Repo identity (used for redirect targets) ----------
GITHUB_USER = os.getenv("GITHUB_USER", "siran")
REPO_NAME   = os.getenv("REPO_NAME", "preferredframe")
GH_BRANCH   = os.getenv("GH_BRANCH", "main")

# ---------- BASE_URL selection ----------
def compute_base_url() -> str:
    v = os.getenv("BASE_URL")
    if v:
        return v.rstrip("/")
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        return f"https://{GITHUB_USER}.github.io/{REPO_NAME}"
    return "http://127.0.0.1:8000"

BASE_URL = compute_base_url()

def write_cname_if_custom(base_url: str):
    """If using a custom domain, write site/CNAME automatically."""
    host = urlparse(base_url).netloc
    if host and not host.endswith(".github.io"):
        OUTD.mkdir(parents=True, exist_ok=True)
        (OUTD / "CNAME").write_text(host + "\n", encoding="utf-8")

# ---------- Helpers ----------
def now_nyc() -> tuple[str, str]:
    dt = datetime.now(ZoneInfo("America/New_York"))
    return dt.strftime("%Y-%m-%d %H:%M"), dt.strftime("%Z")

def is_dot(name: str) -> bool: return name.startswith(".")
def is_md(p: Path) -> bool: return p.is_file() and p.suffix.lower() == ".md"
def is_pdf(p: Path) -> bool: return p.is_file() and p.suffix.lower() == ".pdf"

def read_title(md_abs: Path) -> str:
    try:
        with md_abs.open("r", encoding="utf-8") as f:
            first = f.readline().rstrip("\n")
        if first.startswith("% "):
            return first[2:].strip()
    except Exception:
        pass
    return md_abs.stem

def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""

def copy_static():
    OUTD.mkdir(parents=True, exist_ok=True)
    if SRC.exists():
        for p in SRC.iterdir():
            # templates are included (not copied); everything else gets copied
            if p.name in ("header.html", "footer.html", "coda.html"):
                continue
            dst = OUTD / p.name
            if p.is_file():
                shutil.copy2(p, dst)
            elif p.is_dir():
                if dst.exists(): shutil.rmtree(dst)
                shutil.copytree(p, dst)

def collect_folders():
    if not PRINTS.exists(): return []
    return sorted([d for d in PRINTS.iterdir() if d.is_dir() and not is_dot(d.name)])

def collect_items_for_root():
    """Pick one representative .md per folder (first non-README.md, newest first)."""
    items = []
    for folder in collect_folders():
        md_files = sorted(
            [p for p in folder.glob("*.md") if p.name.lower() != "readme.md"],
            key=lambda p: p.stat().st_mtime, reverse=True
        )
        if not md_files: continue
        md = md_files[0]
        items.append({"title": read_title(md), "folder": folder, "md": md})
    return items

# ---------- Page writers ----------
def sandwich_write(out_html_path: Path, md_content: str):
    """
    Write: header.html + md_content + footer.html + '(updated: ... TZ)' + coda.html
    Always append the updated line; do not auto-insert any links if footer is empty.
    """
    header = load_text(SRC / "header.html")
    footer = load_text(SRC / "footer.html")
    coda   = load_text(SRC / "coda.html")

    ts, tz = now_nyc()
    updated_line = f"(updated: {ts} {tz})"

    out_html_path.parent.mkdir(parents=True, exist_ok=True)
    parts = [header, md_content, footer, "", updated_line, "", coda]
    # Clean trailing whitespace; ensure single newline at end
    html = "\n".join([s.rstrip() for s in parts if s is not None]).rstrip() + "\n"
    out_html_path.write_text(html, encoding="utf-8")

def render_root_markdown(items):
    lines = ["## Latest publications", ""]
    if not items:
        lines.append("> No prints yet.")
        return "\n".join(lines)
    for it in items[:10]:
        lines.append(f"- [{it['title']}]({BASE_URL}/prints/{it['folder'].name}/)")
    return "\n".join(lines)

def render_folder_markdown(folder: Path):
    mds  = sorted([p for p in folder.iterdir() if is_md(p) and p.name.lower() != "readme.md"])
    pdfs = {p.stem: p for p in folder.iterdir() if is_pdf(p)}
    if not mds:
        return "> No markdown files found."

    title = read_title(mds[0])
    lines = [f"## {title}", "", "Available files:", ""]

    for md in mds:
        rel_md   = md.relative_to(PRINTS).as_posix()      # e.g., Folder/File.md
        url_md   = f"{BASE_URL}/prints/{rel_md}"          # stub -> GitHub RAW
        url_mdui = f"{BASE_URL}/prints/{rel_md}.github"   # stub -> GitHub BLOB

        lines.append(f"[Markdown]({url_md})")
        lines.append("")
        lines.append(f"[Markdown (GitHub)]({url_mdui})")

        if md.stem in pdfs:
            rel_pdf = pdfs[md.stem].relative_to(PRINTS).as_posix()
            url_pdf = f"{BASE_URL}/prints/{rel_pdf}"      # stub -> GitHub RAW PDF
            lines.append("")
            lines.append(f"[PDF]({url_pdf})")

        lines.append("")  # spacer
    return "\n".join(lines).rstrip() + "\n"

# ---------- Redirect stubs ----------
def make_redirect_stub(path: Path, target_url: str, label: str):
    """
    Minimal only: meta refresh + fallback text + anchor + charset.
    No header/footer/coda.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    html = (
        f'<meta http-equiv="refresh" content="0; url={target_url}" />\n\n'
        f'If not redirected automatically, please visit {target_url}\n'
        f'or click here: <a href="{target_url}">{label}</a>\n\n'
        f'<meta charset="utf-8">\n'
    )
    path.write_text(html, encoding="utf-8")

def create_stubs_for_folder(folder: Path):
    """
    For each .md create:
      - prints/<Folder>/<File>.md/index.html         -> RAW of MD
      - prints/<Folder>/<File>.md.github/index.html  -> BLOB of MD (UI)
    For each .pdf create:
      - prints/<Folder>/<File>.pdf/index.html        -> RAW of PDF
    """
    for f in sorted(folder.iterdir()):
        if is_md(f):
            rel_md_repo = (REPO / "prints" / f.relative_to(PRINTS)).relative_to(REPO).as_posix()
            raw_md  = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{GH_BRANCH}/{rel_md_repo}"
            blob_md = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/blob/{GH_BRANCH}/{rel_md_repo}"

            make_redirect_stub(
                OUTD / "prints" / folder.name / f"{f.name}" / "index.html",
                raw_md,
                f"{f.name} (raw)"
            )
            make_redirect_stub(
                OUTD / "prints" / folder.name / f"{f.name}.github" / "index.html",
                blob_md,
                f"{f.name} (GitHub)"
            )

            pdf = f.with_suffix(".pdf")
            if pdf.exists():
                rel_pdf_repo = (REPO / "prints" / pdf.relative_to(PRINTS)).relative_to(REPO).as_posix()
                raw_pdf = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/raw/{GH_BRANCH}/{rel_pdf_repo}"
                make_redirect_stub(
                    OUTD / "prints" / folder.name / f"{pdf.name}" / "index.html",
                    raw_pdf,
                    f"{pdf.name}"
                )

        elif is_pdf(f):
            rel_pdf_repo = (REPO / "prints" / f.relative_to(PRINTS)).relative_to(REPO).as_posix()
            raw_pdf = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/raw/{GH_BRANCH}/{rel_pdf_repo}"
            make_redirect_stub(
                OUTD / "prints" / folder.name / f"{f.name}" / "index.html",
                raw_pdf,
                f"{f.name}"
            )

# ---------- Build ----------
def build():
    copy_static()

    # Root page
    items = collect_items_for_root()
    sandwich_write(OUTD / "index.html", render_root_markdown(items))

    # Folder pages + stubs
    for folder in collect_folders():
        sandwich_write(OUTD / "prints" / folder.name / "index.html", render_folder_markdown(folder))
        create_stubs_for_folder(folder)

    # Serve verbatim; write CNAME if using custom domain
    (OUTD / ".nojekyll").write_text("", encoding="utf-8")
    write_cname_if_custom(BASE_URL)

if __name__ == "__main__":
    build()
