#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, subprocess, urllib.parse, shutil, re, json
from pathlib import Path
from dataclasses import dataclass
from urllib.parse import urlparse
from datetime import datetime
from zoneinfo import ZoneInfo

# ---------- config ----------
EXCLUDE_NAMES = {
    "site","venv",".venv","env",".env","node_modules",".git",
    "__pycache__", ".mypy_cache",".pytest_cache",".ruff_cache",".cache",
    "Makefile","index.html"
}
MIRROR_EXTS = {".html",".pdf",".md",".pandoc.md",".yaml",".yml"}


# ---------- repo autodetect ----------
def _parse_remote(url: str):
    try:
        if url.startswith("git@"):
            path = url.split(":", 1)[1]
        else:
            path = urllib.parse.urlparse(url).path.lstrip("/")
        if path.endswith(".git"): path = path[:-4]
        owner, repo = path.split("/", 1)
        return owner, repo
    except Exception:
        return None, None

def detect_repo_branch():
    owner = os.getenv("SITE_OWNER")
    repo  = os.getenv("SITE_REPO")
    branch= os.getenv("SITE_BRANCH")

    gh = os.getenv("GITHUB_REPOSITORY")  # "owner/repo"
    if gh and "/" in gh:
        o, r = gh.split("/", 1)
        owner = owner or o
        repo  = repo  or r
    branch = branch or os.getenv("GITHUB_REF_NAME")

    if not (owner and repo):
        try:
            url = subprocess.check_output(
                ["git","config","--get","remote.origin.url"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            o, r = _parse_remote(url)
            owner = owner or o
            repo  = repo  or r
        except Exception:
            pass
    if not branch:
        try:
            branch = subprocess.check_output(
                ["git","rev-parse","--abbrev-ref","HEAD"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            branch = "main"

    if not owner: owner = "siran"
    if not repo:  repo  = Path.cwd().name
    return owner, repo, branch

OWNER, REPO, BRANCH = detect_repo_branch()

# ---------- paths ----------
ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / "site"
SRC  = ROOT / ".scripts" / "src"   # header.html / footer.html / coda.html / submit.html

# ---------- base url & CNAME ----------
def compute_base_url() -> str:
    v = os.getenv("BASE_URL")
    if v: return v.rstrip("/")
    if os.getenv("GITHUB_ACTIONS","").lower() == "true":
        return f"https://{OWNER}.github.io/{REPO}"
    return "http://127.0.0.1:8000"

BASE_URL = compute_base_url()

def write_cname_if_custom(base_url: str):
    host = urlparse(base_url).hostname  # strip port
    if not host: return
    if host.endswith(".github.io"): return
    if host in {"localhost", "127.0.0.1"}: return
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "CNAME").write_text(host + "\n", encoding="utf-8")

# ---------- helpers ----------
def rel(p: Path) -> Path: return p.relative_to(ROOT)

def raw_url(relpath: Path) -> str:
    return f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/{relpath.as_posix()}"

def blob_url(relpath: Path) -> str:
    return f"https://github.com/{OWNER}/{REPO}/blob/{BRANCH}/{relpath.as_posix()}"

def prune_dirs(root: str, dirnames: list[str]):
    keep=[]
    for d in dirnames:
        if d in EXCLUDE_NAMES: continue
        if d.startswith(".") and d != ".well-known": continue
        if (Path(root)/d/"pyvenv.cfg").exists(): continue
        keep.append(d)
    dirnames[:] = keep

def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""

@dataclass
class Item:
    name: str
    is_dir: bool
    mtime: float
    path: Path

# ---------- templating ----------
def write_html(out_html: Path, body_html: str):
    header = load_text(SRC / "header.html")
    footer = load_text(SRC / "footer.html")
    coda   = load_text(SRC / "coda.html")

    doc = "".join(s for s in (header, body_html, footer) if s is not None)

    ny = ZoneInfo("America/New_York")
    now = datetime.now(ny)
    offset = now.utcoffset()
    hrs = int(offset.total_seconds() // 3600) if offset else 0
    timestamp = f"(generated at: {now.strftime('%Y-%m-%d %H:%M %Z')} {hrs:+d})"

    if not doc.endswith("\n"):
        doc += "\n"
    doc += timestamp
    if coda is not None:
        doc += coda

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(doc, encoding="utf-8")

def write_md_like_page(out_html: Path, md_body: str):
    # trivial Markdown subset rendering -> <pre> would be too raw.
    # We’ll just wrap it as <main><pre> for now or keep original behavior.
    body = "<main>\n<pre>\n" + md_body.replace("&","&amp;").replace("<","&lt;") + "\n</pre>\n</main>\n"
    write_html(out_html, body)

# ---------- tiny YAML loader (fallback) ----------
def read_yaml(p: Path) -> dict:
    try:
        import yaml
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        # minimal, tolerant parser for our provenance.yaml structure
        data = {}
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except Exception:
            return {}
        stack = [data]
        indents = [0]
        last_key_stack = [None]
        for ln in lines:
            if not ln.strip() or ln.lstrip().startswith("#"):
                continue
            m = re.match(r'^(\s*)([^:]+):\s*(.*)$', ln)
            if not m:
                continue
            indent = len(m.group(1).replace("\t","  "))
            key = m.group(2).strip()
            val = m.group(3).strip()
            # unwind
            while indents and indent < indents[-1]:
                stack.pop(); indents.pop(); last_key_stack.pop()
            cur = stack[-1]
            if val == "" or val == "|":
                cur[key] = {}
                stack.append(cur[key]); indents.append(indent+2); last_key_stack.append(key)
            else:
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                cur[key] = val
        return data

# ---------- slugs, dates ----------
def slug_title(s: str) -> str:
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+','-', s)
    s = re.sub(r'-{2,}','-', s).strip('-')
    return s or "x"

def month_year(iso_date: str) -> str:
    try:
        dt = datetime.strptime(iso_date, "%Y-%m-%d")
        return dt.strftime("%B %Y")
    except Exception:
        try:
            dt = datetime.strptime(iso_date, "%Y-%m")
            return dt.strftime("%B %Y")
        except Exception:
            try:
                dt = datetime.strptime(iso_date, "%Y")
                return dt.strftime("%Y")
            except Exception:
                return iso_date

# ---------- article page builder ----------
def build_article_pages():
    """
    Finds all prints/*/*/<stem>/provenance.yaml and emits:
      site/q/{slug(title)}--{doi_suffix}/index.html        (permalink)
    Also mirrors assets to site/prints/.../
    """
    prints = ROOT / "prints"
    if not prints.exists():
        return

    for prov in prints.glob("*/*/*/provenance.yaml"):
        try:
            data = read_yaml(prov)
        except Exception:
            continue
        # extract fields
        title  = ((data.get("parsed_from_pnpmd") or {}).get("title")) or ""
        authors= (data.get("parsed_from_pnpmd") or {}).get("authors") or []
        abstract = (data.get("parsed_from_pnpmd") or {}).get("abstract") or ""
        kws    = (data.get("parsed_from_pnpmd") or {}).get("keywords") or []
        date_norm = (data.get("parsed_from_pnpmd") or {}).get("date_normalized") or (data.get("date_folder") or "")
        pub_line = f"Preferred Frame — {month_year(date_norm)}" if date_norm else "Preferred Frame"

        zenodo  = data.get("zenodo") or {}
        doi     = zenodo.get("doi") or zenodo.get("reserved_doi") or ""
        concept = zenodo.get("concept_doi") or ""
        record  = zenodo.get("record_id")
        doi_suffix = doi.split("/")[-1] if doi else ""
        permalink = (data.get("site") or {}).get("permalink")
        html_canonical = (data.get("site") or {}).get("html_canonical")

        # filesystem locations
        stem_dir = prov.parent
        rel_stem = rel(stem_dir)
        # mirror assets
        for f in stem_dir.iterdir():
            if f.is_file() and f.suffix.lower() in MIRROR_EXTS:
                dst = OUT / rel(f)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst)

        # derive local links
        md_name  = (data.get("artifacts") or {}).get("main") or (html_canonical and Path(html_canonical).name.replace(".html",".md"))
        html_name= Path(html_canonical).name if html_canonical else None
        pdf_name = ((data.get("artifacts") or {}).get("additional") or {}).get("pdf")
        pandoc_md_name = ((data.get("artifacts") or {}).get("additional") or {}).get("pandoc_md")

        local_md   = f"/{(OUT/rel_stem/md_name).relative_to(OUT).as_posix()}" if md_name else None
        local_html = f"/{(OUT/rel_stem/html_name).relative_to(OUT).as_posix()}" if html_name else None
        local_pdf  = f"/{(OUT/rel_stem/pdf_name).relative_to(OUT).as_posix()}" if pdf_name else None
        local_pmd  = f"/{(OUT/rel_stem/pandoc_md_name).relative_to(OUT).as_posix()}" if pandoc_md_name else None

        # author line
        def fmt_author(a):
            name = a.get("name") if isinstance(a, dict) else str(a)
            orcid = a.get("orcid") if isinstance(a, dict) else None
            if orcid:
                return f'{name} (<a href="{orcid}">ORCID</a>)'
            return name
        authors_html = ", ".join(fmt_author(a) for a in authors) if authors else ""

        # related links
        doi_url = f"https://doi.org/{doi_suffix}" if doi_suffix else ""
        z_rec   = f"https://zenodo.org/records/{record}" if record else (doi_url or "")
        kw_html = ", ".join(kws)

        # build body HTML
        body = []
        body.append("<main class='paper'>")
        body.append(f"<h1>{title}</h1>")
        if authors_html:
            body.append(f"<p class='authors'>{authors_html}</p>")
        body.append(f"<p class='publine'>Published in <strong>Preferred Frame</strong> — {month_year(date_norm)}</p>")
        # links row
        links = []
        if local_html: links.append(f'<a href="{local_html}">HTML</a>')
        if local_pdf:  links.append(f'<a href="{local_pdf}">PDF</a>')           # direct file
        elif doi_url:  links.append(f'<a href="{doi_url}">PDF</a>')              # fallback to DOI
        if local_md:   links.append(f'<a href="{local_md}">Markdown</a>')
        if local_pmd:  links.append(f'<a href="{local_pmd}">Preprocessed MD</a>')
        if z_rec and z_rec != doi_url:  links.append(f'<a href="{z_rec}">Zenodo</a>')
        body.append("<p class='links'>" + " · ".join(links) + "</p>")
        if kw_html:
            body.append(f"<p class='keywords'><strong>Keywords:</strong> {kw_html}</p>")
        if abstract:
            body.append("<h2>Abstract</h2>")
            body.append(f"<p>{abstract}</p>")
        if concept and doi and concept != doi:
            body.append(f"<p class='concept'><small>Concept DOI (all versions): <a href='https://doi.org/{concept.split('/')[-1]}'>{concept}</a></small></p>")
        body.append("</main>\n")

        # permalink path
        if not permalink and title and doi_suffix:
            permalink = f"https://preferredframe.com/q/{slug_title(title)}--{doi_suffix}"
        if permalink:
            # emit page at site/q/...
            parsed = urlparse(permalink)
            q_path = parsed.path.lstrip("/") or f"q/{slug_title(title)}--{doi_suffix}"
            out_html = OUT / q_path / "index.html"
            write_html(out_html, "\n".join(body))

# ---------- directory index builder with mirrors ----------
def breadcrumbs(rel_dir: Path) -> str:
    depth = len(rel_dir.parts)
    to_root = "./" if depth == 0 else "../" * depth
    crumbs = [f"[🏠 Home]({to_root})"]
    for i, part in enumerate(rel_dir.parts):
        up = "../" * (len(rel_dir.parts) - i - 1) or "./"
        crumbs.append(f"/ [📂 {part}]({up})")
    return " ".join(crumbs)

def format_dir_index(dir_abs: Path, items: list[Item]) -> str:
    rel_dir = rel(dir_abs) if dir_abs != ROOT else Path()
    title = (rel_dir.name or f"{REPO} index")

    lines = []
    lines.append(f"## {title}")
    lines.append("")
    lines.append(breadcrumbs(rel_dir))
    lines.append("")

    items_sorted = sorted(items, key=lambda e: (not e.is_dir, e.name.lower()))
    for it in items_sorted:
        if it.is_dir:
            href = (it.name + "/") if rel_dir.parts else (rel(it.path).as_posix() + "/")
            lines.append(f"- 📂 {it.name}/: [{href}]({href})")
        else:
            p_rel = rel(it.path)
            view = None
            mirrored = OUT / p_rel
            if mirrored.exists() and it.path.suffix.lower() in {".html",".pdf",".md",".yaml",".yml"}:
                view = "/" + mirrored.relative_to(OUT).as_posix()
            lines.append(f"- 📄 {it.name}")
            if view:
                lines.append(f"  - [open]({view})")


    lines.append("")
    return "\n".join(lines)

def copy_static():
    """Copy static pages from .scripts/src/ into site/."""
    OUT.mkdir(parents=True, exist_ok=True)
    static_names = ["submit.html"]
    for name in static_names:
        src = SRC / name
        if src.exists():
            dst = OUT / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

# ---------- build ----------
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/".nojekyll").write_text("", encoding="utf-8")
    write_cname_if_custom(BASE_URL)

    # FIRST: build article pages & mirror assets so directory indexes can link to "view"
    build_article_pages()

    # THEN: build directory indexes and mirror any remaining assets
    for dirpath, dirnames, filenames in os.walk(ROOT):
        d = Path(dirpath)
        if d == OUT:
            dirnames.clear(); continue
        if dirpath != str(ROOT):
            first = Path(dirpath).relative_to(ROOT).parts[0]
            if first in EXCLUDE_NAMES:
                dirnames.clear(); continue
            if (Path(dirpath)/"pyvenv.cfg").exists():
                dirnames.clear(); continue
        prune_dirs(dirpath, dirnames)

        # mirror selected assets into OUT to serve from preferredframe.com
        for fname in filenames:
            if fname.startswith("."): continue
            p = d / fname
            if p.suffix.lower() in MIRROR_EXTS and "prints" in p.parts:
                dst = OUT / rel(p)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dst)

        items: list[Item] = []
        for p in sorted([x for x in d.iterdir() if x.is_dir()], key=lambda x: x.name.lower()):
            if p.name in EXCLUDE_NAMES: continue
            if p.name.startswith(".") and p.name != ".well-known": continue
            if (p/"pyvenv.cfg").exists(): continue
            items.append(Item(name=p.name, is_dir=True, mtime=p.stat().st_mtime, path=p))

        for p in sorted([x for x in d.iterdir() if x.is_file() and not x.name.startswith(".")],
                        key=lambda x: x.name.lower()):
            if p.name in EXCLUDE_NAMES: continue
            items.append(Item(name=p.name, is_dir=False, mtime=p.stat().st_mtime, path=p))

        out_html = (OUT / rel(d) / "index.html") if d != ROOT else (OUT / "index.html")
        md_body = format_dir_index(d, items)
        write_md_like_page(out_html, md_body)

    copy_static()

if __name__ == "__main__":
    main()
