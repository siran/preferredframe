#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PNPMD → PDF/HTML preprocessor and renderer (Pandoc + pandoc-crossref via Docker)

Usage:
  python render.py [--timeout N] [--omit-toc] [--omit-numbering] [--as-is]
                   [--pdf | --html | --all] [file.md]

Defaults:
  --all (renders both PDF and HTML)

Outputs (next to source .md):
  - <name>.pandoc.md (preprocessed)
  - <name>.pdf        (if --pdf or --all)
  - <name>.html       (if --html or --all)

Exit codes:
  0   success
  124 docker timeout
  130 interrupted
  >0  failure (message printed to stdout)
"""
import argparse, re, shutil, subprocess, sys, time, shlex, tempfile, os
from pathlib import Path
from typing import Optional, Tuple, Set, Dict, List

# ---------- Utility helpers ----------
def echo_cmd(cmd_list: List[str]):
    print("+", " ".join(shlex.quote(x) for x in cmd_list), flush=True)

def run_visible(cmd_list: List[str], *, timeout=0) -> int:
    echo_cmd(cmd_list)
    start = time.time()
    try:
        p = subprocess.Popen(cmd_list)
        while True:
            if p.poll() is not None:
                return p.returncode
            if timeout and time.time() - start > timeout:
                try:
                    p.terminate(); time.sleep(0.5); p.kill()
                except Exception:
                    pass
                return 124
            time.sleep(0.1)
    except KeyboardInterrupt:
        try: p.kill()
        except Exception: pass
        return 130
    except Exception:
        return 1

def die(msg: str, code: int = 1):
    print(f"ERROR: {msg}")
    sys.exit(code)

# ---------- Repo root / map ----------
def discover_md_in_cwd() -> Path:
    cwd = Path.cwd()
    cands = [p for p in cwd.iterdir()
             if p.is_file() and p.suffix.lower()==".md"
             and not p.name.startswith(".")
             and not re.search(r"\.[A-Za-z0-9_-]+\.md$", p.name)]
    if len(cands)==1: return cands[0]
    if not cands: die("No .md in current directory.")
    die("Ambiguous .md in CWD:\n" + "\n".join(f" - {p.name}" for p in sorted(cands)))

def find_repo_root(start: Path) -> Path:
    try:
        top = subprocess.check_output(
            ["git","rev-parse","--show-toplevel"],
            cwd=start, text=True, stderr=subprocess.DEVNULL
        ).strip()
        if top: return Path(top)
    except Exception:
        pass
    cur = start
    while True:
        if (cur / "pnpmd.map").exists():
            return cur
        if cur.parent == cur: break
        cur = cur.parent
    die("pnpmd.map not found in repo root or ancestors")

def _trim_ascii(s: str, *, left=True, right=True) -> str:
    if left:  s = re.sub(r'^[ \t]+', '', s)
    if right: s = re.sub(r'[ \t]+$', '', s)
    return s

def load_map(map_path: Path):
    if not map_path.exists():
        die(f"Map file not found: {map_path}")
    out=[]
    for raw in map_path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.lstrip().startswith("#") or "=" not in raw: continue
        lhs, rhs = raw.split("=", 1)
        lhs = _trim_ascii(lhs); rhs = _trim_ascii(rhs)
        if lhs == "": continue
        is_regex = lhs.startswith("/") and lhs.endswith("/") and len(lhs) >= 2
        out.append((lhs, rhs, is_regex))
    return out

# ---------- Protection of code, math ----------
_FENCE_RE = re.compile(r'(^|\n)(?P<f>```+|~~~+)[^\n]*\n.*?(\n(?P=f)[ \t]*\n|$)', re.DOTALL)
_INLINE_CODE_RE = re.compile(r'(?P<ticks>`+)(?P<body>[^`]*?)\1')
_MATH_BLOCK_RE = re.compile(r'(^|\n)\$\$[\s\S]*?\$\$(?=\s*(\n|$))', re.MULTILINE)
_INLINE_MATH_RE = re.compile(r'(?<!\$)\$(?!\$)(?:\\\$|[^$])+\$(?!\$)')

def _protect(text: str):
    blobs=[]
    def stash(m):
        i=len(blobs); blobs.append(m.group(0))
        return f"\u0000B{i}\u0000"
    text=_FENCE_RE.sub(stash, text)
    text=_INLINE_CODE_RE.sub(stash, text)
    text=_MATH_BLOCK_RE.sub(stash, text)
    text=_INLINE_MATH_RE.sub(stash, text)
    return text, blobs

def _unprotect(text: str, blobs):
    return re.sub(r'\u0000B(\d+)\u0000', lambda mm: blobs[int(mm.group(1))], text)

# ---------- Mapping ----------
def apply_mappings_safe(s: str, entries):
    prot, blobs = _protect(s)
    for lhs, rhs, is_regex in (e for e in entries if e[2]):
        rep = f"${rhs}$" if rhs.startswith("\\") else rhs
        prot = re.sub(lhs[1:-1], rep, prot, flags=re.DOTALL)
    for lhs, rhs, is_regex in (e for e in entries if not e[2]):
        rep = f"${rhs}$" if rhs.startswith("\\") else rhs
        prot = prot.replace(lhs, rep)
    return _unprotect(prot, blobs)

# ---------- % header ----------
_PERC_LINE = re.compile(r'^\s*%\s*(.*)\s*$')
def extract_percent_block(text: str):
    lines = text.splitlines()
    meta = {"title": None, "authors": [], "date": None}
    i = 0
    for j in range(min(3, len(lines))):
        m = _PERC_LINE.match(lines[j])
        if not m: break
        val = m.group(1).strip()
        if j == 0: meta["title"] = val or None
        elif j == 1:
            parts = [p.strip() for chunk in re.split(r'\band\b|,', val) for p in [chunk] if p.strip()]
            meta["authors"] = parts
        elif j == 2: meta["date"] = val or None
        i += 1
    raw_head = lines[:i]
    stripped = "\n".join(lines[i:]).lstrip("\n") if i else text
    return stripped, meta, raw_head

# ---------- IDs, anchors ----------
_HDR_RE = re.compile(r'^(?P<hash>#{1,6})\s+(?P<title>.+?)(?:\s+\{(?P<attrs>[^}]*)\})?\s*$')
_ATTR_ID_RE = re.compile(r'(?:^|\s)#([A-Za-z0-9_:-]+)(?=\s|$)')
_LINK_LABEL_RE = re.compile(r'\[([^\]]+)\]\([^)]+\)')
_FORMAT_MARKER_RE = re.compile(r'[*_~`]+')

def _auto_slug(title: str) -> str:
    t = _LINK_LABEL_RE.sub(r'\1', title)
    t = _FORMAT_MARKER_RE.sub('', t)
    t = t.lower()
    t = re.sub(r'[^0-9a-zA-Z _-]+', '', t)
    t = t.strip().replace(' ', '-')
    t = re.sub(r'-{2,}', '-', t).strip('-')
    return t or 'x'

def collect_all_ids(md: str) -> Set[str]:
    ids=set()
    for ln in md.splitlines():
        m=_HDR_RE.match(ln)
        if m:
            title=m.group('title')
            attrs=m.group('attrs') or ''
            for mm in _ATTR_ID_RE.finditer(attrs):
                ids.add(mm.group(1))
            ids.add(_auto_slug(title))
        for mm in re.finditer(r'\{#([A-Za-z0-9_:-]+)\}', ln):
            ids.add(mm.group(1))
    return ids

_ATTR_BLOCK_RE = re.compile(r'\{#([A-Za-z0-9_:-]+)\}')
_BRACKETED_LABEL_ANCHOR_RE = re.compile(r'\[([^\]]+?)\]\s*\{#([A-Za-z0-9_:-]+)\}')

def prose_anchors_and_labels(md: str) -> Tuple[str, Dict[str,str]]:
    prot, blobs = _protect(md)
    out_lines=[]; label_map: Dict[str,str] = {}
    for ln in prot.splitlines():
        if _HDR_RE.match(ln):
            out_lines.append(ln); continue
        for m in _BRACKETED_LABEL_ANCHOR_RE.finditer(ln):
            label = m.group(1); pid = m.group(2)
            if ":" in pid: continue
            label_map.setdefault(pid, label)
        def sub_attr(m):
            pid = m.group(1)
            if ":" in pid: return m.group(0)
            start = m.start(); prefix = ln[:start]
            if re.search(r'\[\]\s*$', prefix): return m.group(0)
            if re.search(r'\]\s*$', prefix):   return m.group(0)
            return f'[]{{#{pid}}}'
        ln2 = _ATTR_BLOCK_RE.sub(sub_attr, ln)
        out_lines.append(ln2)
    result = "\n".join(out_lines)
    return _unprotect(result, blobs), label_map

_DEST_NORM_RE = re.compile(r'\]\(\s*@(?:(sec|fig|eq|tbl):)?([A-Za-z0-9_-]+)\s*\)')
def normalize_link_destinations(md: str) -> str:
    prot, blobs = _protect(md)
    def repl(m):
        kind = m.group(1); ident = m.group(2)
        return f'](#{kind+":"+ident if kind else ident})'
    prot = _DEST_NORM_RE.sub(repl, prot)
    return _unprotect(prot, blobs)

_AT_UNBRACKETED = re.compile(r'(?<![A-Za-z0-9._%+-])@(?P<id>[A-Za-z0-9_-]+)\b')
_AT_BRACKETED   = re.compile(r'\[\s*@(?P<id>[A-Za-z0-9_-]+)\s*\]')
_EMPTY_SPAN_ANCHOR_RE = re.compile(r'\[\]\{#([A-Za-z0-9_-]+)\}')

def rewrite_at_tokens(md: str, *, label_map: Dict[str,str], span_ids: Set[str], header_ids: Set[str]) -> str:
    prot, blobs = _protect(md)
    outs=[]
    def keep(s: str) -> str:
        i=len(outs); outs.append(s); return f"\u0000L{i}\u0000"
    def make_link(ident: str, bracketed: bool) -> str:
        if ":" in ident: return f'@{ident}' if not bracketed else f'[@{ident}]'
        if ident in label_map: return f'[{label_map[ident]}](#{ident})'
        if ident in span_ids or ident in header_ids: return f'[@{ident}](#{ident})'
        return f'@{ident}' if not bracketed else f'[@{ident}]'
    prot = _AT_BRACKETED.sub(lambda m: keep(make_link(m.group("id"), True)), prot)
    prot = _AT_UNBRACKETED.sub(lambda m: keep(make_link(m.group("id"), False)), prot)
    prot = re.sub(r'\u0000L(\d+)\u0000', lambda mm: outs[int(mm.group(1))], prot)
    return _unprotect(prot, blobs)

_SEC_UNBR = re.compile(r'(?<![A-Za-z0-9._%+-])@sec:([A-Za-z0-9_-]+)\b')
_SEC_BRKT = re.compile(r'\[\s*@sec:([A-Za-z0-9_-]+)\s*\]')
def atsec_to_nameref(md: str) -> str:
    prot, blobs = _protect(md)
    prot = _SEC_BRKT.sub(lambda m: f"\\nameref{{sec:{m.group(1)}}}", prot)
    prot = _SEC_UNBR.sub(lambda m: f"\\nameref{{sec:{m.group(1)}}}", prot)
    return _unprotect(prot, blobs)

_BARE_HASH_RE = re.compile(r'(?<![#A-Za-z0-9_{(])#([A-Za-z0-9_:-]+)\b(?!\()')
def rewrite_hash_anchors(md: str) -> str:
    prot, blobs = _protect(md)
    def repl_line(ln: str) -> str:
        if _HDR_RE.match(ln): return ln
        return _BARE_HASH_RE.sub(lambda m: f'[](#{m.group(1)})', ln)
    new_lines = [repl_line(ln) for ln in prot.splitlines()]
    prot2 = "\n".join(new_lines)
    return _unprotect(prot2, blobs)

_TOC_MARK_RE = re.compile(r'^\s*\[\[TOC\]\]\s*$', re.MULTILINE)
def insert_toc_after_keywords_content(md: str) -> str:
    if _TOC_MARK_RE.search(md): return md
    lines = md.splitlines()
    start_idx=None; lvl=None
    for i, ln in enumerate(lines):
        m=_HDR_RE.match(ln)
        if not m: continue
        title=m.group('title').strip()
        if title.lower().startswith('keywords'):
            start_idx=i; lvl=len(m.group('hash')); break
    if start_idx is None: return md
    end=len(lines)
    for j in range(start_idx+1, len(lines)):
        m=_HDR_RE.match(lines[j])
        if m and len(m.group('hash'))<=lvl:
            end=j; break
    lines.insert(end, ""); lines.insert(end+1, "\n[[TOC]]\n"); lines.insert(end+2, "")
    return "\n".join(lines)

def replace_toc_marker(md: str) -> Tuple[str,bool]:
    if _TOC_MARK_RE.search(md):
        return _TOC_MARK_RE.sub(r'\n\\tableofcontents\n', md), True
    return md, False

def normalize_heading_spacing(md: str) -> str:
    prot, blobs = _protect(md)
    lines = prot.splitlines()
    out=[]
    for i, ln in enumerate(lines):
        if _HDR_RE.match(ln):
            if len(out)>=1 and out[-1].strip()!="": out.append("")
            if len(out)>=2 and out[-2].strip()!="": out.append("")
            out.append(ln)
            if i+1<len(lines) and lines[i+1].strip()!="": out.append("")
        else:
            out.append(ln)
    return _unprotect("\n".join(out), blobs)

# ---------- Core render ----------
def _prepare_preprocessed(src: Path, omit_toc: bool, omit_numbering: bool) -> tuple[Path, Path, list, list, list]:
    repo = find_repo_root(src.parent)
    entries = load_map(repo / "pnpmd.map")
    print(f"Using map: {repo/'pnpmd.map'}  (rules={len(entries)})")
    raw = src.read_text(encoding="utf-8").replace("\r\n","\n")

    mapped = apply_mappings_safe(raw, entries)
    stripped, meta, raw_head = extract_percent_block(mapped)
    header_and_inline_ids = collect_all_ids(stripped)

    body, label_map = prose_anchors_and_labels(stripped)
    body = normalize_link_destinations(body)
    span_ids = set(_EMPTY_SPAN_ANCHOR_RE.findall(body))
    body = rewrite_at_tokens(body, label_map=label_map, span_ids=span_ids, header_ids=header_and_inline_ids)
    body = atsec_to_nameref(body)
    body = rewrite_hash_anchors(body)
    body = normalize_heading_spacing(body)

    final_pandoc_md = src.with_suffix(".pandoc.md")
    keep_head = "\n".join(raw_head) + ("\n\n" if raw_head else "")
    final_pandoc_md.write_text(keep_head + body, encoding="utf-8")

    body2 = body
    has_toc_marker = False
    if not omit_toc:
        body2 = insert_toc_after_keywords_content(body2)
        body2, has_toc_marker = replace_toc_marker(body2)

    tmpdir = Path(tempfile.mkdtemp(prefix="pnpmd_"))
    in_tmp  = tmpdir / "in.md"
    text_for_pandoc = keep_head + (body2 if not omit_toc else body)
    in_tmp.write_text(text_for_pandoc, encoding="utf-8")

    meta_args=[]
    if meta.get("title"): meta_args += ["-M", f"title={meta['title']}"]
    for a in meta.get("authors", []): meta_args += ["-M", f"author={a}"]
    if meta.get("date"): meta_args += ["-M", f"date={meta['date']}"]
    meta_args += ["-M","autoSectionLabels=true",
                  "-M","autoSectionLabelsDepth=6",
                #   "-M","autoSectionLabelsPrefix=sec:",
                  "-M","toc-title=Table of Contents"]
    meta_args += ["-M","linkReferences=true"]

    def min_heading_level(md: str) -> Optional[int]:
        lvl=None
        for ln in md.splitlines():
            m=_HDR_RE.match(ln)
            if not m: continue
            n=len(m.group('hash'))
            lvl=n if lvl is None else min(lvl, n)
        return lvl
    shift=0
    mhl=min_heading_level(body2)
    if mhl and mhl>1:
        shift = 1 - mhl
    shift_args = ["--shift-heading-level-by", str(shift)] if shift != 0 else []

    reader = "markdown+tex_math_dollars+raw_tex"
    # FIX: respect omit_toc and omit_numbering here
    toc_flag = [] if (omit_toc or has_toc_marker) else ["--toc"]
    numbering_flag = [] if omit_numbering else ["--number-sections"]

    return in_tmp, final_pandoc_md, meta_args, shift_args, (["--toc-depth=2"] + numbering_flag + toc_flag + ["-f", reader])

def _render_pdf(in_tmp: Path, out_tmp: Path, meta_args: list, shift_args: list, common_args: list, timeout: int):
    cmd = (["docker","run","--rm",
            "--mount", f"type=bind,source={str(in_tmp.parent)},target=/data",
            "-w","/data","pandoc/extra",
            "--standalone", *common_args, *shift_args, *meta_args,
            "--filter","pandoc-crossref",
            "in.md", "-o", out_tmp.name])
    rc=run_visible(cmd,timeout=timeout)
    return rc

def _render_html(in_tmp: Path, out_tmp: Path, meta_args: list, shift_args: list, common_args: list, timeout: int):
    cmd = (["docker","run","--rm",
            "--mount", f"type=bind,source={str(in_tmp.parent)},target=/data",
            "-w","/data","pandoc/extra",
            "--standalone", *common_args, *shift_args, *meta_args,
            "--filter","pandoc-crossref",
            "in.md", "-t","html5", "-o", out_tmp.name])
    rc=run_visible(cmd,timeout=timeout)
    return rc

def render(path: str|None=None, *, timeout=0, omit_toc=False, omit_numbering=False, as_is: bool=False,
           make_pdf: bool=True, make_html: bool=True) -> tuple[Optional[Path], Optional[Path]]:
    src = Path(path) if path else discover_md_in_cwd()
    if not src.exists(): die(f"Missing source: {src}")

    if as_is:
        tmpdir = Path(tempfile.mkdtemp(prefix="pnpmd_"))
        in_tmp  = tmpdir / "in.md"
        in_tmp.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        reader = "markdown+tex_math_dollars+raw_tex"
        toc_flag = [] if omit_toc else ["--toc"]
        numbering_flag = [] if omit_numbering else ["--number-sections"]
        pdf_path = src.with_suffix(".pdf") if make_pdf else None
        html_path = src.with_suffix(".html") if make_html else None

        if make_pdf:
            out_pdf = tmpdir/"out.pdf"
            rc = _render_pdf(in_tmp, out_pdf, [], [], (["--toc-depth=2"]+toc_flag+numbering_flag+["-f", reader]), timeout)
            if rc!=0: die(f"Docker pandoc (PDF) failed (rc={rc})")
            shutil.copy2(out_pdf, pdf_path)

        if make_html:
            out_html = tmpdir/"out.html"
            rc = _render_html(in_tmp, out_html, [], [], (["--toc-depth=2"]+toc_flag+numbering_flag+["-f", reader]), timeout)
            if rc!=0: die(f"Docker pandoc (HTML) failed (rc={rc})")
            shutil.copy2(out_html, html_path)

        if make_pdf: print(f"✅ Wrote {pdf_path}")
        if make_html: print(f"✅ Wrote {html_path}")
        return (pdf_path.resolve() if pdf_path else None, html_path.resolve() if html_path else None)

    # Preprocessed path
    in_tmp, final_pandoc_md, meta_args, shift_args, common_args = _prepare_preprocessed(
        src, omit_toc, omit_numbering
    )
    pdf_path = src.with_suffix(".pdf") if make_pdf else None
    html_path = src.with_suffix(".html") if make_html else None

    if make_pdf:
        out_pdf = in_tmp.parent / "out.pdf"
        rc = _render_pdf(in_tmp, out_pdf, meta_args, shift_args, common_args, timeout)
        if rc!=0: die(f"Docker pandoc (PDF) failed (rc={rc})")
        shutil.copy2(out_pdf, pdf_path)

    if make_html:
        out_html = in_tmp.parent / "out.html"
        rc = _render_html(in_tmp, out_html, meta_args, shift_args, common_args, timeout)
        if rc!=0: die(f"Docker pandoc (HTML) failed (rc={rc})")
        shutil.copy2(out_html, html_path)

    wrote = [str(p) for p in [pdf_path, html_path, final_pandoc_md] if p]
    print("✅ Wrote " + ", ".join(wrote))
    return (pdf_path.resolve() if pdf_path else None, html_path.resolve() if html_path else None)

# ---------- CLI ----------
def main(argv=None):
    ap=argparse.ArgumentParser(
        description="PNPMD → PDF/HTML (Pandoc + crossref; TOC after Keywords; spacing; link/anchor sugar).")
    ap.add_argument("file",nargs="?",help="Markdown file; if omitted, exactly one .md in CWD is required.")
    ap.add_argument("--timeout",type=int,default=0,help="Timeout seconds (0=no timeout).")
    ap.add_argument("--omit-toc",action="store_true",
        help="Do not include a table of contents in the final outputs.")
    ap.add_argument("--omit-numbering",action="store_true",
        help="Disable section numbering in the final outputs.")
    ap.add_argument("--as-is",action="store_true",
        help="Bypass preprocessing and pass the original Markdown directly to Pandoc.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--pdf",action="store_true", help="Render PDF only.")
    g.add_argument("--html",action="store_true", help="Render HTML only.")
    g.add_argument("--all",action="store_true", help="Render both PDF and HTML (default).")
    args=ap.parse_args(argv)

    args.omit_toc = True # always omit TOC

    try:
        make_pdf = True; make_html = True
        if args.pdf:  make_html = False
        if args.html: make_pdf  = False
        # default if none given: --all
        render(args.file, timeout=args.timeout,
               omit_toc=args.omit_toc,
               omit_numbering=args.omit_numbering,
               as_is=args.as_is,
               make_pdf=make_pdf, make_html=make_html)
    except SystemExit:
        raise
    except Exception as e:
        die(str(e))

if __name__=="__main__":
    main()
