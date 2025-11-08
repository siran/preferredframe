#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, subprocess, urllib.parse, shutil, re, json
from pathlib import Path
from dataclasses import dataclass
from urllib.parse import urlparse, quote
from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo
import yaml

# ---------- config ----------
EXCLUDE_NAMES = {
    "site","venv",".venv","env",".env","node_modules",".git",
    "__pycache__", ".mypy_cache",".pytest_cache",".ruff_cache",".cache",
    "Makefile","index.html","_staging"
}
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

    gh = os.getenv("GITHUB_REPOSITORY")
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
SRC  = ROOT / ".scripts" / "src"

# ---------- base url ----------
def compute_base_url() -> str:
    v = os.getenv("BASE_URL")
    if v: return v.rstrip("/")
    if os.getenv("GITHUB_ACTIONS","").lower() == "true":
        return f"https://{OWNER}.github.io/{REPO}"
    return "http://127.0.0.1:8000"

BASE_URL = compute_base_url()

def write_cname_if_custom(base_url: str):
    host = urlparse(base_url).hostname
    if not host: return
    if host.endswith(".github.io"): return
    if host in {"localhost","127.0.0.1"}: return
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"CNAME").write_text(host+"\n", encoding="utf-8")

# ---------- helpers ----------
def rel(p: Path) -> Path: return p.relative_to(ROOT)
def rel_out(p: Path) -> Path: return p.relative_to(OUT)
def load_text(p: Path) -> str: return p.read_text(encoding="utf-8") if p.exists() else ""

@dataclass
class Item:
    name: str
    is_dir: bool
    mtime: float
    path: Path

