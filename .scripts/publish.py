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

import os, re, sys, shutil, subprocess
from pathlib import Path
import time
import traceback
from typing import List, Optional, Dict, Tuple
from datetime import date, datetime
import yaml
from markdown_it import MarkdownIt



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

DOI_RE = re.compile(r'\b10\.\d{4,9}/\S+\b')
ORCID_ID_RE  = re.compile(r'\b(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])\b', re.I)
ORCID_URL_RE = re.compile(r'\bhttps?://orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])\b', re.I)

def _orcid_parts(s: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (bare_id, canonical_url) if an ORCID is found anywhere in s,
    else (None, None). Bare id is what's expected by Zenodo's metadata.
    """
    if not s:
        return None, None
    m = ORCID_URL_RE.search(s) or ORCID_ID_RE.search(s)
    if not m:
        return None, None
    bare = m.group(1)
    return bare, f"https://orcid.org/{bare}"

def normalize_orcid(s: str) -> Optional[str]:
    s = s.strip()
    if not s: return None
    if s.startswith("http"): return s
    return f"https://orcid.org/{s}"

def section_text(md: str, name: str) -> str:
    pat = re.compile(rf'^\s*##\s+{re.escape(name)}\s*$', re.I | re.M)
    m = pat.search(md)
    if not m: return ""
    start = m.end()
    m2 = re.search(r'^\s*##\s+.+?$', md[start:], re.M)
    end = start + (m2.start() if m2 else len(md) - start)
    return md[start:end].strip()

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


import re
from typing import Dict, List
from markdown_it import MarkdownIt

# --- regex helpers ---
EMAIL_RE = re.compile(r'(?i)\b[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}\b')
# ORCID ID = 16 chars grouped 4-4-4-3 + checksum char (0-9X)
ORCID_ID_RE  = re.compile(r'\b(0000-\d{4}-\d{4}-\d{3}[0-9X])\b', re.I)
ORCID_URL_RE = re.compile(r'\bhttps?://orcid\.org/(0000-\d{4}-\d{4}-\d{3}[0-9X])\b', re.I)

DOI_RE = re.compile(r'\b10\.\d{4,9}/[^\s"<>]+', re.I)

def normalize_orcid(raw: str) -> str:
    """Return uppercase checksum and normalized hyphenation for an ORCID id."""
    if not raw:
        return ""
    oid = raw.upper()
    # ensure hyphenated blocks 4-4-4-3+1
    oid = oid.replace(" ", "").replace("/", "").replace("ORCID.ORG", "")
    # if it's already hyphenated correctly, keep it
    m = ORCID_ID_RE.search(oid)
    return m.group(1) if m else ""

def _orcid_parts(text: str):
    """Find first ORCID in text; return (id, url) normalized/canonical if any."""
    m_url = ORCID_URL_RE.search(text)
    if m_url:
        oid = normalize_orcid(m_url.group(1))
        return (oid, f"https://orcid.org/{oid}") if oid else (None, None)
    m_id = ORCID_ID_RE.search(text)
    if m_id:
        oid = normalize_orcid(m_id.group(1))
        return (oid, f"https://orcid.org/{oid}") if oid else (None, None)
    return (None, None)

def _split_header_authors(raw_line: str) -> List[str]:
    """
    Split the 2nd header line into author names.
    Respect the spec: it's a simple list of names.
    We split on commas or the word 'and' when used as a separator.
    """
    # Replace ' and ' with comma to unify
    s = re.sub(r'\band\b', ',', raw_line, flags=re.I)
    # Now split on commas and strip
    parts = [p.strip() for p in s.split(',')]
    # Drop empties
    parts = [p for p in parts if p]
    return parts

def parse_pnpmd(md_text: str) -> Dict:
    """
    Parse PNPMD using markdown-it-py for robust section extraction.
    Header lines:
      % Title
      % Author(s)
      % Date
    Sections used:
      ## One-Sentence Summary
      ## Abstract
      ## Keywords        (first non-empty line; comma-separated)
      ## About Author(s) (list items: name, optional orcid/email)
    Also scans ORCIDs and DOIs anywhere in the document.
    """
    # --- percent header (Pandoc-style) ---
    lines = md_text.replace("\r\n", "\n").splitlines()
    head = []
    for i in range(min(3, len(lines))):
        if lines[i].lstrip().startswith("%"):
            head.append(lines[i].lstrip()[1:].strip())
        else:
            break
    title = head[0] if len(head) >= 1 else ""
    raw_authors_line = head[1] if len(head) >= 2 else ""
    pub_date = head[2] if len(head) >= 3 else ""

    # Split authors from the 2nd line: commas and standalone "and"
    # Avoid empty fragments; strip spaces.
    header_authors = []
    if raw_authors_line:
        # Replace " and " with comma, then split on commas
        tmp = re.sub(r'\s+\band\b\s+', ',', raw_authors_line)
        header_authors = [a.strip() for a in tmp.split(",") if a.strip()]

    # strip header from body for section parsing
    body_start = len(head)
    md_body = "\n".join(lines[body_start:])

    # --- parse sections with markdown-it ---
    md = MarkdownIt("commonmark")
    tokens = md.parse(md_body)

    def collect_sections(tok_list) -> Dict[str, str]:
        sections = {}
        i = 0
        while i < len(tok_list):
            t = tok_list[i]
            if t.type == "heading_open" and t.tag in {"h2", "h3", "h4", "h5", "h6"}:
                if i + 1 < len(tok_list) and tok_list[i + 1].type == "inline":
                    sec_title = tok_list[i + 1].content.strip()
                    level = int(t.tag[1])
                    j = i + 2
                    buf = []
                    while j < len(tok_list):
                        tt = tok_list[j]
                        if tt.type == "heading_open" and int(tt.tag[1]) <= level:
                            break
                        buf.append(tt.map and "\n".join(lines[tt.map[0]+body_start:tt.map[1]+body_start]) if tt.map else tt.content)
                        j += 1
                    sections[sec_title] = "\n".join(x for x in buf if x is not None).strip()
                    i = j
                    continue
            i += 1
        return sections

    secs = collect_sections(tokens)

    def get_sec(name: str) -> str:
        for k, v in secs.items():
            if k.strip().lower() == name.strip().lower():
                return v
        return ""

    one_sentence = get_sec("One-Sentence Summary")
    abstract     = get_sec("Abstract")
    kb           = get_sec("Keywords")
    about        = get_sec("About Author(s)")

    # --- keywords: first non-empty line, comma-separated ---
    keywords = []
    if kb:
        first_line = next((ln.strip() for ln in kb.splitlines() if ln.strip()), "")
        if first_line:
            keywords = [k.strip() for k in first_line.split(",") if k.strip()]

    # ---------- Author parsing helpers ----------
    def _normalize_name(name: str) -> str:
        # Lowercase, collapse spaces, strip punctuation except period (keeps initials)
        base = re.sub(r"[^\w.\s]", "", name.lower())
        return re.sub(r"\s+", " ", base).strip()

    def _extract_email(text: str) -> Optional[str]:
        m = re.search(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", text)
        return m.group(0) if m else None

    def _extract_orcid(text: str) -> Tuple[Optional[str], Optional[str]]:
        # Prefer URL if present; otherwise bare ID
        murl = ORCID_URL_RE.search(text)
        mid  = ORCID_ID_RE.search(text)
        if murl:
            oid = normalize_orcid(murl.group(1))
            return oid, f"https://orcid.org/{oid}" if oid else None
        if mid:
            oid = normalize_orcid(mid.group(1))
            return oid, f"https://orcid.org/{oid}" if oid else None
        return None, None

    # ---------- Parse About Author(s) lines ----------
    about_authors: Dict[str, Dict[str, str]] = {}
    if about:
        for raw in about.splitlines():
            line = raw.strip()
            if not line:
                continue
            # Accept bullet "* " or "- " or bare line
            m = re.match(r'^[\*\-\u2022]\s+(.*)$', line)
            body = m.group(1).strip() if m else line

            # Split by commas NOT inside parentheses
            parts = [p.strip() for p in re.split(r',(?![^()]*\))', body) if p.strip()]
            if not parts:
                continue

            name = parts[0]
            email = _extract_email(body)
            orcid_id, orcid_url = _extract_orcid(body)

            entry = {"name": name}
            if email:
                entry["email"] = email
            if orcid_id:
                entry["orcid"] = orcid_id
            if orcid_url:
                entry["orcid_url"] = orcid_url

            about_authors[_normalize_name(name)] = entry

    # ---------- Merge: start from header order, enrich from About ----------
    merged: List[Dict[str, str]] = []
    seen_keys = set()

    for nm in header_authors:
        key = _normalize_name(nm)
        base = {"name": nm}
        if key in about_authors:
            # enrich while preserving header display name
            enriched = dict(about_authors[key])
            enriched["name"] = nm
            merged.append(enriched)
            seen_keys.add(key)
        else:
            merged.append(base)
            seen_keys.add(key)

    # Append About-only authors not present in header
    for key, entry in about_authors.items():
        if key not in seen_keys:
            merged.append(entry)

    # ---------- Fallback: if no authors parsed at all ----------
    if not merged and raw_authors_line:
        merged = [{"name": nm} for nm in header_authors]

    # --- scans (global) ---
    found_orcids = sorted({
        o for o in (
            [normalize_orcid(m.group(1)) for m in ORCID_URL_RE.finditer(md_text)] +
            [normalize_orcid(m.group(1)) for m in ORCID_ID_RE.finditer(md_text)]
        ) if o
    })

    dois = set(DOI_RE.findall(md_text))
    doi_urls = sorted({"https://doi.org/" + d.rstrip('.,);:]') for d in dois})

    # Ensure at least one ORCID appears inside authors if any ORCID is found globally
    if found_orcids and all("orcid" not in a for a in merged):
        # Assign the first found ORCID to the first author (best-effort fallback)
        merged[0]["orcid"] = found_orcids[0]
        merged[0]["orcid_url"] = f"https://orcid.org/{found_orcids[0]}"

    return {
        "title": title,
        "authors": merged,
        "date": pub_date,
        "one_sentence": (one_sentence or "").strip(),
        "abstract": (abstract or "").strip(),
        "keywords": keywords,
        "scanned_orcids": found_orcids,
        "reference_doi_urls": doi_urls
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

def normalize_pub_date(pnpmd_date: Optional[str]) -> str:
    cand = pnpmd_date.strip()
    if cand:
        dt = _try_parse_date(cand)
        if dt:
            day = dt.day if dt.day != 0 else 1
            return f"{dt.year:04d}-{dt.month:02d}-{day:02d}"
    t = date.today(); return t.strftime("%Y-%m-%d")


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

def delete_file_if_exists(api: str, token: str, dep_id: int, filename: str):
    files = list_files(api, token, dep_id)
    for f in files:
        if (f.get("filename")) == filename:
            file_id = f.get("id")
            if file_id:
                echo(f"+ DELETE existing file on Zenodo: {filename} (id={file_id})")
                http_json("DELETE", f"{api}/deposit/depositions/{dep_id}/files/{file_id}", token)
            break

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
    publication_date_long = format_long_date(publication_date_iso)

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
