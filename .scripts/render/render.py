#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
from typing import Optional

from pnpmd_preprocess import prepare_preprocessed
from pnpmd_pandoc import render_pdf, render_html, render_epub
from pnpmd_book import render_book_yaml
from pnpmd_util import discover_md_in_cwd, die


def render(
    path: str | None = None,
    *,
    timeout: int = 0,
    omit_toc: bool = False,
    omit_numbering: bool = False,
    as_is: bool = False,
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
    Main render entrypoint.

    Returns: (pdf_path or None, html_path or None)
    """
    src = Path(path) if path else discover_md_in_cwd()
    if not src.exists():
        die(f"Missing source: {src}")

    # --- Book mode (YAML metadata) ---
    if src.suffix.lower() in (".yml", ".yaml"):
        return render_book_yaml(
            src,
            timeout=timeout,
            omit_toc=omit_toc,
            omit_numbering=omit_numbering,
            make_pdf=make_pdf,
            make_html=make_html,
            make_epub=make_epub,
            toc_depth=toc_depth,
            shift_headings=shift_headings,
            auto_shift=auto_shift,
            number_offset=number_offset,
            epub_chapter_level=epub_chapter_level,
        )

    # --- Normal (single .md) mode ---
    if as_is:
        from tempfile import mkdtemp
        import shutil

        tmpdir = Path(mkdtemp(prefix="pnpmd_"))
        in_tmp = tmpdir / "in.md"
        in_tmp.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

        reader = "markdown+tex_math_dollars+raw_tex"

        toc_flag: list[str] = [] if omit_toc else ["--toc"]
        numbering_flag: list[str] = [] if omit_numbering else ["--number-sections"]
        if number_offset is not None and not omit_numbering:
            numbering_flag += ["--number-offset", number_offset]

        toc_opts: list[str] = []
        if not omit_toc:
            toc_opts.append(f"--toc-depth={toc_depth}")

        shift_args: list[str] = []
        if shift_headings is not None:
            shift_args = ["--shift-heading-level-by", str(shift_headings)]

        common_args = toc_opts + numbering_flag + toc_flag + ["-f", reader]
        if epub_chapter_level is not None:
            common_args += ["--epub-chapter-level", str(epub_chapter_level)]

        pdf_path = src.with_suffix(".pdf") if make_pdf else None
        html_path = src.with_suffix(".html") if make_html else None
        epub_path = src.with_suffix(".epub") if make_epub else None

        if make_pdf:
            out_pdf = tmpdir / "out.pdf"
            rc = render_pdf(in_tmp, out_pdf, [], shift_args, common_args, timeout)
            if rc != 0:
                die(f"Docker pandoc (PDF) failed (rc={rc})")
            shutil.copy2(out_pdf, pdf_path)

        if make_html:
            out_html = tmpdir / "out.html"
            rc = render_html(in_tmp, out_html, [], shift_args, common_args, timeout)
            if rc != 0:
                die(f"Docker pandoc (HTML) failed (rc={rc})")
            shutil.copy2(out_html, html_path)

        if make_epub:
            out_epub = tmpdir / "out.epub"
            rc = render_epub(in_tmp, out_epub, [], shift_args, common_args, timeout)
            if rc != 0:
                die(f"Docker pandoc (EPUB) failed (rc={rc})")
            shutil.copy2(out_epub, epub_path)

        if make_pdf:
            print(f"✅ Wrote {pdf_path}")
        if make_html:
            print(f"✅ Wrote {html_path}")
        if make_epub:
            print(f"✅ Wrote {epub_path}")

        return (
            pdf_path.resolve() if pdf_path else None,
            html_path.resolve() if html_path else None,
        )

    # Preprocessed path
    in_tmp, final_pandoc_md, meta_args, shift_args, common_args = prepare_preprocessed(
        src,
        omit_toc=omit_toc,
        omit_numbering=omit_numbering,
        toc_depth=toc_depth,
        shift_headings=shift_headings,
        auto_shift=auto_shift,
        number_offset=number_offset,
        epub_chapter_level=epub_chapter_level,
    )

    pdf_path = src.with_suffix(".pdf") if make_pdf else None
    html_path = src.with_suffix(".html") if make_html else None
    epub_path = src.with_suffix(".epub") if make_epub else None

    import shutil

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

    wrote = [str(p) for p in [pdf_path, html_path, epub_path, final_pandoc_md] if p]
    print("✅ Wrote " + ", ".join(wrote))

    return (
        pdf_path.resolve() if pdf_path else None,
        html_path.resolve() if html_path else None,
    )


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="PNPMD → PDF/HTML/EPUB (Pandoc + crossref; TOC after Keywords; spacing; link/anchor sugar)."
    )
    ap.add_argument(
        "file",
        nargs="?",
        help="Markdown or YAML (book) file; if omitted, exactly one .md in CWD is required.",
    )
    ap.add_argument(
        "--timeout", type=int, default=0, help="Timeout seconds (0=no timeout)."
    )
    ap.add_argument(
        "--omit-toc",
        action="store_true",
        help="Do not include a table of contents in the final outputs.",
    )
    ap.add_argument(
        "--omit-numbering",
        action="store_true",
        help="Disable section numbering in the final outputs.",
    )
    ap.add_argument(
        "--as-is",
        action="store_true",
        help="Bypass preprocessing and pass the original Markdown directly to Pandoc.",
    )
    ap.add_argument("--toc-depth", type=int, default=2, help="TOC depth for pandoc.")
    ap.add_argument(
        "--shift-headings",
        type=int,
        help="Explicit pandoc --shift-heading-level-by value (overrides auto in preprocessed mode).",
    )
    ap.add_argument(
        "--no-auto-shift",
        action="store_true",
        help="Disable automatic heading-level shifting in preprocessed mode.",
    )
    ap.add_argument(
        "--number-offset",
        type=str,
        help="Value for pandoc --number-offset (e.g. '0', '1', '1.2').",
    )
    ap.add_argument(
        "--epub-chapter-level",
        type=int,
        help="Heading level to start new EPUB chapters (pandoc --epub-chapter-level).",
    )

    g = ap.add_mutually_exclusive_group()
    g.add_argument("--pdf", action="store_true", help="Render PDF only.")
    g.add_argument("--html", action="store_true", help="Render HTML only.")
    ap.add_argument(
        "--epub",
        action="store_true",
        help="Also render EPUB in addition to PDF/HTML selection.",
    )
    g.add_argument(
        "--all", action="store_true", help="Render both PDF and HTML (default)."
    )

    args = ap.parse_args(argv)

    try:
        make_pdf = args.pdf or args.all
        make_html = args.html or args.all
        make_epub = args.epub or args.all

        render(
            args.file,
            timeout=args.timeout,
            omit_toc=args.omit_toc,
            omit_numbering=args.omit_numbering,
            as_is=args.as_is,
            make_pdf=make_pdf,
            make_html=make_html,
            make_epub=make_epub,
            toc_depth=args.toc_depth,
            shift_headings=args.shift_headings,
            auto_shift=not args.no_auto_shift,
            number_offset=args.number_offset,
            epub_chapter_level=args.epub_chapter_level,
        )
    except SystemExit:
        raise
    except Exception as e:
        die(str(e))


if __name__ == "__main__":
    main()