# ---------- templating ----------
def write_html(out_html: Path, body_html: str, head_extra: str = ""):
    header = load_text(SRC / "header.html")
    footer = load_text(SRC / "footer.html")
    coda   = load_text(SRC / "coda.html")

    doc = "".join(s for s in (header, body_html, footer) if s)

    if head_extra:
        charset = '<meta charset="UTF-8">'
        if charset not in head_extra:
            head_extra = charset + "\n" + head_extra
        m = re.search(r"</head\s*>", doc, re.IGNORECASE)
        if m:
            doc = doc[:m.start()] + head_extra + doc[m.start():]
        else:
            doc = head_extra + doc

    ny = ZoneInfo("America/New_York")
    now = datetime.now(ny)
    offset = now.utcoffset()
    hrs = int(offset.total_seconds()//3600) if offset else 0
    stamp = f"(generated at: {now.strftime('%Y-%m-%d %H:%M %Z')} {hrs:+d})"

    if not doc.endswith("\n"):
        doc += "\n"
    doc += stamp
    if coda:
        doc += coda

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(doc, encoding="utf-8")

def write_md_like_page(out_html: Path, md_body: str, head_extra: str = ""):
    body = "<main>\n<pre>\n" + md_body.replace("&","&amp;").replace("<","&lt;") + "\n</pre>\n</main>\n"
    write_html(out_html, body, head_extra=head_extra)

def crumb_link(parts: list[str]) -> str:
    html = ['<nav class="breadcrumbs">']
    html.append('<a href="/">🏠 Home</a>')
    base = ""
    for label in parts:
        base = base.rstrip("/") + "/" + quote(label)
        html.append(' / ')
        html.append(f'<a href="{base}/">📂 {label}</a>')
    html.append('</nav>')
    return "".join(html)

# ---------- dates ----------
def _to_datetime(obj) -> datetime | None:
    if isinstance(obj, datetime): return obj
    if isinstance(obj, date):    return datetime.combine(obj, datetime.min.time())
    if isinstance(obj, str):
        for fmt in ("%Y-%m-%d","%Y-%m","%Y"):
            try: return datetime.strptime(obj, fmt)
            except Exception: pass
    return None

def month_year(d) -> str:
    dt = _to_datetime(d)
    if not dt:
        return str(d) if d is not None else ""
    return dt.strftime("%B %Y")

def scholar_date(x) -> str:
    if isinstance(x, datetime): return x.strftime("%Y/%m/%d")
    if isinstance(x, date):    return x.strftime("%Y/%m/%d")
    if isinstance(x, str):
        x = x.strip()
        if not x: return ""
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", x):
            y,m,d = x.split("-"); return f"{y}/{m}/{d}"
        if re.fullmatch(r"\d{4}-\d{2}", x):
            y,m = x.split("-");   return f"{y}/{m}"
        if re.fullmatch(r"\d{4}", x): return x
        return x.replace("-", "/")
    return ""

def iso_date_str(x) -> str:
    if isinstance(x, datetime): return x.date().isoformat()
    if isinstance(x, date):     return x.isoformat()
    if isinstance(x, str):      return x.strip()
    return str(x) if x else ""

def extract_html_body(html_text: str) -> str:
    m_open = re.search(r"<body[^>]*>", html_text, flags=re.IGNORECASE|re.DOTALL)
    m_close = re.search(r"</body\s*>", html_text, flags=re.IGNORECASE|re.DOTALL)
    if m_open and m_close and m_close.start() > m_open.end():
        return html_text[m_open.end():m_close.start()]
    return html_text

# ---------- authors ----------
def normalize_authors(auth_list):
    out = []
    for a in (auth_list or []):
        if isinstance(a, dict):
            nm = (a.get("name") or a.get("full_name") or "").strip()
            oc = (a.get("orcid") or a.get("id") or "").strip()
        else:
            nm = str(a).strip(); oc = ""
        if not nm: continue
        if nm.lower() == "name": continue
        out.append({"name": nm, "orcid": oc})
    return out

def fmt_author(a):
    nm = a.get("name","").strip()
    oc = a.get("orcid","").strip()
    if not nm: return ""
    if oc: return f'{nm} (<a href="{oc}">ORCID</a>)'
    return nm

# ---------- article pages ----------
def build_article_pages():
    prints = ROOT/"prints"
    if not prints.exists(): return

    records = []
    for prov in prints.glob("*/*/*/provenance.yaml"):
        data = yaml.safe_load(prov.read_text(encoding="utf-8"))

        stem = prov.parent.parent.parent.name
        doi_prefix = prov.parent.parent.name
        doi_suffix = prov.parent.name

        pf = data.get("parsed_from_pnpmd") or {}
        title   = pf.get("title") or ""
        authors = normalize_authors(pf.get("authors"))
        abstract= pf.get("abstract") or ""
        kws     = pf.get("keywords") or []
        date_norm = pf.get("date") or ""
        zenodo  = data.get("zenodo") or {}
        doi     = zenodo.get("doi") or ""
        concept = zenodo.get("concept_doi") or ""
        site_block = data.get("site") or {}
        html_canonical = site_block.get("html_canonical")
        assets_pdf = (data.get("assets") or {}).get("pdf") or ""

        artifacts = (data.get("artifacts") or {})
        md_name = artifacts.get("main") or (html_canonical and Path(html_canonical).name.replace(".html",".md"))
        add = artifacts.get("additional") or {}
        html_name = Path(html_canonical).name if html_canonical else add.get("html")
        pmd_name = add.get("pandoc_md")

        records.append({
            "prov": prov, "stem": stem,
            "doi_prefix": doi_prefix, "doi_suffix": doi_suffix,
            "title": title, "authors": authors,
            "abstract": abstract, "kws": kws,
            "date": date_norm, "doi": doi, "concept": concept,
            "assets_pdf": assets_pdf,
            "md_name": md_name, "html_name": html_name, "pmd_name": pmd_name
        })

    groups = {}
    for r in records:
        groups.setdefault(r["stem"], []).append(r)

    for stem, items in groups.items():
        def sort_key(it):
            dt = _to_datetime(it["date"])
            return dt or datetime.fromtimestamp(it["prov"].stat().st_mtime)
        versions = sorted(items, key=sort_key, reverse=True)
        latest = versions[0]

        # --- each VERSION page ---
        for it in versions:
            src = it["prov"].parent
            out_dir = OUT/"prints"/stem/it["doi_prefix"]/it["doi_suffix"]
            out_dir.mkdir(parents=True, exist_ok=True)

            for f in src.iterdir():
                if f.is_file() and f.suffix.lower() in MIRROR_EXTS:
                    dst = OUT/rel(f)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dst)

            local_md   = f"/{(OUT/rel(src/it['md_name'])).relative_to(OUT).as_posix()}" if it["md_name"] else None
            local_html = f"/{(OUT/rel(src/it['html_name'])).relative_to(OUT).as_posix()}" if it["html_name"] else None
            local_pmd  = f"/{(OUT/rel(src/it['pmd_name'])).relative_to(OUT).as_posix()}" if it["pmd_name"] else None

            html_body = ""
            if it["html_name"] and (src/it["html_name"]).exists():
                try:
                    htxt = (src/it["html_name"]).read_text(encoding="utf-8")
                    html_body = extract_html_body(htxt)
                except Exception:
                    html_body = ""

            top_links = []
            if local_md:  top_links.append(f'<a href="{local_md}">Markdown</a>')
            if it["assets_pdf"]: top_links.append(f'<a href="{it["assets_pdf"]}">PDF</a>')
            if local_pmd: top_links.append(f'<a href="{local_pmd}">Preprocessed MD</a>')

            breadcrumbs = crumb_link(["prints", stem, it["doi_prefix"], it["doi_suffix"]])
            files_list = []
            prov_local = f"/{(OUT/rel(it['prov'])).relative_to(OUT).as_posix()}"
            if local_html: files_list.append(f'<li><a href="{local_html}">{it["html_name"]}</a></li>')
            if local_md:   files_list.append(f'<li><a href="{local_md}">{it["md_name"]}</a></li>')
            files_list.append(f'<li><a href="{prov_local}">provenance.yaml</a></li>')
            if it["assets_pdf"]: files_list.append(f'<li><a href="{it["assets_pdf"]}">PDF</a></li>')
            files_ul = "<ul>" + "".join(files_list) + "</ul>"

            display_authors = it["authors"]
            authors_html = ", ".join(filter(None, (fmt_author(a) for a in display_authors)))

            body = []
            body.append("<main class='paper'>")
            body.append(breadcrumbs)
            body.append(f"<h1>{it['title']}</h1>")
            if authors_html: body.append(f"<p class='authors'>{authors_html}</p>")
            body.append(f"<p class='publine'>Preferred Frame — {month_year(it['date'])}</p>")
            body.append("<p class='links'>" + " · ".join(top_links) + "</p>")
            if it["abstract"]:
                body.append("<h2>Abstract</h2>")
                body.append(f"<p>{it['abstract']}</p>")
            body.append("<h2>Files</h2>")
            body.append(files_ul)
            if html_body:
                body.append("<h2>Article</h2>")
                body.append(html_body)
            body.append("</main>")

            version_url = f"{BASE_URL}/prints/{stem}/{it['doi_prefix']}/{it['doi_suffix']}/"
            head = []
            head.append('<meta charset="UTF-8">')
            head.append(f'<link rel="canonical" href="{version_url}">')
            if it["assets_pdf"]:
                head.append(f'<link rel="alternate" type="application/pdf" href="{it["assets_pdf"]}">')
            head.append('<meta name="robots" content="index,follow">')
            if it['title']: head.append(f'<meta name="citation_title" content="{it["title"]}">')
            for a in display_authors:
                nm = a.get("name","")
                if nm: head.append(f'<meta name="citation_author" content="{nm}">')
            if it["date"]:
                head.append(f'<meta name="citation_publication_date" content="{scholar_date(it["date"])}">')
            head.append('<meta name="citation_journal_title" content="Preferred Frame">')
            if it["assets_pdf"]:
                head.append(f'<meta name="citation_pdf_url" content="{it["assets_pdf"]}">')
            if it["doi"]:
                head.append(f'<meta name="citation_doi" content="{it["doi"]}">')
            desc = it["abstract"] or it["title"]
            if desc:
                head.append(f'<meta name="description" content="{desc}">')
                head.append(f'<meta property="og:description" content="{desc}">')
            head.append(f'<meta property="og:type" content="article">')
            head.append(f'<meta property="og:title" content="{it["title"]}">')
            head.append(f'<meta property="og:url" content="{version_url}">')

            authors_ld = []
            for a in display_authors:
                nm = a.get("name","").strip()
                oc = a.get("orcid","").strip()
                if not nm: continue
                ent = {"@type":"Person","name": nm}
                if oc: ent["sameAs"] = [oc]
                authors_ld.append(ent)
            enc = []
            if it["assets_pdf"]:
                enc.append({"@type":"MediaObject","contentUrl": it["assets_pdf"],"encodingFormat":"application/pdf"})
            article_ld = {
                "@context":"https://schema.org",
                "@type":"Article",
                "headline": it["title"],
                "author": authors_ld or [{"@type":"Person","name":"Unknown"}],
                "datePublished": iso_date_str(it["date"]),
                "isPartOf": {"@type":"Periodical","name":"Preferred Frame"},
                "url": version_url
            }
            if enc: article_ld["encoding"] = enc
            if it["doi"]:
                article_ld["sameAs"] = [f"https://doi.org/{it['doi'].split('/')[-1]}"]
            head.append(
                '<script type="application/ld+json">'
                + json.dumps(article_ld, ensure_ascii=False)
                + '</script>'
            )
            head_extra = "\n".join(head) + "\n"

            write_html(out_dir/"index.html", "\n".join(body), head_extra=head_extra)

            # DOI alias
            alias_dir = OUT/"prints"/"doi"/it["doi_prefix"]/it["doi_suffix"]
            alias_dir.mkdir(parents=True, exist_ok=True)
            write_html(alias_dir/"index.html", "\n".join(body), head_extra=head_extra)

        # --- STEM page ---
        it = latest
        src = it["prov"].parent
        stem_out = OUT/"prints"/stem
        stem_out.mkdir(parents=True, exist_ok=True)

        for f in src.iterdir():
            if f.is_file() and f.suffix.lower() in MIRROR_EXTS:
                dst = OUT/rel(f)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst)

        local_md   = f"/{(OUT/rel(src/it['md_name'])).relative_to(OUT).as_posix()}" if it["md_name"] else None
        local_html = f"/{(OUT/rel(src/it['html_name'])).relative_to(OUT).as_posix()}" if it["html_name"] else None
        local_pmd  = f"/{(OUT/rel(src/it['pmd_name'])).relative_to(OUT).as_posix()}" if it["pmd_name"] else None

        html_body = ""
        if it["html_name"] and (src/it["html_name"]).exists():
            try:
                htxt = (src/it["html_name"]).read_text(encoding="utf-8")
                html_body = extract_html_body(htxt)
            except Exception:
                html_body = ""

        breadcrumbs = crumb_link(["prints", stem])

        versions_list = []
        for v in versions:
            ver_url = f"/prints/{stem}/{v['doi_prefix']}/{v['doi_suffix']}/"
            doi_disp = f"{v['doi_prefix']}/{v['doi_suffix']}"
            date_disp = v["date"] or ""
            versions_list.append(f"<li>{date_disp} — <a href='{ver_url}'>{doi_disp}</a></li>")
        versions_ul = "<ul>" + "".join(versions_list) + "</ul>"

        files_list = []
        prov_local = f"/{(OUT/rel(it['prov'])).relative_to(OUT).as_posix()}"
        if local_html: files_list.append(f'<li><a href="{local_html}">{it["html_name"]}</a></li>')
        if local_md:   files_list.append(f'<li><a href="{local_md}">{it["md_name"]}</a></li>')
        files_list.append(f'<li><a href="{prov_local}">provenance.yaml</a></li>')
        if it["assets_pdf"]: files_list.append(f'<li><a href="{it["assets_pdf"]}">PDF</a></li>')
        files_ul = "<ul>" + "".join(files_list) + "</ul>"

        top_links = []
        if local_md:  top_links.append(f'<a href="{local_md}">Markdown (latest)</a>')
        if it["assets_pdf"]: top_links.append(f'<a href="{it["assets_pdf"]}">PDF (latest)</a>')
        if local_pmd: top_links.append(f'<a href="{local_pmd}">Preprocessed MD</a>')

        display_authors = it["authors"]
        authors_html = ", ".join(filter(None, (fmt_author(a) for a in display_authors)))

        body = []
        body.append("<main class='paper'>")
        body.append(breadcrumbs)
        body.append(f"<h1>{it['title']}</h1>")
        if authors_html: body.append(f"<p class='authors'>{authors_html}</p>")
        body.append(f"<p class='publine'>Preferred Frame — {month_year(it['date'])}</p>")
        body.append("<p class='links'>" + " · ".join(top_links) + "</p>")
        if versions_ul:
            body.append("<h2>Versions</h2>")
            body.append(versions_ul)
        body.append("<h2>Files (latest)</h2>")
        body.append(files_ul)
        if it["abstract"]:
            body.append("<h2>Abstract</h2>")
            body.append(f"<p>{it['abstract']}</p>")
        if html_body:
            body.append("<h2>Article (latest)</h2>")
            body.append(html_body)
        body.append("</main>")

        stem_url = f"{BASE_URL}/prints/{stem}/"
        head = []
        head.append('<meta charset="UTF-8">')
        head.append(f'<link rel="canonical" href="{stem_url}">')
        if it["assets_pdf"]:
            head.append(f'<link rel="alternate" type="application/pdf" href="{it["assets_pdf"]}">')
        head.append('<meta name="robots" content="index,follow">')
        if it['title']: head.append(f'<meta name="citation_title" content="{it["title"]}">')
        for a in display_authors:
            nm = a.get("name","")
            if nm: head.append(f'<meta name="citation_author" content="{nm}">')
        if it["date"]:
            head.append(f'<meta name="citation_publication_date" content="{scholar_date(it["date"])}">')
        head.append('<meta name="citation_journal_title" content="Preferred Frame">')
        if it["assets_pdf"]:
            head.append(f'<meta name="citation_pdf_url" content="{it["assets_pdf"]}">')
        if it["doi"]:
            head.append(f'<meta name="citation_doi" content="{it["doi"]}">')
        desc = it["abstract"] or it["title"]
        if desc:
            head.append(f'<meta name="description" content="{desc}">')
            head.append(f'<meta property="og:description" content="{desc}">')
        head.append(f'<meta property="og:type" content="article">')
        head.append(f'<meta property="og:title" content="{it["title"]}">')
        head.append(f'<meta property="og:url" content="{stem_url}">')

        authors_ld = []
        for a in display_authors:
            nm = a.get("name","").strip()
            oc = a.get("orcid","").strip()
            if not nm: continue
            ent = {"@type":"Person","name": nm}
            if oc: ent["sameAs"] = [oc]
            authors_ld.append(ent)
        enc = []
        if it["assets_pdf"]:
            enc.append({"@type":"MediaObject","contentUrl": it["assets_pdf"],"encodingFormat":"application/pdf"})
        article_ld = {
            "@context":"https://schema.org",
            "@type":"Article",
            "headline": it["title"],
            "author": authors_ld or [{"@type":"Person","name":"Unknown"}],
            "datePublished": iso_date_str(it["date"]),
            "isPartOf": {"@type":"Periodical","name":"Preferred Frame"},
            "url": stem_url
        }
        if enc: article_ld["encoding"] = enc
        if it["doi"]:
            article_ld["sameAs"] = [f"https://doi.org/{it['doi'].split('/')[-1]}"]
        head.append(
            '<script type="application/ld+json">'
            + json.dumps(article_ld, ensure_ascii=False)
            + '</script>'
        )
        head_extra = "\n".join(head) + "\n"

        write_html(stem_out/"index.html", "\n".join(body), head_extra=head_extra)

