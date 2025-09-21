#!/usr/bin/env python3
"""
make_html.py: Render Markdown/PNPMD to HTML with pandoc.
Flags aligned with PNPMD v1.02 recommendations.
"""
import sys, subprocess
from pathlib import Path

def run(cmd): subprocess.run(cmd, check=True)

def main():
    if len(sys.argv) < 3:
        print("usage: make_html.py input.md output.html", file=sys.stderr)
        sys.exit(2)

    md, out = Path(sys.argv[1]), Path(sys.argv[2])
    bib = md.parent / "generated.bib"
    cmd = [
        "pandoc", str(md),
        "--from", "markdown+yaml_metadata_block",
        "--standalone",
        "--toc", "--toc-depth=2",
        "--number-sections",
        "--reference-links",
        "--citeproc", "-M", "link-citations=true",
        "-F", "pandoc-crossref",
        "-o", str(out)
    ]
    if bib.exists():
        cmd.extend(["--bibliography", str(bib)])
    run(cmd)
    print(f"[make_html] HTML written: {out}")

if __name__ == "__main__":
    main()
