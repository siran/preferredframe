#!/usr/bin/env python3
"""
Write immutable per-version sidecar: <workdir>/versions/<doi_safe>.yml
Also refresh mutable <workdir>/source.yml (latest pointer).

Sidecar fields:
- version_doi, concept_doi, title, issued_date (UTC ISO-8601)
- repo: { url, github_commit, github_md_raw }
- files: { md, pnpmd, html, pdf }  (served from BASE_URL + repo-relative path)
- one_sentence_summary, abstract, keywords
- zenodo_record (human HTML record URL for this version)
"""
from __future__ import annotations
from pathlib import Path
import os, sys, yaml, subprocess, re
from datetime import datetime, timezone

def die(m): print(m, file=sys.stderr); sys.exit(1)
def iso_utc_now() -> str: return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---------- PNPMD parsing ----------
HDR_ABS  = re.compile(r"(?mi)^##\s*Abstract\s*$")
HDR_SUM  = re.compile(r"(?mi)^##\s*One-Sentence\s+Summary\s*$")
HDR_KEYS = re.compile(r"(?mi)^##\s*Keywords\s*$")
HDR_NEXT = re.compile(r"(?m)^##\s+")

def _section_text(txt: str, hdr: re.Pattern) -> str:
    m = hdr.search(txt)
    if not m: return ""
    start = m.end()
    nxt = HDR_NEXT.search(txt, pos=start)
    block = txt[start:nxt.start()] if nxt else txt[start:]
    lines = [ln.rstrip() for ln in block.splitlines()]
    while lines and not lines[0].strip(): lines.pop(0)
    while lines and not lines[-1].strip(): lines.pop()
    return "\n".join(lines)

def parse_one_sentence_summary(txt: str) -> str:
    block = _section_text(txt, HDR_SUM)
    for ln in block.splitlines():
        s = ln.strip()
        if s: return s
    return ""

def parse_abstract(txt: str) -> str:
    return _section_text(txt, HDR_ABS)

def parse_keywords(txt: str) -> list[str]:
    block = _section_text(txt, HDR_KEYS)
    if not block: return []
    out: list[str] = []
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    if len(lines) == 1 and "," in lines[0]:
        out = [w.strip() for w in lines[0].split(",") if w.strip()]
    else:
        for ln in lines:
            ln = re.sub(r"^[-*]\s+", "", ln)
            if ln: out.append(ln)
    return out

def parse_header_lines(txt: str):
    """
    PNPMD header: first three non-empty lines start with '% ':
      % Title
      % Authors
      % Date
    Returns (title, authors_raw, date_raw) or ("", "", "") if not present.
    """
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    if len(lines) >= 3 and all(ln.startswith("%") for ln in lines[:3]):
        title = lines[0][1:].strip()
        authors_raw = lines[1][1:].strip()
        date_raw = lines[2][1:].strip()
        return title, authors_raw, date_raw
    return "", "", ""

# ---------- URL helpers ----------
def github_raw_url(repo: str, ref: str, rel_repo_path: Path) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{rel_repo_path.as_posix()}"

def main():
    if len(sys.argv) < 4:
        die("usage: write_version_sidecar.py <md_path> <version_doi> <concept_doi> [zenodo_record_url]")

    md_path        = Path(sys.argv[1]).resolve()
    version_doi    = sys.argv[2]
    concept_doi    = sys.argv[3]
    zenodo_record  = sys.argv[4] if len(sys.argv) > 4 else ""

    # Repo + commit
    repo = os.getenv("GITHUB_REPOSITORY", "")  # e.g., "siran/preferredframe"
    if not repo:
        die("GITHUB_REPOSITORY env not set")
    repo_url = f"https://github.com/{repo}"
    ref = subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip()
    github_commit_url = f"{repo_url}/commit/{ref}"

    # Path relative to repo root for URLs
    try:
        rel_repo_path = md_path.relative_to(Path.cwd())
    except ValueError:
        rel_repo_path = md_path

    # Public site base
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")

    # Site file URLs — mirror repo layout under BASE_URL
    rel_str = rel_repo_path.as_posix()
    md_url    = f"{base_url}/{rel_str}"
    if rel_str.endswith(".md"):
        pnpmd_url = f"{base_url}/{rel_str[:-3]}pnpmd.md"
        html_url  = f"{base_url}/{rel_str[:-3]}html"
        pdf_url   = f"{base_url}/{rel_str[:-3]}pdf"
    else:
        pnpmd_url = f"{base_url}/{rel_str}.pnpmd.md"
        html_url  = f"{base_url}/{rel_str}.html"
        pdf_url   = f"{base_url}/{rel_str}.pdf"

    # GitHub raw bytes for the MD at this exact commit
    github_md_raw = github_raw_url(repo, ref, rel_repo_path)

    # Extract PNPMD meta from the MD file
    try:
        txt = md_path.read_text(encoding="utf-8")
    except Exception as e:
        die(f"cannot read {md_path}: {e}")

    hdr_title, hdr_authors_raw, _hdr_date = parse_header_lines(txt)
    title = hdr_title or md_path.stem
    # authors as list (split on ',', ';', or ' and ')
    if hdr_authors_raw:
        authors = [a for a in re.split(r'\s*(?:,|;| and )\s*', hdr_authors_raw) if a]
    else:
        authors = []

    one_sentence_summary = parse_one_sentence_summary(txt)
    abstract = parse_abstract(txt)
    keywords = parse_keywords(txt)

    issued_date = os.getenv("ISSUED_DATE") or iso_utc_now()
    title = md_path.stem

    # Immutable per-version sidecar
    doi_safe = version_doi.replace("/", "_")
    versions_dir = md_path.parent / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)

    side = {
        "version_doi": version_doi,
        "concept_doi": concept_doi,
        "title": title,
         "filename": md_path.name,
        "issued_date": issued_date,
        "repo": {
            "url": repo_url,
            "github_commit": github_commit_url,
            "github_md_raw": github_md_raw,
        },
        "files": {
            "md": md_url,
            "pnpmd": pnpmd_url,
            "html": html_url,
            "pdf": pdf_url,
        },
        "authors": authors,
        "one_sentence_summary": one_sentence_summary,
        "abstract": abstract,
        "keywords": keywords,
        "zenodo_record": zenodo_record,
    }

    out_yml = versions_dir / f"{doi_safe}.yml"
    out_yml.write_text(yaml.safe_dump(side, sort_keys=False), encoding="utf-8")

    # Mutable latest pointer (minimal)
    latest = {
        "concept_doi": concept_doi,
        "latest_version_doi": version_doi,
        "repo": repo_url,
        "path": str(rel_repo_path),
        "imported_at": iso_utc_now(),
        "title": title,
        "github_commit": github_commit_url,
    }
    (md_path.parent / "source.yml").write_text(yaml.safe_dump(latest, sort_keys=False), encoding="utf-8")

    print(str(out_yml))

if __name__ == "__main__":
    main()
