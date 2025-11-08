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
    "Makefile","index.html","_staging"
}
# PDFs are NOT mirrored to site/ (served only from assets domain)
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

    doc = "".join(s for s in (header, body_html, footer) if s is not None)

    if head_extra:
        m = re.search(r"</head\s*>", doc, re.IGNORECASE)
        if m:
            doc = doc[:m.start()] + head_extra + doc[m.start():]
        else:
            doc = head_extra + doc

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

def write_md_like_page(out_html: Path, md_body: str, head_extra: str = ""):
    body = "<main>\n<pre>\n" + md_body.replace("&","&amp;").replace("<","&lt;") + "\n</pre>\n</main>\n"
    write_html(out_html, body, head_extra=head_extra)

# ---------- tiny YAML loader (tolerant) ----------
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
        stack = [data]; indents = [0]
        for ln in lines:
            if not ln.strip() or ln.lstrip().startswith("#"): continue
            m = re.match(r'^(\s*)([^:]+):\s*(.*)$', ln)
            if not m: continue
            indent = len(m.group(1).replace("\t","  "))
            key = m.group(2).strip()
            val = m.group(3).strip()
            while indents and indent < indents[-1]:
                stack.pop(); indents.pop()
            cur = stack[-1]
            if val == "" or val == "|":
                cur[key] = {}
                stack.append(cur[key]); indents.append(indent+2)
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

def scholar_date(s: str) -> str:
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%Y/%m/%d")
    except Exception:
        return s.replace("-", "/") if s else ""

def extract_html_body(html_text: str) -> str:
    m_open = re.search(r"<body[^>]*>", html_text, flags=re.IGNORECASE|re.DOTALL)
    m_close = re.search(r"</body\s*>", html_text, flags=re.IGNORECASE|re.DOTALL)
    if m_open and m_close and m_close.start() > m_open.end():
        return html_text[m_open.end():m_close.start()]
    return html_text  # fallback

