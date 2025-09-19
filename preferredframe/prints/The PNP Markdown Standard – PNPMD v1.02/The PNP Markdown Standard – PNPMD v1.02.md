% The PNP Markdown Standard – PNPMD v1.02
% Max Freet, An M. Rodríguez, Adrien Hale
% August 21, 2025

## Abstract

We define the PNP Plain Text Standard PNPMD v1.02 specification.

It is a human-readable *first*, plain-text document format, mathematically aware (using `$...$` and `$$...$$` LaTeX equation blocks) and based on Markdown standards.

The format eases compatibility with naive use of `pandoc`, the default renderer, which converts `.md` to `.pdf`, `.html`, or enhanced `.md` with numbering, links, and TOC.

## One-Sentence Summary

PNPMD v1.02 is a minimal, human-readable *first*, mathematically aware, plain-text Markdown standard for documents.

## Keywords

plain-text, research format, markdown, mathjax, html, PNPMD

PNPMD v1.02 provides a minimal yet complete Markdown structure for mathematically aware documents.
It keeps the format simple and human-readable *first*: a straight ASCII-text document.
It avoids noisy LaTeX wrappers and PDF-only workflows.
Goals: reproducibility, portability, unambiguous interpretation.

In summary:

- human-readable *first*
- clear, simple, LaTeX, math-aware text
- ASCII art
- even tikki figures

## (Suggested) Structure

- Header
- Abstract
- One-Sentence Summary
- Keywords
- Other body sections
- Corresponding Author
- References

**Header:**
```

% Title
% Author(s)
% Date

```

**Abstract:** 3–5 sentences: problem → method → result → significance. No citations or equations.

**One-Sentence Summary:** one sentence summarizing the paper.

**Keywords:** 3–6 topical keywords.

**Other body sections (recommended):** Introduction, Theory/Framework, Derivation, Results, Discussion, Conclusion, Next Work, Appendices.

**Corresponding Author:** immediately before References.

**References:**
- Use DOI links where possible.
- Avoid footnote-style citations; inline references via `@refname` are encouraged.

## References and Cross-References

PNPMD keeps authoring *plain* text files. For free goodies: cross-linking, numbering, and citations are produced by a minimal formatter step and Pandoc.

### Citations
- Use `@key` or `[@key, pp. 33–35]` inline.
- The `## References` (or `## (Suggested) References`) section is parsed to produce `generated.bib`.
- Pandoc is invoked with `--citeproc --bibliography=generated.bib -M link-citations=true`.
- Result: citations are hyperlinked to bibliography entries.
- PNPMD avoids footnote-style references (e.g. “^1 … 1. Author, …”); inline `@key` is always preferred for clarity.

### Anchors and cross-references
- Authors declare anchors with shorthand:
```

## A Section Title #sec\:short

!\[diagram.png]
*This is the setup* #fig\:setup

```
- Refer in text with:
```

As seen in @sec\:short …
As shown in @fig\:setup …

```
- Cross-reference types supported (via `pandoc-crossref`):
- `@sec:…` → numbered section (§2.3)
- `@fig:…` → numbered figure (Figure 1)
- `@eq:…` → numbered equation ((3))
- `@tbl:…` → numbered table (Table 1)

### Inline shorthand
- `[ #id ]` in PNPMD is allowed as a simple inline anchor reference.
- It renders as a clickable link showing `#id` literally.
- To show **numbers**, always use `@id` crossrefs (not `[ #id ]`).

### Footnotes
- Use Pandoc’s inline form:
```

This is a claim.^\[Supporting note.]

```
- PNPMD shorthand is allowed:
- `^[#fn1]` in text
- `(#fn1 Footnote text here.)` elsewhere
- Formatter rewrites shorthand into standard Pandoc numbered footnotes.

### Units
- Always specify units (SI preferred).
- Example: $R = 5.29\times 10^{-11}\,\mathrm{m}$.
- **Important:** PNPMD formatter does not verify consistency of units; authors are responsible for correctness.

## Formatting Rules

**Math**
- Inline math: `$...$` (e.g., $E = mc^2$)
- Display math blocks: `$$...$$`
```

$$
F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu
$$

```
- Do **not** use `\[...\]` or `\(...\)`.
- Always specify units (SI preferred).