# ---------- dir index ----------
def breadcrumbs(rel_dir: Path) -> str:
    depth = len(rel_dir.parts)
    to_root = "./" if depth == 0 else "../"*depth
    items = [f"[🏠 Home]({to_root})"]
    for i, part in enumerate(rel_dir.parts):
        up = "../"*(len(rel_dir.parts)-i-1) or "./"
        items.append(f"/ [📂 {part}]({up})")
    return " ".join(items)

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
            mirrored = OUT/p_rel
            if mirrored.exists() and it.path.suffix.lower() in {".html",".md",".yaml",".yml",".pandoc.md"}:
                view = "/" + mirrored.relative_to(OUT).as_posix()
            lines.append(f"- 📄 {it.name}")
            if view:
                lines.append(f"  - [open]({view})")
    lines.append("")
    return "\n".join(lines)

def copy_static():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ["submit.html"]:
        src = SRC/name
        if src.exists():
            dst = OUT/name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

# ---------- sitemap & robots ----------
def _url_from_out_path(p: Path) -> str:
    """Map a file under OUT/ to its URL (canonical dir URL for index.html)."""
    rp = rel_out(p).as_posix()
    if rp == "index.html":
        return f"{BASE_URL}/"
    if rp.endswith("/index.html"):
        return f"{BASE_URL}/" + rp[:-10]  # strip 'index.html'
    # only include root-level html otherwise (e.g., submit.html)
    if p.suffix.lower() == ".html" and p.parent == OUT:
        return f"{BASE_URL}/" + rp
    return ""  # ignore other files

