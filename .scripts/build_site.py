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
# Do NOT mirror PDFs into site/ (PDFs live only in assets repo)
MIRROR_EXTS = {".html",".md",".pandoc.md",".yaml",".yml"}

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

def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""

@dataclass
class Item:
    name: str
    is_dir: bool
    mtime: float
    path: Path

def strip_html(s: str) -> str:
    return re.sub(r"<[^>]*>", "", s or "")

def trunc(s: str, n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[:n-1].rstrip() + "…"

# ---------- templating with SEO ----------
def inject_head_meta(html: str, head_extra: str) -> str:
    if not head_extra:
        return html
    i = html.lower().find("</head>")
    if i == -1:
        return head_extra + html
    return html[:i] + head_extra + html[i:]

def write_html(out_html: Path, body_html: str, head_extra: str = ""):
    header = load_text(SRC / "header.html")
    footer = load_text(SRC / "footer.html")
    coda   = load_text(SRC / "coda.html")

    doc = "".join(s for s in (header, body_html, footer) if s is not None)
    doc = inject_head_meta(doc, head_extra)

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

def write_md_like_page(out_html: Path, md_body: str, title: str = "", canonical_url: str = ""):
    body = "<main>\n<pre>\n" + md_body.replace("&","&amp;").replace("<","&lt;") + "\n</pre>\n</main>\n"
    head_extra = []
    if title:
        head_extra.append(f"<title>{title}</title>")
        head_extra.append(f'<meta name="robots" content="index,follow">')
    if canonical_url:
        head_extra.append(f'<link rel="canonical" href="{canonical_url}">')
    write_html(out_html, body, "\n".join(h for h in head_extra if h))

# ---------- tiny YAML loader (fallback) ----------
def read_yaml(p: Path) -> dict:
    try:
        import yaml
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
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
    for fmt in ("%Y-%m-%d","%Y-%m","%Y"):
        try:
            dt = datetime.strptime(iso_date, fmt)
            return dt.strftime("%B %Y") if fmt != "%Y" else dt.strftime("%Y")
        except Exception:
            pass
    return iso_date

# ---------- article page builder ----------
def build_article_pages():
    """
    Finds all prints/*/*/<stem>/provenance.yaml and emits:
      site/q/{slug(title)}--{doi_suffix}/index.html        (permalink)
    Also mirrors non-PDF assets to site/prints/.../
    """
    prints = ROOT / "prints"
    if not prints.exists():
        return

    for prov in prints.glob("*/*/*/provenance.yaml"):
        try:
            data = read_yaml(prov)
        except Exception:
            continue

        # parsed fields
        pnp = data.get("parsed_from_pnpmd") or {}
        title   = pnp.get("title") or ""
        authors = pnp.get("authors") or []
        abstract= pnp.get("abstract") or ""
        kws     = pnp.get("keywords") or []
        date_norm = pnp.get("date_normalized") or (data.get("date_folder") or "")
        pub_line = f"Preferred Frame — {month_year(date_norm)}" if date_norm else "Preferred Frame"

        zenodo = data.get("zenodo") or {}
        doi    = zenodo.get("doi") or zenodo.get("reserved_doi") or ""
        concept= zenodo.get("concept_doi") or ""
        doi_suffix = doi.split("/")[-1] if doi else ""
        site_info = data.get("site") or {}
        html_canonical = site_info.get("html_canonical")
        permalink = site_info.get("permalink")
        assets_pdf = (data.get("assets") or {}).get("pdf") or ""

        # filesystem locations
        stem_dir = prov.parent
        rel_stem = rel(stem_dir)

        # mirror non-PDF assets (keep human-readable names, incl. spaces)
        for f in stem_dir.iterdir():
            if f.is_file() and f.suffix.lower() in MIRROR_EXTS:
                dst = OUT / rel(f)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst)

        # derive local links
        md_name  = (data.get("artifacts") or {}).get("main") \
                   or (html_canonical and Path(html_canonical).name.replace(".html",".md"))
        html_name= Path(html_canonical).name if html_canonical else None
        pandoc_md_name = ((data.get("artifacts") or {}).get("additional") or {}).get("pandoc_md")

        local_md   = f"/{(OUT/rel_stem/md_name).relative_to(OUT).as_posix()}"   if md_name else None
        local_html = f"/{(OUT/rel_stem/html_name).relative_to(OUT).as_posix()}" if html_name else None
        local_pmd  = f"/{(OUT/rel_stem/pandoc_md_name).relative_to(OUT).as_posix()}" if pandoc_md_name else None

        # author line (preserve names as-is)
        def fmt_author(a):
            if isinstance(a, dict):
                name = a.get("name","")
                orcid = a.get("orcid")
            else:
                name = str(a); orcid = None
            return f'{name} (<a href="{orcid}">ORCID</a>)' if orcid else name
        authors_html = ", ".join(fmt_author(a) for a in authors) if authors else ""

        # keyword string
        kw_html = ", ".join(kws)

        # preferred canonical & URL
        canonical_url = permalink or html_canonical or ""

        # Links row: PDF always points to assets host (open access)
        links = []
        if local_html: links.append(f'<a href="{local_html}">HTML</a>')
        if assets_pdf: links.append(f'<a href="{assets_pdf}">PDF</a>')
        if local_md:   links.append(f'<a href="{local_md}">Markdown</a>')
        if local_pmd:  links.append(f'<a href="{local_pmd}">Preprocessed MD</a>')
        if doi:        links.append(f'<a href="https://doi.org/{doi_suffix}">DOI</a>')

        # Build body HTML
        body = []
        body.append("<main class='paper'>")
        body.append(f"<h1>{title}</h1>")
        if authors_html:
            body.append(f"<p class='authors'>{authors_html}</p>")
        body.append(f"<p class='publine'>Published in <strong>Preferred Frame</strong> — {month_year(date_norm)}</p>")
        body.append("<p class='links'>" + " · ".join(links) + "</p>")
        if kw_html:
            body.append(f"<p class='keywords'><strong>Keywords:</strong> {kw_html}</p>")
        if abstract:
            body.append("<h2>Abstract</h2>")
            body.append(f"<p>{abstract}</p>")
        if concept and doi and concept != doi:
            body.append(f"<p class='concept'><small>Concept DOI (all versions): <a href='https://doi.org/{concept.split('/')[-1]}'>{concept}</a></small></p>")
        body.append("</main>\n")
        body_html = "\n".join(body)

        # ---- SEO / indexing meta (Google, Scholar, OpenGraph, JSON-LD) ----
        # Description: short, plain text
        meta_desc = trunc(strip_html(abstract or title), 300)

        # Authors for meta
        author_names = []
        for a in authors:
            if isinstance(a, dict): author_names.append(a.get("name",""))
            else: author_names.append(str(a))
        # Scholar meta
        scholar = []
        scholar.append(f'<meta name="citation_title" content="{title}">')
        for nm in author_names:
            if nm: scholar.append(f'<meta name="citation_author" content="{nm}">')
        if date_norm:
            scholar.append(f'<meta name="citation_publication_date" content="{date_norm}">')
        scholar.append('<meta name="citation_journal_title" content="Preferred Frame">')
        if assets_pdf:
            scholar.append(f'<meta name="citation_pdf_url" content="{assets_pdf}">')
        if doi_suffix:
            scholar.append(f'<meta name="citation_doi" content="{doi_suffix}">')
        if local_html:
            scholar.append(f'<meta name="citation_fulltext_html_url" content="{BASE_URL}{local_html}">')
        for kw in kws:
            scholar.append(f'<meta name="citation_keywords" content="{kw}">')

        # OpenGraph / Twitter
        og = []
        url_for_og = canonical_url or (BASE_URL + (local_html or "/"))
        og.append(f'<meta property="og:type" content="article">')
        og.append(f'<meta property="og:site_name" content="Preferred Frame">')
        og.append(f'<meta property="og:title" content="{title}">')
        og.append(f'<meta property="og:description" content="{meta_desc}">')
        og.append(f'<meta property="og:url" content="{url_for_og}">')
        if date_norm:
            og.append(f'<meta property="article:published_time" content="{date_norm}">')
        for kw in kws[:6]:
            og.append(f'<meta property="article:tag" content="{kw}">')

        # JSON-LD
        json_ld = {
            "@context": "https://schema.org",
            "@type": "ScholarlyArticle",
            "name": title,
            "headline": title,
            "isPartOf": {"@type": "Periodical", "name": "Preferred Frame"},
            "author": [{"@type":"Person","name": n} for n in author_names if n],
            "datePublished": date_norm or "",
            "description": meta_desc,
            "isAccessibleForFree": True,
            "url": url_for_og
        }
        if assets_pdf:
            json_ld["encoding"] = [{
                "@type": "MediaObject",
                "fileFormat": "application/pdf",
                "contentUrl": assets_pdf
            }]
        if doi_suffix:
            json_ld["identifier"] = f"https://doi.org/{doi_suffix}"

        head_extra = []
        page_title = f"{title} — Preferred Frame"
        head_extra.append(f"<title>{page_title}</title>")
        if canonical_url:
            head_extra.append(f'<link rel="canonical" href="{canonical_url}">')
        head_extra.append(f'<meta name="description" content="{meta_desc}">')
        head_extra.append(f'<meta name="robots" content="index,follow">')
        head_extra.extend(scholar)
        head_extra.extend(og)
        head_extra.append('<script type="application/ld+json">' + json.dumps(json_ld, ensure_ascii=False) + "</script>")

        # permalink path
        if not permalink and title and doi_suffix:
            permalink = f"https://preferredframe.com/q/{slug_title(title)}--{doi_suffix}"
        if permalink:
            parsed = urlparse(permalink)
            q_path = parsed.path.lstrip("/") or f"q/{slug_title(title)}--{doi_suffix}"
            out_html = OUT / q_path / "index.html"
            write_html(out_html, body_html, "\n".join(head_extra))

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
            if mirrored.exists() and it.path.suffix.lower() in {".html",".md",".yaml",".yml"}:
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

