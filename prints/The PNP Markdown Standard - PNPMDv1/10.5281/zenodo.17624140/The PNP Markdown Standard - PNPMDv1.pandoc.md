% PNPMD Markdown specification — PNPMD v1.0.5
% Max Freet, An M. Rodriguez, Adrien Hale
% November 16, 2025

## One-Sentence Summary

PNPMD is a specification for human-readable-*first*, plain-text, math-aware, markdown documents.


## Abstract

PNPMD is a specification for human-readable-*first*, plain-text, math-aware documents. PNPMD honors Pandoc's flavored markdown, rendered with pdflatex. Uses Pandoc's crossref filter (giving numbered and referenceable equations, figures, tables, etc), and adds some syntax sugar to ease cross-referencing and citations.


## Keywords

plain-text, research format, markdown, mathjax, pandoc, PNPMD


## Introduction

PNPMD is a specification for human-readable-*first*, plain-text, math-aware, markdown documents.

PNPMD:

- provides a complete Markdown structure for mathematically aware documents, with cross-references and citations,
- keeps the format plain-text and human-readable-*first*, and
- avoids noisy LaTeX wrappers and PDF-only workflows


## (Suggested) Structure

* Header
* One-Sentence Summary
* Abstract
* Keywords
* Other body sections
* About Author(s)
* References


### Header

Three lines:

```
% Title
% Author(s)
% Date
```



### One-Sentence Summary

One sentence summarizing the paper.


### Abstract

3–5 sentences: problem $\to$ method $\to$ result $\to$ significance.

No citations or equations.


### Keywords

3–6 topical keywords.


### Other Body Sections (Recommended)

Introduction, Theory/Framework, Derivation, Results, Discussion, Conclusion, Future Work, Appendices.


### About Author(s)

Immediately before References.

A list of authors, with ORCID if available, email if corresponding,
or relevant information.

For example,

* An M. Rodriguez, https://orcid.org/0009-0009-9098-9468, an@preferredframe.com
* Max Freet, max@preferredframe.com


### References

Use DOI links where possible.


## References and Cross-References

Cross-linking, numbering, and citations are produced automatically by Pandoc with the `pandoc-crossref` filter.


## Cross-Reference System and Sugar Substitutions

When using the **PNPMD rendering script**, several syntactic sugars are automatically expanded to Pandoc-compatible links:

- `{#id}` $\to$ `[]{#id}`: For plain prose anchors (no colon).

- `@id` $\to$ `[label](#id)`: If a `[label]{#id}` exists

  - `@id` $\to$ `[@id](#id)`: otherwise

- `[label](@id)` $\to$ `[label](#id)`: Always.

- `[label](@sec:id)` $\to$ `[label](#sec:id)`: Always.

- `@sec:`, `@fig:`, `@eq:`, `@tbl:` $\to$ *(unchanged)*:
  Handled by `pandoc-crossref`.

- bare `#id` $\to$ `[](#id)`: When not inside code blocks,
  headings, or existing links.

Colon-prefixed anchors (e.g., `{#eq:wave}`) are reserved for cross-reference numbering and remain untouched.


## Formatting Rules


### Math

* Inline math: `$...$` (e.g., `$E = mc^2$`)
* Display math:

```
$$
F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu
$$ {#eq:sampleeq}
```

renders as:

$$
F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu
$$ {#eq:sampleeq}

And can be referenced as `@eq:sampleeq`, like so:

See @eq:sampleeq

* MUST NOT use `\[...\]` or `\(...\)` for latex. ONLY USE $..$ and $$..$$ for latex quoting.
* Specify units whenever possible.


### Characters

* UTF-8 required (pdflatex-compatible)
* Unicode symbols allowed only if supported by pdfLaTeX input; otherwise prefer `$...$` or ASCII


### Text Emphasis

Avoid bold/italics/underline unless essential.

Clarity is primary. Don’t pollute the document with unnecessary visual noise.


### Section Separation

* Separate sections with two blank lines
* Never use `---` (horizontal rules) to separate sections
* Do **not** number sections manually; Pandoc handles numbering automatically


## Conclusion

PNPMD is a plain-text specification for mathematically aware documents.

It standardizes minimal syntax, automatic cross-referencing, and deterministic conversion through Pandoc with `pandoc-crossref`.

The format remains simple, portable, and human-readable.

PNPMD: where notation and meaning remain human before machine.


## Corresponding Author

An M. Rodriguez: an@preferredframe.com