# ---------- page builders ----------
def build_article_pages():
    """
    Input layout:
      prints/<stem>/<doi_prefix>/<doi_suffix>/{ <stem>.md, <stem>.html, <stem>.pandoc.md, provenance.yaml }

    Output:
      site/prints/<stem>/<doi_prefix>/<doi_suffix>/index.html   (version page; renders that version's HTML)
      site/prints/<stem>/index.html                             (stem page; renders latest version only)
      site/prints/doi/<doi_prefix>/<doi_suffix>/index.html      (alias of version page)

    PDFs are not mirrored; pages link to assets.preferredframe.com per provenance.
    """
    prints = ROOT / "prints"
    if not prints.exists():
        return

    records = []
    for prov in prints.glob("*/*/*/provenance.yaml"):
        try:
            data = read_yaml(prov)
        except Exception:
            continue

        stem = prov.parent.parent.parent.name
        doi_prefix = prov.parent.parent.name
        doi_suffix = prov.parent.name

        pf = data.get("parsed_from_pnpmd") or {}
        title  = pf.get("title") or ""
        authors= pf.get("authors") or []
        abstract = pf.get("abstract") or ""
        kws    = pf.get("keywords") or []
        date_norm = pf.get("date") or ""
        zenodo  = data.get("zenodo") or {}
        doi     = zenodo.get("doi") or ""
        concept = zenodo.get("concept_doi") or ""
        site_block = data.get("site") or {}
        html_canonical = site_block.get("html_canonical")  # file URL on preferredframe.com
        assets_pdf = (data.get("assets") or {}).get("pdf") or ""

        artifacts = (data.get("artifacts") or {})
        md_name = artifacts.get("main") or (html_canonical and Path(html_canonical).name.replace(".html",".md"))
        add = artifacts.get("additional") or {}
        html_name = Path(html_canonical).name if html_canonical else add.get("html")
        pmd_name = add.get("pandoc_md")

        records.append({
            "prov": prov, "stem": stem,
            "doi_prefix": doi_prefix, "doi_suffix": doi_suffix,
            "title": title, "authors": authors, "abstract": abstract, "kws": kws,
            "date": date_norm, "doi": doi, "concept": concept,
            "assets_pdf": assets_pdf,
            "md_name": md_name, "html_name": html_name, "pmd_name": pmd_name
        })

    if not records:
        return

    # group by stem
    groups = {}
    for r in records:
        groups.setdefault(r["stem"], []).append(r)

    # utility: author formatting
    def fmt_author(a):
        name = a.get("name") if isinstance(a, dict) else str(a)
        orcid = a.get("orcid") if isinstance(a, dict) else None
        if orcid:
            return f'{name} (<a href="{orcid}">ORCID</a>)'
        return name

    for stem, items in groups.items():
        # sort versions by date desc; fallback to file mtime
        def sort_key(it):
            try:
                return datetime.strptime(it["date"], "%Y-%m-%d")
            except Exception:
                return datetime.fromtimestamp(it["prov"].stat().st_mtime)
        versions = sorted(items, key=sort_key, reverse=True)
        latest = versions[0]

        # ---------- Build each VERSION page ----------
        for it in versions:
            src_dir = it["prov"].parent
            out_dir = OUT / "prints" / stem / it["doi_prefix"] / it["doi_suffix"]
            out_dir.mkdir(parents=True, exist_ok=True)

            # mirror non-PDF artifacts
            for f in src_dir.iterdir():
                if f.is_file() and f.suffix.lower() in MIRROR_EXTS:
                    dst = OUT / rel(f)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dst)

            # local links (within site/)
            local_md   = f"/{(OUT/rel(src_dir/it['md_name'])).relative_to(OUT).as_posix()}" if it["md_name"] else None
            local_html = f"/{(OUT/rel(src_dir/it['html_name'])).relative_to(OUT).as_posix()}" if it["html_name"] else None
            local_pmd  = f"/{(OUT/rel(src_dir/it['pmd_name'])).relative_to(OUT).as_posix()}" if it["pmd_name"] else None

            # read HTML body to embed
            html_body = ""
            if it["html_name"] and (src_dir / it["html_name"]).exists():
                try:
                    htxt = (src_dir / it["html_name"]).read_text(encoding="utf-8")
                    html_body = extract_html_body(htxt)
                except Exception:
                    html_body = ""

            # top links: MD + PDF (+ pmd if exists)
            links = []
            if local_md:  links.append(f'<a href="{local_md}">Markdown</a>')
            if it["assets_pdf"]: links.append(f'<a href="{it["assets_pdf"]}">PDF</a>')
            if local_pmd: links.append(f'<a href="{local_pmd}">Preprocessed MD</a>')

            # page body
            body = []
            body.append("<main class='paper'>")
            body.append(f"<h1>{it['title']}</h1>")
            authors_html = ", ".join(fmt_author(a) for a in it["authors"]) if it["authors"] else ""
            if authors_html: body.append(f"<p class='authors'>{authors_html}</p>")
            body.append(f"<p class='publine'>Preferred Frame — {month_year(it['date'])}</p>")
            body.append("<p class='links'>" + " · ".join(links) + "</p>")
            if it["abstract"]:
                body.append("<h2>Abstract</h2>")
                body.append(f"<p>{it['abstract']}</p>")

            if html_body:
                body.append("<h2>Article</h2>")
                body.append("<section class='html-embed'>")
                body.append(html_body)
                body.append("</section>")

            body.append("</main>\n")

            # HEAD metadata (version)
            version_url = f"{BASE_URL}/prints/{stem}/{it['doi_prefix']}/{it['doi_suffix']}/"
            head_lines = []
            head_lines.append(f'<link rel="canonical" href="{version_url}">')
            if it["assets_pdf"]: head_lines.append(f'<link rel="alternate" type="application/pdf" href="{it["assets_pdf"]}">')
            head_lines.append('<meta name="robots" content="index,follow">')
            if it['title']: head_lines.append(f'<meta name="citation_title" content="{it["title"]}">')
            for a in it["authors"]:
                head_lines.append(f'<meta name="citation_author" content="{(a.get("name") if isinstance(a, dict) else str(a))}">')
            if it["date"]:
                head_lines.append(f'<meta name="citation_publication_date" content="{scholar_date(it["date"])}">')
            head_lines.append('<meta name="citation_journal_title" content="Preferred Frame">')
            if it["assets_pdf"]: head_lines.append(f'<meta name="citation_pdf_url" content="{it["assets_pdf"]}">')
            if it["doi"]: head_lines.append(f'<meta name="citation_doi" content="{it["doi"]}">')
            desc = it["abstract"] or it["title"]
            if desc:
                head_lines.append(f'<meta name="description" content="{desc}">')
                head_lines.append(f'<meta property="og:description" content="{desc}">')
            head_lines.append(f'<meta property="og:type" content="article">')
            head_lines.append(f'<meta property="og:title" content="{it["title"]}">')
            head_lines.append(f'<meta property="og:url" content="{version_url}">')

            # JSON-LD
            authors_ld = []
            for a in it["authors"]:
                nm = a.get("name") if isinstance(a, dict) else str(a)
                orcid = (a.get("orcid") if isinstance(a, dict) else None) or ""
                ent = {"@type":"Person","name": nm}
                if orcid: ent["sameAs"] = [orcid]
                authors_ld.append(ent)
            enc = []
            if it["assets_pdf"]:
                enc.append({"@type":"MediaObject","contentUrl": it["assets_pdf"],"encodingFormat":"application/pdf"})
            article_ld = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": it["title"],
                "author": authors_ld or [{"@type":"Person","name":"Unknown"}],
                "datePublished": it["date"] or "",
                "isPartOf": {"@type":"Periodical","name":"Preferred Frame"},
                "url": version_url
            }
            if enc: article_ld["encoding"] = enc
            if it["doi"]:
                article_ld["sameAs"] = [f"https://doi.org/{it['doi'].split('/')[-1]}"]
            head_lines.append('<script type="application/ld+json">' +
                              json.dumps(article_ld, ensure_ascii=False) +
                              '</script>')
            head_extra = "\n".join(head_lines) + "\n"

            # write version page
            out_html = out_dir / "index.html"
            write_html(out_html, "\n".join(body), head_extra=head_extra)

            # DOI alias page (optional)
            doi_alias_dir = OUT / "prints" / "doi" / it["doi_prefix"] / it["doi_suffix"]
            doi_alias_dir.mkdir(parents=True, exist_ok=True)
            alias_out = doi_alias_dir / "index.html"
            write_html(alias_out, "\n".join(body), head_extra=head_extra)

        # ---------- Build STEM (latest only) ----------
        it = latest
        src_dir = it["prov"].parent
        stem_out = OUT / "prints" / stem
        stem_out.mkdir(parents=True, exist_ok=True)

        # mirror latest artifacts (redundant if version loop already did, but harmless)
        for f in src_dir.iterdir():
            if f.is_file() and f.suffix.lower() in MIRROR_EXTS:
                dst = OUT / rel(f)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst)

        # local links for latest
        local_md   = f"/{(OUT/rel(src_dir/it['md_name'])).relative_to(OUT).as_posix()}" if it["md_name"] else None
        local_html = f"/{(OUT/rel(src_dir/it['html_name'])).relative_to(OUT).as_posix()}" if it["html_name"] else None
        local_pmd  = f"/{(OUT/rel(src_dir/it['pmd_name'])).relative_to(OUT).as_posix()}" if it["pmd_name"] else None

        # read latest HTML body
        html_body = ""
        if it["html_name"] and (src_dir / it["html_name"]).exists():
            try:
                htxt = (src_dir / it["html_name"]).read_text(encoding="utf-8")
                html_body = extract_html_body(htxt)
            except Exception:
                html_body = ""

        # top links: MD + PDF (+ pmd)
        links = []
        if local_md:  links.append(f'<a href="{local_md}">Markdown</a>')
        if it["assets_pdf"]: links.append(f'<a href="{it["assets_pdf"]}">PDF</a>')
        if local_pmd: links.append(f'<a href="{local_pmd}">Preprocessed MD</a>')

        # stem page body (latest only)
        body = []
        body.append("<main class='paper'>")
        body.append(f"<h1>{it['title']}</h1>")
        authors_html = ", ".join(fmt_author(a) for a in it["authors"]) if it["authors"] else ""
        if authors_html: body.append(f"<p class='authors'>{authors_html}</p>")
        body.append(f"<p class='publine'>Preferred Frame — {month_year(it['date'])}</p>")
        body.append("<p class='links'>" + " · ".join(links) + "</p>")
        if it["abstract"]:
            body.append("<h2>Abstract</h2>")
            body.append(f"<p>{it['abstract']}</p>")
        if html_body:
            body.append("<h2>Article</h2>")
            body.append("<section class='html-embed'>")
            body.append(html_body)
            body.append("</section>")
        body.append("</main>\n")

        # HEAD metadata (stem -> latest)
        stem_url = f"{BASE_URL}/prints/{stem}/"
        head_lines = []
        head_lines.append(f'<link rel="canonical" href="{stem_url}">')
        if it["assets_pdf"]: head_lines.append(f'<link rel="alternate" type="application/pdf" href="{it["assets_pdf"]}">')
        head_lines.append('<meta name="robots" content="index,follow">')
        if it['title']: head_lines.append(f'<meta name="citation_title" content="{it["title"]}">')
        for a in it["authors"]:
            head_lines.append(f'<meta name="citation_author" content="{(a.get("name") if isinstance(a, dict) else str(a))}">')
        if it["date"]:
            head_lines.append(f'<meta name="citation_publication_date" content="{scholar_date(it["date"])}">')
        head_lines.append('<meta name="citation_journal_title" content="Preferred Frame">')
        if it["assets_pdf"]:
            head_lines.append(f'<meta name="citation_pdf_url" content="{it["assets_pdf"]}">')
        if it["doi"]:
            head_lines.append(f'<meta name="citation_doi" content="{it["doi"]}">')
        desc = it["abstract"] or it["title"]
        if desc:
            head_lines.append(f'<meta name="description" content="{desc}">')
            head_lines.append(f'<meta property="og:description" content="{desc}">')
        head_lines.append(f'<meta property="og:type" content="article">')
        head_lines.append(f'<meta property="og:title" content="{it["title"]}">')
        head_lines.append(f'<meta property="og:url" content="{stem_url}">')

        # JSON-LD
        authors_ld = []
        for a in it["authors"]:
            nm = a.get("name") if isinstance(a, dict) else str(a)
            orcid = (a.get("orcid") if isinstance(a, dict) else None) or ""
            ent = {"@type":"Person","name": nm}
            if orcid: ent["sameAs"] = [orcid]
            authors_ld.append(ent)
        enc = []
        if it["assets_pdf"]:
            enc.append({"@type":"MediaObject","contentUrl": it["assets_pdf"],"encodingFormat":"application/pdf"})
        article_ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": it["title"],
            "author": authors_ld or [{"@type":"Person","name":"Unknown"}],
            "datePublished": it["date"] or "",
            "isPartOf": {"@type":"Periodical","name":"Preferred Frame"},
            "url": stem_url
        }
        if enc: article_ld["encoding"] = enc
        if it["doi"]:
            article_ld["sameAs"] = [f"https://doi.org/{it['doi'].split('/')[-1]}"]
        head_lines.append('<script type="application/ld+json">' +
                          json.dumps(article_ld, ensure_ascii=False) +
                          '</script>')
        head_extra = "\n".join(head_lines) + "\n"

        out_html = stem_out / "index.html"
        write_html(out_html, "\n".join(body), head_extra=head_extra)

# ---------- directory index ----------
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
            if mirrored.exists() and it.path.suffix.lower() in {".html",".md",".yaml",".yml",".pandoc.md"}:
                view = "/" + mirrored.relative_to(OUT).as_posix()
            lines.append(f"- 📄 {it.name}")
            if view:
                lines.append(f"  - [open]({view})")
    lines.append("")
    return "\n".join(lines)

def copy_static():
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

    # FIRST: build article pages & mirror assets (except PDFs)
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
        # prune visible dirs
        keep=[]
        for dd in list(dirnames):
            if dd in EXCLUDE_NAMES: continue
            if dd.startswith(".") and dd != ".well-known": continue
            if (Path(dirpath)/dd/"pyvenv.cfg").exists(): continue
            keep.append(dd)
        dirnames[:] = keep

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
