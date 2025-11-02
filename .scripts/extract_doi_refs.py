#!/usr/bin/env python3
import re, sys, json
from pathlib import Path

DOI_RE = re.compile(r'\b10\.\d{4,9}/\S+\b')

def extract(text: str):
    raw = set(DOI_RE.findall(text))
    out = set()
    for d in raw:
        d = d.rstrip('.,);:]')
        out.add("https://doi.org/"+d if not d.startswith("10.") else "https://doi.org/"+d)
    return sorted(out)

def main():
    if len(sys.argv) != 2:
        print("usage: extract_doi_refs.py <file.md>")
        sys.exit(2)
    md = Path(sys.argv[1]).read_text(encoding="utf-8")
    dois = extract(md)
    print(json.dumps(dois, indent=2))

if __name__ == "__main__":
    main()