# ---------- robots.txt & sitemap ----------
def write_robots_and_sitemap():
    OUT.mkdir(parents=True, exist_ok=True)
    # robots.txt
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: {}/sitemap.xml\n".format(BASE_URL), encoding="utf-8")

    # sitemap.xml (simple)
    urls = []
    for p in OUT.rglob("index.html"):
        relp = "/" + p.relative_to(OUT).as_posix()
        if relp.startswith("/."):  # skip hidden
            continue
        urls.append(BASE_URL + relp)
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in sorted(set(urls)):
        sm.append("<url><loc>{}</loc></url>".format(u))
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")

# ---------- build ----------
def prune_dirs(root: str, dirnames: list[str]):
    keep=[]
    for d in dirnames:
        if d in EXCLUDE_NAMES: continue
        if d.startswith(".") and d != ".well-known": continue
        if (Path(root)/d/"pyvenv.cfg").exists(): continue
        keep.append(d)
    dirnames[:] = keep

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/".nojekyll").write_text("", encoding="utf-8")
    write_cname_if_custom(BASE_URL)

    # FIRST: build article pages (emits permalinks and mirrors non-PDF artifacts)
    build_article_pages()

    # THEN: build directory indexes and mirror remaining non-PDF assets
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

        rel_dir = rel(d) if d != ROOT else Path()
        out_html = (OUT / rel_dir / "index.html") if d != ROOT else (OUT / "index.html")
        canonical = BASE_URL + ("/" + rel_dir.as_posix() + "/") if rel_dir.as_posix() else BASE_URL + "/"
        md_body = format_dir_index(d, items)
        write_md_like_page(out_html, md_body, title=(rel_dir.name or REPO), canonical_url=canonical)

    copy_static()
    write_robots_and_sitemap()

if __name__ == "__main__":
    main()
