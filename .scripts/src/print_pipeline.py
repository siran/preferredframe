#!/usr/bin/env python3
"""
print_pipeline.py
- Enforce exactly one .md under preferredframe/prints/*/*.md
- Rebuild pnp.md/html/pdf; verify
- Write sidecar print.json
- Commit & push assets
- (Optional) Mint DOI (ZENODO_ACCESS_TOKEN)
- Emit artifact_path=<folder> to $GITHUB_OUTPUT
"""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRINTS = ROOT / "preferredframe" / "prints"

def sh(args, check=True):
    return subprocess.run(args, cwd=ROOT, check=check, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def run(args):
    r = sh(args)
    sys.stdout.write(r.stdout)
    return r

def find_single_md() -> Path:
    mds = list(PRINTS.glob("*/*.md"))
    if len(mds) == 0:
        print("[print][ERROR] No .md under preferredframe/prints/*/")
        sys.exit(1)
    if len(mds) > 1:
        print("[print][ERROR] Multiple .md files found. Only one allowed:")
        for m in mds:
            print(" -", m.relative_to(ROOT))
        sys.exit(1)
    return mds[0]

def read_title(md: Path) -> str:
    for ln in md.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s: continue
        if s.startswith("% "): return s[2:].strip()
        break
    return md.stem

def slugify(title: str) -> str:
    import re
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", title)
    safe = re.sub(r"-{2,}", "-", safe).strip("-")
    return safe or "untitled"

def build(md: Path):
    stem = md.with_suffix("")
    pnp  = stem.with_suffix(".pnp.md")
    html = stem.with_suffix(".html")
    pdf  = stem.with_suffix(".pdf")

    print(f"[print] Build {md.relative_to(ROOT)}")
    run([sys.executable, str(ROOT/".scripts/src/make_pnpmd.py"), str(md),  str(pnp)])
    run([sys.executable, str(ROOT/".scripts/src/make_html.py"),  str(pnp), str(html)])
    run([sys.executable, str(ROOT/".scripts/src/make_pdf.py"),   str(pnp), str(pdf)])

    for f in (md, pnp, html, pdf):
        if not f.exists() or f.stat().st_size == 0:
            print(f"[print][ERROR] Missing/empty: {f.relative_to(ROOT)}", file=sys.stderr)
            sys.exit(1)
    print(f"[print][OK] {pnp.name}, {html.name}, {pdf.name}")
    return pnp, html, pdf

def write_sidecar(md: Path, pnp: Path, html: Path, pdf: Path, doi: str | None) -> Path:
    title = read_title(md)
    data = {
        "title": title,
        "slug": slugify(title),
        "paths": {
            "md": str(md.relative_to(ROOT)),
            "pnpmd": str(pnp.relative_to(ROOT)),
            "html": str(html.relative_to(ROOT)),
            "pdf": str(pdf.relative_to(ROOT)),
        },
        "commit": sh(["git", "rev-parse", "HEAD"]).stdout.strip(),
        "branch": sh(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "doi": doi or "pending"
    }
    sidecar = md.with_name("print.json")
    sidecar.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"[print] Wrote sidecar: {sidecar.relative_to(ROOT)}")
    return sidecar

def maybe_mint_doi(target_dir: Path) -> str | None:
    token = os.environ.get("ZENODO_ACCESS_TOKEN")
    if not token:
        print("[print] ZENODO_ACCESS_TOKEN not set; skipping DOI.")
        return None
    zp = ROOT / ".scripts" / "src" / "zenodo_publish.py"
    if not zp.exists():
        print("[print] zenodo_publish.py not found; skipping DOI.")
        return None
    try:
        r = sh([sys.executable, str(zp), str(target_dir)], check=True)
        print(r.stdout)
        for line in r.stdout.splitlines():
            if line.strip().lower().startswith("doi:"):
                return line.split(":", 1)[1].strip()
    except subprocess.CalledProcessError as e:
        print("[print] DOI mint failed; continuing.\n" + e.stdout)
    return None

def git_commit_and_push(paths: list[Path], msg: str):
    run(["git", "config", "user.name", "preferredframe-bot"])
    run(["git", "config", "user.email", "bot@users.noreply.github.com"])
    run(["git", "add"] + [str(p.relative_to(ROOT)) for p in paths])
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
        print("[print] No changes to commit.")
        return
    run(["git", "commit", "-m", msg])
    branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    run(["git", "push", "origin", branch])
    print(f"[print] Pushed commit to {branch}")

def main():
    md = find_single_md()
    pnp, html, pdf = build(md)
    doi = maybe_mint_doi(md.parent)
    sidecar = write_sidecar(md, pnp, html, pdf, doi)
    git_commit_and_push([pnp, html, pdf, sidecar], "Print assets: pnpmd/html/pdf + sidecar")

    # Emit artifact_path to GITHUB_OUTPUT
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            print(f"artifact_path={(md.with_suffix('').parent).relative_to(ROOT)}", file=fh)

if __name__ == "__main__":
    main()
