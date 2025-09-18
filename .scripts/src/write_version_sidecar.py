#!/usr/bin/env python3
"""
Write immutable per-version sidecar: preferredframe/prints/<Work>/versions/<doi_safe>.yml
Also refresh mutable preferredframe/prints/<Work>/source.yml (latest pointer).

Sidecar points to:
- preferredframe site for .md and .pnp.md
- siran/assets (raw GitHub) for .html and .pdf
- Zenodo record (version page)
"""
from __future__ import annotations
from pathlib import Path
import os, sys, yaml, subprocess, re
from datetime import datetime, timezone

def die(m): print(m, file=sys.stderr); sys.exit(1)
def iso_utc_now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_header_lines(txt: str):
    nonempty = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    if len(nonempty) >= 3 and all(ln.startswith("%") for ln in nonempty[:3]):
        title   = nonempty[0][1:].strip()
        authors = [a for a in re.split(r'\s*(?:,|;| and )\s*', nonempty[1][1:].strip()) if a]
        date    = nonempty[2][1:].strip()
        return title, authors, date
    return "", [], ""

HDR_ABS   = re.compile(r"(?mi)^##\s*Abstract\s*$")
HDR_SUM   = re.compile(r"(?mi)^##\s*One-Sentence\s+Summary\s*$")
HDR_KEYS  = re.compile(r"(?mi)^##\s*Keywords\s*$")
HDR_NEXT  = re.compile(r"(?m)^##\s+")

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

def main():
    if len(sys.argv) < 4:
        die("usage: write_version_sidecar.py <md_path> <version_doi> <concept_doi> [zenodo_record_url]")

    md_path        = Path(sys.argv[1]).resolve()
    version_doi    = sys.argv[2]
    concept_doi    = sys.argv[3]
    zenodo_record  = sys.argv[4] if len(sys.argv) > 4 else ""

    repo = os.getenv("GITHUB_REPOSITORY", "")  # "siran/preferredframe"
    repo_url = f"https://github.com/{repo}" if repo else ""
    commit = subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip()

    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    assets_repo   = os.getenv("ASSETS_REPO", "siran/assets")
    assets_branch = os.getenv("ASSETS_BRANCH", "main")

    # repo-relative path (for preferredframe site URLs)
    try:
        rel_repo_path = md_path.relative_to(Path.cwd())
    except ValueError:
        rel_repo_path = md_path
    rel_no_ext = rel_repo_path.with_suffix("")  # strip .md

    # Preferred Frame site URLs (.md, .pnp.md)
    md_url    = f"{base_url}/{rel_no_ext.as_posix()}.md"
    pnp_url   = f"{base_url}/{rel_no_ext.as_posix()}.pnp.md"

    # Assets URLs (.html, .pdf) served from siran/assets raw
    # Path pattern: preferredframe/<Title>/<DOI_SAFE>/<Title>.{html,pdf}
    title_from_header, authors, header_date = "", [], ""
    txt = md_path.read_text(encoding="utf-8")
    title_from_header, authors, header_date = parse_header_lines(txt)
    title = title_from_header or md_path.stem
    doi_safe = version_doi.replace("/", "_")
    assets_base = f"https://raw.githubusercontent.com/{assets_repo}/{assets_branch}/preferredframe/{title}/{doi_safe}"
    html_url = f"{assets_base}/{title}.html"
    pdf_url  = f"{assets_base}/{title}.pdf"

    # Derived sections
    one_sentence_summary = parse_one_sentence_summary(txt)
    abstract = parse_abstract(txt)
    keywords = parse_keywords(txt)

    issued_date = os.getenv("ISSUED_DATE") or iso_utc_now()

    # Write immutable per-version sidecar
    versions_dir = md_path.parent / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)

    side = {
        "version_doi": version_doi,
        "concept_doi": concept_doi,
        "title": title,
        "filename": md_path.name,
        "authors": authors,
        "header_date": header_date,
        "issued_date": issued_date,
        "repo": {
            "url": repo_url,
            "github_commit": f"{repo_url}/commit/{commit}" if repo_url else "",
            "github_md_raw": f"https://raw.githubusercontent.com/{repo}/{commit}/{rel_repo_path.as_posix()}" if repo else "",
        },
        "files": {
            "md": md_url,
            "pnp_md": pnp_url,
            "html": html_url,
            "pdf": pdf_url,
        },
        "one_sentence_summary": one_sentence_summary or None,
        "abstract": abstract or None,
        "keywords": keywords or None,
        "zenodo_record": zenodo_record or None,
    }
    # drop None/empty
    side = {k:v for k,v in side.items() if v not in ("", None)}
    if "repo" in side:
        side["repo"] = {k:v for k,v in side["repo"].items() if v not in ("", None)}

    out_yml = versions_dir / f"{doi_safe}.yml"
    out_yml.write_text(yaml.safe_dump(side, sort_keys=False), encoding="utf-8")

    # Mutable latest pointer
    latest = {
        "concept_doi": concept_doi,
        "latest_version_doi": version_doi,
        "repo": repo_url or repo,
        "path": str(rel_repo_path),
        "imported_at": issued_date,
        "title": title,
        "github_commit": f"{repo_url}/commit/{commit}" if repo_url else commit,
    }
    (md_path.parent / "source.yml").write_text(yaml.safe_dump(latest, sort_keys=False), encoding="utf-8")

    print(str(out_yml))

if __name__ == "__main__":
    main()