def build_sitemap_and_robots():
    urls = []
    for path in OUT.rglob("*.html"):
        if path.name.startswith("."):
            continue
        loc = _url_from_out_path(path)
        if not loc:
            continue
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        lastmod = mtime.strftime("%Y-%m-%dT%H:%M:%SZ")
        urls.append((loc, lastmod))

    # de-dup while preserving lastmod of latest file seen
    seen = {}
    for loc, lastmod in urls:
        if (loc not in seen) or (lastmod > seen[loc]):
            seen[loc] = lastmod

    items = []
    for loc, lastmod in sorted(seen.items()):
        items.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            "    <changefreq>weekly</changefreq>\n"
            "    <priority>0.6</priority>\n"
            "  </url>"
        )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(items) + "\n</urlset>\n"
    )
    (OUT/"sitemap.xml").write_text(sitemap, encoding="utf-8")

    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )
    (OUT/"robots.txt").write_text(robots, encoding="utf-8")

# ---------- build ----------
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/".nojekyll").write_text("", encoding="utf-8")
    write_cname_if_custom(BASE_URL)

    build_article_pages()

    # directory listings
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

        keep=[]
        for dd in list(dirnames):
            if dd in EXCLUDE_NAMES: continue
            if dd.startswith(".") and dd != ".well-known": continue
            if (Path(dirpath)/dd/"pyvenv.cfg").exists(): continue
            keep.append(dd)
        dirnames[:] = keep

        for fname in filenames:
            if fname.startswith("."): continue
            p = d/fname
            if p.suffix.lower() in MIRROR_EXTS and "prints" in p.parts:
                dst = OUT/rel(p)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dst)

        items = []
        for p in sorted([x for x in d.iterdir() if x.is_dir()], key=lambda x: x.name.lower()):
            if p.name in EXCLUDE_NAMES: continue
            if p.name.startswith(".") and p.name != ".well-known": continue
            if (p/"pyvenv.cfg").exists(): continue
            items.append(Item(name=p.name, is_dir=True, mtime=p.stat().st_mtime, path=p))
        for p in sorted([x for x in d.iterdir() if x.is_file() and not x.name.startswith(".")],
                        key=lambda x: x.name.lower()):
            if p.name in EXCLUDE_NAMES: continue
            items.append(Item(name=p.name, is_dir=False, mtime=p.stat().st_mtime, path=p))

        out_html = (OUT/rel(d)/"index.html") if d != ROOT else (OUT/"index.html")
        if out_html.exists(): continue

        md_body = format_dir_index(d, items)
        write_md_like_page(out_html, md_body)

    copy_static()

    # finally: sitemap + robots
    build_sitemap_and_robots()

if __name__ == "__main__":
    main()
