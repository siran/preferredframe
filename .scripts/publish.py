#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preferred Frame publisher (PNPMD-driven, commit = publication; DOI reserved first)

Fix: normalize PNPMD date -> ISO 'YYYY-MM-DD' for Zenodo.
"""

import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from datetime import date, datetime

# ---------------- util: stdout-only, echo every command ----------------

def echo(msg: str):
    print(msg, flush=True)

def die(msg: str, code: int = 1):
    echo(f"ERROR: {msg}")
    sys.exit(code)

def run(cmd: List[str], cwd: Optional[Path]=None, check=True) -> str:
    echo("+ " + " ".join(str(x) for x in cmd))
    p = subprocess.run(cmd,
                       cwd=str(cwd) if cwd else None,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       text=True)
    out = (p.stdout or "")
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    if check and p.returncode != 0:
        die(f"command failed with exit code {p.returncode}", p.returncode)
    return out

# ---------------- git helpers ----------------

def git_repo_root(path: Path) -> Path:
    out = run(["git", "rev-parse", "--show-toplevel"], cwd=path)
    root = out.strip()
    if not root:
        die("not inside a git repository")
    return Path(root)

def git_status_clean(repo: Path) -> bool:
    out = run(["git", "status", "--porcelain"], cwd=repo)
    return out.strip() == ""

def git_head(repo: Path) -> str:
    return run(["git", "rev-parse", "HEAD"], cwd=repo).strip()

def git_origin_url(repo: Path) -> str:
    out = run(["git", "config", "--get", "remote.origin.url"], cwd=repo)
    return out.strip()

# ---------------- env / http ----------------

def zenodo_api_and_token(use_sandbox: bool=False) -> Tuple[str, str]:
    api = os.environ.get("ZENODO_API",
                         "https://sandbox.zenodo.org/api" if use_sandbox else "https://zenodo.org/api")
    token_env = "ZENODO_SANDBOX_TOKEN" if use_sandbox else "ZENODO_TOKEN"
    token = os.environ.get(token_env)
    if not token:
        die(f"Missing token. Set {token_env}.")
    return api, token

def http_json(method: str, url: str, token: str, data=None, files=None) -> Dict:
    try:
        import requests
    except Exception:
        die("Missing dependency: requests. Install with: pip install requests")
    echo(f"+ HTTP {method.upper()} {url}")
    headers = {"Authorization": f"Bearer {token}"}
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
ORCID_URL_RE = re.compile(r'https?://orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])\b', re.I)
ORCID_ID_RE  = re.compile(r'\b(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])\b')

def normalize_orcid(s: str) -> Optional[str]:
    s = (s or "").strip()
    if not s:
        return None
    if s.startswith("http"):
        return s
    return f"https://orcid.org/{s}"

def parse_pnpmd(md_text: str) -> Dict:
    lines = md_text.splitlines()
    head = []
    for i in range(min(3, len(lines))):
        if lines[i].lstrip().startswith("%"):
            head.append(lines[i].lstrip()[1:].strip())
        else:
            break
    title = head[0] if len(head) >= 1 else ""
    raw_authors_line = head[1] if len(head) >= 2 else ""
    pub_date = head[2] if len(head) >= 3 else ""

    header_authors = []
    if raw_authors_line:
        parts = re.split(r'\band\b|,', raw_authors_line)
        header_authors = [p.strip() for p in parts if p.strip()]

    def section_text(name: str) -> str:
        pat = re.compile(rf'^\s*##\s+{re.escape(name)}\s*$', re.I | re.M)
        m = pat.search(md_text)
        if not m: return ""
        start = m.end()
        m2 = re.search(r'^\s*##\s+.+?$', md_text[start:], re.M)
        end = start + (m2.start() if m2 else len(md_text) - start)
        return md_text[start:end].strip()

    one_sentence = section_text("One-Sentence Summary").strip()
    abstract = section_text("Abstract").strip()
    keywords_block = section_text("Keywords").strip()

    keywords = []
    if keywords_block:
        first_line = next((ln.strip() for ln in keywords_block.splitlines() if ln.strip()), "")
        if first_line:
            keywords = [k.strip() for k in first_line.split(",") if k.strip()]

    about = section_text("About Author(s)")
    parsed_authors = []
    for ln in about.splitlines():
        m = re.match(r'^\s*[\*\-]\s+(.*)$', ln)
        if not m: continue
        body = m.group(1).strip()
        parts = [p.strip() for p in body.split(",")]
        name = parts[0] if parts else ""
        orcid = None
        email = None
        for p in parts[1:]:
            if "orcid.org" in p or ORCID_ID_RE.search(p):
                oid = ORCID_URL_RE.search(p)
                orcid = normalize_orcid(oid.group(1)) if oid else normalize_orcid(ORCID_ID_RE.search(p).group(1))
            elif "@" in p:
                email = p
        if name:
            entry = {"name": name}
            if orcid: entry["orcid"] = orcid
            if email: entry["email"] = email
            parsed_authors.append(entry)

    if not parsed_authors and header_authors:
        parsed_authors = [{"name": nm} for nm in header_authors]

    found_orcids = sorted({normalize_orcid(m.group(1)) for m in ORCID_URL_RE.finditer(md_text)} |
                          {normalize_orcid(m.group(1)) for m in ORCID_ID_RE.finditer(md_text)} - {None})
    dois = set(DOI_RE.findall(md_text))
    doi_urls = sorted({"https://doi.org/" + d.rstrip('.,);:]') for d in dois})

    return {
        "title": title,
        "authors": parsed_authors,
        "date": pub_date,
        "one_sentence": one_sentence,
        "abstract": abstract,
        "keywords": keywords,
        "scanned_orcids": found_orcids,
        "reference_doi_urls": doi_urls
    }

# ---- date normalization ----

MONTHS = {
    m.lower(): i for i, m in enumerate(
        ["January","February","March","April","May","June","July","August","September","October","November","December"], 1
    )
}
def _try_parse_date(s: str) -> Optional[datetime]:
    s = s.strip()
    fmts = [
        "%Y-%m-%d", "%Y/%m/%d",
        "%Y-%m", "%Y/%m",
        "%Y",
        "%B %Y",        # October 2025
        "%b %Y",        # Oct 2025
        "%B %d, %Y",    # October 3, 2025
        "%b %d, %Y",    # Oct 3, 2025
        "%d %B %Y",     # 3 October 2025
        "%d %b %Y",     # 3 Oct 2025
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    # Free-form: "October 2025" with extra spaces, etc.
    m = re.match(r'^\s*([A-Za-z]+)\s+(\d{4})\s*$', s)
    if m:
        mon = MONTHS.get(m.group(1).lower())
        yr  = int(m.group(2))
        if mon:
            return datetime(yr, mon, 1)
    return None

def normalize_pub_date(pnpmd_date: Optional[str], folder_date: str) -> str:
    # Prefer PNPMD header if parseable; else use folder date; else today's date
    cand = (pnpmd_date or "").strip()
    if cand:
        dt = _try_parse_date(cand)
        if dt:
            # If only year/month given, ensure day exists
            day = dt.day if dt.day != 0 else 1
            return f"{dt.year:04d}-{dt.month:02d}-{day:02d}"
    # Folder date should already be ISO (prints/YYYY-MM-DD)
    if re.match(r"^\d{4}-\d{2}-\d{2}$", folder_date):
        return folder_date
    # Fallback to today
    t = date.today()
    return t.strftime("%Y-%m-%d")

# Minimal YAML writer (no external dependency)
def to_yaml(obj, indent=0):
    sp = "  " * indent
    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, str):
        if obj == "" or obj.strip() != obj or any(c in obj for c in [":", "-", "{", "}", "[", "]", "#", ",", "&", "*", "!", "|", ">", "'", '"', "%", "@", "`"]):
            s = obj.replace("\\","\\\\").replace('"','\\"')
            return f"\"{s}\""
        return obj
    if isinstance(obj, list):
        if not obj:
            return "[]"
        lines=[]
        for it in obj:
            val = to_yaml(it, indent+1)
            if "\n" in val:
                lines.append(f"{sp}- |\n" + "\n".join(("  "*(indent+1)+l) for l in val.splitlines()))
            else:
                lines.append(f"{sp}- {val}")
        return "\n".join(lines)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        lines=[]
        for k,v in obj.items():
            key = str(k)
            val = to_yaml(v, indent+1)
            if isinstance(v, (dict, list)):
                lines.append(f"{sp}{key}:\n{val}")
            else:
                lines.append(f"{sp}{key}: {val}")
        return "\n".join(lines)
    return to_yaml(str(obj), indent)

# ---------------- main ----------------

def main():
    ap = argparse.ArgumentParser(
        description="Publish a Preferred Frame print (commit = publish; DOI reserved first; PNPMD-driven)."
    )
    ap.add_argument("md_path", help="Path to the source .md (must be inside a git repo).")
    ap.add_argument("--date", help="YYYY-MM-DD folder under prints/. Defaults to today.")
    ap.add_argument("--license", default="CC-BY-4.0", help="License (e.g., CC-BY-4.0).")
    ap.add_argument("--community", help="Zenodo community slug (e.g., preferredframe).")
    ap.add_argument("--journal", default="Preferred Frame", help="Journal title for Zenodo metadata.")
    ap.add_argument("--sandbox", action="store_true", help="Use Zenodo sandbox.")
    ap.add_argument("--yes", action="store_true", help="Proceed without interactive confirmation.")
    ap.add_argument("--push", action="store_true", help="git push after each commit.")
    args = ap.parse_args()

    script_dir = Path(__file__).resolve().parent
    src_md = Path(args.md_path).resolve()
    if not src_md.exists() or src_md.suffix.lower() != ".md":
        die("Path must exist and point to a .md file.")

    # Source repo must be clean
    try:
        src_repo = git_repo_root(src_md.parent)
    except SystemExit:
        die("Source file is not inside a git repository.")
    if not git_status_clean(src_repo):
        die(f"Source repo has uncommitted changes: {src_repo}")
    src_commit = git_head(src_repo)
    src_origin = git_origin_url(src_repo)

    # Site repo = current working dir, must be clean
    try:
        site_repo = git_repo_root(Path.cwd())
    except SystemExit:
        die("Current working directory is not inside a git repository (site repo).")
    if not git_status_clean(site_repo):
        die(f"Site repo has uncommitted changes: {site_repo}")
    site_head_before = git_head(site_repo)

    # Destination layout
    if args.date:
        date_str = args.date
    else:
        date_str = date.today().isoformat()
    original_stem = src_md.stem  # exact stem, no slugging
    dst_dir = site_repo / "prints" / date_str / original_stem
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst_md = dst_dir / src_md.name

    # Copy .md
    echo(f"+ copy {src_md} -> {dst_md}")
    shutil.copy2(src_md, dst_md)

    # Render (no fallback). Must produce pdf, html, pandoc.md
    render_py = (script_dir / "render.py") if (script_dir / "render.py").exists() else Path(shutil.which("render.py") or "")
    if not render_py or not render_py.exists():
        die("render.py not found beside this script or in PATH.")
    run([sys.executable, str(render_py), "--all", str(dst_md)], cwd=dst_dir, check=True)

    dst_pdf = dst_md.with_suffix(".pdf")
    dst_html = dst_md.with_suffix(".html")
    dst_pandoc_md = dst_md.with_suffix(".pandoc.md")

    if not dst_pdf.exists():
        die(f"Expected PDF missing after render: {dst_pdf}")
    if not dst_html.exists():
        die(f"Expected HTML missing after render: {dst_html}")
    if not dst_pandoc_md.exists():
        die(f"Expected pandoc-preprocessed MD missing: {dst_pandoc_md}")

    # Parse PNPMD
    md_text = dst_md.read_text(encoding="utf-8")
    parsed = parse_pnpmd(md_text)

    title = parsed["title"] or original_stem
    creators = []
    for a in parsed["authors"]:
        c = {"name": a["name"]}
        if "orcid" in a and a["orcid"]:
            c["orcid"] = a["orcid"]
        creators.append(c)
    abstract = parsed["abstract"]
    keywords = parsed["keywords"]
    ref_dois = parsed["reference_doi_urls"]
    pnpmd_date_raw = parsed["date"].strip() if parsed["date"] else ""
    publication_date = normalize_pub_date(pnpmd_date_raw, date_str)  # <-- ISO fix

    # Zenodo metadata (reservation)
    related_identifiers = [{"relation": "references",
                            "identifier": d,
                            "resource_type": "publication"} for d in ref_dois]
    zenodo_meta = {
        "upload_type": "publication",
        "publication_type": "article",
        "title": title,
        "creators": creators or [{"name": "Unknown"}],
        "description": abstract or "No description provided.",
        "keywords": keywords or [],
        "journal_title": args.journal,
        "publication_date": publication_date,      # <-- ISO guaranteed
        "license": args.license,
        "prereserve_doi": True
    }
    if related_identifiers:
        zenodo_meta["related_identifiers"] = related_identifiers

    api, token = zenodo_api_and_token(args.sandbox)

    # Create deposition, PUT metadata to reserve DOI
    dep = http_json("POST", f"{api}/deposit/depositions", token, data={})
    dep_id = dep.get("id")
    if not dep_id:
        die("Could not create deposition (no id).")
    dep = http_json("PUT", f"{api}/deposit/depositions/{dep_id}", token, data={"metadata": zenodo_meta})
    reserved_doi = None
    try:
        reserved_doi = (dep.get("metadata", {}).get("prereserve_doi", {}) or {}).get("doi")
    except Exception:
        reserved_doi = None

    # Provenance (YAML) — include reserved DOI + both dates
    provenance = {
        "published_by_commit": True,
        "journal": args.journal,
        "site_repo": str(site_repo),
        "site_repo_head": site_head_before,
        "source": {
            "md_path": str(src_md),
            "repo": str(src_repo),
            "origin": src_origin,
            "commit": src_commit
        },
        "copied_to": str(dst_md),
        "date_folder": date_str,
        "artifacts": {
            "main": dst_md.name,
            "additional": {
                "pdf": dst_pdf.name,
                "html": dst_html.name,
                "pandoc_md": dst_pandoc_md.name
            }
        },
        "parsed_from_pnpmd": {
            "title": title,
            "authors": creators,
            "date_raw": pnpmd_date_raw,                 # original PNPMD date
            "date_normalized": publication_date,        # ISO used for Zenodo
            "one_sentence_summary": parsed["one_sentence"],
            "abstract": abstract,
            "keywords": keywords
        },
        "scanned": {
            "authors_orcid": parsed["scanned_orcids"],
            "references_doi": ref_dois
        },
        "zenodo": {
            "deposition_id": dep_id,
            "reserved_doi": reserved_doi,
            "doi": None,
            "record_id": None
        }
    }
    prov_path = dst_dir / "provenance.yaml"

    # Preview & confirm (or --yes)
    zenodo_meta_preview = dict(zenodo_meta)
    if args.community:
        zenodo_meta_preview["communities"] = [{"identifier": args.community}]

    echo("\n--- PROVENANCE (YAML to be written) ---")
    echo(to_yaml(provenance))
    echo("\n--- ZENODO METADATA (reserved DOI phase) ---")
    echo(json.dumps(zenodo_meta_preview, indent=2))
    echo(f"\n--- RESERVED DOI ---\n{reserved_doi or '(unavailable)'}")
    echo("\n--- FILES TO COMMIT (publication) ---")
    for p in [dst_md, dst_pdf, dst_html, dst_pandoc_md, prov_path]:
        echo(f" - {p.relative_to(site_repo)}")
    echo("\n--- FILES TO UPLOAD TO ZENODO ---")
    for p in [dst_pdf, dst_md, dst_pandoc_md, dst_html]:
        echo(f" - {p.name}")

    if not args.yes:
        ans = input("\nProceed with publication commit and DOI minting? [y/N]: ").strip().lower()
        if ans not in ("y","yes"):
            die("Aborted by user.", 0)

    # Commit = publication
    echo(f"+ write {prov_path}")
    prov_path.write_text(to_yaml(provenance) + "\n", encoding="utf-8")
    run(["git", "add", "-A"], cwd=site_repo)
    run(["git", "commit", "-m",
         f"Publish print: {title} ({publication_date}); source {src_commit[:10]} as '{original_stem}'"], cwd=site_repo)
    if args.push:
        run(["git", "push"], cwd=site_repo)

    # Upload files and publish
    for path in [dst_pdf, dst_md, dst_pandoc_md, dst_html]:
        with open(path, "rb") as fh:
            http_json("POST", f"{api}/deposit/depositions/{dep_id}/files", token,
                      files={"file": (path.name, fh)})

    if args.community:
        http_json("PUT", f"{api}/deposit/depositions/{dep_id}", token,
                  data={"metadata": {"communities": [{"identifier": args.community}]}})

    published = http_json("POST", f"{api}/deposit/depositions/{dep_id}/actions/publish", token)
    final_doi = (published.get("doi") or (published.get("metadata") or {}).get("doi"))
    record_id = published.get("record_id")

    # Write back final DOI
    provenance["zenodo"]["doi"] = final_doi
    provenance["zenodo"]["record_id"] = record_id
    echo(f"+ update {prov_path} with final DOI/record_id")
    prov_path.write_text(to_yaml(provenance) + "\n", encoding="utf-8")
    run(["git", "add", str(prov_path)], cwd=site_repo)
    run(["git", "commit", "-m", f"Record DOI for {title}: {final_doi}"], cwd=site_repo)
    if args.push:
        run(["git", "push"], cwd=site_repo)

    echo(f"\n✅ Publication committed and DOI minted\nReserved DOI: {reserved_doi}\nFinal DOI: {final_doi}\nRecord ID: {record_id}\nFolder: {dst_dir}")

if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code if isinstance(e.code, int) else 0)
    except Exception as e:
        die(str(e))
