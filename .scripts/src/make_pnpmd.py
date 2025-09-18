#!/usr/bin/env python3
from pathlib import Path
import sys

def main():
    if len(sys.argv) != 2+1:
        print("usage: make_pnpmd.py in.md out.pnpmd.md", file=sys.stderr); sys.exit(2)
    src = Path(sys.argv[1]); dst = Path(sys.argv[2])
    txt = src.read_text(encoding="utf-8")
    txt = txt.replace("\r\n","\n").replace("\r","\n")  # normalize
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(txt, encoding="utf-8")
    print(f"Wrote {dst}")

if __name__ == "__main__":
    main()
