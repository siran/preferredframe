#!/usr/bin/env python3
"""
make_html.py: Render Markdown/PNPMD to HTML with pandoc.
Used for previews and asset generation (from .pnp.md).
"""
import sys, subprocess
from pathlib import Path

def run(cmd): subprocess.run(cmd, check=True)

def main():
    if len(sys.argv) < 3:
        print("usage: make_html.py input.md output.html", file=sys.stderr)
        sys.exit(2)

    md, out = Path(sys.argv[1]), Path(sys.argv[2])
    run([
        "pandoc", str(md),
        "--from", "gfm+yaml_metadata_block",
        "--standalone",
        "--toc", "--toc-depth=2",
        "-F", "pandoc-crossref",
        "-o", str(out)
    ])
    print(f"HTML written: {out}")

if __name__ == "__main__":
    main()
