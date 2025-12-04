# pnpmd_book.py

from pathlib import Path
from typing import Optional
import re
import shutil

from pnpmd_util import title_from_book_yaml, die, run_visible
from pnpmd_preprocess import prepare_preprocessed
from pnpmd_pandoc import render_pdf, render_html, render_epub


def _split_front_matter(text: str) -> tuple[Optional[str], str]:
    """
    Split a markdown file into (front_matter_text_or_None, body_text).

    Front matter is assumed to be a YAML block starting with '---' at the very
    top of the file and ending at the next line that is exactly '---'.
    """
    lines = text.splitlines()
    if not lines:
        return None, text
    if lines[0].strip() != "---":
        return None, text

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        # malformed, treat as no front matter
        return None, text

    meta_block = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :])
    body = body.lstrip("\n")
    return meta_block, body


def _title_from_front_matter(meta_block: str, base_title: str = "") -> Optional[str]:
    """
    Extract 'title: ...' from a YAML-like front matter block and optionally strip
    a leading '<base_title> - ' / '<base_title> – ' / '<base_title>: ' prefix.
    """
    m = re.search(r"^title\s*:\s*(.+)$", meta_block, re.MULTILINE)
    if not m:
        return None
    title = m.group(1).strip()
    # strip wrapping quotes
    if (title.startswith('"') and title.endswith('"')) or (
        title.startswith("'") and title.endswith("'")
    ):
        title = title[1:-1].strip()

    if base_title:
        # build a case-insensitive prefix pattern: ^<base_title>\s*[-–:]\s*
        pattern = re.compile(
            rf"^{re.escape(base_title)}\s*[-–:]\s*",
            re.IGNORECASE,
        )
        title = pattern.sub("", title, count=1).strip()

    return title or None