**Characters**
- UTF-8 required.
- Some Unicode symbols are allowed only if supported by pdfLaTeX utf8 input; otherwise prefer `$...$` or ASCII.
- No inline math formats other than `$...$` or `$$...$$`.
- No math in abstract or metadata.

**Text emphasis**
- Avoid bold/italics/underline unless essential.

**Section separation**
- Separate sections with two blank lines.
- Never use `---` (horizontal rules) to separate sections.

**Figures**
- Optional; ASCII diagrams are allowed. Example:
```

Core
(  o  )
\   /
\_/

```

## Example Section

Theory
Let $U:\mathbb{R}^3\times\mathbb{R} \to \mathbb{R}$ be the scalar energy field.
$$ F = d(*dU) $$
Source-free dynamics:
$$ dF = 0, \quad d\!\star F = 0 $$
Energy density and Poynting vector:
$$
u = \frac{\varepsilon_0}{2}(E^2 + c^2 B^2), \quad \mathbf{S} = \frac{1}{\mu_0} \mathbf{E} \times \mathbf{B}
$$

Results
For TE$_{11}$ mode geometry:
$$
\alpha = \frac{\kappa}{2\pi^2 R} \cdot \frac{e^2}{\varepsilon_0}
$$
Numerical value: $\alpha \approx 6.41\,\mathrm{eV}$.

## Rendering & Pipeline (reference implementation)

PNPMD ships with a simple local renderer to preview PDFs while keeping sources human-first.

- **Pre-normalization & mapping:** unwanted characters are stripped and Unicode is mapped to TeX-safe forms using a repo-wide map `pnpmd.map`.
- **CRLF→LF normalization:** input is normalized to Unix line endings.
- **pandoc.md generation:** the formatter applies PNPMD shorthands (e.g., `#hash` → `{#pnpref:hash}`, `@hash` → `@pnpref:hash`, inline `[ #id ]` → `[ref](#pnpref:id)`, citation extraction to `generated.bib`).
- **Pandoc rendering:** `pandoc` (via `pandoc/latex`) produces the final PDF/HTML/Markdown.

### Local render helper

Repository script: `.scripts/renderpdf.sh` defines a `render-pdf` function that:

1) Resolves repo root; finds the first `*.md` (depth ≤ 2).
2) Builds a sed script from `pnpmd.map` (supports literal and regex rules).
3) Normalizes CRLF→LF; applies the map; streams to `pandoc/latex` in Docker.
4) Writes a PDF next to the input (`foo.md` → `foo.pdf`).

> The map (`pnpmd.map`) includes: control-char stripping; NBSP→`~`; punctuation normalization; safe TeX replacements for math symbols; sets ℝ/ℤ/ℕ/ℚ/ℂ; Greek letters, etc.

**Recommended Pandoc options (aligned with PNPMD v1.02):**
```

\--toc --toc-depth=2
\--number-sections
\--reference-links
\--citeproc --bibliography=generated.bib -M link-citations=true
-F pandoc-crossref
\--standalone

```
(Apply as appropriate in your Docker invocation or wrapper. HTML builds use the same flags with `-o out.html`.)

## Conclusion

PNPMD v1.02 is a plain-text specification for mathematically aware documents.

## Next Work

A PNPMD v2 could extend this with optional metadata for ORCID, funding, and cross-links between related preprints.

## Corresponding author(s)

An Rodriguez: an@preferredframe.com

## References

1. Palma, A., Rodríguez, A. M., & Freet, M. (2025). Point–Not–Point: Deriving Maxwell Electrodynamics from a Scalar Energy Field and Explaining Particle–Wave Duality. DOI:[10.13140/RG.2.2.16877.91368](https://doi.org/10.13140/RG.2.2.16877.91368)

---

## Changes from v1.001 → v1.02

- **Citations clarified:** only `@key` inline form; no footnote-style references.
- **Anchors:** defined with shorthand `#id`; referenced with `@id`.
- **Crossref types:** `@sec:…`, `@fig:…`, `@eq:…`, `@tbl:…` supported via `pandoc-crossref`.
- **Inline shorthand:** `[ #id ]` allowed for literal clickable references; no numbering.
- **Footnotes:** use `^[text]` or shorthand `^[#id]` + `(#id text)` form.
- **Units:** always specify; consistency must be verified by authors.
- **Pipeline:** clarified `.scripts/renderpdf.sh` and `pnpmd.map` as reference implementation.
- **TOC/numbering:** recommend `--toc --toc-depth=2 --number-sections`.
