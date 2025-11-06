#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preferred Frame publisher (PNPMD-driven; commit = publication; reserved DOI = final DOI)

Flow:
  1) Preflight: source & site repos clean; create work branch (slugged)
  2) Copy src.md -> prints/YYYY-MM-DD/<stem>/<src.md>
  3) render.py --all (must produce .pdf, .html, .pandoc.md)
  4) Parse PNPMD; scan ORCIDs & DOIs; normalize publication_date (ISO)
  5) Detect prior provenance (versions)
  6) Reserve DOI; build permalink from reserved DOI; write provenance
  7) Single confirmation (or abort -> prompt cleanup)
  8) Commit (publication)
  9) Copy PDF to assets repo (default ../assets) & push (default ON); also copy PDF into site/assets mirror
 10) Upload files; publish (reserved DOI becomes final); sanity check
 11) Prompt to push branch; prompt to merge to main
On any error or manual abort, offer cleanup.

Env:
  ZENODO_TOKEN (prod) or ZENODO_SANDBOX_TOKEN (--sandbox)
  ZENODO_API (optional override)
"""

import argparse, os, re, shutil, subprocess, sys
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from datetime import date, datetime

# ---------------- util ----------------

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

# --- safe git ref/branch slug (filenames are NEVER slugged) ---
def slug_branch(s: str) -> str:
    s = s.lower()
    s = re.sub(r'[^a-z0-9._-]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    s = s.lstrip('.-')
    if s.endswith('.lock'):
        s = s[:-5] + '-lock'
    return s[:80] or 'x'

def slug_title_for_permalink(s: str) -> str:
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+','-', s)
    s = re.sub(r'-{2,}','-', s).strip('-')
    return s or "x"

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

def normalize_pub_date(pnpmd_date: Optional[str], folder_date: str) -> str:
    cand = (pnpmd_date or "").strip()
    if cand:
        dt = _try_parse_date(cand)
        if dt:
            day = dt.day if dt.day != 0 else 1
            return f"{dt.year:04d}-{dt.month:02d}-{day:02d}"
    if re.match(r"^\d{4}-\d{2}-\d{2}$", folder_date): return folder_date
    t = date.today(); return t.strftime("%Y-%m-%d")

# ---- YAML (minimal writer) ----

def to_yaml(obj, indent=0):
    sp = "  " * indent
    if obj is None: return "null"
    if isinstance(obj, bool): return "true" if obj else "false"
    if isinstance(obj, (int, float)): return str(obj)
    if isinstance(obj, str):
        # keep simple; only quote when necessary
        specials = [":","{","}","[","]","#",",","&","*","!","|",">","'",'"',"%","@","`"]
        if obj == "" or obj.strip() != obj or any(c in obj for c in specials):
            s = obj.replace("\\","\\\\").replace('"','\\"'); return f"\"{s}\""
        return obj
    if isinstance(obj, list):
        if not obj: return "[]"
        lines=[]
        for it in obj:
            val = to_yaml(it, indent+1)
            if "\n" in val:
                lines.append(f"{sp}- |\n" + "\n".join(("  "*(indent+1)+l) for l in val.splitlines()))
            else:
                lines.append(f"{sp}- {val}")
        return "\n".join(lines)
    if isinstance(obj, dict):
        if not obj: return "{}"
        lines=[]
        for k,v in obj.items():
            key = str(k); val = to_yaml(v, indent+1)
            if isinstance(v, (dict, list)):
                lines.append(f"{sp}{key}:\n{val}")
            else:
                lines.append(f"{sp}{key}: {val}")
        return "\n".join(lines)
    return to_yaml(str(obj), indent)

# ---------------- provenance discovery (versions) ----------------

def newest_provenance_for_stem(site_repo: Path, stem: str) -> Optional[Path]:
    prints = site_repo / "prints"
    if not prints.exists(): return None
    cands = list(prints.glob(f"*/*/{stem}/provenance.yaml"))
    if not cands:
        return None
    def date_key(p: Path):
        try:
            d = p.parent.parent.name  # YYYY-MM-DD
            return d if re.match(r"^\d{4}-\d{2}-\d{2}$", d) else "0000-00-00"
        except Exception:
            return "0000-00-00"
    cands.sort(key=date_key, reverse=True)
    return cands[0]

def load_yaml_quick(path: Path) -> Dict:
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        out={}
        try:
            for ln in path.read_text(encoding="utf-8").splitlines():
                if ":" in ln and not ln.strip().startswith("#"):
                    k,v = ln.split(":",1)
                    out[k.strip()] = v.strip().strip('"')
        except Exception:
            return {}
        return out

# ---------------- cleanup helper ----------------

def prompt_and_cleanup(site_repo: Path, branch_name: str, site_head_before: str,
                       dst_dir: Path, api: Optional[str], token: Optional[str],
                       dep_id: Optional[int], main_branch: str):
    choice = input("Clean up: delete Zenodo draft (if any), remove local folder, drop branch? [y/N]: ").strip().lower()
    if choice not in ("y","yes"):
        return
    # delete draft
    if api and token and dep_id:
        try:
            http_json("DELETE", f"{api}/deposit/depositions/{dep_id}", token)
        except SystemExit:
            pass
    # reset and remove folder/branch
    try:
        echo(f"+ git reset --hard {site_head_before}")
        run(["git", "reset", "--hard", site_head_before], cwd=site_repo)
    except Exception:
        pass
    try:
        echo(f"+ remove print folder {dst_dir}")
        shutil.rmtree(dst_dir, ignore_errors=True)
    except Exception:
        pass
    try:
        echo(f"+ git checkout {main_branch}")
        run(["git", "checkout", main_branch], cwd=site_repo)
    except Exception:
        pass
    try:
        echo(f"+ git branch -D {branch_name}")
        run(["git", "branch", "-D", branch_name], cwd=site_repo, check=False)
    except Exception:
        pass

# ---------------- main ----------------

def main():
    ap = argparse.ArgumentParser(
        description="Publish a Preferred Frame print (versions; reserved DOI first; PNPMD-driven)."
    )
    ap.add_argument("md_path", help="Path to the source .md (must be inside a git repo).")
    ap.add_argument("--date", help="YYYY-MM-DD folder under prints/. Defaults to today.")
    ap.add_argument("--license", default="CC-BY-4.0", help="License (e.g., CC-BY-4.0).")
    ap.add_argument("--community", default="preferredframe", help="Zenodo community slug.")
    ap.add_argument("--journal", default="Preferred Frame", help="Journal title for Zenodo metadata.")
    ap.add_argument("--sandbox", action="store_true", help="Use Zenodo sandbox.")
    # assets defaults and control
    ap.add_argument("--assets-dir", default="../assets",
                    help="Path to local assets repo (default: ../assets).")
    ap.add_argument("--assets-base-url", default="https://assets.preferredframe.com",
                    help="Public base URL for assets (default: https://assets.preferredframe.com)")
    ap.add_argument("--no-assets-push", action="store_true",
                    help="Do not push the assets repo (default: push).")
    # main branch name
    ap.add_argument("--main", default="main", help="Main branch name to merge into (default: main).")
    args = ap.parse_args()

    # state for cleanup
    dep_id_for_cleanup = None
    created_branch = None
    created_dst_dir = None

    try:
        script_dir = Path(__file__).resolve().parent
        src_md = Path(args.md_path).resolve()
        if not src_md.exists() or src_md.suffix.lower() != ".md":
            die("Path must exist and point to a .md file.")

        # Repos clean
        try: src_repo = git_repo_root(src_md.parent)
        except SystemExit: die("Source file is not inside a git repository.")
        if not git_status_clean(src_repo): die(f"Source repo has uncommitted changes: {src_repo}")
        src_commit = git_head(src_repo); src_origin = git_origin_url(src_repo)

        try: site_repo = git_repo_root(Path.cwd())
        except SystemExit: die("Current working directory is not inside a git repository (site repo).")
        if not git_status_clean(site_repo): die(f"Site repo has uncommitted changes: {site_repo}")
        site_head_before = git_head(site_repo)
        site_origin = git_origin_url(site_repo)

        # Destination
        date_str = args.date or date.today().isoformat()
        stem = src_md.stem  # keep as-is (human-first; spaces allowed)

        # Create work branch
        src8 = src_commit[:8]
        branch_name = f"publish/{date_str}-{slug_branch(stem)}-{src8}"
        created_branch = branch_name
        echo(f"+ git checkout -b {branch_name}")
        run(["git", "checkout", "-b", branch_name], cwd=site_repo)

        dst_dir = site_repo / "prints" / date_str / stem
        created_dst_dir = dst_dir
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst_md = dst_dir / src_md.name

        echo(f"+ copy {src_md} -> {dst_md}")
        shutil.copy2(src_md, dst_md)

        # Render
        render_py = (script_dir / "render.py") if (script_dir / "render.py").exists() else Path(shutil.which("render.py") or "")
        if not render_py or not render_py.exists(): die("render.py not found beside this script or in PATH.")
        run([sys.executable, str(render_py), "--all", str(dst_md)], cwd=dst_dir, check=True)

        dst_pdf = dst_md.with_suffix(".pdf")
        dst_html = dst_md.with_suffix(".html")
        dst_pandoc_md = dst_md.with_suffix(".pandoc.md")
        if not dst_pdf.exists(): die(f"Expected PDF missing after render: {dst_pdf}")
        if not dst_html.exists(): die(f"Expected HTML missing after render: {dst_html}")
        if not dst_pandoc_md.exists(): die(f"Expected pandoc-preprocessed MD missing: {dst_pandoc_md}")

        # Parse PNPMD
        md_text = dst_md.read_text(encoding="utf-8")
        parsed = parse_pnpmd(md_text)
        title = parsed["title"] or stem
        creators = [{"name": a["name"], **({"orcid": a["orcid"]} if a.get("orcid") else {})} for a in parsed["authors"]]
        abstract = parsed["abstract"]; keywords = parsed["keywords"]
        ref_dois = parsed["reference_doi_urls"]
        pnpmd_date_raw = parsed["date"].strip() if parsed["date"] else ""
        publication_date = normalize_pub_date(pnpmd_date_raw, date_str)

        # PreferredFrame site URLs (HTML & MD)
        site_html_url = f"https://preferredframe.com/prints/{date_str}/{stem}/{dst_md.stem}.html"
        site_md_url   = f"https://preferredframe.com/prints/{date_str}/{stem}/{dst_md.name}"

        # Assets PDF URL (we compute URL now; copy/push happens AFTER confirmation)
        assets_pdf_url = f"{args.assets_base_url}/preferredframe/{date_str}/{dst_pdf.name}"

        # Version detection
        prior_prov = newest_provenance_for_stem(site_repo, stem)
        api, token = zenodo_api_and_token(args.sandbox)

        # Create or newversion deposition (reserve DOI later via PUT)
        if prior_prov and prior_prov.exists():
            prov_data = load_yaml_quick(prior_prov)
            prior_dep_id = None
            try:
                prior_dep_id = (prov_data.get("zenodo") or {}).get("deposition_id") or prov_data.get("zenodo_deposition_id")
            except Exception:
                prior_dep_id = None
            if not prior_dep_id:
                die(f"Found previous provenance but no zenodo.deposition_id in {prior_prov}")

            _ = http_json("POST", f"{api}/deposit/depositions/{prior_dep_id}/actions/newversion", token, data={})
            latest = http_json("GET", f"{api}/deposit/depositions/{prior_dep_id}", token, data={})
            latest_draft_url = (latest.get("links") or {}).get("latest_draft")
            if not latest_draft_url:
                die("Could not locate latest draft link after newversion.")
            draft = http_json("GET", latest_draft_url, token, data={})
            dep_id = draft.get("id")
            if not dep_id:
                die("New draft deposition has no id.")
        else:
            dep = http_json("POST", f"{api}/deposit/depositions", token, data={})
            dep_id = dep.get("id")
            if not dep_id: die("Could not create deposition (no id).")

        dep_id_for_cleanup = dep_id

        # Related identifiers (site + assets PDF + references)
        related_identifiers = [
            {"relation": "isIdenticalTo", "identifier": site_html_url, "resource_type": "publication"},
            {"relation": "isIdenticalTo", "identifier": site_md_url,   "resource_type": "publication"},
            {"relation": "isIdenticalTo", "identifier": assets_pdf_url, "resource_type": "publication"},
        ]
        for d in ref_dois:
            related_identifiers.append({"relation": "references", "identifier": d, "resource_type": "publication"})

        # Put metadata with prereserve
        zenodo_meta = {
            "upload_type": "publication",
            "publication_type": "article",
            "title": title,
            "creators": creators or [{"name": "Unknown"}],
            "description": abstract or "No description provided.",
            "keywords": keywords or [],
            "journal_title": args.journal,
            "publication_date": publication_date,
            "license": args.license,
            "related_identifiers": related_identifiers,
            "communities": [{"identifier": args.community}],
            "prereserve_doi": True
        }
        dep = http_json("PUT", f"{api}/deposit/depositions/{dep_id}", token, data={"metadata": zenodo_meta})
        pr = (dep.get("metadata") or {}).get("prereserve_doi") or {}
        reserved_doi = pr.get("doi")
        concept_doi = pr.get("conceptdoi")

        # Build permalink from reserved DOI (reserved = final on publish)
        doi_sfx = (reserved_doi or "").split("/")[-1]
        permalink = f"https://preferredframe.com/q/{slug_title_for_permalink(title)}--{doi_sfx}"

        # Provenance (YAML) prior to publication commit (single commit flow)
        provenance = {
            "published_by_commit": True,
            "journal": args.journal,
            "site_repo_origin": site_origin,
            "site_repo_head": site_head_before,
            "source": {
                "md_path": str(src_md),      # human-first; keep as-is
                "repo_origin": src_origin,
                "commit": src_commit
            },
            "copied_to": str(dst_md),
            "date_folder": date_str,
            "artifacts": {
                "main": dst_md.name,
                "additional": {"pdf": dst_pdf.name, "html": dst_html.name, "pandoc_md": dst_pandoc_md.name}
            },
            "parsed_from_pnpmd": {
                "title": title,
                "authors": creators,
                "date_raw": parsed["date"] or "",
                "date_normalized": publication_date,
                "one_sentence_summary": parsed["one_sentence"],
                "abstract": abstract,
                "keywords": keywords
            },
            "scanned": {
                "authors_orcid": parsed["scanned_orcids"],
                "references_doi": ref_dois
            },
            "site": {
                "html_canonical": site_html_url,
                "permalink": permalink
            },
            "zenodo": {
                "deposition_id": dep_id,
                "reserved_doi": reserved_doi,
                "concept_doi": concept_doi
            },
            "mirrors": {
                "assets_pdf": assets_pdf_url
            }
        }
        prov_path = dst_dir / "provenance.yaml"

        # Preview
        echo("\n--- PROVENANCE (YAML to be written) ---")
        echo(to_yaml(provenance))
        echo("\n--- RESERVED DOI ---")
        echo(reserved_doi or "(unavailable)")
        echo("\n--- FILES TO COMMIT (publication, site repo) ---")
        for p in [dst_md, dst_html, dst_pandoc_md, prov_path]:
            echo(f" - {p.relative_to(site_repo)}")
        echo("\n--- FILES TO COMMIT (assets repo) ---")
        echo(f" - preferredframe/{date_str}/{dst_pdf.name}  (PDF)")
        echo("\n--- FILES TO UPLOAD TO ZENODO ---")
        for p in [dst_pdf, dst_md, dst_pandoc_md, dst_html]:
            echo(f" - {p.name}")

        ans = input("\nProceed with publication commit and DOI minting? [y/N]: ").strip().lower()
        if ans not in ("y","yes"):
            prompt_and_cleanup(site_repo, branch_name, site_head_before, dst_dir,
                               api, token, dep_id_for_cleanup, args.main)
            die("Aborted by user.", 0)

        # Commit = publication (PDF excluded from site repo commit)
        echo(f"+ write {prov_path}")
        prov_path.write_text(to_yaml(provenance) + "\n", encoding="utf-8")
        run(["git", "add", str(dst_md)], cwd=site_repo)
        run(["git", "add", str(dst_html)], cwd=site_repo)
        run(["git", "add", str(dst_pandoc_md)], cwd=site_repo)
        run(["git", "add", str(prov_path)], cwd=site_repo)
        run(["git", "commit", "-m",
             f"Publish print: {title} ({publication_date}); source {src_commit[:10]} as '{stem}'"], cwd=site_repo)

        # Copy PDF to assets repo & push (after confirmation, as requested)
        if args.assets_dir:
            assets_repo = Path(args.assets_dir).resolve()
            if not (assets_repo / ".git").exists():
                die(f"Assets dir is not a git repo: {assets_repo}")
            dest = assets_repo / "preferredframe" / date_str / dst_pdf.name  # NOTE: no <stem> in path
            dest.parent.mkdir(parents=True, exist_ok=True)
            echo(f"+ copy {dst_pdf} -> {dest}")
            shutil.copy2(dst_pdf, dest)
            if not args.no_assets_push:
                run(["git", "add", "-A"], cwd=assets_repo)
                run(["git", "commit", "-m", f"Add PDF for {title} ({publication_date})"], cwd=assets_repo)
                run(["git", "push"], cwd=assets_repo)
            # also mirror into local site/ to mimic production
            site_assets_pdf = site_repo / "site" / "assets" / "preferredframe" / date_str / dst_pdf.name
            site_assets_pdf.parent.mkdir(parents=True, exist_ok=True)
            echo(f"+ copy {dst_pdf} -> {site_assets_pdf}")
            shutil.copy2(dst_pdf, site_assets_pdf)

        # Upload files & publish (reserved DOI becomes final)
        for path in [dst_pdf, dst_md, dst_pandoc_md, dst_html]:
            with open(path, "rb") as fh:
                http_json("POST", f"{api}/deposit/depositions/{dep_id}/files", token,
                          files={"file": (path.name, fh)})

        _published = http_json("POST", f"{api}/deposit/depositions/{dep_id}/actions/publish", token)
        # We intentionally trust reserved DOI == final DOI; only warn if different:
        final_doi = reserved_doi
        if (_published.get("doi") or (_published.get("metadata") or {}).get("doi")) and \
           (_published.get("doi") or (_published.get("metadata") or {}).get("doi")) != reserved_doi:
            echo("WARNING: final DOI differs from reserved DOI.")

        # Prompt to push the branch
        do_push = input("Push branch to origin now? [y/N]: ").strip().lower() in ("y","yes")
        if do_push:
            run(["git", "push", "--set-upstream", "origin", branch_name], cwd=site_repo)

        # Prompt to merge into main
        do_merge = input(f"Merge '{branch_name}' into '{args.main}' and push? [y/N]: ").strip().lower() in ("y","yes")
        if do_merge:
            echo(f"+ git checkout {args.main}")
            run(["git", "checkout", args.main], cwd=site_repo)
            echo(f"+ git merge --no-ff {branch_name}")
            run(["git", "merge", "--no-ff", branch_name], cwd=site_repo)
            if do_push:
                run(["git", "push"], cwd=site_repo)
            echo(f"+ git branch -d {branch_name}")
            run(["git", "branch", "-d", branch_name], cwd=site_repo)

        echo(f"\n✅ Publication committed and DOI minted"
             f"\nConcept DOI: {concept_doi}"
             f"\nVersion DOI: {final_doi}"
             f"\nPermalink: {permalink}"
             f"\nFolder: {dst_dir}")

    except SystemExit as e:
        # honor explicit exits without extra prompts
        raise
    except Exception as e:
        echo(f"ERROR: {e}")
        # Offer cleanup on unexpected error
        try:
            # We need context objects; recover a few from locals if present
            site_repo = locals().get("site_repo")
            branch_name = locals().get("branch_name") or ""
            site_head_before = locals().get("site_head_before") or ""
            dst_dir = locals().get("dst_dir")
            api = locals().get("api")
            token = locals().get("token")
            dep_id_for_cleanup = locals().get("dep_id_for_cleanup")
            main_branch = locals().get("args").main if locals().get("args") else "main"
            if site_repo and dst_dir and branch_name and site_head_before:
                prompt_and_cleanup(site_repo, branch_name, site_head_before, dst_dir,
                                   api, token, dep_id_for_cleanup, main_branch)
        finally:
            sys.exit(1)
    finally:
        # If user aborted earlier without cleanup, offer it here as a last resort.
        # (No-op if we already cleaned or merged.)
        pass

if __name__ == "__main__":
    main()
