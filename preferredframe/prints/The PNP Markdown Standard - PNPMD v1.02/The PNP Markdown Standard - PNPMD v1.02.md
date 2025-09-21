% The PNP Markdown Standard - PNPMD v1.02
% Max Freet, An M. Rodriguez, Adrien Hale
% August 21, 2025

## Abstract

We define the PNP Plain Text Standard PNPMD v1.02 specification.

It is a human-readable *first*, plain-text document format, mathematically aware (using `$...$` and `$$...$$` LaTeX equation blocks) and based on Markdown standards.

The format eases compatibility with naive use of `pandoc`, the default renderer, which converts `.md` to `.pdf`, `.html`, or enhanced `.md` with numbering, links, and TOC.

## One-Sentence Summary

PNPMD v1.02 is a minimal, human-readable *first*, mathematically aware, plain-text Markdown standard for documents.

## Keywords

plain-text, research format, markdown, mathjax, html, PNPMD

## Introduction

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

### Header
Composed of 3 lines:
```

% Title
% Author(s)
% Date

```
- Title must be ascii only.

### Abstract
3–5 sentences: problem → method → result → significance. No citations or equations.

### One-Sentence Summary
One sentence summarizing the paper.

### Keywords
3–6 topical keywords.

### Other body sections (recommended)
Introduction, Theory/Framework, Derivation, Results, Discussion, Conclusion, Next Work, Appendices.

### Corresponding Author
Immediately before References.

### References
- Use DOI links where possible.
- Avoid footnote-style citations; inline references via `@refname` are encouraged.

## References and Cross-References

PNPMD keeps authoring plain text. Cross-linking, numbering, and citations are produced by a minimal formatter step plus Pandoc.

### Citations

- Cite literature with Pandoc’s syntax: `[@key]`, `[@key, pp. 33–35]`.
- The `## References` section is parsed to produce `generated.bib`.
- Invoke Pandoc with: `--citeproc --bibliography=generated.bib -M link-citations=true`.
- Result: citations hyperlink to bibliography entries.
- Do not use footnote-style references. Use inline `[@key]`.

### Anchors

Anchors are declared with a trailing hash on the defining line.
The preprocessor rewrites these into Pandoc attributes.

#### Untyped

```

## Introduction #intro

```

Reference:

```

@intro

```

→ rewritten to `[@pnpmd:intro]`.

If type is omitted, the namespace defaults to `pnpmd`.

#### Typed

```

## Introduction #sec:intro

@sec:intro

![diagram](setup.png)
*Setup* #fig:setup
@fig:setup

$E = mc^2$
#eq:mc2
@eq:mc2

```

Typed forms preserve numbering by type via `pandoc-crossref`:

- `@sec:...` → numbered section (§2.3)
- `@fig:...` → numbered figure (Figure 1)
- `@eq:...`  → numbered equation (1)
- `@tbl:...` → numbered table (Table 1)

#### Inline literal anchor

```

[ #intro ]

```

Displays the raw `#intro` text literally and links to the anchor (no numbering).

### Cross-references

- **Typed references (preferred):**
  `@sec:intro`, `@fig:setup`, `@eq:mc2`, `@tbl:run-a`
  → resolved to numbered cross-references handled by `pandoc-crossref`.

- **Untyped shorthand:**
  `@intro` → `[@pnpmd:intro]`
  → clickable link to the anchor, but not numbered.

### Behavior and constraints

- The preprocessor does **not** alter Pandoc citations `[@key]`.
- Code fences and inline code are left untouched.
- Ids must be ASCII `[A-Za-z0-9_-]`.
- **Type may be omitted** (defaults to `pnpmd`).
- **Id may not be omitted**: references require a concrete identifier to resolve.

## Formatting Rules

### Math
- Inline math: `$...$` (e.g., $E = mc^2$)
- Display math blocks: `$$...$$`
```

$$
F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu
$$

```
- Do not use `\[...\]` or `\(...\)`.
- Always specify units (SI preferred).

### Characters
- UTF-8 required.
- Unicode symbols are allowed only if supported by pdfLaTeX utf8 input; otherwise prefer `$...$` or ASCII.
- No inline math formats other than `$...$` or `$$...$$`.
- No math in abstract or metadata sections.

### Text emphasis
- Avoid bold/italics/underline unless essential.

### Section separation
- Separate sections with two blank lines.
- Never use `---` (horizontal rules) to separate sections.

### Figures
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

### Pre-normalization & mapping
Unwanted characters are stripped and Unicode is mapped to TeX-safe forms using a repo-wide map `pnpmd.map`.

### CRLF→LF normalization
Input is normalized to Unix line endings.

### pnp.md generation
The formatter applies PNPMD shorthands (e.g., `#hash` → `{#pnpmd:hash}`, `@hash` → `@pnpmd:hash`, inline `[ #id ]` → `[ref](#pnpmd:id)`, citation extraction to `generated.bib`).

### Pandoc rendering
`pandoc` (via `pandoc/latex`) produces the final PDF/HTML/Markdown.

### Local render helper
Repository script: `.scripts/renderpdf.sh` defines a `render-pdf` function that:

1. Resolves repo root; finds the first `*.md` (depth ≤ 2).
2. Builds a sed script from `pnpmd.map` (supports literal and regex rules).
3. Normalizes CRLF→LF; applies the map; streams to `pandoc/latex` in Docker.
4. Writes a PDF next to the input (`foo.md` → `foo.pdf`).

> The map (`pnpmd.map`) includes: control-char stripping; NBSP→`~`; punctuation normalization; safe TeX replacements for math symbols; sets ℝ/ℤ/ℕ/ℚ/ℂ; Greek letters, etc.

### Recommended Pandoc options (aligned with PNPMD v1.02)
```

--toc --toc-depth=2
--number-sections
--reference-links
--citeproc --bibliography=generated.bib -M link-citations=true -F pandoc-crossref
--standalone

```
(Apply as appropriate in your Docker invocation or wrapper. HTML builds use the same flags with `-o out.html`.)

## Conclusion

PNPMD v1.02 is a plain-text specification for mathematically aware documents.

## Corresponding author(s)

An Rodriguez: an@preferredframe.com

## References

1. Palma, A., Rodriguez, A. M., & Freet, M. (2025). Point–Not–Point: Deriving Maxwell Electrodynamics from a Scalar Energy Field and Explaining Particle–Wave Duality. DOI:[10.13140/RG.2.2.16877.91368](https://doi.org/10.13140/RG.2.2.16877.91368)

## Changes from v1.001 → v1.02

### Citations clarified
Only `@key` inline form; no footnote-style references.

### Anchors
Defined with shorthand `#id`; referenced with `@id`.
If type omitted, defaults to `pnpmd`.

### Crossref types
`@sec:...`, `@fig:...`, `@eq:...`, `@tbl:...` supported via `pandoc-crossref`.

### Inline shorthand
`[ #id ]` allowed for literal clickable references; no numbering.

### Footnotes
Use `^[text]` or shorthand `^[#id]` + `(#id text)` form.

### Units
Always specify; consistency must be verified by authors.

### Pipeline
Clarified `.scripts/renderpdf.sh` and `pnpmd.map` as reference implementation.

### TOC/numbering
Recommend `--toc --toc-depth=2 --number-sections`.
