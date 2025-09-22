#!/usr/bin/env python3
# PNPMD → HTML via dockerized pandoc/latex, with tracing and self-installing pandoc-crossref.
import sys, subprocess, shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run(cmd):
    print("++", " ".join(shlex.quote(c) for c in cmd))
    subprocess.run(cmd, check=True)

def main():
    if len(sys.argv) != 3:
        print("usage: make_html.py input.md output.html", file=sys.stderr); sys.exit(2)

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
        "-o", str(rout),
    ]
    if has_bib:
        pandoc_cmd += ["--bibliography", str(rbib_rel)]

    # Download static crossref if missing (works on Debian/Alpine). Trace commands with set -ex.
    inner_cmd = " && ".join([
        "set -ex",
        # ensure curl + xz exist (for both apt and apk)
        "if command -v apt-get >/dev/null 2>&1; then apt-get update && apt-get install -y curl xz-utils; "
        "elif command -v apk >/dev/null 2>&1; then apk add --no-cache curl xz; "
        "fi",
        # install pandoc-crossref if missing
        "if ! command -v pandoc-crossref >/dev/null 2>&1; then "
        "  curl -fsSL -o /tmp/pandoc-crossref.txz https://github.com/lierdakil/pandoc-crossref/releases/latest/download/pandoc-crossref-Linux.tar.xz && "
        "  mkdir -p /usr/local/bin && tar -xJf /tmp/pandoc-crossref.txz -C /usr/local/bin && "
        "  chmod +x /usr/local/bin/pandoc-crossref; "
        "fi",
        "pandoc --version",
        "pandoc-crossref --version",
        " ".join(shlex.quote(x) for x in pandoc_cmd),
    ])

    cmd = [
        "docker","run","--rm",
        "-v", f"{ROOT}:/work","-w","/work",
        "--entrypoint","/bin/sh",
        "pandoc/latex",
        "-ec", inner_cmd
    ]
    run(cmd)
    print(f"[make_html] HTML written: {out_path}")

if __name__ == "__main__":
    main()
