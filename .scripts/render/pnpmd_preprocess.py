# pnpmd_preprocess.py

import re
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Set, Dict, List

from pnpmd_util import find_repo_root, load_map

# ---------- Protection of code, math ----------
_FENCE_RE = re.compile(r'(^|\n)(?P<f>```+|~~~+)[^\n]*\n.*?(\n(?P=f)[ \t]*\n|$)', re.DOTALL)
_INLINE_CODE_RE = re.compile(r'(?P<ticks>`+)(?P<body>[^`]*?)\1')
_MATH_BLOCK_RE = re.compile(r'(^|\n)\$\$[\s\S]*?\$\$(?=\s*(\n|$))', re.MULTILINE)
_INLINE_MATH_RE = re.compile(r'(?<!\$)\$(?!\$)(?:\\\$|[^$])+\$(?!\$)')


def _protect(text: str):
    blobs: List[str] = []

    def stash(m):
        i = len(blobs)
        blobs.append(m.group(0))
        return f"\u0000B{i}\u0000"

    text = _FENCE_RE.sub(stash, text)
    text = _INLINE_CODE_RE.sub(stash, text)
    text = _MATH_BLOCK_RE.sub(stash, text)
    text = _INLINE_MATH_RE.sub(stash, text)
    return text, blobs


def _unprotect(text: str, blobs: List[str]):
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
        if not m:
            break
        val = m.group(1).strip()
        if j == 0:
            meta["title"] = val or None
        elif j == 1:
            parts = [
                p.strip()
                for chunk in re.split(r'\band\b|,', val)
                for p in [chunk]
                if p.strip()
            ]
            meta["authors"] = parts
        elif j == 2:
            meta["date"] = val or None
        i += 1
    raw_head = lines[:i]
    stripped = "\n".join(lines[i:]).lstrip("\n") if i else text
    return stripped, meta, raw_head


# ---------- IDs, anchors ----------
_HDR_RE = re.compile(
    r'^(?P<hash>#{1,6})\s+(?P<title>.+?)(?:\s+\{(?P<attrs>[^}]*)\})?\s*$'
)
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
    ids: Set[str] = set()
    for ln in md.splitlines():
        m = _HDR_RE.match(ln)
        if m:
            title = m.group('title')
            attrs = m.group('attrs') or ''
            for mm in _ATTR_ID_RE.finditer(attrs):
                ids.add(mm.group(1))
            ids.add(_auto_slug(title))
        for mm in re.finditer(r'\{#([A-Za-z0-9_:-]+)\}', ln):
            ids.add(mm.group(1))
    return ids


_ATTR_BLOCK_RE = re.compile(r'\{#([A-Za-z0-9_:-]+)\}')
_BRACKETED_LABEL_ANCHOR_RE = re.compile(r'\[([^\]]+?)\]\s*\{#([A-Za-z0-9_:-]+)\}')
_EMPTY_SPAN_ANCHOR_RE = re.compile(r'\[\]\{#([A-Za-z0-9_-]+)\}')


def prose_anchors_and_labels(md: str) -> Tuple[str, Dict[str, str]]:
    prot, blobs = _protect(md)
    out_lines: List[str] = []
    label_map: Dict[str, str] = {}
    for ln in prot.splitlines():
        if _HDR_RE.match(ln):
            out_lines.append(ln)
            continue
        for m in _BRACKETED_LABEL_ANCHOR_RE.finditer(ln):
            label = m.group(1)
            pid = m.group(2)
            if ":" in pid:
                continue
            label_map.setdefault(pid, label)

        def sub_attr(m):
            pid = m.group(1)
            if ":" in pid:
                return m.group(0)
            start = m.start()
            prefix = ln[:start]
            if re.search(r'\[\]\s*$', prefix):
                return m.group(0)
            if re.search(r'\]\s*$', prefix):
                return m.group(0)
            return f'[]{{#{pid}}}'

        ln2 = _ATTR_BLOCK_RE.sub(sub_attr, ln)
        out_lines.append(ln2)
    result = "\n".join(out_lines)
    return _unprotect(result, blobs), label_map


