#!/usr/bin/env python3
"""
validate_pnpmd.py
- Expect exactly one .md under preferredframe/prints/*/*.md
- Build .pnp.md, .html, .pdf alongside it (via dockerized makers)
- Emit artifact_path=<folder> to $GITHUB_OUTPUT
"""
from __future__ import annotations
import os, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRINTS = ROOT / "preferredframe" / "prints"

def sh(args):
    subprocess.run(args, check=True)

def find_single_md() -> Path:
    mds = list(PRINTS.glob("*/*.md"))
    if len(mds) == 0:
        print("[validate][ERROR] No .md file found under preferredframe/prints/*/")
        sys.exit(1)
    if len(mds) > 1:
        print("[validate][ERROR] Multiple .md files found. Only one allowed:")
        for m in mds:
            print(" -", m.relative_to(ROOT))
        sys.exit(1)
    return mds[0]

def build(md: Path):
    stem = md.with_suffix("")              # preferredframe/prints/<Title>/<Title>
    pnp  = stem.with_suffix(".pnp.md")
    html = stem.with_suffix(".html")
    pdf  = stem.with_suffix(".pdf")

    print(f"[validate] Building {md.relative_to(ROOT)}")
    sh([sys.executable, str(ROOT/".scripts/src/make_pnpmd.py"), str(md),  str(pnp)])
    sh([sys.executable, str(ROOT/".scripts/src/make_html.py"),  str(pnp), str(html)])
    sh([sys.executable, str(ROOT/".scripts/src/make_pdf.py"),   str(pnp), str(pdf)])

    for f in (md, pnp, html, pdf):
        if not f.exists() or f.stat().st_size == 0:
            print(f"[validate][ERROR] Missing or empty: {f.relative_to(ROOT)}")
            sys.exit(1)

    folder = stem.parent
    print(f"[validate][OK] -> {pnp.name}, {html.name}, {pdf.name}")

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            print(f"artifact_path={folder.relative_to(ROOT)}", file=fh)

def main():
    md = find_single_md()
    build(md)

if __name__ == "__main__":
    main()
