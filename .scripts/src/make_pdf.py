#!/usr/bin/env python3
"""
Deterministic PDF build for PNPMD using pandoc + xelatex.
Includes citeproc and crossref.
"""
from pathlib import Path
import sys, subprocess

def run(cmd):
    subprocess.run(cmd, check=True)

def main():
    if len(sys.argv) < 3:
        print("usage: make_pdf.py input.md output.pdf", file=sys.stderr)
        sys.exit(2)
    md = Path(sys.argv[1]).resolve()
    pdf = Path(sys.argv[2]).resolve()
    bib = md.parent / "generated.bib"

    cmd = [
        "pandoc", str(md),
        "--from", "markdown+yaml_metadata_block",
        "--toc", "--toc-depth=2",
        "--number-sections",
        "--standalone",
        "--reference-links",
        "--citeproc", "-M", "link-citations=true",
        "-F", "pandoc-crossref",
        "--pdf-engine=xelatex",
        "-o", str(pdf),
    ]
    if bib.exists():
        cmd.extend(["--bibliography", str(bib)])

    run(cmd)
    print(f"[make_pdf] PDF written: {pdf}")

if __name__ == "__main__":
    main()
