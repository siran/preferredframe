#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, subprocess, urllib.parse, shutil, re, json, io, sys, concurrent.futures
from pathlib import Path
from dataclasses import dataclass
from urllib.parse import urlparse, quote
from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo
import yaml
from feedgen.feed import FeedGenerator

# ---------- config ----------
EXCLUDE_NAMES = {
    "site","venv",".venv","env",".env","node_modules",".git",
    "__pycache__", ".mypy_cache",".pytest_cache",".ruff_cache",".cache",
    "Makefile","index.html","_staging", "pnpmd.map", "requirements.txt",
    "gpt5push.sh"
}
MIRROR_EXTS = {
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".yaml",
    ".yml",
    ".pandoc.md",
    ".txt",
}

MD_EXTS = {".md", ".markdown", ".pandoc.md"}

# ---------- Journal naming based on CNAME ----------
DEFAULT_JOURNAL = "Preferred Frame"
PREFERRED_JOURNAL = DEFAULT_JOURNAL

# ---------- repo autodetect ----------
def _parse_remote(url: str):
    try:
        if url.startswith("git@"):
            path = url.split(":", 1)[1]
        else:
            path = urllib.parse.urlparse(url).path.lstrip("/")
        if path.endswith(".git"):
            path = path[:-4]
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

    if not owner:
        owner = "siran"
    if not repo:
        repo = Path.cwd().name
    return owner, repo, branch

OWNER, REPO, BRANCH = detect_repo_branch()

# ---------- paths ----------
ROOT = Path(__file__).resolve().parents[2]
OUT  = ROOT / "site"
SRC  = ROOT / ".scripts" / "src"

# ---------- .gitignore handling ----------
def load_gitignored_paths() -> set[Path]:
    try:
        out = subprocess.check_output(
            ["git", "ls-files", "-i", "--exclude-standard", "--others", "--directory"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return set()
    paths: set[Path] = set()
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        p = (ROOT / line.rstrip("/")).resolve()
        paths.add(p)
    return paths

GITIGNORED_PATHS = load_gitignored_paths()

def is_gitignored(path: Path) -> bool:
    p = path.resolve()
    for ign in GITIGNORED_PATHS:
        try:
            p.relative_to(ign)
            return True
        except ValueError:
            continue
    return False

# ---------- base url ----------
def compute_base_url() -> str:
    v = os.getenv("BASE_URL")
    if v:
        return v.rstrip("/")
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        return f"https://{OWNER}.github.io/{REPO}"
    return "http://127.0.0.1:8000"

BASE_URL = compute_base_url()

def write_cname_if_custom(base_url: str) -> None:
    root_cname = ROOT / "CNAME"
    if root_cname.exists():
        OUT.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root_cname, OUT / "CNAME")
        return

    host = urlparse(base_url).hostname
    if not host:
        return
    if host.endswith(".github.io"):
        return
    if host in {"localhost", "127.0.0.1"}:
        return

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "CNAME").write_text(host + "\n", encoding="utf-8")

# ---------- helpers ----------
def rel(p: Path) -> Path:
    return p.relative_to(ROOT)

def rel_out(p: Path) -> Path:
    return p.relative_to(OUT)

def load_text(p: Path) -> str:
    text = p.read_text(encoding="utf-8")

    # remove exactly one trailing newline
    if text.endswith("\n"):
        return text[:-1]
    return text

@dataclass
class Item:
    name: str
    is_dir: bool
    mtime: float
    path: Path

def _asset_url(x) -> str:
    if not x:
        return ""
    if isinstance(x, str):
        return x.strip()
    if isinstance(x, dict):
        return (x.get("url") or x.get("href") or x.get("path") or "").strip()
    return ""

def _canonical_origin_from_provenance() -> str | None:
    try:
        prints_dir = ROOT / "prints"
        if not prints_dir.exists():
            return None
        for prov in prints_dir.glob("*/*/*/provenance.yaml"):
            try:
                data = yaml.safe_load(prov.read_text(encoding="utf-8")) or {}
                u = (data.get("permalink") or "").strip()
                if not u:
                    site_block = (data.get("site") or {})
                    u = (site_block.get("permalink") or site_block.get("html_canonical") or "").strip()
                if u.startswith("http"):
                    p = urlparse(u)
                    if p.scheme and p.netloc:
                        return f"{p.scheme}://{p.netloc}"
            except Exception:
                continue
    except Exception:
        pass
    return None

def iter_provenance_files():
    for top in ROOT.iterdir():
        if not top.is_dir():
            continue
        if top == OUT:
            continue
        if top.name in EXCLUDE_NAMES:
            continue
        if top.name.startswith(".") and top.name != ".well-known":
            continue
        for prov in top.glob("**/provenance.yaml"):
            if is_gitignored(prov):
                continue
            yield prov

def hidden_stems_from_provenance() -> set[tuple[str, str]]:
    stems_with_pref: set[tuple[str, str]] = set()
    stems_with_nonpref: set[tuple[str, str]] = set()

    for prov in iter_provenance_files():
        try:
            data = yaml.safe_load(prov.read_text(encoding="utf-8")) or {}
        except Exception:
            continue

        j = (data.get("journal") or "").strip()
        rel_parts = rel(prov).parts
        if len(rel_parts) < 2:
            continue
        top, stem = rel_parts[0], rel_parts[1]
        key = (top, stem)

        if not j:
            continue
        if j == PREFERRED_JOURNAL:
            stems_with_pref.add(key)
        else:
            stems_with_nonpref.add(key)

    return {k for k in stems_with_nonpref if k not in stems_with_pref}

def _origin_from_cname() -> str | None:
    for base in (ROOT, OUT):
        cname = base / "CNAME"
        if not cname.exists():
            continue
        try:
            first_line = cname.read_text(encoding="utf-8").splitlines()[0].strip()
        except Exception:
            continue
        if not first_line:
            continue
        return f"https://{first_line}"
    return None

