#!/usr/bin/env python3
"""
Deterministic PDF build for PNPMD using pandoc.
No citeproc yet (kept minimal by request).
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

    run([
        "pandoc", str(md),
        "--from", "gfm+yaml_metadata_block",
        "--pdf-engine", "xelatex",
        "--toc", "--toc-depth=2",
        "--standalone",
        "-F", "pandoc-crossref",
        "-o", str(pdf),
    ])
    print(f"PDF written: {pdf}")

if __name__ == "__main__":
    main()
