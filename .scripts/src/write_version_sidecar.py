#!/usr/bin/env python3
"""
Deprecated in favor of print_pipeline.py:write_sidecar().
Kept for compatibility; writes same payload when invoked directly.

usage:
  write_version_sidecar.py path/to/file.md
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from datetime import datetime, timezone
import subprocess

ROOT = Path(__file__).resolve().parents[2]

def sh_co(args):
    p = subprocess.run(args, cwd=ROOT, check=True, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.stdout.strip()

def read_title(md: Path) -> str:
    for ln in md.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s: continue
        if s.startswith("% "): return s[2:].strip()
        break
    return md.stem

def slugify(title: str) -> str:
    import re
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", title)
    safe = re.sub(r"-{2,}", "-", safe).strip("-")
    return safe or "untitled"

def main():
    if len(sys.argv) != 2:
        print("usage: write_version_sidecar.py path/to/file.md", file=sys.stderr)
        sys.exit(2)
    md = Path(sys.argv[1]).resolve()
    stem = md.with_suffix("")
    sidecar = md.with_name("print.json")
    title = read_title(md)
    payload = {
        "title": title,
        "slug": slugify(title),
        "paths": {
            "md": str(md.relative_to(ROOT)),
            "pnpmd": str(stem.with_suffix(".pnp.md").relative_to(ROOT)),
            "html": str(stem.with_suffix(".html").relative_to(ROOT)),
            "pdf": str(stem.with_suffix(".pdf").relative_to(ROOT)),
        },
        "commit": sh_co(["git", "rev-parse", "HEAD"]),
        "branch": sh_co(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "doi": "pending"
    }
    sidecar.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[sidecar] Wrote {sidecar}")

if __name__ == "__main__":
    main()