def _current_origin() -> str:
    return (
        _origin_from_cname()
        or _canonical_origin_from_provenance()
        or os.getenv("BASE_URL")
        or BASE_URL
    ).rstrip("/")

# ---------- templating ----------
def write_html(out_html: Path, body_html: str, head_extra: str = "", title: str = ""):
    # All pages (including *.md.html mirrors) get header + breadcrumb (for mirrors)
    # + body + footer + coda.
    header = load_text(SRC / "header.html")
    footer = load_text(SRC / "footer.html")
    coda   = load_text(SRC / "coda.html")

    rel_html = rel_out(out_html).as_posix()
    breadcrumb_html = ""
    if rel_html.endswith(".md.html"):
        # Use same crumb_link style as article pages, based on path without trailing .html
        rel_no_html = re.sub(r"\.html$", "", rel_html)
        parts = list(Path(rel_no_html).parts)
        if parts and parts[-1] == "index":
            parts = parts[:-1]
        breadcrumb_html = crumb_link(parts)

    doc = "".join(
        s for s in (
            header,
            breadcrumb_html + "\n" if breadcrumb_html else "",
            body_html,
            footer,
        ) if s
    )

    # NOTE: head_extra injection is currently disabled. Re-enable this block
    # if per-page <title>/<meta> should be injected again.
    if head_extra:
        charset = '<!DOCTYPE html><meta charset="UTF-8">'
        title_tag = f"<title>{title} - {PREFERRED_JOURNAL}</title>"
        if charset not in head_extra:
            head_extra = charset + "\n" + title_tag + "\n" + head_extra
        m = re.search(r"</head\s*>", doc, re.IGNORECASE)
        if m:
            doc = doc[:m.start()] + head_extra + doc[m.start():]
        else:
            doc = head_extra + doc

    ny = ZoneInfo("America/New_York")
    now = datetime.now(ny)
    offset = now.utcoffset()
    hrs = int(offset.total_seconds() // 3600) if offset else 0
    stamp = f"(built: {now.strftime('%Y-%m-%d %H:%M %Z')} UTC{hrs:+d})"

    if not doc.endswith("\n"):
        doc += "\n"
    doc += stamp
    if coda:
        doc += coda

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(doc, encoding="utf-8")

def render_markdown_file(src: Path, dst_html: Path, title: str):
    md = src.read_text(encoding="utf-8")
    # Replace YAML front matter with a Markdown H1 so mirrors show the title, not raw YAML.
    m_front = re.match(r"^---\s*\n(.*?)\n---\s*\n", md, flags=re.DOTALL)
    if m_front:
        front = m_front.group(1)
        title_val = None
        m_title = re.search(r"^title\s*:\s*(.+)$", front, flags=re.MULTILINE)
        if m_title:
            title_val = m_title.group(1).strip().strip('"\'')
        # Remove front matter
        md = md[m_front.end():]
        if title_val:
            md = f"# {title_val}\n\n" + md
    body_html = md

    rel_html = dst_html.relative_to(OUT).as_posix()
    origin = _current_origin()
    page_url = f"{origin}/{rel_html}"
    head = [
        '<meta charset="utf-8">',
        f'<link rel="canonical" href="{page_url}">',
        f'<meta name="description" content="Rendered Markdown view for {title}">',
    ]
    head_extra = "\n".join(head) + "\n"

    write_html(dst_html, body_html, head_extra=head_extra, title=title)

def _render_single_book(book_dir: Path, meta_name: str, render_py: Path) -> tuple[Path, int, str]:
    cmd = [
        sys.executable,
        str(render_py),
        "--html",
        "--epub",
        "--omit-numbering",
        "--omit-toc",
        meta_name,
    ]
    proc = subprocess.run(
        cmd,
        cwd=book_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return book_dir, proc.returncode, proc.stdout or ""

def render_book_dirs(skip: bool = False, max_workers: int | None = None):
    """
    Find directories that declare a book.yml/book.yaml and render them to
    HTML+EPUB (skip PDF) before mirroring the tree into site().

    skip=True will bypass book rendering (useful for local quick builds).
    max_workers limits parallelism; default uses min(4, number of books).
    """
    if skip:
        print("[DEBUG] Skipping book renders (--skip-books)")
        return

    render_py = ROOT / ".scripts" / "render" / "render.py"
    if not render_py.exists():
        print(f"[DEBUG] render.py not found at {render_py}; skipping book renders")
        return

    seen: set[Path] = set()
    candidates: list[Path] = []
    for ext in ("book.yml", "book.yaml"):
        candidates.extend(ROOT.rglob(ext))

    for meta in candidates:
        try:
            meta_rel = rel(meta)
        except Exception:
            continue

        # Skip gitignored, OUT/, excluded, or hidden paths
        if is_gitignored(meta):
            continue
        try:
            meta.relative_to(OUT)
            continue
        except ValueError:
            pass

        parts = meta_rel.parts
        if not parts:
            continue
        if parts[0] in EXCLUDE_NAMES:
            continue
        if any(p.startswith(".") and p != ".well-known" for p in parts):
            continue

        book_dir = meta.parent
        if book_dir in seen:
            continue
        seen.add(book_dir)

        print(f"[DEBUG] Queued book render: {rel(book_dir)} ({meta.name})")

    book_dirs = list(seen)
    if not book_dirs:
        return

    workers = max_workers or min(4, len(book_dirs))
    print(f"[DEBUG] Rendering {len(book_dirs)} book(s) with {workers} worker(s)")

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = []
        for book_dir in book_dirs:
            meta_name = None
            for ext in ("book.yml", "book.yaml"):
                if (book_dir / ext).exists():
                    meta_name = ext
                    break
            if not meta_name:
                continue
            futures.append(
                ex.submit(_render_single_book, book_dir, meta_name, render_py)
            )

        for fut in concurrent.futures.as_completed(futures):
            book_dir, rc, out = fut.result()
            if out:
                print(out, end="" if out.endswith("\n") else "\n")
            if rc != 0:
                print(
                    f"[DEBUG] WARNING: book render failed (rc={rc}) "
                    f"for {rel(book_dir)}; continuing build"
                )

def build_simple_page_from_md(src_name: str, slug: str, title: str):
    src_md = ROOT / src_name
    if not src_md.exists():
        return
    dst_html = OUT / slug / "index.html"
    render_markdown_file(src_md, dst_html, title)

def write_md_like_page(out_html: Path, md_body: str, title: str | None = None):
    body = md_body.replace("&", "&amp;").replace("<", "&lt;")

    rel_html = rel_out(out_html).as_posix()
    origin = _current_origin()
    page_url = f"{origin}/{rel_html}"

    t = title or ""
    head = [
        '<meta charset="utf-8">',
        f'<link rel="canonical" href="{page_url}">',
        '<meta name="robots" content="index,follow">',
        f'<meta name="description" content="{t}">',
    ]
    head_extra = "\n".join(head) + "\n"

    write_html(out_html, body, head_extra=head_extra, title=t or "Index")

def crumb_link(parts: list[str]) -> str:
    html = ['<nav class="breadcrumbs">']
    html.append('<a href="/">🏠 Home</a>')
    base = ""
    for label in parts:
        base = base.rstrip("/") + "/" + quote(label)
        html.append(" / ")
        html.append(f'<a href="{base}/">📂 {label}</a>')
    html.append("</nav>")
    return "".join(html)

# ---------- dates ----------
def _to_datetime(obj) -> datetime | None:
    if isinstance(obj, datetime):
        return obj
    if isinstance(obj, date):
        return datetime.combine(obj, datetime.min.time())
    if isinstance(obj, str):
        s = obj.strip()
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
    return None

def month_year(d) -> str:
    dt = _to_datetime(d)
    if not dt:
        return str(d) if d is not None else ""
    return dt.strftime("%B %Y")

def scholar_date(x) -> str:
    if isinstance(x, datetime):
        return x.strftime("%Y/%m/%d")
    if isinstance(x, date):
        return x.strftime("%Y/%m/%d")
    if isinstance(x, str):
        x = x.strip()
        if not x:
            return ""
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", x):
            y, m, d = x.split("-")
            return f"{y}/{m}/{d}"
        if re.fullmatch(r"\d{4}-\d{2}", x):
            y, m = x.split("-")
            return f"{y}/{m}"
        if re.fullmatch(r"\d{4}", x):
            return x
        return x.replace("-", "/")
    return ""

def iso_date_str(x) -> str:
    if isinstance(x, datetime):
        return x.date().isoformat()
    if isinstance(x, date):
        return x.isoformat()
    if isinstance(x, str):
        return x.strip()
    return str(x) if x else ""

def extract_html_body(html_text: str) -> str:
    m_open = re.search(r"<body[^>]*>", html_text, flags=re.IGNORECASE | re.DOTALL)
    m_close = re.search(r"</body\s*>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if m_open and m_close and m_close.start() > m_open.end():
        return html_text[m_open.end():m_close.start()]
    return html_text

# ---------- authors ----------
def _orcid_url(v: str) -> str:
    v = (v or "").strip()
    if not v:
        return ""
    if v.startswith("http"):
        return v
    m = re.search(r"(\d{4}-\d{4}-\d{4}-\d{3}[0-9Xx])", v)
    return f"https://orcid.org/{m.group(1).upper()}" if m else ""

def normalize_authors(auth_list):
    out = []
    for a in (auth_list or []):
        if isinstance(a, dict):
            nm = (a.get("name") or a.get("full_name") or "").strip()
            oc = _orcid_url(a.get("orcid") or a.get("id") or a.get("orcid_id") or "")
            em = (a.get("email") or "").strip()
        else:
            nm = str(a).strip()
            oc = ""
            em = ""
        if not nm or nm.lower() == "name":
            continue
        item = {"name": nm}
        if oc:
            item["orcid"] = oc
        if em:
            item["email"] = em
        out.append(item)
    return out

def fmt_author(a):
    nm = a.get("name", "").strip()
    oc = _orcid_url(a.get("orcid", "").strip())
    if not nm:
        return ""
    if oc:
        return f'{nm} (<a href="{oc}">ORCID</a>)'
    return nm

# ---------- article pages ----------
def build_article_pages():
    origin = _current_origin()

    records = []
    for prov in iter_provenance_files():
        try:
            data = yaml.safe_load(prov.read_text(encoding="utf-8")) or {}
        except Exception:
            continue

        rel_parts = rel(prov).parts
        if len(rel_parts) < 4:
            continue

        top = rel_parts[0]
        stem = rel_parts[1]
        doi_prefix = rel_parts[2]
        doi_suffix = rel_parts[3]

        journal = (data.get("journal") or "").strip()

        pf_block = data.get("parsed_from_pnpmd") or {}

        title    = (data.get("title") or pf_block.get("title") or "") or ""
        abstract = (data.get("abstract") or pf_block.get("abstract") or "") or ""
        kws      = (data.get("keywords") or pf_block.get("keywords") or []) or []
        onesent  = (
            data.get("one_sentence_summary")
            or pf_block.get("one_sentence_summary")
            or pf_block.get("one_sentence")
            or ""
        )
        onesent = (onesent or "").strip()

        authors  = normalize_authors(data.get("authors") or pf_block.get("authors"))

        date_norm = (
            data.get("publication_date")
            or data.get("creation_date")
            or pf_block.get("date")
            or ""
        )

        zenodo = data.get("zenodo") or {}
        doi     = (data.get("doi") or zenodo.get("doi") or "") or ""
        concept = (data.get("concept_doi") or zenodo.get("concept_doi") or "") or ""

        permalink = (data.get("permalink") or "").strip()
        site_block = data.get("site") or {}
        html_canonical = (
            site_block.get("html_canonical")
            or site_block.get("permalink")
            or permalink
            or ""
        ).strip()

        assets = (data.get("assets") or {})
        canonical_assets = (data.get("canonical_assets") or {})
        artifacts = (data.get("artifacts") or {})

        md_name   = (artifacts.get("md") or artifacts.get("main") or None)
        html_name = (artifacts.get("html_name") or None)
        pmd_name  = (artifacts.get("pandoc_md_name") or artifacts.get("pandoc_md") or None)
        add_old   = artifacts.get("additional") or {}
        if not html_name:
            html_name = add_old.get("html")
        if not pmd_name:
            pmd_name  = add_old.get("pandoc_md")

        if not md_name and artifacts.get("md_url"):
            md_name = Path(artifacts["md_url"]).name
        if not html_name and artifacts.get("html_url"):
            html_name = Path(artifacts["html_url"]).name
        if not pmd_name and artifacts.get("pandoc_md_url"):
            pmd_name = Path(artifacts["pandoc_md_url"]).name

        assets_pdf = (
            artifacts.get("pdf_url")
            or _asset_url(assets.get("pdf"))
            or _asset_url(canonical_assets.get("pdf"))
            or ""
        )

        references_doi = data.get("references_doi") or pf_block.get("references_doi") or []
        if not isinstance(references_doi, list):
            references_doi = [references_doi]

        records.append({
            "prov": prov, "top": top, "stem": stem,
            "doi_prefix": doi_prefix, "doi_suffix": doi_suffix,
            "title": title, "authors": authors,
            "abstract": abstract, "onesent": onesent,
            "kws": kws,
            "date": date_norm, "doi": doi, "concept": concept,
            "assets_pdf": assets_pdf,
            "md_name": md_name, "html_name": html_name, "pmd_name": pmd_name,
            "html_canonical": html_canonical,
            "references_doi": references_doi,
            "journal": journal,
        })

        json.dumps(records, indent=2, default=str)

    if not records:
        return

    # group by (top-level folder, stem)
    groups: dict[tuple[str, str], list[dict]] = {}
    for r in records:
        key = (r["top"], r["stem"])
        groups.setdefault(key, []).append(r)

    for (top, stem), items in groups.items():
        def sort_key(it):
            dt = _to_datetime(it["date"])
            return dt or datetime.fromtimestamp(it["prov"].stat().st_mtime)

        versions = sorted(items, key=sort_key, reverse=True)
        latest = versions[0]

        # --- each VERSION page ---
        for it in versions:
            src = it["prov"].parent
            out_dir = OUT / top / stem / it["doi_prefix"] / it["doi_suffix"]
            out_dir.mkdir(parents=True, exist_ok=True)

            for f in src.iterdir():
                if f.is_file() and f.suffix.lower() in MIRROR_EXTS:
                    dst = OUT / rel(f)
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
            if local_md:
                top_links.append(f'<a href="{local_md}">Markdown</a>')
            if it["assets_pdf"]:
                top_links.append(f'<a href="{it["assets_pdf"]}">PDF</a>')
            if local_pmd:
                top_links.append(f'<a href="{local_pmd}">Preprocessed MD</a>')

            share_html = ""
            doi_clean = (it["doi"] or "").replace(" ", "")
            doi_fallback = ""
            if it["doi_prefix"] and it["doi_suffix"]:
                doi_fallback = f"{it['doi_prefix']}/{it['doi_suffix']}"
            if doi_clean or doi_fallback:
                doi_value = doi_clean or doi_fallback
                doi_url = f"https://doi.org/{doi_value}"
                origin = _current_origin()
                doi_alias = f"{origin}/{top}/doi/{it['doi_prefix']}/{it['doi_suffix']}"
                share_html = (
                    "<div class=\"share\"><strong>Share as:</strong><br>"
                    f'<a href="{doi_alias}">{doi_alias}</a><br>'
                    f'<a href="{doi_url}">{doi_url}</a>'
                    "</div>"
                )

            breadcrumbs = crumb_link([top, stem, it["doi_prefix"], it["doi_suffix"]])
            files_list = []
            prov_local = f"/{(OUT/rel(it['prov'])).relative_to(OUT).as_posix()}"
            if local_html:
                files_list.append(f'<li><a href="{local_html}">{it["html_name"]}</a></li>')
            if local_md:
                files_list.append(f'<li><a href="{local_md}">{it["md_name"]}</a></li>')
            files_list.append(f'<li><a href="{prov_local}">provenance.yaml</a></li>')
            if it["assets_pdf"]:
                files_list.append(f'<li><a href="{it["assets_pdf"]}">PDF</a></li>')
            files_ul = "<ul>" + "".join(files_list) + "</ul>"

            display_authors = it["authors"]
            authors_html = ", ".join(filter(None, (fmt_author(a) for a in display_authors)))

            body = []
            body.append(breadcrumbs)
            body.append("<main class='paper'>")
            body.append(f"<h1>{it['title']}</h1>")
            if authors_html:
                body.append(f"<p class='authors'>{authors_html}</p>")
            body.append(f"<p class='publine'>{PREFERRED_JOURNAL} — {month_year(it['date'])}</p>")
            body.append("<p class='links'>" + " · ".join(top_links) + "</p>")
            if share_html:
                body.append(share_html)

            if it["onesent"]:
                body.append("<h2>One-Sentence Summary</h2>")
                body.append(f"<p>{it['onesent']}</p>")

            if it["abstract"]:
                body.append("<h2>Abstract</h2>")
                body.append(f"<p>{it['abstract']}</p>")

            body.append("<h2>Files</h2>")
            body.append(files_ul)

            if html_body:
                body.append("<h2>Article</h2>")
                body.append(html_body)

            if it["references_doi"]:
                body.append("<h2>References (DOI)</h2>")
                refs_items = []
                for ref_url in it["references_doi"]:
                    ref_url = (ref_url or "").strip()
                    if not ref_url:
                        continue
                    refs_items.append(f'<li><a href="{ref_url}">{ref_url}</a></li>')
                if refs_items:
                    body.append("<ul>" + "".join(refs_items) + "</ul>")

            body.append("</main>")

            stem_seg = quote(stem, safe="")
            version_url = f"{origin}/{top}/{stem_seg}/{it['doi_prefix']}/{it['doi_suffix']}/"

            head = []
            head.append('<meta charset="utf-8">')
            head.append(f'<link rel="canonical" href="{version_url}">')
            if it["assets_pdf"]:
                head.append(f'<link rel="alternate" type="application/pdf" href="{it["assets_pdf"]}">')
            head.append('<meta name="robots" content="index,follow">')
            if it["title"]:
                head.append(f'<meta name="citation_title" content="{it["title"]}">')
            for a in display_authors:
                nm = a.get("name", "")
                if nm:
                    head.append(f'<meta name="citation_author" content="{nm}">')
            if it["date"]:
                head.append(f'<meta name="citation_publication_date" content="{scholar_date(it["date"])}">')
            head.append(f'<meta name="citation_journal_title" content="{PREFERRED_JOURNAL}">')
            if it["assets_pdf"]:
                head.append(f'<meta name="citation_pdf_url" content="{it["assets_pdf"]}">')
            if it["doi"]:
                head.append(f'<meta name="citation_doi" content="{it["doi"]}">')
            desc = it["abstract"] or it["onesent"] or it["title"]
            if desc:
                head.append(f'<meta name="description" content="{desc}">')
                head.append(f'<meta property="og:description" content="{desc}">')
            head.append('<meta property="og:type" content="article">')
            head.append(f'<meta property="og:title" content="{it["title"]}">')
            head.append(f'<meta property="og:url" content="{version_url}">')

            authors_ld = []
            for a in display_authors:
                nm = a.get("name", "").strip()
                oc = _orcid_url(a.get("orcid", "").strip())
                if not nm:
                    continue
                ent = {"@type": "Person", "name": nm}
                if oc:
                    ent["sameAs"] = [oc]
                authors_ld.append(ent)
            enc = []
            if it["assets_pdf"]:
                enc.append({
                    "@type": "MediaObject",
                    "contentUrl": it["assets_pdf"],
                    "encodingFormat": "application/pdf",
                })
            article_ld = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": it["title"],
                "author": authors_ld or [{"@type": "Person", "name": "Unknown"}],
                "datePublished": iso_date_str(it["date"]),
                "isPartOf": {"@type": "Periodical", "name": PREFERRED_JOURNAL},
                "url": version_url,
            }
            if enc:
                article_ld["encoding"] = enc
            if it["doi"]:
                article_ld["sameAs"] = [f"https://doi.org/{it['doi'].split('/')[-1]}"]
            head.append(
                '<script type="application/ld+json">'
                + json.dumps(article_ld, ensure_ascii=False)
                + "</script>"
            )
            head_extra = "\n".join(head) + "\n"
            body_html = "\n".join(body)

            write_html(out_dir/"index.html", body_html, head_extra=head_extra, title=it["title"])

            # DOI aliases live under the same top-level (prints/doi or documents/doi)
            alias_dir = OUT / top / "doi" / it["doi_prefix"] / it["doi_suffix"]
            alias_dir.mkdir(parents=True, exist_ok=True)
            write_html(alias_dir/"index.html", body_html, head_extra=head_extra, title=it["title"])

            mirror_dir = OUT / rel(src)
            mirror_dir.mkdir(parents=True, exist_ok=True)
            write_html(mirror_dir/"index.html", body_html, head_extra=head_extra, title=it["title"])

        # --- STEM page (latest) ---
        it = latest
        src = it["prov"].parent
        stem_out = OUT / top / stem
        stem_out.mkdir(parents=True, exist_ok=True)

        for f in src.iterdir():
            if f.is_file() and f.suffix.lower() in MIRROR_EXTS:
                dst = OUT / rel(f)
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

        breadcrumbs = crumb_link([top, stem])

        # Only treat records with the SAME concept DOI as versions
        same_family = []
        for v in versions:
            if it["concept"] and v["concept"] == it["concept"]:
                same_family.append(v)
            elif not it["concept"] and not v["concept"]:
                same_family.append(v)

        versions_list = []
        for v in same_family:
            ver_url  = f"/{top}/{stem}/{v['doi_prefix']}/{v['doi_suffix']}/"
            doi_disp = f"{v['doi_prefix']}/{v['doi_suffix']}"
            date_disp = v["date"] or ""
            versions_list.append(f"<li>{date_disp} — <a href='{ver_url}'>{doi_disp}</a></li>")
        versions_ul = "<ul>" + "".join(versions_list) + "</ul>" if versions_list else ""

        files_list = []
        prov_local = f"/{(OUT/rel(it['prov'])).relative_to(OUT).as_posix()}"
        if local_html:
            files_list.append(f'<li><a href="{local_html}">{it["html_name"]}</a></li>')
        if local_md:
            files_list.append(f'<li><a href="{local_md}">{it["md_name"]}</a></li>')
        files_list.append(f'<li><a href="{prov_local}">provenance.yaml</a></li>')
        if it["assets_pdf"]:
            files_list.append(f'<li><a href="{it["assets_pdf"]}">PDF</a></li>')
        files_ul = "<ul>" + "".join(files_list) + "</ul>"

        top_links = []
        if local_md:
            top_links.append(f'<a href="{local_md}">Markdown (latest)</a>')
        if it["assets_pdf"]:
            top_links.append(f'<a href="{it["assets_pdf"]}">PDF (latest)</a>')
        if local_pmd:
            top_links.append(f'<a href="{local_pmd}">Preprocessed MD</a>')

        share_html = ""
        doi_clean = (it["doi"] or "").replace(" ", "")
        doi_fallback = ""
        if it["doi_prefix"] and it["doi_suffix"]:
            doi_fallback = f"{it['doi_prefix']}/{it['doi_suffix']}"
        if doi_clean or doi_fallback:
            doi_value = doi_clean or doi_fallback
            doi_url = f"https://doi.org/{doi_value}"
            origin = _current_origin()
            doi_alias = f"{origin}/{top}/doi/{it['doi_prefix']}/{it['doi_suffix']}"
            share_html = (
                "<div class=\"share\"><strong>Share as:</strong><br>"
                f'<a href="{doi_alias}">{doi_alias}</a><br>'
                f'<a href="{doi_url}">{doi_url}</a>'
                "</div>"
            )

        display_authors = it["authors"]
        authors_html = ", ".join(filter(None, (fmt_author(a) for a in display_authors)))

        body = []
        body.append(breadcrumbs)
        body.append("<main class='paper'>")
        body.append(f"<h1>{it['title']}</h1>")
        if authors_html:
            body.append(f"<p class='authors'>{authors_html}</p>")
        body.append(f"<p class='publine'>{PREFERRED_JOURNAL} — {month_year(it['date'])}</p>")
        body.append("<p class='links'>" + " · ".join(top_links) + "</p>")
        if share_html:
            body.append(share_html)
        if versions_ul:
            body.append("<h2>Versions</h2>")
            body.append(versions_ul)
        body.append("<h2>Files (latest)</h2>")
        body.append(files_ul)

        if it["onesent"]:
            body.append("<h2>One-Sentence Summary</h2>")
            body.append(f"<p>{it['onesent']}</p>")

        if it["abstract"]:
            body.append("<h2>Abstract</h2>")
            body.append(f"<p>{it['abstract']}</p>")

        if html_body:
            body.append("<h2>Article (latest)</h2>")
            body.append(html_body)

        if it["references_doi"]:
            body.append("<h2>References (DOI)</h2>")
            refs_items = []
            for ref_url in it["references_doi"]:
                ref_url = (ref_url or "").strip()
                if not ref_url:
                    continue
                refs_items.append(f'<li><a href="{ref_url}">{ref_url}</a></li>')
            if refs_items:
                body.append("<ul>" + "".join(refs_items) + "</ul>")
        body.append("</main>")

        stem_seg = quote(stem, safe="")
        stem_url = f"{origin}/{top}/{stem_seg}/"
        head = []
        head.append('<meta charset="utf-8">')
        head.append(f'<link rel="canonical" href="{stem_url}">')
        if it["assets_pdf"]:
            head.append(f'<link rel="alternate" type="application/pdf" href="{it["assets_pdf"]}">')
        head.append('<meta name="robots" content="index,follow">')
        if it["title"]:
            head.append(f'<meta name="citation_title" content="{it["title"]}">')
        for a in display_authors:
            nm = a.get("name", "")
            if nm:
                head.append(f'<meta name="citation_author" content="{nm}">')
        if it["date"]:
            head.append(f'<meta name="citation_publication_date" content="{scholar_date(it["date"])}">')
        head.append(f'<meta name="citation_journal_title" content="{PREFERRED_JOURNAL}">')
        if it["assets_pdf"]:
            head.append(f'<meta name="citation_pdf_url" content="{it["assets_pdf"]}">')
        if it["doi"]:
            head.append(f'<meta name="citation_doi" content="{it["doi"]}">')
        desc = it["abstract"] or it["onesent"] or it["title"]
        if desc:
            head.append(f'<meta name="description" content="{desc}">')
            head.append(f'<meta property="og:description" content="{desc}">')
        head.append('<meta property="og:type" content="article">')
        head.append(f'<meta property="og:title" content="{it["title"]}">')
        head.append(f'<meta property="og:url" content="{stem_url}">')

        authors_ld = []
        for a in display_authors:
            nm = a.get("name", "").strip()
            oc = _orcid_url(a.get("orcid", "").strip())
            if not nm:
                continue
            ent = {"@type": "Person", "name": nm}
            if oc:
                ent["sameAs"] = [oc]
            authors_ld.append(ent)
        enc = []
        if it["assets_pdf"]:
            enc.append({
                "@type": "MediaObject",
                "contentUrl": it["assets_pdf"],
                "encodingFormat": "application/pdf",
            })
        article_ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": it["title"],
            "author": authors_ld or [{"@type": "Person", "name": "Unknown"}],
            "datePublished": iso_date_str(it["date"]),
            "isPartOf": {"@type": "Periodical", "name": PREFERRED_JOURNAL},
            "url": stem_url,
        }
        if enc:
            article_ld["encoding"] = enc
        if it["doi"]:
            article_ld["sameAs"] = [f"https://doi.org/{it['doi'].split('/')[-1]}"]
        head.append(
            '<script type="application/ld+json">'
            + json.dumps(article_ld, ensure_ascii=False)
            + "</script>"
        )
        head_extra = "\n".join(head) + "\n"

        write_html(stem_out/"index.html", "\n".join(body), head_extra=head_extra, title=it["title"])

# ---------- dir index ----------
def breadcrumbs(rel_dir: Path) -> str:
    depth = len(rel_dir.parts)
    to_root = "./" if depth == 0 else "../"*depth
    items = [f"[/   ]({to_root})"]
    for i, part in enumerate(rel_dir.parts):
        up = "../"*(len(rel_dir.parts)-i-1) or "./"
        items.append(f"[📂 {part} /]({up})")
    return " ".join(items)

def format_dir_index(dir_abs: Path, items: list[Item]) -> str:
    rel_dir = rel(dir_abs) if dir_abs != ROOT else Path()
    title = (rel_dir.name or f"{REPO} index")

    lines = []
    lines.append(breadcrumbs(rel_dir))
    lines.append("")

    items_sorted = sorted(items, key=lambda e: (not e.is_dir, e.name.lower()))
    for it in items_sorted:
        if it.is_dir:
            href = (it.name + "/") if rel_dir.parts else (rel(it.path).as_posix() + "/")
            href = quote(href, safe="/:@-._~")
            lines.append(f"- 📂 [{it.name}]({href})")
        else:
            p_rel = rel(it.path)          # path in repo (e.g. books/.../file.md)
            ext = it.path.suffix.lower()

            if ext in MD_EXTS:
                # rendered file lives at: OUT / <p_rel>.html
                rendered = (OUT / p_rel).with_suffix(p_rel.suffix + ".html")
                mirrored = OUT / p_rel
                rel_url = rel_out(mirrored).as_posix()
                url_local_raw = "/" + quote(rel_url, safe="/:@-._~")
                # assume it exists; if it doesn't, that's a build bug
                rel_rendered = rel_out(rendered).as_posix()
                url_local = "/" + quote(rel_rendered, safe="/:@-._~")

                gh_path = quote(p_rel.as_posix(), safe="/:@-._~")
                gh_url = (
                    f"https://github.com/{OWNER}/{REPO}/blob/"
                    f"{BRANCH}/{gh_path}"
                )

                lines.append(f"- 📄 [{it.name}]({url_local}) ([[Raw]({url_local_raw})] [[GH]({gh_url})])")
            else:
                mirrored = OUT / p_rel
                if mirrored.exists():
                    rel_url = rel_out(mirrored).as_posix()
                    url_local = "/" + quote(rel_url, safe="/:@-._~")
                    lines.append(f"- 📄 [{it.name}]({url_local})")
                else:
                    # file exists in repo but wasn't mirrored (should not happen)
                    lines.append(f"- 📄 {it.name}")

    lines.append("")
    return title, "\n".join(lines)

def copy_static():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ["submit.html"]:
        src = SRC / name
        if src.exists():
            dst = OUT / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

# ---------- sitemap & robots ----------
def _url_from_out_path(p: Path) -> str:
    rp = rel_out(p).as_posix()
    suf = p.suffix.lower()

    if suf == ".html":
        if rp == "index.html":
            path = "/"
        elif rp.endswith("/index.html"):
            path = "/" + rp[:-10]
        else:
            path = "/" + rp
    elif suf == ".md":
        path = "/" + rp
    else:
        return ""

    return quote(path, safe="/:@-._~")

def build_sitemap_and_robots():
    origin = _current_origin()

    urls = []
    for path in OUT.rglob("*"):
        if path.name.startswith("."):
            continue
        if path.suffix.lower() not in {".html", ".md"}:
            continue

        rel_url = _url_from_out_path(path)
        if not rel_url:
            continue

        loc = origin + rel_url
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        lastmod = mtime.strftime("%Y-%m-%dT%H:%M:%SZ")
        urls.append((loc, lastmod))

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
    (OUT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {origin}/sitemap.xml\n"
    )
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")

# ---------- RSS ----------
def build_rss_feed():
    origin = _current_origin()

    by_stem = {}
    for prov in iter_provenance_files():
        try:
            data = yaml.safe_load(prov.read_text(encoding="utf-8")) or {}
        except Exception:
            continue

        journal = (data.get("journal") or "").strip()
        if journal and journal != PREFERRED_JOURNAL:
            continue

        rel_parts = rel(prov).parts
        if len(rel_parts) < 2:
            continue
        top  = rel_parts[0]
        stem = rel_parts[1]

        pf_block = data.get("parsed_from_pnpmd") or {}
        title    = (data.get("title") or pf_block.get("title") or stem)
        authors  = normalize_authors(data.get("authors") or pf_block.get("authors"))
        abstract = (data.get("abstract") or pf_block.get("abstract") or "")
        onesent  = (
            data.get("one_sentence_summary")
            or pf_block.get("one_sentence_summary")
            or pf_block.get("one_sentence")
            or ""
        )
        date_norm= (data.get("publication_date") or data.get("creation_date") or pf_block.get("date") or None)
        doi      = (data.get("doi") or (data.get("zenodo") or {}).get("doi") or "")

        permalink = (data.get("permalink") or "").strip()
        if permalink and permalink.startswith("http"):
            item_url = permalink.rstrip("/")
        else:
            item_url = f"{origin}/{quote(top, safe='')}/{quote(stem, safe='')}/"

        dt = _to_datetime(date_norm) or datetime.fromtimestamp(prov.stat().st_mtime)
        keep = by_stem.get((top, stem))
        if not keep or dt > keep["date"]:
            by_stem[(top, stem)] = {
                "stem": stem,
                "top": top,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "onesent": onesent,
                "date": dt,
                "url": item_url,
                "doi": doi,
            }

    if not by_stem:
        return

    fg = FeedGenerator()
    fg.load_extension("podcast")
    fg.title(f"{PREFERRED_JOURNAL} — Publications")
    fg.link(href=origin + "/", rel="alternate")
    fg.link(href=origin + "/rss.xml", rel="self")
    fg.description(f"Latest publications from {PREFERRED_JOURNAL}")
    fg.language("en")

    items = sorted(by_stem.values(), key=lambda x: x["date"], reverse=True)
    for it in items:
        fe = fg.add_entry()
        fe.id(it["url"])
        fe.link(href=it["url"])
        fe.title(it["title"])
        desc = it["abstract"] or it["onesent"]
        if desc:
            fe.description(desc)
        for a in it["authors"]:
            nm = a.get("name", "").strip()
            if nm:
                fe.author({"name": nm})
        fe.pubDate(it["date"].astimezone(timezone.utc))
        if it["doi"]:
            fe.link(href=f'https://doi.org/{it["doi"].split("/")[-1]}', rel="related")

    rss_xml = fg.rss_str(pretty=True).decode("utf-8")
    (OUT / "rss.xml").write_text(rss_xml, encoding="utf-8")

# ---------- build ----------
def main():
    import argparse

    ap = argparse.ArgumentParser(description="Build static site")
    ap.add_argument(
        "--skip-books",
        action="store_true",
        help="Skip rendering book.yml/book.yaml directories (faster local builds).",
    )
    ap.add_argument(
        "--book-workers",
        type=int,
        default=None,
        help="Max parallel workers for book renders (default: min(4, #books)).",
    )
    args = ap.parse_args()

    global PREFERRED_JOURNAL
    PREFERRED_JOURNAL = _compute_preferred_journal()

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/".nojekyll").write_text("", encoding="utf-8")
    write_cname_if_custom(BASE_URL)

    print(f"[DEBUG] ROOT: {ROOT}")
    print(f"[DEBUG] OUT:  {OUT}")
    print(f"[DEBUG] SRC:  {SRC}")
    print(f"[DEBUG] BASE_URL: {BASE_URL}")
    print(f"[DEBUG] gitignored paths: {len(GITIGNORED_PATHS)}")

    site_src = SRC / "site"
    print(f"[DEBUG] site_src: {site_src} (exists={site_src.exists()})")

    if site_src.exists():
        for src_path in site_src.rglob("*"):
            if not src_path.is_file():
                continue
            rel_path = src_path.relative_to(site_src)
        print(f"[DEBUG] site asset found: {rel_path}")
        if src_path.suffix.lower() == ".md":
            dst_rel = rel_path.with_suffix(rel_path.suffix + ".html")
            dst_path = OUT / dst_rel
            print(f"[DEBUG]   MD (site) -> {dst_rel}")
            render_markdown_file(src_path, dst_path, title=rel_path.stem)
        else:
            dst_path = OUT / rel_path
            print(f"[DEBUG]   COPY -> {rel_path} → {dst_path.relative_to(OUT)}")
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
    else:
        print("[DEBUG] WARNING: site_src does not exist; no site/ assets copied")

    # Render any books (book.yml/book.yaml) ahead of mirroring so their
    # generated .md/.pandoc.md/.html/.epub files are present in the tree.
    render_book_dirs(skip=args.skip_books, max_workers=args.book_workers)

    build_article_pages()

    hidden_stems = hidden_stems_from_provenance()

    for dirpath, dirnames, filenames in os.walk(ROOT):
        d = Path(dirpath)

        if is_gitignored(d):
            dirnames.clear()
            continue

        if d == OUT:
            dirnames.clear()
            continue

        if dirpath != str(ROOT):
            first = Path(dirpath).relative_to(ROOT).parts[0]
            if first in EXCLUDE_NAMES:
                dirnames.clear()
                continue
            if (Path(dirpath)/"pyvenv.cfg").exists():
                dirnames.clear()
                continue

        keep=[]
        for dd in list(dirnames):
            child = Path(dirpath) / dd
            if is_gitignored(child):
                continue
            if dd in EXCLUDE_NAMES:
                continue
            if dd.startswith(".") and dd != ".well-known":
                continue
            if (Path(dirpath)/dd/"pyvenv.cfg").exists():
                continue
            keep.append(dd)
        dirnames[:] = keep

        for fname in filenames:
            p = d / fname
            if fname.startswith("."):
                continue
            if is_gitignored(p):
                continue

            if d == ROOT and fname == "index.html":
                continue

            dst = OUT / rel(p)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)

            if p.suffix.lower() == ".md":
                rendered_dst = dst.with_suffix(dst.suffix + ".html")
                render_markdown_file(p, rendered_dst, title=p.stem)

        rel_parts_d = rel(d).parts if d != ROOT else ()
        in_hidden_stem = (
            len(rel_parts_d) >= 2 and (rel_parts_d[0], rel_parts_d[1]) in hidden_stems
        )

        out_html = (OUT/rel(d)/"index.html") if d != ROOT else (OUT/"index.html")
        if out_html.exists() or in_hidden_stem:
            continue

        items = []
        for p in sorted([x for x in d.iterdir() if x.is_dir()], key=lambda x: x.name.lower()):
            if is_gitignored(p):
                continue
            if p.name in EXCLUDE_NAMES:
                continue
            if p.name.startswith(".") and p.name != ".well-known":
                continue
            if (p/"pyvenv.cfg").exists():
                continue
            p_rel_parts = rel(p).parts
            if len(p_rel_parts) >= 2 and (p_rel_parts[0], p_rel_parts[1]) in hidden_stems:
                continue
            items.append(Item(name=p.name, is_dir=True, mtime=p.stat().st_mtime, path=p))

        for p in sorted([x for x in d.iterdir() if x.is_file() and not x.name.startswith(".")],
                        key=lambda x: x.name.lower()):
            if is_gitignored(p):
                continue
            if p.name in EXCLUDE_NAMES:
                continue
            if d == ROOT and p.name == "CNAME":
                continue
            items.append(Item(name=p.name, is_dir=False, mtime=p.stat().st_mtime, path=p))

        title, md_body = format_dir_index(d, items)
        write_md_like_page(out_html, md_body, title=title)

    copy_static()
    build_sitemap_and_robots()
    build_rss_feed()

def _compute_preferred_journal() -> str:
    """
    Determine journal name from canonical origin (host).

    Mapping:
      writing.preferredframe.com   → Preferred Frame Writing
      preprints.preferredframe.com → Preferred Frame Pre-Prints
      preferredframe.com (root)    → Preferred Frame
    """
    from urllib.parse import urlparse

    host = ""
    try:
        # read exactly the same origin logic used everywhere else
        from __main__ import _current_origin  # safe because resolved after import
        origin = _current_origin()
        host = (urlparse(origin).hostname or "").lower()
    except Exception:
        return DEFAULT_JOURNAL

    if host.startswith("writing."):
        return "Preferred Frame Writing"
    if host.startswith("preprints."):
        return "Preferred Frame Pre-Prints"
    return DEFAULT_JOURNAL

if __name__ == "__main__":
    main()
