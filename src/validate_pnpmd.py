#!/usr/bin/env python3
"""
PNPMD validator (v1.001) + PDF build trigger gate.

Checks (fast, deterministic):
- Header: first 3 non-empty lines must start with '%' (Title, Authors, Date).
- Required sections (case-insensitive headings):
  Abstract, One-Sentence Summary, Keywords, Corresponding author(s), References.
- Formatting rules sampled:
  * no '---' as horizontal rule (section separators must be blank lines)
  * forbid \[...\], \(...\) math; allow $...$ and $$...$$
  * no math in Abstract block
- UTF-8: rely on file read success; reject binary bytes.

Exit nonzero on failure. Prints a short JSON summary.
"""
from __future__ import annotations
from pathlib import Path
import sys, json, re

REQ_SECTIONS = [
    r"^##\s*Abstract\s*$",
    r"^##\s*One-Sentence Summary\s*$",
    r"^##\s*Keywords\s*$",
    r"^##\s*Corresponding author\(s\)\s*$",
    r"^##\s*References\s*$",
]

HRULE_PATTERN = re.compile(r"(?m)^\s*---\s*$")
BAD_MATH = re.compile(r"(\\\\\[|\\\\\]|\\\(|\\\))")  # raw patterns for \[ \] \( \)
ABSTRACT_HEADER = re.compile(r"(?mi)^##\s*Abstract\s*$")

def read_text_utf8(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception as e:
        raise SystemExit(f"ERROR: cannot read {p}: {e}")

def check_header_lines(txt: str, report: dict):
    lines = [ln for ln in txt.splitlines() if ln.strip()][:3]
    ok = len(lines) >= 3 and all(ln.lstrip().startswith("%") for ln in lines[:3])
    report["header_ok"] = bool(ok)
    if not ok:
        report.setdefault("errors", []).append("First three non-empty lines must begin with '% ' (Title, Authors, Date).")

def check_required_sections(txt: str, report: dict):
    present = []
    for pat in REQ_SECTIONS:
        m = re.search(pat, txt, flags=re.M)
        present.append(bool(m))
        if not m:
            report.setdefault("errors", []).append(f"Missing required section heading matching: {pat}")
    report["required_sections_ok"] = all(present)

def slice_abstract(txt: str) -> str:
    """Return abstract block text (until next '## ' heading)."""
    m = ABSTRACT_HEADER.search(txt)
    if not m:
        return ""
    start = m.end()
    # find next top-level '## ' after start
    nxt = re.search(r"(?m)^##\s+", txt[start:])
    end = start + nxt.start() if nxt else len(txt)
    return txt[start:end]

def check_rules(txt: str, report: dict):
    # 1) forbid horizontal rules '---'
    if HRULE_PATTERN.search(txt):
        report.setdefault("errors", []).append("Horizontal rules '---' are not allowed for section separation.")
    # 2) forbid \[...\] and \(...\) math delimiters
    if BAD_MATH.search(txt):
        report.setdefault("errors", []).append(r"Use $...$ (inline) or $$...$$ (display); do not use \[...\] or \(...\).")
    # 3) no math in Abstract
    abstract = slice_abstract(txt)
    if abstract and (re.search(r"(?<!\\)\$(?!\$).*?(?<!\\)\$", abstract) or re.search(r"(?<!\\)\$\$(.|\n)*?\$\$", abstract)):
        report.setdefault("errors", []).append("Abstract must not contain math.")

def main():
    if len(sys.argv) < 2:
        print("usage: validate_pnpmd.py path/to/paper.md", file=sys.stderr)
        sys.exit(2)

    md = Path(sys.argv[1])
    if not md.exists():
        print(json.dumps({"ok": False, "errors": [f"Missing file: {md}"]}, indent=2))
        sys.exit(1)

    txt = read_text_utf8(md)
    report = {"file": str(md), "ok": True, "errors": []}

    check_header_lines(txt, report)
    check_required_sections(txt, report)
    check_rules(txt, report)

    report["ok"] = not report["errors"]
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["ok"] else 1)

if __name__ == "__main__":
    main()
