#!/usr/bin/env python3
"""
make_pnpmd.py: generate normalized PNPMD (.pnp.md) from the original .md

- CRLF→LF normalization
- PNPMD v1.02 preprocessor:
    * header ' ...  #slug'  → '{#sec:slug}'
    * inline '@slug'        → '[@sec:slug]'
- Skips transformations inside fenced code blocks, inline code, and display math $$...$$.
- Leaves Pandoc citations [@key] untouched.
"""
import sys, re
from pathlib import Path

# --- Patterns (ASCII ids only) ---
HEADER_RE = re.compile(r"^(#{1,6}\s+.*?)(\s+)#([A-Za-z0-9_-]+)\s*$")
AT_REF_RE = re.compile(r"(?<![@\w])@([A-Za-z0-9_-]+)")  # '@slug' not preceded by @ or word-char
# Inline code and math sentinels
INLINE_CODE_RE = re.compile(r"`[^`]*`")
DISPLAY_MATH_OPEN = re.compile(r"^\s*\$\$\s*$")
DISPLAY_MATH_CLOSE = DISPLAY_MATH_OPEN

def conv_header(line: str) -> str:
    m = HEADER_RE.match(line)
    if not m:
        return line
    before, sp, slug = m.groups()
    return f"{before}{sp}" + "{#sec:" + slug + "}"

def protect_ranges(line: str):
    """Return list of (start,end) spans to skip for inline code on this line."""
    spans = []
    for m in INLINE_CODE_RE.finditer(line):
        spans.append((m.start(), m.end()))
    return spans

def in_protected(idx: int, spans) -> bool:
    return any(a <= idx < b for a, b in spans)

def conv_refs_line(line: str) -> str:
    # skip changes inside inline code
    spans = protect_ranges(line)

    def repl(m):
        s, e = m.span()
        if in_protected(s, spans):
            return m.group(0)
        slug = m.group(1)
        return f"[@sec:{slug}]"

    return AT_REF_RE.sub(repl, line)

def preprocess(text: str) -> str:
    out_lines = []
    in_fence = False
    in_dmath = False
    for raw in text.splitlines():
        line = raw

        # track fenced code blocks ``` or ~~~ (GitHub Markdown style)
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            out_lines.append(line)
            continue

        # track display math blocks $$ on a line
        if DISPLAY_MATH_OPEN.match(line):
            in_dmath = not in_dmath
            out_lines.append(line)
            continue

        if in_fence or in_dmath:
            out_lines.append(line)
            continue

        # 1) header anchors
        h = conv_header(line)
        if h != line:
            out_lines.append(h)
            continue

        # 2) inline @slug → [@sec:slug] (leave [@key] citations alone)
        out_lines.append(conv_refs_line(line))

    return "\n".join(out_lines)

def main():
    if len(sys.argv) != 3:
        print("usage: make_pnpmd.py input.md output.pnp.md", file=sys.stderr)
        sys.exit(2)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    txt = src.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    out = preprocess(txt)

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    print(f"Wrote {dst}")

if __name__ == "__main__":
    main()
