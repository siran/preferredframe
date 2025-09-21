#!/usr/bin/env python3
"""
make_pnpmd.py: generate normalized PNPMD (.pnp.md) from the original .md

- CRLF→LF normalization
- PNPMD v1.02 preprocessor:
    * header ' ...  #id'        → '{#pnpmd:id}'
    * header ' ...  #type:id'   → '{#type:id}'
    * untyped '@id'             → '[@pnpmd:id]'   (typed '@sec:id' / '@fig:id' / '@eq:id' / '@tbl:id' untouched)
    * literal '[ #id ]'         → '[#id](#pnpmd:id)'
- Skips transformations inside fenced code blocks, inline code, and display math $$...$$.
- Leaves Pandoc citations [@key] untouched.
"""
import sys, re
from pathlib import Path

# --- Patterns (ASCII ids only) ---
HEADER_RE = re.compile(r"^(#{1,6}\s+.*?)(\s+)#([A-Za-z0-9_-]+(?::[A-Za-z0-9_-]+)?)\s*$")
UNTYPED_AT_RE = re.compile(r"(?<![@\w])@([A-Za-z0-9_-]+)(?!:[A-Za-z0-9_-])")  # '@id' not followed by ':'
INLINE_CODE_RE = re.compile(r"`[^`]*`")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
DMATH_LINE_RE = re.compile(r"^\s*\$\$\s*$")
LITERAL_REF_RE = re.compile(r"\[\s*#([A-Za-z0-9_-]+)\s*\]")

def conv_header(line: str) -> str:
    m = HEADER_RE.match(line)
    if not m: return line
    before, sp, slug = m.groups()
    # slug may be 'type:id' or just 'id'
    if ":" in slug:
        return f"{before}{sp}" + "{#" + slug + "}"
    else:
        return f"{before}{sp}" + "{#pnpmd:" + slug + "}"

def _protect_inline_spans(line: str):
    return [(m.start(), m.end()) for m in INLINE_CODE_RE.finditer(line)]

def _in_spans(i: int, spans) -> bool:
    return any(a <= i < b for a, b in spans)

def conv_untyped_refs_line(line: str) -> str:
    spans = _protect_inline_spans(line)

    def repl(m):
        s, _ = m.span()
        if _in_spans(s, spans):
            return m.group(0)
        slug = m.group(1)
        return f"[@pnpmd:{slug}]"

    # IMPORTANT: do not touch Pandoc citations [@key] or typed '@type:id'
    return UNTYPED_AT_RE.sub(repl, line)

def conv_literal_inline(line: str) -> str:
    def repl(m):
        ident = m.group(1)
        return f"[#{ident}](#pnpmd:{ident})"
    return LITERAL_REF_RE.sub(repl, line)

def preprocess(text: str) -> str:
    out = []
    in_fence = False
    in_dmath = False
    for raw in text.splitlines():
        line = raw

        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append(line); continue

        if DMATH_LINE_RE.match(line):
            in_dmath = not in_dmath
            out.append(line); continue

        if in_fence or in_dmath:
            out.append(line); continue

        h = conv_header(line)
        if h != line:
            out.append(h); continue

        line2 = conv_literal_inline(line)
        line3 = conv_untyped_refs_line(line2)
        out.append(line3)

    return "\n".join(out)

def main():
    if len(sys.argv) != 3:
        print("usage: make_pnpmd.py input.md output.pnp.md", file=sys.stderr)
        sys.exit(2)

    src = Path(sys.argv[1]); dst = Path(sys.argv[2])
    txt = src.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    out = preprocess(txt)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    print(f"[make_pnpmd] Wrote {dst}")

if __name__ == "__main__":
    main()
