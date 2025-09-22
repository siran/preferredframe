#!/usr/bin/env python3
# PDF build via dockerized pandoc/latex (pdflatex). No runtime installs.
# Assumes .pnp.md is already TeX-safe (via pnpmd.map in your pipeline).
import sys, subprocess, shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run(cmd):
    print("++", " ".join(shlex.quote(c) for c in cmd), flush=True)
    subprocess.run(cmd, check=True)

def main():
    if len(sys.argv) != 3:
        print("Usage: make_pdf.py input.pnp.md output.pdf", file=sys.stderr)
        sys.exit(1)

    pnp = Path(sys.argv[1]).resolve()
    pdf = Path(sys.argv[2]).resolve()

    # compute paths relative to ROOT, then address them inside the container as /data/<rel>
    rin  = pnp.relative_to(ROOT)
    rout = pdf.relative_to(ROOT)

    pandoc_args = [
        "pandoc", f"/data/{rin}",
        "--pdf-engine=pdflatex",
        "--standalone",
        "--toc", "--toc-depth=2",
        "--number-sections",
        "--reference-links",
        "--citeproc", "-M", "link-citations=true",
        "-o", f"/data/{rout}",
    ]

    cmd = [
        "docker","run","--rm",
        "-v", f"{ROOT}:/data", "-w", "/data",
        "pandoc/latex",
        *pandoc_args,
    ]
    run(cmd)
    print(f"[make_pdf] PDF written: {pdf}")

if __name__ == "__main__":
    main()
