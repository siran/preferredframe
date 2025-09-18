#!/usr/bin/env python3
from pathlib import Path
import sys, subprocess

def run(cmd): subprocess.run(cmd, check=True)

def main():
    if len(sys.argv) != 2+1:
        print("usage: make_html.py input.md output.html", file=sys.stderr); sys.exit(2)
    md  = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    cmd = [
        "pandoc", str(md),
        "--toc", "--toc-depth=2",
        "--number-sections", "--number-offset=1",
        "--reference-links",
        "--citeproc", "-M", "link-citations=true",
        "-F", "pandoc-crossref",
        "--standalone",
        "-o", str(out),
    ]
    bib = md.parent / "generated.bib"
    if bib.exists(): cmd.extend(["--bibliography", str(bib)])
    run(cmd)
    print(f"HTML written: {out}")

if __name__ == "__main__":
    main()
