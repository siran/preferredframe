#!/usr/bin/env python3
# PNPMD → PDF via dockerized pandoc/latex (pdflatex), with tracing.
# Applies pnpmd.map ONLY for PDF (after .pnp.md is produced).
import sys, subprocess, shlex, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAPFILE = ROOT / "pnpmd.map"

def run(cmd):
    print("++", " ".join(shlex.quote(c) for c in cmd))
    subprocess.run(cmd, check=True)

def load_map():
    """Return list of (regex, replacement, wrap_math) rules.
       /regex/=rhs → regex; literalLHS=rhs → literal; if rhs starts with '\' wrap as $rhs$."""
    rules = []
    if not MAPFILE.exists(): return rules
    for raw in MAPFILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        lhs, rhs = (s.strip() for s in line.split("=", 1))
        if not lhs: continue
        rep = f"${rhs}$" if rhs.startswith("\\") else rhs
        if len(lhs) >= 2 and lhs[0] == "/" and lhs[-1] == "/":
            pat = re.compile(lhs[1:-1])
        else:
            pat = re.compile(re.escape(lhs))
        rules.append((pat, rep))
    return rules

def apply_map_stream(text: str, rules):
    """Apply map line-wise; skip fenced code and $$ display math blocks; preserve inline code."""
    FENCE_RE = re.compile(r"^\s*(```|~~~)")
    DMATH_LINE_RE = re.compile(r"^\s*\$\$\s*$")
    INLINE_CODE_RE = re.compile(r"`[^`]*`")
    def protect_spans(line):
        return [(m.start(), m.end()) for m in INLINE_CODE_RE.finditer(line)]
    def in_spans(i, spans):
        return any(a <= i < b for a,b in spans)
    out = []
    in_fence = False
    in_dmath = False
    for raw in text.splitlines():
        line = raw
        if FENCE_RE.match(line):
            in_fence = not in_fence; out.append(line); continue
        if DMATH_LINE_RE.match(line):
            in_dmath = not in_dmath; out.append(line); continue
        if not (in_fence or in_dmath) and rules:
            spans = protect_spans(line)
            for pat, rep in rules:
                # custom sub that skips inline-code spans
                def repl(m):
                    s, e = m.span()
                    return m.group(0) if in_spans(s, spans) else rep
                line = pat.sub(repl, line)
        out.append(line)
    return "\n".join(out)

def main():
    if len(sys.argv) != 3:
        print("usage: make_pdf.py input.pnp.md output.pdf", file=sys.stderr); sys.exit(2)

    in_path  = Path(sys.argv[1]).resolve()
    out_path = Path(sys.argv[2]).resolve()
    rin  = in_path.relative_to(ROOT)
    rout = out_path.relative_to(ROOT)
    rbib = in_path.parent / "generated.bib"
    has_bib = rbib.exists()
    rbib_rel = rbib.relative_to(ROOT) if has_bib else None

    # 1) Apply pnpmd.map to a temp TeX-safe copy of .pnp.md
    mapped_path = in_path.with_suffix(".texsafe.pnp.md")
    rules = load_map()
    src_txt = in_path.read_text(encoding="utf-8")
    mapped_txt = apply_map_stream(src_txt, rules) if rules else src_txt
    mapped_path.write_text(mapped_txt, encoding="utf-8")
    rmap = mapped_path.relative_to(ROOT)

    pandoc_cmd = [
        "pandoc", str(rmap),
        "--from", "markdown+yaml_metadata_block",
        "--standalone",
        "--toc", "--toc-depth=2",
        "--number-sections",
        "--reference-links",
        "--citeproc", "-M", "link-citations=true",
        "-F", "pandoc-crossref",
        "--pdf-engine=pdflatex",
        "--pdf-engine-opt=-interaction=nonstopmode",
        "--pdf-engine-opt=-file-line-error",
        "-o", str(rout),
    ]
    if has_bib:
        pandoc_cmd += ["--bibliography", str(rbib_rel)]

    # 2) Inside container: install minimal tools + static pandoc-crossref, then render
    inner_cmd = " && ".join([
        "set -ex",
        "if command -v apt-get >/dev/null 2>&1; then "
        "  apt-get update && apt-get install -y curl xz-utils texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended; "
        "elif command -v apk >/dev/null 2>&1; then "
        "  apk add --no-cache curl xz texlive-full; "
        "fi",
        "if ! command -v pandoc-crossref >/dev/null 2>&1; then "
        "  curl -fsSL -o /tmp/pandoc-crossref.txz https://github.com/lierdakil/pandoc-crossref/releases/latest/download/pandoc-crossref-Linux.tar.xz && "
        "  mkdir -p /usr/local/bin && tar -xJf /tmp/pandoc-crossref.txz -C /usr/local/bin && chmod +x /usr/local/bin/pandoc-crossref; "
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
    print(f"[make_pdf] PDF written: {out_path}")

if __name__ == "__main__":
    main()
