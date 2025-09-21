#!/usr/bin/env python3
"""
validate_pnpmd.py
Build .pnp.md, .html, .pdf for changed prints and report status.

Change detection:
- Compares against origin/main if available; else builds all found MDs.
- Watches under preferredframe/prints/**/**.md
"""
from __future__ import annotations
import subprocess, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRINTS = ROOT / "preferredframe" / "prints"

def sh_co(args, cwd=ROOT) -> str:
    p = subprocess.run(args, cwd=cwd, check=True, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.stdout.strip()

def sh(args, cwd=ROOT):
    subprocess.run(args, cwd=cwd, check=True)

def changed_md() -> list[Path]:
    try:
        sh(["git", "fetch", "origin", "main"])
        base = "origin/main"
        out = sh_co(["git", "diff", "--name-only", f"{base}...HEAD", "--", "preferredframe/prints/**/*.md"])
        c = [ROOT / p for p in out.splitlines() if p.strip().endswith(".md")]
        if c:
            return c
    except Exception:
        pass
    # fallback: all
    return list(PRINTS.glob("**/*.md"))

def build_one(md: Path) -> tuple[Path, Path, Path]:
    stem = md.with_suffix("")  # drop .md
    pnp = stem.with_suffix(".pnp.md")
    html = stem.with_suffix(".html")
    pdf  = stem.with_suffix(".pdf")

    print(f"[validate] Building: {md.relative_to(ROOT)}")
    sh([sys.executable, str(ROOT / ".scripts" / "src" / "make_pnpmd.py"), str(md), str(pnp)])
    sh([sys.executable, str(ROOT / ".scripts" / "src" / "make_html.py"),  str(pnp), str(html)])
    sh([sys.executable, str(ROOT / ".scripts" / "src" / "make_pdf.py"),   str(pnp), str(pdf)])

    for f in (pnp, html, pdf):
        if not f.exists() or f.stat().st_size == 0:
            print(f"[validate][ERROR] Missing/empty: {f.relative_to(ROOT)}", file=sys.stderr)
            raise SystemExit(1)
    print(f"[validate][OK] {md.name} -> {pnp.name}, {html.name}, {pdf.name}")
    return pnp, html, pdf

def main():
    mds = changed_md()
    if not mds:
        print("[validate] No target markdown files. Nothing to do.")
        return
    for md in mds:
        build_one(md)

if __name__ == "__main__":
    main()