_DEST_NORM_RE = re.compile(
    r'\]\(\s*@(?:(sec|fig|eq|tbl):)?([A-Za-z0-9_-]+)\s*\)'
)


def normalize_link_destinations(md: str) -> str:
    prot, blobs = _protect(md)

    def repl(m):
        kind = m.group(1)
        ident = m.group(2)
        return f'](#{"%s:%s" % (kind, ident) if kind else ident})'

    prot = _DEST_NORM_RE.sub(repl, prot)
    return _unprotect(prot, blobs)


_AT_UNBRACKETED = re.compile(r'(?<![A-Za-z0-9._%+-])@(?P<id>[A-Za-z0-9_-]+)\b')
_AT_BRACKETED = re.compile(r'\[\s*@(?P<id>[A-Za-z0-9_-]+)\s*\]')


def rewrite_at_tokens(
    md: str,
    *,
    label_map: Dict[str, str],
    span_ids: Set[str],
    header_ids: Set[str],
) -> str:
    prot, blobs = _protect(md)
    outs: List[str] = []

    def keep(s: str) -> str:
        i = len(outs)
        outs.append(s)
        return f"\u0000L{i}\u0000"

    def make_link(ident: str, bracketed: bool) -> str:
        if ":" in ident:
            return f'@{ident}' if not bracketed else f'[@{ident}]'
        if ident in label_map:
            return f'[{label_map[ident]}](#{ident})'
        if ident in span_ids or ident in header_ids:
            return f'[@{ident}](#{ident})'
        return f'@{ident}' if not bracketed else f'[@{ident}]'

    prot = _AT_BRACKETED.sub(
        lambda m: keep(make_link(m.group('id'), True)), prot
    )
    prot = _AT_UNBRACKETED.sub(
        lambda m: keep(make_link(m.group('id'), False)), prot
    )
    prot = re.sub(r'\u0000L(\d+)\u0000', lambda mm: outs[int(mm.group(1))], prot)
    return _unprotect(prot, blobs)


_SEC_UNBR = re.compile(r'(?<![A-Za-z0-9._%+-])@sec:([A-Za-z0-9_-]+)\b')
_SEC_BRKT = re.compile(r'\[\s*@sec:([A-Za-z0-9_-]+)\s*\]')


def atsec_to_nameref(md: str) -> str:
    prot, blobs = _protect(md)
    prot = _SEC_BRKT.sub(
        lambda m: f"\\nameref{{sec:{m.group(1)}}}", prot
    )
    prot = _SEC_UNBR.sub(
        lambda m: f"\\nameref{{sec:{m.group(1)}}}", prot
    )
    return _unprotect(prot, blobs)


_BARE_HASH_RE = re.compile(r'(?<![#A-Za-z0-9_{(])#([A-Za-z0-9_:-]+)\b(?!\()')


def rewrite_hash_anchors(md: str) -> str:
    prot, blobs = _protect(md)

    def repl_line(ln: str) -> str:
        if _HDR_RE.match(ln):
            return ln
        return _BARE_HASH_RE.sub(lambda m: f'[](#{m.group(1)})', ln)

    new_lines = [repl_line(ln) for ln in prot.splitlines()]
    prot2 = "\n".join(new_lines)
    return _unprotect(prot2, blobs)


# ---------- TOC, heading spacing ----------
_TOC_MARK_RE = re.compile(r'^\s*\[\[TOC\]\]\s*$', re.MULTILINE)


def insert_toc_after_keywords_content(md: str) -> str:
    if _TOC_MARK_RE.search(md):
        return md
    lines = md.splitlines()
    start_idx = None
    lvl = None
    for i, ln in enumerate(lines):
        m = _HDR_RE.match(ln)
        if not m:
            continue
        title = m.group('title').strip()
        if title.lower().startswith('keywords'):
            start_idx = i
            lvl = len(m.group('hash'))
            break
    if start_idx is None:
        return md
    end = len(lines)
    for j in range(start_idx + 1, len(lines)):
        m = _HDR_RE.match(lines[j])
        if m and len(m.group('hash')) <= lvl:
            end = j
            break
    lines.insert(end, "")
    lines.insert(end + 1, "\n[[TOC]]\n")
    lines.insert(end + 2, "")
    return "\n".join(lines)


