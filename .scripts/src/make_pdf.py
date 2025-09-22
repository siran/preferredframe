#!/usr/bin/env python3
import sys, subprocess, shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run(cmd):
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run(cmd, check=True)

def main():
    if len(sys.argv) != 3:
        print("Usage: make_pdf.py input.md output.pdf", file=sys.stderr)
        sys.exit(1)

    pnp, pdf = map(Path, sys.argv[1:])

    pandoc_cmd = [
        "pandoc", str(pnp),
        "--pdf-engine=pdflatex",
        "--standalone", "--toc", "--toc-depth=2",
        "--number-sections", "--reference-links",
        "--citeproc", "-M", "link-citations=true",
        "-o", str(pdf)
    ]

    run([
        "docker", "run", "--rm",
        "-v", f"{ROOT}:/data", "-w", "/data",
        "pandoc/latex"
    ] + pandoc_cmd)

if __name__ == "__main__":
    main()
