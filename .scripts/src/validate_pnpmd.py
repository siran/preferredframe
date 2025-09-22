#!/usr/bin/env python3
"""
CI validator:
- Exactly one .md under prints/*/*.md
- Build .pnp.md, .html, .pdf (dockerized makers)
- Emit artifact_path=<folder> to $GITHUB_OUTPUT
"""
from __future__ import annotations
import os, sys, subprocess
from pathlib import Path

ROOT   = Path(__file__).resolve().parents[2]
PRINTS = ROOT / "prints"  # <-- no 'preferredframe' prefix

def sh(args): subprocess.run(args, check=True)

def find_single_md() -> Path:
    mds = list(PRINTS.glob("*/*.md"))
    if not mds:
        print("[validate][ERROR] No .md under prints/*/"); sys.exit(1)
    if len(mds) > 1:
        print("[validate][ERROR] Multiple .md files found:"); [print(" -", m.relative_to(ROOT)) for m in mds]; sys.exit(1)
    return mds[0]

def build(md: Path):
    # IMPORTANT: derive outputs directly from md to preserve '.02' etc.
    pnp  = md.with_suffix(".pnp.md")
    html = md.with_suffix(".html")
    pdf  = md.with_suffix(".pdf")

    print(f"[validate] Building {md.relative_to(ROOT)}")
    sh([sys.executable, str(ROOT/".scripts/src/make_pnpmd.py"), str(md),  str(pnp)])
    sh([sys.executable, str(ROOT/".scripts/src/make_html.py"),  str(pnp), str(html)])
    sh([sys.executable, str(ROOT/".scripts/src/make_pdf.py"),   str(pnp), str(pdf)])

    for f in (md, pnp, html, pdf):
        if not f.exists() or f.stat().st_size == 0:
            print(f"[validate][ERROR] Missing/empty: {f.relative_to(ROOT)}"); sys.exit(1)

    folder = md.parent
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
