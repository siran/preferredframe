#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preferred Frame publisher (PNPMD-driven; commit = publication; reserved DOI ≠ guaranteed final DOI)

Flow:
  1) Preflight: source & site repos clean; create work branch (slugged)
  2) Copy src.md -> prints/YYYY-MM/<stem>/<src.md>
  3) render.py --all (must produce .pdf, .html, .pandoc.md)
  4) Parse PNPMD; scan ORCIDs & DOIs; normalize publication_date (ISO)
  5) Detect prior provenance (versions) → create new Zenodo draft or new version
  6) Reserve DOI + set metadata (uses assets URL, HTML, MD as related identifiers)
  7) Upload artifacts to Zenodo; PUBLISH → obtain FINAL DOI
  8) Push PDF to assets repo (no PDF mirrored into site/)
  9) Show FULL provenance preview (final DOI, concept DOI, permalink) → single confirmation
 10) Write provenance.yaml (uses FINAL DOI); commit (site repo)
 11) Merge locally into main and push ONLY main; delete work branch
"""

import os, re, sys, shutil, subprocess
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
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = (p.stdout or "")
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    if check and p.returncode != 0:
        die(f"command failed with exit code {p.returncode}", p.returncode)
    return out

# ---------------- git helpers ----------------

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

def zenodo_api_and_token() -> Tuple[str, str]:
    api = os.environ.get("ZENODO_API")
    token = os.environ.get("ZENODO_TOKEN") or os.environ.get("ZENODO_SANDBOX_TOKEN")
    if not token:
        die("Missing token. Set ZENODO_TOKEN or ZENODO_SANDBOX_TOKEN.")
    if not api:
        api = "https://zenodo.org/api" if os.environ.get("ZENODO_TOKEN") else "https://sandbox.zenodo.org/api"
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

    one_sentence = section_text(md_text, "One-Sentence Summary")
    abstract = section_text(md_text, "Abstract")
    kb = section_text(md_text, "Keywords")
    keywords = []
    if kb:
        first_line = next((ln.strip() for ln in kb.splitlines() if ln.strip()), "")
        if first_line:
            keywords = [k.strip() for k in first_line.split(",") if k.strip()]

    about = section_text(md_text, "About Author(s)")
    parsed_authors = []
    for ln in about.splitlines():
        m = re.match(r'^\s*[\*\-]\s+(.*)$', ln)
        if not m: continue
        body = m.group(1).strip()
        parts = [p.strip() for p in body.split(",")]
        name = parts[0] if parts else ""
        orcid = None; email = None
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
        "one_sentence": one_sentence.strip(),
        "abstract": abstract.strip(),
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

# ---- YAML (compact, minimal quoting) ----

def yaml_str(v: str) -> str:
    if v is None: return "null"
    if not isinstance(v, str): return str(v)
    if v.strip() != v or "\n" in v:
        s = v.replace("\\","\\\\").replace('"','\\"')
        return f"\"{s}\""
    return v

def to_yaml(obj, indent=0):
    sp = "  " * indent
    if obj is None: return "null"
    if isinstance(obj, bool): return "true" if obj else "false"
    if isinstance(obj, (int, float)): return str(obj)
    if isinstance(obj, str): return yaml_str(obj)
    if isinstance(obj, list):
        if not obj: return "[]"
        lines=[]
        for it in obj:
            if isinstance(it, dict):
                first = True
                for k, v in it.items():
                    if first:
                        if isinstance(v, (dict, list)):
                            lines.append(f"{sp}- {k}:")
                            lines.append(to_yaml(v, indent+2))
                        else:
                            lines.append(f"{sp}- {k}: {to_yaml(v, indent+1)}")
                        first = False
                    else:
                        if isinstance(v, (dict, list)):
                            lines.append(f"{sp}  {k}:")
                            lines.append(to_yaml(v, indent+2))
                        else:
                            lines.append(f"{sp}  {k}: {to_yaml(v, indent+1)}")
                continue
            lines.append(f"{sp}- {to_yaml(it, indent+1)}")
        return "\n".join(lines)
    if isinstance(obj, dict):
        if not obj: return "{}"
        lines=[]
        for k,v in obj.items():
            key = str(k)
            if isinstance(v, (dict, list)):
                lines.append(f"{sp}{key}:")
                lines.append(to_yaml(v, indent+1))
            else:
                lines.append(f"{sp}{key}: {to_yaml(v, indent+1)}")
        return "\n".join(lines)
    return yaml_str(str(obj))

# ---------------- provenance discovery (versions) ----------------

def newest_provenance_for_stem(site_repo: Path, stem: str) -> Optional[Path]:
    prints = site_repo / "prints"
    if not prints.exists(): return None
    cands = list(prints.glob(f"*/*/{stem}/provenance.yaml"))
    if not cands: return None
    def date_key(p: Path):
        try:
            d = p.parent.parent.name
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

# ---------------- steps ----------------

def prepare_paths_and_branch(src_md: Path, site_repo: Path, src_commit: str) -> Tuple[Path, Path, Path, str, str]:
    date_str = date.today().strftime("%Y-%m")
    stem = src_md.stem  # keep spaces; human-first
    branch_name = f"publish/{date_str}-{slug_branch(stem)}-{src_commit[:8]}"
    echo(f"+ git checkout -b {branch_name}")
    run(["git", "checkout", "-b", branch_name], cwd=site_repo)
    dst_dir = site_repo / "prints" / date_str / stem
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst_md = dst_dir / src_md.name
    echo(f"+ copy {src_md} -> {dst_md}")
    shutil.copy2(src_md, dst_md)
    return dst_dir, dst_md, Path(dst_md.with_suffix(".pdf")), date_str, branch_name

def render_all(dst_md: Path):
    script_dir = Path(__file__).resolve().parent
    render_py = (script_dir / "render.py") if (script_dir / "render.py").exists() else Path(shutil.which("render.py") or "")
    if not render_py or not render_py.exists(): die("render.py not found beside this script or in PATH.")
    run([sys.executable, str(render_py), "--all", str(dst_md)], cwd=dst_md.parent, check=True)
    dst_pdf = dst_md.with_suffix(".pdf")
    dst_html = dst_md.with_suffix(".html")
    dst_pandoc_md = dst_md.with_suffix(".pandoc.md")
    if not dst_pdf.exists(): die(f"Expected PDF missing after render: {dst_pdf}")
    if not dst_html.exists(): die(f"Expected HTML missing after render: {dst_html}")
    if not dst_pandoc_md.exists(): die(f"Expected pandoc-preprocessed MD missing: {dst_pandoc_md}")
    return dst_pdf, dst_html, dst_pandoc_md

def reserve_deposition_and_metadata(api: str, token: str, prior_prov: Optional[Path],
                                    title: str, creators: List[Dict], abstract: str,
                                    one_sentence: str, keywords: List[str],
                                    publication_date: str, site_html_url: str,
                                    site_md_url: str, assets_pdf_url: str,
                                    community: str, journal: str) -> Tuple[int, str, str]:
    if prior_prov and prior_prov.exists():
        prov_data = load_yaml_quick(prior_prov)
        prior_dep_id = (prov_data.get("zenodo") or {}).get("deposition_id") or prov_data.get("zenodo_deposition_id")
        if not prior_dep_id: die(f"Found previous provenance but no zenodo.deposition_id in {prior_prov}")
        _ = http_json("POST", f"{api}/deposit/depositions/{prior_dep_id}/actions/newversion", token, data={})
        latest = http_json("GET", f"{api}/deposit/depositions/{prior_dep_id}", token, data={})
        latest_draft_url = (latest.get("links") or {}).get("latest_draft")
        if not latest_draft_url: die("Could not locate latest draft link after newversion.")
        draft = http_json("GET", latest_draft_url, token, data={})
        dep_id = draft.get("id")
        if not dep_id: die("New draft deposition has no id.")
    else:
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
        "creators": creators or [{"name": "Unknown"}],
        "description": abstract or "No description provided.",
        "notes": one_sentence or "",
        "keywords": keywords or [],
        "journal_title": journal,
        "publication_date": publication_date,
        "license": "CC-BY-4.0",
        "related_identifiers": related_identifiers,
        "communities": [{"identifier": community}],
        "prereserve_doi": True
    }
    dep = http_json("PUT", f"{api}/deposit/depositions/{dep_id}", token, data={"metadata": zenodo_meta})
    pr = (dep.get("metadata") or {}).get("prereserve_doi") or {}
    reserved_doi = pr.get("doi")
    concept_doi = pr.get("conceptdoi")
    return dep_id, reserved_doi, concept_doi

def write_provenance(dst_dir: Path, dst_md: Path, dst_pdf: Path, dst_html: Path, dst_pandoc_md: Path,
                     site_origin: str, site_head_before: str,
                     src_origin: str, src_commit: str,
                     title: str, creators: List[Dict], parsed: Dict,
                     publication_date: str, date_str: str,
                     final_doi: str, reserved_doi: str, concept_doi: str,
                     assets_pdf_url: str, site_html_url: str, permalink: str) -> Path:
    provenance = {
        "published_by_commit": True,
        "journal": "Preferred Frame",
        "site_repo_origin": site_origin,
        "site_repo_head": site_head_before,
        "source": {"repo_origin": src_origin, "commit": src_commit},
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
            "date_raw": parsed["date"] or "",
            "date_normalized": publication_date,
            "one_sentence_summary": parsed["one_sentence"],
            "abstract": parsed["abstract"],
            "keywords": parsed["keywords"]
        },
        "scanned": {
            "authors_orcid": parsed["scanned_orcids"],
            "references_doi": parsed["reference_doi_urls"]
        },
        "zenodo": {
            "doi": final_doi or "",
            "reserved_doi": reserved_doi or "",
            "concept_doi": concept_doi or "",
            "deposition_id": (final_doi or reserved_doi or "").split("/")[-1]
        },
        "assets": {"pdf": assets_pdf_url},
        "site": {"html_canonical": site_html_url, "permalink": permalink}
    }
    prov_path = dst_dir / "provenance.yaml"
    echo(f"+ write {prov_path}")
    prov_path.write_text(to_yaml(provenance) + "\n", encoding="utf-8")
    return prov_path

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Publish a Preferred Frame print (PNPMD).")
    ap.add_argument("md_path", help="Path to the source .md (must be inside a git repo).")
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
    if not git_status_clean(src_repo): die(f"Source repo has uncommitted changes: {src_repo}")
    src_commit = git_head(src_repo); src_origin = git_origin_url(src_repo)

    site_repo = git_repo_root(Path.cwd())
    if not git_status_clean(site_repo): die(f"Site repo has uncommitted changes: {site_repo}")
    site_head_before = git_head(site_repo); site_origin = git_origin_url(site_repo)

    # ---- branch, copy, render ----
    dst_dir, dst_md, dst_pdf_path, date_str, branch_name = prepare_paths_and_branch(src_md, site_repo, src_commit)
    dst_pdf, dst_html, dst_pandoc_md = render_all(dst_md)

    # ---- parse PNPMD & dates ----
    parsed = parse_pnpmd(dst_md.read_text(encoding="utf-8"))
    title = parsed["title"] or dst_md.stem
    creators = [{"name": a["name"], **({"orcid": a["orcid"]} if a.get("orcid") else {})} for a in parsed["authors"]]
    publication_date = normalize_pub_date(parsed["date"] or "", date_str)

    # ---- site URLs (keep spaces; browsers handle them) ----
    site_html_url = f"https://preferredframe.com/prints/{date_str}/{dst_md.stem}/{dst_md.stem}.html"
    site_md_url   = f"https://preferredframe.com/prints/{date_str}/{dst_md.stem}/{dst_md.name}"
    assets_pdf_url = f"{args.assets_base_url}/preferredframe/{date_str}/{dst_pdf.name}"

    # ---- Zenodo API ----
    api, token = zenodo_api_and_token()

    # ---- version detection ----
    prior_prov = newest_provenance_for_stem(site_repo, dst_md.stem)

    # ---- reserve DOI + metadata ----
    dep_id, reserved_doi, concept_doi = reserve_deposition_and_metadata(
        api, token, prior_prov,
        title, creators, parsed["abstract"], parsed["one_sentence"], parsed["keywords"],
        publication_date, site_html_url, site_md_url, assets_pdf_url,
        args.community, args.journal
    )

    # ---- upload to Zenodo & publish (to obtain FINAL DOI) ----
    for path in [dst_pdf, dst_md, dst_pandoc_md, dst_html]:
        with open(path, "rb") as fh:
            http_json("POST", f"{api}/deposit/depositions/{dep_id}/files", token,
                      files={"file": (path.name, fh)})

    published = http_json("POST", f"{api}/deposit/depositions/{dep_id}/actions/publish", token)
    final_doi_reported = (published.get("doi") or (published.get("metadata") or {}).get("doi"))
    final_doi = final_doi_reported or reserved_doi
    if reserved_doi and final_doi_reported and final_doi_reported != reserved_doi:
        echo("WARNING: final DOI differs from reserved DOI.")

    # ---- permalink (human-facing) from FINAL DOI ----
    doi_sfx = (final_doi or "").split("/")[-1]
    permalink = f"https://preferredframe.com/q/{slug_title_for_permalink(title)}--{doi_sfx}"

    # ---- copy PDF to assets & push (AFTER publish) ----
    if args.assets_dir:
        assets_repo = Path(args.assets_dir).resolve()
        if not (assets_repo / ".git").exists():
            die(f"Assets dir is not a git repo: {assets_repo}")
        dest = assets_repo / "preferredframe" / date_str / dst_pdf.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        echo(f"+ copy {dst_pdf} -> {dest}")
        shutil.copy2(dst_pdf, dest)
        if not args.no_assets_push:
            run(["git", "add", "-A"], cwd=assets_repo)
            # include date in message if we parsed a full ISO
            run(["git", "commit", "-m", f"Add PDF for {title} ({publication_date})"], cwd=assets_repo)
            run(["git", "push"], cwd=assets_repo)

    # ---- FULL provenance preview (FINAL DOI) ----
    prov_preview = {
        "title": title,
        "date": publication_date,
        "doi_final": final_doi,
        "doi_reserved": reserved_doi,
        "concept_doi": concept_doi,
        "permalink": permalink,
        "site_repo_origin": site_origin,
        "source_repo_origin": src_origin,
        "artifacts": [dst_md.name, dst_html.name, dst_pandoc_md.name, dst_pdf.name],
        "assets_pdf": assets_pdf_url,
        "site_html_canonical": site_html_url
    }
    echo("\n--- PREVIEW (FINAL) ---")
    echo(to_yaml(prov_preview))
    echo("\nThis will be written to provenance.yaml and committed. Proceed?")
    ans = input("Confirm publication commit & merge? [y/N]: ").strip().lower()
    if ans not in ("y","yes"):
        echo("Aborted before writing provenance / committing.")
        sys.exit(0)

    # ---- write provenance & commit (site) ----
    prov_path = write_provenance(dst_dir, dst_md, dst_pdf, dst_html, dst_pandoc_md,
                                 site_origin, site_head_before, src_origin, src_commit,
                                 title, creators, parsed, publication_date, date_str,
                                 final_doi, reserved_doi, concept_doi,
                                 assets_pdf_url, site_html_url, permalink)

    run(["git", "add", str(dst_md)], cwd=site_repo)
    run(["git", "add", str(dst_html)], cwd=site_repo)
    run(["git", "add", str(dst_pandoc_md)], cwd=site_repo)
    run(["git", "add", str(prov_path)], cwd=site_repo)
    run(["git", "commit", "-m",
         f"Publish print: {title} ({publication_date}); source {src_commit[:10]} as '{dst_md.stem}'"], cwd=site_repo)

    # ---- merge locally into main; push ONLY main (no feature branch push) ----
    run(["git", "checkout", "main"], cwd=site_repo)
    run(["git", "pull", "--rebase"], cwd=site_repo)
    run(["git", "merge", "--no-ff", branch_name], cwd=site_repo)
    run(["git", "push"], cwd=site_repo)
    run(["git", "branch", "-d", branch_name], cwd=site_repo)

    echo(f"\n✅ Publication committed and DOI minted"
         f"\nConcept DOI: {concept_doi}"
         f"\nVersion DOI: {final_doi}"
         f"\nPermalink: https://preferredframe.com/q/{slug_title_for_permalink(title)}--{(final_doi or '').split('/')[-1]}"
         f"\nFolder: {dst_dir}")

if __name__ == "__main__":
    main()
