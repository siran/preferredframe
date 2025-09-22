#!/usr/bin/env python3
# Render PNPMD → PDF using dockerized pandoc/latex (pdflatex) + crossref + citeproc.
import sys, subprocess, shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run(cmd): subprocess.run(cmd, check=True)

def main():
    if len(sys.argv) != 3:
        print("usage: make_pdf.py input.md output.pdf", file=sys.stderr); sys.exit(2)

    in_path  = Path(sys.argv[1]).resolve()
    out_path = Path(sys.argv[2]).resolve()
    rin  = in_path.relative_to(ROOT)
    rout = out_path.relative_to(ROOT)
    rbib = in_path.parent / "generated.bib"
    has_bib = rbib.exists()
    rbib_rel = rbib.relative_to(ROOT) if has_bib else None

    pandoc_cmd = [
        "pandoc", str(rin),
        "--from", "markdown+yaml_metadata_block",
        "--standalone",
        "--toc", "--toc-depth=2",
        "--number-sections",
        "--reference-links",
        "--citeproc", "-M", "link-citations=true",
        "-F", "pandoc-crossref",
        "--pdf-engine=pdflatex",
        "-o", str(rout),
    ]
    if has_bib:
        pandoc_cmd += ["--bibliography", str(rbib_rel)]

    inner_cmd = " && ".join([
        "set -xeuo pipefail",
        "apt-get update",
        "apt-get install -y pandoc-crossref",
        " ".join(shlex.quote(x) for x in pandoc_cmd),
    ])

    run([
        "docker","run","--rm",
        "-v", f"{ROOT}:/work","-w","/work",
        "--entrypoint","/bin/bash",
        "pandoc/latex",
        "-lc", inner_cmd
    ])
    print(f"[make_pdf] PDF written: {out_path}")

if __name__ == "__main__":
    main()