def replace_toc_marker(md: str) -> Tuple[str, bool]:
    if _TOC_MARK_RE.search(md):
        return _TOC_MARK_RE.sub(r'\n\\tableofcontents\n', md), True
    return md, False


def normalize_heading_spacing(md: str) -> str:
    prot, blobs = _protect(md)
    lines = prot.splitlines()
    out: List[str] = []
    for i, ln in enumerate(lines):
        if _HDR_RE.match(ln):
            if len(out) >= 1 and out[-1].strip() != "":
                out.append("")
            if len(out) >= 2 and out[-2].strip() != "":
                out.append("")
            out.append(ln)
            if i + 1 < len(lines) and lines[i + 1].strip() != "":
                out.append("")
        else:
            out.append(ln)
    return _unprotect("\n".join(out), blobs)


def _min_heading_level(md: str) -> Optional[int]:
    lvl = None
    for ln in md.splitlines():
        m = _HDR_RE.match(ln)
        if not m:
            continue
        n = len(m.group('hash'))
        lvl = n if lvl is None else min(lvl, n)
    return lvl


# ---------- Core entry ----------
def prepare_preprocessed(
    src: Path,
    *,
    omit_toc: bool,
    omit_numbering: bool,
    toc_depth: int = 2,
    shift_headings: Optional[int] = None,
    auto_shift: bool = True,
    number_offset: Optional[str] = None,
    epub_chapter_level: Optional[int] = None,
):
    """
    Returns:
      in_tmp, final_pandoc_md, meta_args, shift_args, common_args
    """
    repo = find_repo_root(src.parent)
    entries = load_map(repo / "pnpmd.map")
    print(f"Using map: {repo / 'pnpmd.map'}  (rules={len(entries)})")

    raw = src.read_text(encoding="utf-8").replace("\r\n", "\n")

    mapped = apply_mappings_safe(raw, entries)
    stripped, meta, raw_head = extract_percent_block(mapped)
    header_and_inline_ids = collect_all_ids(stripped)

    body, label_map = prose_anchors_and_labels(stripped)
    body = normalize_link_destinations(body)
    span_ids = set(_EMPTY_SPAN_ANCHOR_RE.findall(body))
    body = rewrite_at_tokens(
        body, label_map=label_map, span_ids=span_ids, header_ids=header_and_inline_ids
    )
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
    in_tmp = tmpdir / "in.md"
    text_for_pandoc = keep_head + (body2 if not omit_toc else body)
    in_tmp.write_text(text_for_pandoc, encoding="utf-8")

    # Only propagate title/authors/date; no extra policy defaults.
    meta_args: List[str] = []
    if meta.get("title"):
        meta_args += ["-M", f"title={meta['title']}"]
    for a in meta.get("authors", []):
        meta_args += ["-M", f"author={a}"]
    if meta.get("date"):
        meta_args += ["-M", f"date={meta['date']}"]

    # heading shift: explicit > auto > 0
    shift = 0
    if shift_headings is not None:
        shift = shift_headings
    elif auto_shift:
        mhl = _min_heading_level(body2)
        if mhl and mhl > 1:
            shift = 1 - mhl
    shift_args = ["--shift-heading-level-by", str(shift)] if shift != 0 else []

    reader = "markdown+tex_math_dollars+raw_tex"
    toc_flag: List[str] = [] if (omit_toc or has_toc_marker) else ["--toc"]
    numbering_flag: List[str] = [] if omit_numbering else ["--number-sections"]
    if number_offset is not None and not omit_numbering:
        numbering_flag += ["--number-offset", number_offset]

    toc_opts: List[str] = []
    if not omit_toc:
        toc_opts.append(f"--toc-depth={toc_depth}")

    common_args = toc_opts + numbering_flag + toc_flag + ["-f", reader]
    if epub_chapter_level is not None:
        common_args += ["--epub-chapter-level", str(epub_chapter_level)]

    return in_tmp, final_pandoc_md, meta_args, shift_args, common_args