def _extract_cover_image(yaml_text: str) -> Optional[str]:
    """
    Extract 'cover-image: ...' from book.yml (scalar, one-line value).
    Returns the raw value (URL or path) or None if not present.
    """
    m = re.search(r"^cover-image\s*:\s*(.+)$", yaml_text, re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    # strip simple quotes
    if (val.startswith('"') and val.endswith('"')) or (
        val.startswith("'") and val.endswith("'")
    ):
        val = val[1:-1].strip()
    return val or None


# def _strip_conflicting_keys(yaml_text: str) -> str:
#     """
#     Remove keys that may cause weird template output like 'truetrue'
#     when printed by the HTML template (e.g. booleans).

#     We strip:
#       - autoSectionLabels
#       - autoSectionLabelsDepth
#       - linkReferences
#     """
#     lines = yaml_text.replace("\r\n", "\n").splitlines()
#     out: list[str] = []
#     skip = {"autosectionlabels", "autosectionlabelsdepth", "linkreferences"}

#     for line in lines:
#         raw = line.lstrip()
#         if not raw or raw.startswith("#"):
#             out.append(line)
#             continue
#         key = raw.split(":", 1)[0].strip()
#         if key.lower() in skip:
#             continue
#         out.append(line)

#     return "\n".join(out)


def _normalize_book_yaml_as_front_matter(yaml_text: str) -> str:
    """
    Ensure book.yml content becomes a valid top-level YAML metadata block
    with explicit '---' ... '---' delimiters, after stripping conflicting keys.
    """
    # yaml_text = _strip_conflicting_keys(yaml_text)
    lines = yaml_text.replace("\r\n", "\n").splitlines()

    if not lines:
        return "---\n---\n\n"

    # case 1: already starts with '---'
    if lines[0].strip() == "---":
        has_closing = any(line.strip() == "---" for line in lines[1:])
        if not has_closing:
            lines.append("---")
        return "\n".join(lines) + "\n\n"

    # case 2: no leading '---' => wrap in a block
    return "---\n" + "\n".join(lines) + "\n---\n\n"


def render_book_yaml(
    src: Path,
    *,
    timeout: int = 0,
    omit_toc: bool = False,
    omit_numbering: bool = False,
    make_pdf: bool = True,
    make_html: bool = True,
    make_epub: bool = False,
    toc_depth: int = 2,
    shift_headings: Optional[int] = None,
    auto_shift: bool = True,
    number_offset: Optional[str] = None,
    epub_chapter_level: Optional[int] = None,
) -> tuple[Optional[Path], Optional[Path]]:
    """
    Book mode:
      - src is a *.yml / *.yaml book metadata file
      - collect all *.md in that directory (alphabetically)
      - build one big <Title>.md with:
          * book.yml as a single YAML metadata block (properly delimited, without
            conflicting keys like autoSectionLabels/linkReferences)
          * for each chapter .md:
              - strip its own front matter
              - inject '# <chapter title>' from that front matter (or filename)
              - append body
      - produce <Title>.pdf / <Title>.html / <Title>.epub
    """
    if not src.exists():
        die(f"Missing source: {src}")

    book_dir = src.parent
    base = title = title_from_book_yaml(src)

    print(f"Book mode: metadata={src.name}  title={title!r}  base={base}")

    big_md_path = book_dir / f"{base}.md"

    md_files = sorted(
        p
        for p in book_dir.iterdir()
        if p.is_file()
        and p.suffix.lower() == ".md"
        and p.name != f"{base}.md"
        and p.name != f"{base}.pandoc.md"
    )
    if not md_files:
        die(f"No .md files found in {book_dir}")

    # 1) book-level YAML front matter (from book.yml), normalized and cleaned
    raw_yaml_text = src.read_text(encoding="utf-8")
    cover_value = _extract_cover_image(raw_yaml_text)
    yaml_block = _normalize_book_yaml_as_front_matter(raw_yaml_text)

    with big_md_path.open("w", encoding="utf-8") as f:
        f.write(yaml_block)

        # 2) each chapter .md becomes '# title' + body (front matter stripped)
        for p in md_files:
            chapter_raw = p.read_text(encoding="utf-8").replace("\r\n", "\n")
            meta_block, body = _split_front_matter(chapter_raw)

            chapter_title: Optional[str] = None
            if meta_block is not None:
                chapter_title = _title_from_front_matter(meta_block, base)
            if not chapter_title:
                chapter_title = p.stem

            f.write(f"# {chapter_title}\n\n")
            f.write(body)
            f.write("\n\n")

    print(f"✅ Built combined markdown {big_md_path}")

    in_tmp, final_pandoc_md, meta_args, shift_args, common_args = prepare_preprocessed(
        big_md_path,
        omit_toc=omit_toc,
        omit_numbering=omit_numbering,
        toc_depth=toc_depth,
        shift_headings=shift_headings,
        auto_shift=auto_shift,
        number_offset=number_offset,
        epub_chapter_level=epub_chapter_level,
    )

    # If cover-image was specified in book.yml, ensure a local copy exists in
    # the tmp dir (where pandoc runs) and rewrite the metadata to point to it.
    if cover_value:
        tmpdir = in_tmp.parent

        local_name: Optional[str] = None
        cv = cover_value

        if cv.startswith("http://") or cv.startswith("https://"):
            # Download via curl to tmpdir/cover.ext
            from urllib.parse import urlparse

            parsed = urlparse(cv)
            ext = Path(parsed.path).suffix or ".jpg"
            dest = tmpdir / ("cover" + ext)
            rc = run_visible(["curl", "-L", "-o", str(dest), cv])
            if rc != 0:
                die(f"curl failed for cover-image: {cv}")
            local_name = dest.name
        else:
            # Treat as filesystem path (absolute or relative to book_dir)
            src_img = Path(cv)
            if not src_img.is_absolute():
                src_img = book_dir / src_img
            if not src_img.exists():
                die(f"cover-image not found: {src_img}")
            dest = tmpdir / src_img.name
            shutil.copy2(src_img, dest)
            local_name = dest.name

        # Rewrite the cover-image metadata in in_tmp YAML to point to local_name
        if local_name:
            text = in_tmp.read_text(encoding="utf-8")
            lines = text.splitlines()
            if lines and lines[0].strip() == "---":
                # Walk inside the front matter until the closing '---'
                for i in range(1, len(lines)):
                    if lines[i].strip() == "---":
                        break
                    stripped = lines[i].lstrip()
                    if stripped.startswith("cover-image"):
                        indent = lines[i][: len(lines[i]) - len(stripped)]
                        lines[i] = f"{indent}cover-image: {local_name}"
                        break
                text = "\n".join(lines)
                in_tmp.write_text(text, encoding="utf-8")

    pdf_path = big_md_path.with_suffix(".pdf") if make_pdf else None
    html_path = big_md_path.with_suffix(".html") if make_html else None
    epub_path = big_md_path.with_suffix(".epub") if make_epub else None

    if make_pdf:
        out_pdf = in_tmp.parent / "out.pdf"
        rc = render_pdf(in_tmp, out_pdf, meta_args, shift_args, common_args, timeout)
        if rc != 0:
            die(f"Docker pandoc (PDF) failed (rc={rc})")
        shutil.copy2(out_pdf, pdf_path)

    if make_html:
        out_html = in_tmp.parent / "out.html"
        rc = render_html(in_tmp, out_html, meta_args, shift_args, common_args, timeout)
        if rc != 0:
            die(f"Docker pandoc (HTML) failed (rc={rc})")
        shutil.copy2(out_html, html_path)

    if make_epub:
        out_epub = in_tmp.parent / "out.epub"
        rc = render_epub(in_tmp, out_epub, meta_args, shift_args, common_args, timeout)
        if rc != 0:
            die(f"Docker pandoc (EPUB) failed (rc={rc})")
        shutil.copy2(out_epub, epub_path)

    wrote = [
        str(p)
        for p in [pdf_path, html_path, epub_path, big_md_path, final_pandoc_md]
        if p
    ]
    print("✅ Wrote " + ", ".join(wrote))

    return (
        pdf_path.resolve() if pdf_path else None,
        html_path.resolve() if html_path else None,
    )
