# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import env


def load_text(p: Path) -> str:
    text = p.read_text(encoding="utf-8")
    if text.endswith("\n"):
        return text[:-1]
    return text


def write_html(out_html: Path, body_html: str, head_extra: str = "", title: str = ""):
    header = load_text(env.SRC / "header.html")
    footer = load_text(env.SRC / "footer.html")
    coda = load_text(env.SRC / "coda.html")

    doc = "".join(s for s in (header, body_html, footer) if s)

    # head_extra is currently unused; header.html carries <head>/<title>.
    # If you want to reinject per-page <meta>, re-enable the injection here.

    ny = ZoneInfo("America/New_York")
    now = datetime.now(ny)
    offset = now.utcoffset()
    hrs = int(offset.total_seconds() // 3600) if offset else 0
    stamp = f"(built: {now.strftime('%Y-%m-%d %H:%M %Z')} UTC{hrs:+d})"

    if not doc.endswith("\n"):
        doc += "\n"
    doc += stamp
    if coda:
        doc += coda

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(doc, encoding="utf-8")


def render_markdown_file(src: Path, dst_html: Path, title: str):
    md = src.read_text(encoding="utf-8")
    body_html = md

    # We still compute canonical URL even if head_extra isn't injected.
    # If you want them visible, wire head_extra into write_html.
    from env import current_origin

    rel_html = dst_html.relative_to(env.OUT).as_posix()
    origin = current_origin()
    page_url = f"{origin}/{rel_html}"

    head = [
        '<meta charset="utf-8">',
        f'<link rel="canonical" href="{page_url}">',
        '<meta name="robots" content="noindex,follow">',
        f'<meta name="description" content="Rendered Markdown view for {title}">',
    ]
    head_extra = "\n".join(head) + "\n"

    write_html(dst_html, body_html, head_extra=head_extra, title=title)


def write_md_like_page(out_html: Path, md_body: str, title: str | None = None):
    body = md_body.replace("&", "&amp;").replace("<", "&lt;")

    from env import current_origin

    rel_html = out_html.relative_to(env.OUT).as_posix()
    origin = current_origin()
    page_url = f"{origin}/{rel_html}"

    t = title or ""
    head = [
        '<meta charset="utf-8">',
        f'<link rel="canonical" href="{page_url}">',
        '<meta name="robots" content="index,follow">',
        f'<meta name="description" content="{t}">',
    ]
    head_extra = "\n".join(head) + "\n"

    write_html(out_html, body, head_extra=head_extra, title=t or "Index")


def extract_html_body(html_text: str) -> str:
    import re

    m_open = re.search(r"<body[^>]*>", html_text, flags=re.IGNORECASE | re.DOTALL)
    m_close = re.search(r"</body\s*>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if m_open and m_close and m_close.start() > m_open.end():
        return html_text[m_open.end():m_close.start()]
    return html_text
