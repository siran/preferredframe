# -*- coding: utf-8 -*-
import json
from pathlib import Path
from urllib.parse import quote

import yaml

import env
from config import MIRROR_EXTS
from dates import month_year, scholar_date, iso_date_str, _to_datetime
from gitutil import is_gitignored
from provenance import iter_provenance_files, normalize_authors, fmt_author
from templating import write_html, extract_html_body


def crumb_link(parts: list[str]) -> str:
    html = ['<nav class="breadcrumbs">']
    html.append('<a href="/">🏠 Home</a>')
    base = ""
    for label in parts:
        base = base.rstrip("/") + "/" + quote(label)
        html.append(" / ")
        html.append(f'<a href="{base}/">📂 {label}</a>')
    html.append("</nav>")
    return "".join(html)


def build_article_pages(preferred_journal: str):
    origin = env.current_origin()

    records = []
    for prov in iter_provenance_files():
        data = yaml.safe_load(prov.read_text(encoding="utf-8")) or {}

        rel_parts = prov.relative_to(env.ROOT).parts
        if len(rel_parts) < 4:
            continue

        top = rel_parts[0]
        stem = rel_parts[1]
        doi_prefix = rel_parts[2]
        doi_suffix = rel_parts[3]

        journal = (data.get("journal") or "").strip()

        pf_block = data.get("parsed_from_pnpmd") or {}

        title = (data.get("title") or pf_block.get("title") or "") or ""
        abstract = (data.get("abstract") or pf_block.get("abstract") or "") or ""
        kws = (data.get("keywords") or pf_block.get("keywords") or []) or []
        onesent = (
            data.get("one_sentence_summary")
            or pf_block.get("one_sentence_summary")
            or pf_block.get("one_sentence")
            or ""
        )
        onesent = (onesent or "").strip()

        authors = normalize_authors(data.get("authors") or pf_block.get("authors"))

        date_norm = (
            data.get("publication_date")
            or data.get("creation_date")
            or pf_block.get("date")
            or ""
        )

        zenodo = data.get("zenodo") or {}
        doi = (data.get("doi") or zenodo.get("doi") or "") or ""
        concept = (data.get("concept_doi") or zenodo.get("concept_doi") or "") or ""

        permalink = (data.get("permalink") or "").strip()
        site_block = data.get("site") or {}
        html_canonical = (
            site_block.get("html_canonical")
            or site_block.get("permalink")
            or permalink
            or ""
        ).strip()

        assets = (data.get("assets") or {})
        canonical_assets = (data.get("canonical_assets") or {})
        artifacts = (data.get("artifacts") or {})

        md_name = (artifacts.get("md") or artifacts.get("main") or None)
        html_name = (artifacts.get("html_name") or None)
        pmd_name = (artifacts.get("pandoc_md_name") or artifacts.get("pandoc_md") or None)
        add_old = artifacts.get("additional") or {}
        if not html_name:
            html_name = add_old.get("html")
        if not pmd_name:
            pmd_name = add_old.get("pandoc_md")

        if not md_name and artifacts.get("md_url"):
            md_name = Path(artifacts["md_url"]).name
        if not html_name and artifacts.get("html_url"):
            html_name = Path(artifacts["html_url"]).name
        if not pmd_name and artifacts.get("pandoc_md_url"):
            pmd_name = Path(artifacts["pandoc_md_url"]).name

        assets_pdf = (
            artifacts.get("pdf_url")
            or (assets.get("pdf") or {}).get("url")
            or (canonical_assets.get("pdf") or {}).get("url")
            or ""
        )

        references_doi = data.get("references_doi") or pf_block.get("references_doi") or []
        if not isinstance(references_doi, list):
            references_doi = [references_doi]

        records.append(
            {
                "prov": prov,
                "top": top,
                "stem": stem,
                "doi_prefix": doi_prefix,
                "doi_suffix": doi_suffix,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "onesent": onesent,
                "kws": kws,
                "date": date_norm,
                "doi": doi,
                "concept": concept,
                "assets_pdf": assets_pdf,
                "md_name": md_name,
                "html_name": html_name,
                "pmd_name": pmd_name,
                "html_canonical": html_canonical,
                "references_doi": references_doi,
                "journal": journal,
            }
        )

    json.dumps(records, indent=2, default=str)

    if not records:
        return

    groups: dict[tuple[str, str], list[dict]] = {}
    for r in records:
        key = (r["top"], r["stem"])
        groups.setdefault(key, []).append(r)

    for (top, stem), items in groups.items():
        def sort_key(it):
            dt = _to_datetime(it["date"])
            return dt or it["prov"].stat().st_mtime

        versions = sorted(items, key=sort_key, reverse=True)
        latest = versions[0]

        # --- version pages ---
        for it in versions:
            src = it["prov"].parent
            out_dir = env.OUT / top / stem / it["doi_prefix"] / it["doi_suffix"]
            out_dir.mkdir(parents=True, exist_ok=True)

            for f in src.iterdir():
                if f.is_file() and f.suffix.lower() in MIRROR_EXTS:
                    dst = env.OUT / f.relative_to(env.ROOT)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(f.read_bytes())

            local_md = (
                f"/{(env.OUT / src.joinpath(it['md_name']).relative_to(env.ROOT)).relative_to(env.OUT).as_posix()}"
                if it["md_name"]
                else None
            )
            local_html = (
                f"/{(env.OUT / src.joinpath(it['html_name']).relative_to(env.ROOT)).relative_to(env.OUT).as_posix()}"
                if it["html_name"]
                else None
            )
            local_pmd = (
                f"/{(env.OUT / src.joinpath(it['pmd_name']).relative_to(env.ROOT)).relative_to(env.OUT).as_posix()}"
                if it["pmd_name"]
                else None
            )

            html_body = ""
            if it["html_name"] and src.joinpath(it["html_name"]).exists():
                htxt = src.joinpath(it["html_name"]).read_text(encoding="utf-8")
                html_body = extract_html_body(htxt)

            top_links = []
            if local_md:
                top_links.append(f'<a href="{local_md}">Markdown</a>')
            if it["assets_pdf"]:
                top_links.append(f'<a href="{it["assets_pdf"]}">PDF</a>')
            if local_pmd:
                top_links.append(f'<a href="{local_pmd}">Preprocessed MD</a>')

            breadcrumbs = crumb_link([top, stem, it["doi_prefix"], it["doi_suffix"]])
            files_list = []
            prov_local = (
                f"/{(env.OUT / it['prov'].relative_to(env.ROOT)).relative_to(env.OUT).as_posix()}"
            )
            if local_html:
                files_list.append(
                    f'<li><a href="{local_html}">{it["html_name"]}</a></li>'
                )
            if local_md:
                files_list.append(
                    f'<li><a href="{local_md}">{it["md_name"]}</a></li>'
                )
            files_list.append(f'<li><a href="{prov_local}">provenance.yaml</a></li>')
            if it["assets_pdf"]:
                files_list.append(
                    f'<li><a href="{it["assets_pdf"]}">PDF</a></li>'
                )
            files_ul = "<ul>" + "".join(files_list) + "</ul>"

            display_authors = it["authors"]
            authors_html = ", ".join(
                filter(None, (fmt_author(a) for a in display_authors))
            )

            body = []
            body.append("<main class='paper'>")
            body.append(breadcrumbs)
            body.append(f"<h1>{it['title']}</h1>")
            if authors_html:
                body.append(f"<p class='authors'>{authors_html}</p>")
            body.append(
                f"<p class='publine'>{preferred_journal} — {month_year(it['date'])}</p>"
            )
            body.append("<p class='links'>" + " · ".join(top_links) + "</p>")

            if it["onesent"]:
                body.append("<h2>One-Sentence Summary</h2>")
                body.append(f"<p>{it['onesent']}</p>")

            if it["abstract"]:
                body.append("<h2>Abstract</h2>")
                body.append(f"<p>{it['abstract']}</p>")

            body.append("<h2>Files</h2>")
            body.append(files_ul)

            if html_body:
                body.append("<h2>Article</h2>")
                body.append(html_body)

            if it["references_doi"]:
                body.append("<h2>References (DOI)</h2>")
                refs_items = []
                for ref_url in it["references_doi"]:
                    ref_url = (ref_url or "").strip()
                    if not ref_url:
                        continue
                    refs_items.append(f'<li><a href="{ref_url}">{ref_url}</a></li>')
                if refs_items:
                    body.append("<ul>" + "".join(refs_items) + "</ul>")

            body.append("</main>")

            stem_seg = quote(stem, safe="")
            version_url = f"{origin}/{top}/{stem_seg}/{it['doi_prefix']}/{it['doi_suffix']}/"

            head = []
            head.append('<meta charset="utf-8">')
            head.append(f'<link rel="canonical" href="{version_url}">')
            if it["assets_pdf"]:
                head.append(
                    f'<link rel="alternate" type="application/pdf" href="{it["assets_pdf"]}">'
                )
            head.append('<meta name="robots" content="index,follow">')
            if it["title"]:
                head.append(
                    f'<meta name="citation_title" content="{it["title"]}">'
                )
            for a in display_authors:
                nm = a.get("name", "")
                if nm:
                    head.append(
                        f'<meta name="citation_author" content="{nm}">'
                    )
            if it["date"]:
                head.append(
                    f'<meta name="citation_publication_date" content="{scholar_date(it["date"])}">'
                )
            head.append(
                f'<meta name="citation_journal_title" content="{preferred_journal}">'
            )
            if it["assets_pdf"]:
                head.append(
                    f'<meta name="citation_pdf_url" content="{it["assets_pdf"]}">'
                )
            if it["doi"]:
                head.append(
                    f'<meta name="citation_doi" content="{it["doi"]}">'
                )
            desc = it["abstract"] or it["onesent"] or it["title"]
            if desc:
                head.append(f'<meta name="description" content="{desc}">')
                head.append(
                    f'<meta property="og:description" content="{desc}">'
                )
            head.append('<meta property="og:type" content="article">')
            head.append(f'<meta property="og:title" content="{it["title"]}">')
            head.append(f'<meta property="og:url" content="{version_url}">')

            authors_ld = []
            for a in display_authors:
                nm = a.get("name", "").strip()
                oc = a.get("orcid", "").strip()
                if not nm:
                    continue
                ent = {"@type": "Person", "name": nm}
                if oc:
                    ent["sameAs"] = [_orcid_url(oc)] if not oc.startswith("http") else [oc]
                authors_ld.append(ent)
            enc = []
            if it["assets_pdf"]:
                enc.append(
                    {
                        "@type": "MediaObject",
                        "contentUrl": it["assets_pdf"],
                        "encodingFormat": "application/pdf",
                    }
                )
            article_ld = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": it["title"],
                "author": authors_ld or [{"@type": "Person", "name": "Unknown"}],
                "datePublished": iso_date_str(it["date"]),
                "isPartOf": {
                    "@type": "Periodical",
                    "name": preferred_journal,
                },
                "url": version_url,
            }
            if enc:
                article_ld["encoding"] = enc
            if it["doi"]:
                article_ld["sameAs"] = [
                    f"https://doi.org/{it['doi'].split('/')[-1]}"
                ]
            head.append(
                '<script type="application/ld+json">'
                + json.dumps(article_ld, ensure_ascii=False)
                + "</script>"
            )
            head_extra = "\n".join(head) + "\n"
            body_html = "\n".join(body)

            write_html(out_dir / "index.html", body_html, head_extra=head_extra)

            alias_dir = env.OUT / top / "doi" / it["doi_prefix"] / it["doi_suffix"]
            alias_dir.mkdir(parents=True, exist_ok=True)
            write_html(alias_dir / "index.html", body_html, head_extra=head_extra)

            mirror_dir = env.OUT / it["prov"].parent.relative_to(env.ROOT)
            mirror_dir.mkdir(parents=True, exist_ok=True)
            write_html(mirror_dir / "index.html", body_html, head_extra=head_extra)

        # --- stem page (latest) ---
        it = latest
        src = it["prov"].parent
        stem_out = env.OUT / it["top"] / it["stem"]
        stem_out.mkdir(parents=True, exist_ok=True)

        for f in src.iterdir():
            if f.is_file() and f.suffix.lower() in MIRROR_EXTS:
                dst = env.OUT / f.relative_to(env.ROOT)
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(f.read_bytes())

        local_md = (
            f"/{(env.OUT / src.joinpath(it['md_name']).relative_to(env.ROOT)).relative_to(env.OUT).as_posix()}"
            if it["md_name"]
            else None
        )
        local_html = (
            f"/{(env.OUT / src.joinpath(it['html_name']).relative_to(env.ROOT)).relative_to(env.OUT).as_posix()}"
            if it["html_name"]
            else None
        )
        local_pmd = (
            f"/{(env.OUT / src.joinpath(it['pmd_name']).relative_to(env.ROOT)).relative_to(env.OUT).as_posix()}"
            if it["pmd_name"]
            else None
        )

        html_body = ""
        if it["html_name"] and src.joinpath(it["html_name"]).exists():
            htxt = src.joinpath(it["html_name"]).read_text(encoding="utf-8")
            html_body = extract_html_body(htxt)

        breadcrumbs = crumb_link([it["top"], it["stem"]])

        same_family: list[dict] = []
        for v in versions:
            if it["concept"] and v["concept"] == it["concept"]:
                same_family.append(v)
            elif not it["concept"] and not v["concept"]:
                same_family.append(v)

        versions_list = []
        for v in same_family:
            ver_url = f"/{v['top']}/{v['stem']}/{v['doi_prefix']}/{v['doi_suffix']}/"
            doi_disp = f"{v['doi_prefix']}/{v['doi_suffix']}"
            date_disp = v["date"] or ""
            versions_list.append(
                f"<li>{date_disp} — <a href='{ver_url}'>{doi_disp}</a></li>"
            )
        versions_ul = "<ul>" + "".join(versions_list) + "</ul>" if versions_list else ""

        files_list = []
        prov_local = (
            f"/{(env.OUT / it['prov'].relative_to(env.ROOT)).relative_to(env.OUT).as_posix()}"
        )
        if local_html:
            files_list.append(
                f'<li><a href="{local_html}">{it["html_name"]}</a></li>'
            )
        if local_md:
            files_list.append(
                f'<li><a href="{local_md}">{it["md_name"]}</a></li>'
            )
        files_list.append(f'<li><a href="{prov_local}">provenance.yaml</a></li>')
        if it["assets_pdf"]:
            files_list.append(
                f'<li><a href="{it["assets_pdf"]}">PDF</a></li>'
            )
        files_ul = "<ul>" + "".join(files_list) + "</ul>"

        top_links = []
        if local_md:
            top_links.append(f'<a href="{local_md}">Markdown (latest)</a>')
        if it["assets_pdf"]:
            top_links.append(f'<a href="{it["assets_pdf"]}">PDF (latest)</a>')
        if local_pmd:
            top_links.append(f'<a href="{local_pmd}">Preprocessed MD</a>')

        display_authors = it["authors"]
        authors_html = ", ".join(
            filter(None, (fmt_author(a) for a in display_authors))
        )

        body = []
        body.append("<main class='paper'>")
        body.append(breadcrumbs)
        body.append(f"<h1>{it['title']}</h1>")
        if authors_html:
            body.append(f"<p class='authors'>{authors_html}</p>")
        body.append(
            f"<p class='publine'>{preferred_journal} — {month_year(it['date'])}</p>"
        )
        body.append("<p class='links'>" + " · ".join(top_links) + "</p>")
        if versions_ul:
            body.append("<h2>Versions</h2>")
            body.append(versions_ul)
        body.append("<h2>Files (latest)</h2>")
        body.append(files_ul)

        if it["onesent"]:
            body.append("<h2>One-Sentence Summary</h2>")
            body.append(f"<p>{it['onesent']}</p>")

        if it["abstract"]:
            body.append("<h2>Abstract</h2>")
            body.append(f"<p>{it['abstract']}</p>")

        if html_body:
            body.append("<h2>Article (latest)</h2>")
            body.append(html_body)

        if it["references_doi"]:
            body.append("<h2>References (DOI)</h2>")
            refs_items = []
            for ref_url in it["references_doi"]:
                ref_url = (ref_url or "").strip()
                if not ref_url:
                    continue
                refs_items.append(f'<li><a href="{ref_url}">{ref_url}</a></li>')
            if refs_items:
                body.append("<ul>" + "".join(refs_items) + "</ul>")
        body.append("</main>")

        stem_seg = quote(it["stem"], safe="")
        stem_url = f"{origin}/{it['top']}/{stem_seg}/"
        head = []
        head.append('<meta charset="utf-8">')
        head.append(f'<link rel="canonical" href="{stem_url}">')
        if it["assets_pdf"]:
            head.append(
                f'<link rel="alternate" type="application/pdf" href="{it["assets_pdf"]}">'
            )
        head.append('<meta name="robots" content="index,follow">')
        if it["title"]:
            head.append(
                f'<meta name="citation_title" content="{it["title"]}">'
            )
        for a in display_authors:
            nm = a.get("name", "")
            if nm:
                head.append(
                    f'<meta name="citation_author" content="{nm}">'
                )
        if it["date"]:
            head.append(
                f'<meta name="citation_publication_date" content="{scholar_date(it["date"])}">'
            )
        head.append(
            f'<meta name="citation_journal_title" content="{preferred_journal}">'
        )
        if it["assets_pdf"]:
            head.append(
                f'<meta name="citation_pdf_url" content="{it["assets_pdf"]}">'
            )
        if it["doi"]:
            head.append(
                f'<meta name="citation_doi" content="{it["doi"]}">'
            )
        desc = it["abstract"] or it["onesent"] or it["title"]
        if desc:
            head.append(f'<meta name="description" content="{desc}">')
            head.append(
                f'<meta property="og:description" content="{desc}">'
            )
        head.append('<meta property="og:type" content="article">')
        head.append(f'<meta property="og:title" content="{it["title"]}">')
        head.append(f'<meta property="og:url" content="{stem_url}">')

        authors_ld = []
        for a in display_authors:
            nm = a.get("name", "").strip()
            oc = a.get("orcid", "").strip()
            if not nm:
                continue
            ent = {"@type": "Person", "name": nm}
            if oc:
                ent["sameAs"] = [_orcid_url(oc)] if not oc.startswith("http") else [oc]
            authors_ld.append(ent)
        enc = []
        if it["assets_pdf"]:
            enc.append(
                {
                    "@type": "MediaObject",
                    "contentUrl": it["assets_pdf"],
                    "encodingFormat": "application/pdf",
                }
            )
        article_ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": it["title"],
            "author": authors_ld or [{"@type": "Person", "name": "Unknown"}],
            "datePublished": iso_date_str(it["date"]),
            "isPartOf": {
                "@type": "Periodical",
                "name": preferred_journal,
            },
            "url": stem_url,
        }
        if enc:
            article_ld["encoding"] = enc
        if it["doi"]:
            article_ld["sameAs"] = [
                f"https://doi.org/{it['doi'].split('/')[-1]}"
            ]
        head.append(
            '<script type="application/ld+json">'
            + json.dumps(article_ld, ensure_ascii=False)
            + "</script>"
        )
        head_extra = "\n".join(head) + "\n"

        write_html(
            stem_out / "index.html", "\n".join(body), head_extra=head_extra, title=it["title"]
        )


def _orcid_url(v: str) -> str:
    v = (v or "").strip()
    if not v:
        return ""
    if v.startswith("http"):
        return v
    import re

    m = re.search(r"(\d{4}-\d{4}-\d{4}-\d{3}[0-9Xx])", v)
    return f"https://orcid.org/{m.group(1).upper()}" if m else ""
