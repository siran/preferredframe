#!/usr/bin/env python3
"""
make_pnpmd.py: generate normalized PNPMD (.pnp.md) from the original .md
(currently: CRLF→LF normalization; keep content 1:1 otherwise)
"""
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 3:
        print("usage: make_pnpmd.py input.md output.pnp.md", file=sys.stderr)
        sys.exit(2)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    txt = src.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(txt, encoding="utf-8")
    print(f"Wrote {dst}")

if __name__ == "__main__":
    main()
