#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preferred Frame publisher (PNPMD-driven; commit = publication; DOI = final)

Layout (human-first; spaces preserved):
  - Repo files are stored at: prints/<stem>/<doi_prefix>/<doi_suffix>/{<stem>.md, .html, .pandoc.md, provenance.yaml}
  - PDF lives ONLY in the assets repo at: assets.preferredframe.com/preferredframe/<stem>/<doi_prefix>/<doi_suffix>/<filename>.pdf

Flow:
  1) Preflight: source & site repos clean (prompt to continue if dirty); create work branch (slugged)
  2) Stage copy of src.md into prints/_staging/<stem>/ and render (.pdf, .html, .pandoc.md)
  3) Parse PNPMD; scan ORCIDs & DOIs; normalize publication_date (ISO yyyy-mm-dd)
  4) Reserve deposition; get DOI (& concept DOI if available)
  5) Move rendered files to final path prints/<stem>/<doi_prefix>/<doi_suffix>/
  6) Write full provenance (print it), then single confirmation
  7) Commit site repo; copy PDF to assets repo & push; update Zenodo with FULL metadata; upload files; publish
  8) Merge publish branch into main locally and push only main
"""

import io
import json
import os, re, sys, shutil, subprocess
from pathlib import Path
import time
import traceback
from typing import List, Optional, Dict, Tuple
from datetime import date, datetime
import yaml
import panflute as pf


#### to quote URLs with special characters using PyYaml ####
# characters that tend to confuse parsers if left unquoted in URLs
_URL_UNSAFE_CHARS = set(" \t()[]{}<>|\"'")

class PFYamlDumper(yaml.SafeDumper):
    pass


def _needs_double_quotes_for_url(s: str) -> bool:
    if "://" not in s:
        return False
    # quote if any unsafe char appears
    return any(c in _URL_UNSAFE_CHARS for c in s)

def _pf_represent_str(dumper: yaml.Dumper, data: str):
    # feed raw string to PyYAML; only set style for specific cases
    style = '"' if _needs_double_quotes_for_url(data) else None
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)

PFYamlDumper.add_representer(str, _pf_represent_str)


# ---------------- util ----------------

def echo(msg: str):
    print(msg, flush=True)

def die(msg: str, code: int = 1):
    echo(f"ERROR: {msg}")
    sys.exit(code)

def run(cmd: List[str], cwd: Optional[Path]=None, check=True) -> str:
    echo("+ " + " ".join(str(x) for x in cmd))
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = (p.stdout)
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    if check and p.returncode != 0:
        die(f"command failed with exit code {p.returncode}", p.returncode)
    return out

def format_long_date(d: date | str) -> str:
    """Return 'January 25, 2025'. Accepts date or ISO 'YYYY-MM-DD'."""
    if isinstance(d, str):
        d = date.fromisoformat(d)
    try:
        # Linux/macOS
        return d.strftime("%B %-d, %Y")
    except ValueError:
        # Windows (uses %#d)
        return d.strftime("%B %#d, %Y")

# ---------------- git helpers ----------------

def slug_branch(s: str) -> str:
    s = s.lower()
    s = re.sub(r'[^a-z0-9._-]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    s = s.lstrip('.-')
    if s.endswith('.lock'):
        s = s[:-5] + '-lock'
    return s[:80] or 'x'

def git_repo_root(path: Path) -> Path:
    out = run(["git", "rev-parse", "--show-toplevel"], cwd=path)
    root = out.strip()
    if not root: die("not inside a git repository")
    return Path(root)

def git_status_clean(repo: Path) -> bool:
    out = run(["git", "status", "--porcelain"], cwd=repo)
    return out.strip() == ""

def git_head(repo: Path) -> str:
    return run(["git", "rev-parse", "HEAD"], cwd=repo).strip()

def git_origin_url(repo: Path) -> str:
    return run(["git", "config", "--get", "remote.origin.url"], cwd=repo).strip()

# ---------------- env / http ----------------

def zenodo_api_and_token(env: str) -> Tuple[str, str]:
    """
    Resolve Zenodo API base + token from the selected environment.
    - requires ZENODO_TOKEN, ZENODO_API
    """
    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        die("Missing ZENODO_TOKEN for --env prod.")

    api = os.environ.get("ZENODO_SANDBOX_API", "https://sandbox.zenodo.org/api")
    if env == "prod":
        api = os.environ.get("ZENODO_API", "https://zenodo.org/api")

    return api, token

def http_put_raw(url: str, token: str, fp):
    """PUT raw bytes to Zenodo bucket (S3-like). fp must be a binary file handle."""
    try:
        import requests
    except Exception:
        die("Missing dependency: requests. Install with: pip install requests")
    echo(f"+ HTTP PUT (raw) {url}")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(url, data=fp, headers=headers)
    if not r.ok:
        try: print(r.text)
        except Exception: pass
        die(f"Zenodo bucket PUT error {r.status_code} at {url}")
    return r.json() if "application/json" in (r.headers.get("Content-Type","")) else {}


def http_json(method: str, url: str, token: str, data=None, files=None) -> Dict:
    try:
        import requests
    except Exception:
        die("Missing dependency: requests. Install with: pip install requests")
    echo(f"+ HTTP {method.upper()} {url}")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"{data=}")
    print(f"{files=}")
    if method.upper() in ("POST","PUT","PATCH"):
        r = requests.request(method, url, headers=headers, json=data, files=files)
    else:
        r = requests.request(method, url, headers=headers, params=data)
    if not r.ok:
        try: echo(r.text)
        except Exception: pass
        die(f"Zenodo API error {r.status_code} at {url}")
    try:
        return r.json()
    except Exception:
        return {}

# ---------------- PNPMD parsing & scans ----------------
def normalize_markdown_prose(md: str) -> str:
    """
    Convert markdown prose to a single string without hard-wrapped newlines.
    - Single newlines inside a paragraph → space
    - Blank lines (paragraph breaks) preserved
    """
    if not md:
        return ""

    lines = md.replace("\r\n", "\n").split("\n")
    out = []
    buf = []

    def flush_buf():
        if buf:
            # join wrapped lines into a single paragraph
            out.append(" ".join(x.strip() for x in buf if x.strip()))
            buf.clear()

    for line in lines:
        if not line.strip():  # blank line → paragraph break
            flush_buf()
            out.append("")  # represent blank paragraph
        else:
            buf.append(line)
    flush_buf()

    # rejoin paragraphs with a blank line between them
    return "\n\n".join(out).strip()

def replace_header_date(md_text: str, new_date_iso: str) -> str:
    """
    Replace the 3rd percent-header line with the given date ("Month D, YYYY").
    If no 3rd line exists, insert it after existing % lines (or at top if none).
    """
    lines = md_text.replace("\r\n", "\n").splitlines()
    long_date = format_long_date(new_date_iso)

    # Find/replace within initial consecutive % lines (<= 3 expected)
    head_count = 0
    out = []
    i = 0
    while i < len(lines) and lines[i].lstrip().startswith("%"):
        head_count += 1
        if head_count == 3:
            out.append(f"% {long_date}")      # replace date line
        else:
            out.append(lines[i])              # keep title/authors
        i += 1

    # If there were < 3 header lines, insert the date line now
    if head_count < 3:
        out.append(f"% {long_date}")

    # Append the rest of the document body
    out.extend(lines[i:])
    return "\n".join(out)

# ---- regexes ----
ORCID_URL_RE = re.compile(r"https?://orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[0-9Xx])")
ORCID_ID_RE  = re.compile(r"\b(\d{4}-\d{4}-\d{4}-\d{3}[0-9Xx])\b", re.IGNORECASE)
EMAIL_RE     = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
DOI_RE       = re.compile(r"\b10\.\d{4,9}/[^\s\"<>]+", re.IGNORECASE)

def _norm_orcid(s: str) -> str:
    return s.upper().replace(" ", "")

def _key(n: str) -> str:
    import unicodedata
    n = unicodedata.normalize("NFKC", n).lower()
    return " ".join(ch for ch in re.sub(r"[^0-9a-z. ]+", " ", n).split())

def _collect_section(doc: pf.Doc, title: str):
    blocks = list(doc.content)
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if isinstance(b, pf.Header) and pf.stringify(b).strip().lower() == title.lower():
            level = b.level
            j = i + 1
            out = []
            while j < len(blocks):
                if isinstance(blocks[j], pf.Header) and blocks[j].level <= level:
                    break
                out.append(blocks[j])
                j += 1
            return out
        i += 1
    return []

def _listish(blocks):
    """Yield list items (ListItem) if lists, else paragraphs as singletons."""
    for b in blocks:
        if isinstance(b, (pf.BulletList, pf.OrderedList)):
            for li in b.content:
                yield li
        elif isinstance(b, pf.ListItem):
            yield b
        elif isinstance(b, pf.Para):
            yield b

def _stringify_blocks(blocks) -> str:
    blks = list(blocks)
    if not blks:
        return ""
    # Wrap list of blocks into a single Element so stringify can walk it
    return pf.stringify(pf.Div(*blks)).strip()


def _extract_about_authors(items) -> List[Dict[str, str]]:
    authors = []
    for it in items:
        text = pf.stringify(it).strip()
        if not text:
            continue

        # Name = text up to first comma (keeps commas later intact)
        name = text.split(",", 1)[0].strip()

        m_email = EMAIL_RE.search(text)
        email = m_email.group(0) if m_email else None

        m_orcid_url = ORCID_URL_RE.search(text)
        m_orcid_id  = ORCID_ID_RE.search(text)
        orcid = None
        if m_orcid_url:
            orcid = _norm_orcid(m_orcid_url.group(1))
        elif m_orcid_id:
            orcid = _norm_orcid(m_orcid_id.group(1))

        entry = {"name": name}
        if orcid:
            entry["orcid"] = orcid
        if email:
            entry["email"] = email
        authors.append(entry)
    return authors

def _pandoc_doc(md_text: str) -> pf.Doc:
    # get Pandoc JSON
    p = subprocess.run(
        ["pandoc", "-f", "markdown+tex_math_dollars", "-t", "json"],
        input=md_text.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )
    ast = json.loads(p.stdout)                 # <-- dict
    # feed a *stream* to panflute.load
    return pf.load(io.StringIO(json.dumps(ast)))

def parse_pnpmd(md_text: str) -> Dict:
    """
    Parse PNPMD with Pandoc → Pandoc JSON → panflute.Doc
    Works even if convert_text returns list instead of Doc.
    """
    # Call Pandoc manually and capture JSON
    p = subprocess.run(
        ["pandoc", "-f", "markdown+tex_math_dollars", "-t", "json"],
        input=md_text.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )

    # Load panflute Doc
    doc = _pandoc_doc(md_text)
    meta = doc.get_metadata()
    # --- after reading meta = doc.get_metadata() ---

    def _meta_str(x):
        return x if isinstance(x, str) else pf.stringify(x) if x is not None else ""

    def _split_header_authors(s: str) -> List[str]:
        """
        Split a single author line like 'A, B and C' → ['A','B','C'].
        Conservative: split on ' and ' or commas not inside parentheses.
        """
        # prefer ' and ' and ';'
        parts = re.split(r'\s+\band\b\s+|;', s)
        if len(parts) == 1:
            # fallback: commas not inside parentheses
            parts = re.split(r',(?![^()]*\))', s)
        return [p.strip() for p in parts if p.strip()]

    meta = doc.get_metadata()
    title = _meta_str(meta.get("title", ""))
    pub_date = _meta_str(meta.get("date", ""))

    raw_auth = meta.get("author", [])
    if isinstance(raw_auth, list):
        # some pandoc versions put a single combined string in a 1-item list
        if len(raw_auth) == 1 and isinstance(raw_auth[0], str):
            header_authors = _split_header_authors(raw_auth[0])
        else:
            header_authors = [_meta_str(a) for a in raw_auth]
    elif isinstance(raw_auth, str):
        header_authors = _split_header_authors(raw_auth)
    else:
        header_authors = []


    # Title / date
    def _meta_str(x):
        return x if isinstance(x, str) else pf.stringify(x) if x is not None else ""
    title = _meta_str(meta.get("title", ""))
    pub_date = _meta_str(meta.get("date", ""))

    # Authors from percent header → Pandoc meta
    meta_auth = meta.get("author", [])
    header_authors = []
    if isinstance(meta_auth, list):
        header_authors = [_meta_str(a) for a in meta_auth]
    elif isinstance(meta_auth, str):
        header_authors = [meta_auth]

    # Sections
    one_sentence = _stringify_blocks(_collect_section(doc, "One-Sentence Summary")).strip()
    abstract     = _stringify_blocks(_collect_section(doc, "Abstract")).strip()
    kb_text      = _stringify_blocks(_collect_section(doc, "Keywords"))
    about_blocks = _collect_section(doc, "About Author(s)")
    refs_blocks  = _collect_section(doc, "References")

    # Keywords: first non-empty line, comma-separated
    first_line = next((ln.strip() for ln in kb_text.splitlines() if ln.strip()), "")
    keywords = [k.strip() for k in first_line.split(",") if k.strip()] if first_line else []

    # About authors (list items or paragraphs)
    about_items = list(_listish(about_blocks))
    about_parsed = _extract_about_authors(about_items)
    about_index = {_key(a["name"]): a for a in about_parsed}

    # Merge: preserve header order; enrich from About
    merged = []
    seen = set()
    for nm in header_authors:
        k = _key(nm)
        if k in about_index:
            e = dict(about_index[k]); e["name"] = nm
            merged.append(e); seen.add(k)
        else:
            merged.append({"name": nm}); seen.add(k)
    for k, e in about_index.items():
        if k not in seen:
            merged.append(e)

    # Fallback: if no authors at all but meta has a single string
    if not merged and header_authors:
        merged = [{"name": nm} for nm in header_authors]

    # Reference DOIs: scan the References section only (then de-dup)
    refs_text = _stringify_blocks(refs_blocks)
    ref_dois = sorted({m.group(0).rstrip('.,);:]') for m in DOI_RE.finditer(refs_text)})
    reference_doi_urls = [f"https://doi.org/{d}" for d in ref_dois]

    # Global ORCIDs (optional: may help fill a missing one)
    full_text = pf.stringify(doc)
    global_orcids = sorted({
        _norm_orcid(m.group(1)) for m in ORCID_URL_RE.finditer(full_text)
    } | {
        _norm_orcid(m.group(1)) for m in ORCID_ID_RE.finditer(full_text)
    })
    if global_orcids and all("orcid" not in a for a in merged) and merged:
        merged[0]["orcid"] = global_orcids[0]

    return {
        "title": title,
        "date": pub_date,
        "one_sentence": one_sentence,
        "abstract": abstract,
        "keywords": keywords,
        "authors": merged,                 # [{name, orcid?, email?}]
        "reference_doi_urls": reference_doi_urls
    }


# ---- date normalization ----
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January","February","March","April","May","June","July","August","September","October","November","December"], 1)}

def _try_parse_date(s: str) -> Optional[datetime]:
    s = s.strip()
    fmts = ["%Y-%m-%d","%Y/%m/%d","%Y-%m","%Y/%m","%Y","%B %Y","%b %Y","%B %d, %Y","%b %d, %Y","%d %B %Y","%d %b %Y"]
    for fmt in fmts:
        try: return datetime.strptime(s, fmt)
        except Exception: pass
    m = re.match(r'^\s*([A-Za-z]+)\s+(\d{4})\s*$', s)
    if m:
        mon = MONTHS.get(m.group(1).lower()); yr = int(m.group(2))
        if mon: return datetime(yr, mon, 1)
    return None

# ---------------- steps ----------------

def prepare_branch(site_repo: Path, stem: str, src_commit: str) -> str:
    date_str = date.today().strftime("%Y-%m")
    branch_name = f"publish/{date_str}-{slug_branch(stem)}-{src_commit[:8]}"
    echo(f"+ git checkout -b {branch_name}")
    run(["git", "checkout", "-b", branch_name], cwd=site_repo)
    return branch_name

def render_in_staging(site_repo: Path, src_md: Path) -> Tuple[Path, Path, Path, Path]:
    stem = src_md.stem
    staging = site_repo / "prints" / "_staging" / stem
    staging.mkdir(parents=True, exist_ok=True)
    dst_md = staging / src_md.name
    echo(f"+ copy {src_md} -> {dst_md}")
    shutil.copy2(src_md, dst_md)

    script_dir = Path(__file__).resolve().parent
    render_py = (script_dir / "render.py") if (script_dir / "render.py").exists() else Path(shutil.which("render.py"))
    if not render_py or not render_py.exists():
        die("render.py not found beside this script or in PATH.")
    run([sys.executable, str(render_py), "--all", str(dst_md)], cwd=staging, check=True)

    dst_pdf = dst_md.with_suffix(".pdf")
    dst_html = dst_md.with_suffix(".html")
    dst_pmd  = dst_md.with_suffix(".pandoc.md")
    for p in (dst_pdf, dst_html, dst_pmd):
        if not p.exists(): die(f"Expected artifact missing after render: {p}")
    return staging, dst_md, dst_pdf, dst_html

def reserve_deposition(api: str, token: str,
                       title: str, creators: List[Dict], abstract: str,
                       one_sentence: str, keywords: List[str],
                       publication_date: str, publication_year: str, site_html_url: str,
                       site_md_url: str, assets_pdf_url: str,
                       community: str, journal: str) -> Tuple[int, str, Optional[str]]:
    dep = http_json("POST", f"{api}/deposit/depositions", token, data={})
    dep_id = dep.get("id")
    if not dep_id: die("Could not create deposition (no id).")

    related_identifiers = [
        {"relation": "isIdenticalTo", "identifier": site_html_url,  "resource_type": "publication"},
        {"relation": "isIdenticalTo", "identifier": site_md_url,    "resource_type": "publication"},
        {"relation": "isIdenticalTo", "identifier": assets_pdf_url, "resource_type": "publication"},
    ]

    zenodo_meta = {
        "upload_type": "publication",
        "publication_type": "article",
        "title": title,
        "creators": creators,
        "description": normalize_markdown_prose(abstract),
        "notes": normalize_markdown_prose(one_sentence),
        "keywords": keywords,
        "journal_title": journal,
        "publisher": {"name": journal},
        "publication_year": publication_year,
        "date": publication_date,
        "license": "cc-by-4.0",
        "related_identifiers": related_identifiers,
        "communities": [{"identifier": community}],
        "prereserve_doi": True
    }
    dep = http_json("PUT", f"{api}/deposit/depositions/{dep_id}", token, data={"metadata": zenodo_meta})
    pr = (dep.get("metadata")).get("prereserve_doi")
    reserved_doi = pr.get("doi")
    concept_doi = pr.get("conceptdoi")  # may be missing in sandbox or certain flows
    return dep_id, reserved_doi, concept_doi

def dump_yaml(obj) -> str:
    return yaml.dump(
        obj,
        Dumper=PFYamlDumper,   # our custom SafeDumper subclass
        sort_keys=False,
        allow_unicode=True,
        width=1000,
        default_flow_style=False,
    )


def write_provenance(dst_dir: Path, dst_md: Path, dst_pdf: Path, dst_html: Path, dst_pmd: Path,
                     src_origin: str, src_commit: str,
                     title: str, creators: List[Dict], parsed: Dict,
                     publication_date: str, creation_date: str, doi: str, concept_doi: Optional[str],
                     assets_pdf_url: str, site_html_url: str, site_md_url:str, site_pandoc_md_url:str,
                     version_permalink: str) -> Path:

    prov = {
        "journal": "Preferred Frame",
        "publication_type": "article",
        "title": title,
        "doi": doi,
        "concept_doi": concept_doi,
        "permalink": version_permalink,
        "publication_date": publication_date,
        "creation_date": creation_date,
        "keywords": parsed["keywords"],
        "one_sentence_summary": normalize_markdown_prose(parsed["one_sentence"]),
        "abstract": normalize_markdown_prose(parsed["abstract"]),
        "authors": creators,
        "references_doi": parsed["reference_doi_urls"],
        "source": {
            "repo_origin": src_origin,
            "commit": src_commit,
            "filename": dst_md.name,
        },
        "artifacts": {
            "md": dst_md.name,
            "md_url": site_md_url,
            "pandoc_md_name": dst_pmd.name,
            "pandoc_md_url": site_pandoc_md_url,
            "pdf_name": dst_pdf.name,
            "pdf_url": assets_pdf_url,
            "html_name": dst_html.name,
            "html_url": site_html_url,
        },
    }

    prov_path = dst_dir / "provenance.yaml"
    echo(f"+ write {prov_path}")
    prov_path.write_text(dump_yaml(prov), encoding="utf-8")
    return prov_path

def get_deposition(api: str, token: str, dep_id: int) -> Dict:
    return http_json("GET", f"{api}/deposit/depositions/{dep_id}", token)

def list_files(api: str, token: str, dep_id: int) -> List[Dict]:
    dep = get_deposition(api, token, dep_id)
    return dep.get("files")

def ensure_draft_or_die(api: str, token: str, dep_id: int) -> Dict:
    dep = get_deposition(api, token, dep_id)
    state = dep.get("state")          # "unsubmitted" or "inprogress" are drafts
    submitted = dep.get("submitted")        # True after submit
    links = dep.get("links")
    bucket = links.get("bucket")
    can_upload = (submitted in (False, None)) and bool(bucket)
    if not can_upload:
        echo(f"\nZenodo deposition {dep_id} is not modifiable via bucket:")
        echo(f"  state={state!r}, submitted={submitted!r}, has_bucket={bool(bucket)}")
        die("Cannot upload: need a draft with a bucket link. Create a new version or unlock draft.")
    return dep  # includes links.bucket

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Publish a Preferred Frame print (PNPMD).")
    ap.add_argument("md_path", help="Path to the source .md (must be inside a git repo).")
    ap.add_argument("--env", choices=["sandbox","prod"], default="sandbox",
                    help="Zenodo environment (default: sandbox)")
    ap.add_argument("--community", default="preferredframe", help="Zenodo community slug.")
    ap.add_argument("--journal", default="Preferred Frame", help="Journal title shown in Zenodo.")
    ap.add_argument("--assets-dir", default="../assets", help="Path to local assets repo (default: ../assets).")
    ap.add_argument("--assets-base-url", default="https://assets.preferredframe.com",
                    help="Public base URL for assets (default: https://assets.preferredframe.com)")
    ap.add_argument("--no-assets-push", action="store_true", help="Do not push the assets repo (default: push).")
    args = ap.parse_args()

    # ---- repos & preflight ----
    src_md = Path(args.md_path).resolve()
    src_repo = git_repo_root(src_md.parent)
    if not git_status_clean(src_repo):
        input(f"Source repo has uncommitted changes: {src_repo}. Press Enter to continue or Ctrl-C to abort.")
    src_commit = git_head(src_repo); src_origin = git_origin_url(src_repo)

    site_repo = git_repo_root(Path.cwd())
    if not git_status_clean(site_repo):
        input(f"Site repo has uncommitted changes: {site_repo}. Press Enter to continue or Ctrl-C to abort.")

    stem = src_md.stem

    # ---- branch ----
    branch_name = prepare_branch(site_repo, stem, src_commit)

    # ---- stage & render ----
    staging, staged_md, staged_pdf, staged_html = render_in_staging(site_repo, src_md)
    staged_pmd = staged_md.with_suffix(".pandoc.md")

    # ---- parse PNPMD & normalized date ----
    parsed = parse_pnpmd(staged_md.read_text(encoding="utf-8"))
    creators = []
    for a in parsed["authors"]:
        if not a.get("name"):
            continue
        creators.append({
            "name": a["name"],
            **({"orcid": a["orcid"]} if a.get("orcid") else {}),
            **({"email": a["email"]} if a.get("email") else {}),
        })
    title = parsed["title"]


    # Publication date (today), used for everything
    publication_date_iso = date.today().isoformat()          # e.g. '2025-01-25'
    publication_year = publication_date_iso[0:4]

    # Replace header date in the staged markdown
    md_text = staged_md.read_text(encoding="utf-8")
    md_text = replace_header_date(md_text, publication_date_iso)
    staged_md.write_text(md_text, encoding="utf-8")

    # Make "creation_date" equal to publication date (as requested)
    publication_date = publication_date_iso

    # ---- site URLs (temporary; corrected after final move) ----
    tmp_html_url = f"https://preferredframe.com/prints/_staging/{stem}/{staged_html.name}"
    tmp_md_url   = f"https://preferredframe.com/prints/_staging/{stem}/{staged_md.name}"
    # temporary assets URL (will be recomputed after DOI)
    tmp_assets_pdf_url = f"{args.assets_base_url}/preferredframe/_staging/{stem}/{staged_pdf.name}"

    # ---- Zenodo API (env-aware) ----
    api, token = zenodo_api_and_token(args.env)
    dep_id, reserved_doi, concept_doi = reserve_deposition(
        api, token,
        title, creators, parsed["abstract"], parsed["one_sentence"], parsed["keywords"],
        publication_date, publication_year, tmp_html_url, tmp_md_url, tmp_assets_pdf_url,
        args.community, args.journal
    )
    doi = reserved_doi

    # ---- final destination based on FULL DOI path ----
    # e.g., doi = "10.5281/zenodo.398094" -> prefix "10.5281", suffix "zenodo.398094"
    if "/" in doi:
        doi_prefix, doi_suffix = doi.split("/", 1)
    else:
        die("no / in reserved DOI?")
        # doi_prefix, doi_suffix = "10.xxxx", (doi or "x")
    final_dir = site_repo / "prints" / stem / doi_prefix / doi_suffix
    final_dir.mkdir(parents=True, exist_ok=True)

    # move files into final place
    final_md   = final_dir / staged_md.name
    final_pdf  = final_dir / staged_pdf.name
    final_html = final_dir / staged_html.name
    final_pmd  = final_dir / staged_pmd.name
    for src, dst in [(staged_md, final_md),(staged_pdf, final_pdf),
                     (staged_html, final_html),(staged_pmd, final_pmd)]:
        echo(f"+ move {src} -> {dst}")
        shutil.move(str(src), str(dst))

    # cleanup staging dir (best-effort)
    try:
        shutil.rmtree(staging)
    except Exception:
        pass

    # corrected site URLs (for provenance + Zenodo related_identifiers)
    site_html_url = f"https://preferredframe.com/prints/{stem}/{doi_prefix}/{doi_suffix}/{final_html.name}"
    site_md_url   = f"https://preferredframe.com/prints/{stem}/{doi_prefix}/{doi_suffix}/{final_md.name}"
    site_pandoc_md_url   = f"https://preferredframe.com/prints/{stem}/{doi_prefix}/{doi_suffix}/{final_pmd.name}"
    version_permalink = f"https://preferredframe.com/prints/{stem}/{doi_prefix}/{doi_suffix}/"

    # FINAL assets URL mirrors prints/ (no date folder)
    assets_pdf_url = f"{args.assets_base_url}/preferredframe/{stem}/{doi_prefix}/{doi_suffix}/{final_pdf.name}"

    # ---- write FULL provenance (then show it) ----
    prov_path = write_provenance(final_dir, final_md, final_pdf, final_html, final_pmd,
                                 src_origin, src_commit,
                                 title, creators, parsed, publication_date, publication_year,
                                 doi, concept_doi, assets_pdf_url, site_html_url,
                                 site_md_url, site_pandoc_md_url, version_permalink)

    echo("\n--- PROVENANCE ---")
    print(prov_path)
    with open(prov_path, "r", encoding="utf-8") as f:
        print(f.read(), end="")

    # ---- summary before confirmation ----
    echo("\n--- FILES TO COMMIT (site repo) ---")
    for p in [final_md, final_html, final_pmd, prov_path]:
        echo(f" - {p.relative_to(site_repo)}")
    echo("\n--- FILES TO UPLOAD TO ZENODO ---")
    for p in [final_pdf, final_md, final_pmd, final_html]:
        echo(f" - {p.name}")

    # ---- single confirmation ----
    ans = input("\nProceed with publication commit and DOI minting? [y/N]: ").strip().lower()
    if ans not in ("y","yes"):
        sys.exit(0)

    # ---- commit site repo ----
    run(["git", "add", str(final_md)], cwd=site_repo)
    run(["git", "add", str(final_html)], cwd=site_repo)
    run(["git", "add", str(final_pmd)], cwd=site_repo)
    run(["git", "add", str(prov_path)], cwd=site_repo)
    run(["git", "commit", "-m",
         f"Publish print: {title} ({publication_date}); source {src_commit[:10]} as '{final_md.stem}'"], cwd=site_repo)

    # ---- copy PDF to assets repo & push (default ON) ----
    if args.assets_dir:
        assets_repo = Path(args.assets_dir).resolve()
        if not (assets_repo / ".git").exists():
            die(f"Assets dir is not a git repo: {assets_repo}")
        dest = assets_repo / "preferredframe" / stem / doi_prefix / doi_suffix / final_pdf.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        echo(f"+ copy {final_pdf} -> {dest}")
        shutil.copy2(final_pdf, dest)
        if not args.no_assets_push:
            run(["git", "add", "-A"], cwd=assets_repo)
            run(["git", "commit", "-m", f"{title}.pdf ({publication_date}, {doi})"], cwd=assets_repo)
            run(["git", "push"], cwd=assets_repo)

    # ---- rebuild FULL metadata (same as reservation) + final related_identifiers ----
    final_related = [
        {"relation": "isIdenticalTo", "identifier": site_html_url,  "resource_type": "publication"},
        {"relation": "isIdenticalTo", "identifier": site_md_url,    "resource_type": "publication"},
        {"relation": "isIdenticalTo", "identifier": assets_pdf_url, "resource_type": "publication"},
    ]

    full_meta = {
        "upload_type": "publication",
        "publication_type": "article",
        "title":                       title,
        "creators":                    creators,
        "description":                 normalize_markdown_prose(parsed["abstract"]),
        "notes":                       normalize_markdown_prose(parsed["one_sentence"]),
        "keywords":                    parsed["keywords"],
        "journal_title":               args.journal,
        "publication_date":            publication_date,
        "license":                     "cc-by-4.0",
        "related_identifiers":         final_related,
        "communities":                 [{"identifier": args.community}],
        "prereserve_doi":              True,
    }

    _ = http_json(
        "PUT",
        f"{api}/deposit/depositions/{dep_id}",
        token,
        data={"metadata": full_meta}
    )


    # ---- upload to Zenodo via bucket (overwrites by name) & publish ----
    dep = ensure_draft_or_die(api, token, dep_id)
    bucket_url = (dep.get("links") ).get("bucket")
    if not bucket_url:
        die("Draft has no bucket link; cannot upload.")

    # push artifacts (order: PDF, md, pandoc.md, html)
    for path in [final_pdf, final_md, final_pmd, final_html]:
        fname = path.name
        # Zenodo requires URL-escaped filename segment
        from urllib.parse import quote
        put_url = f"{bucket_url}/{quote(fname)}"
        with open(path, "rb") as fh:
            http_put_raw(put_url, token, fh)


        print("sleeping 1")
        time.sleep(1)


    _published = http_json("POST", f"{api}/deposit/depositions/{dep_id}/actions/publish", token)

    # ---- merge publish branch into main locally, then push only main ----
    run(["git", "checkout", "main"], cwd=site_repo)
    run(["git", "merge", "--no-ff", branch_name], cwd=site_repo)
    run(["git", "push", "origin", "main"], cwd=site_repo)
    run(["git", "branch", "-d", branch_name], cwd=site_repo)

    echo(f"\n✅ Publication committed and DOI minted"
         f"\nVersion DOI: {doi}"
         f"\nConcept DOI: {concept_doi or '(none)'}"
         f"\nPermalink: {version_permalink}"
         f"\nFolder: {final_dir}")

if __name__ == "__main__":
    main()
