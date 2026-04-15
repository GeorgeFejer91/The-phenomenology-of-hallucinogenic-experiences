# Preprint

LaTeX manuscript for the psilocybin-vs-brugmansia mixed-methods paper.

## Structure

```
Preprint/
├── main.tex              Master document (preamble + section inputs)
├── introduction.tex      Introduction (skeleton)
├── methods.tex           Methods (complete)
├── results.tex           Results (skeleton)
├── discussion.tex        Discussion (partial — inter-rater audit section complete)
└── references.bib        BibTeX
```

## Build

```
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

## Status

- **methods.tex** — complete, describes the source corpus, original human coding procedure, and the post-hoc LLM-assisted consistency pipeline (stages 1-6), plus the conservative consensus filter.
- **discussion.tex** — inter-rater audit section complete; phenomenology and limitations sections to be written after results are finalised.
- **introduction.tex, results.tex** — skeletons only.

See also `../1.Recoding/FINAL_REPORT.md` and `../1.Recoding/AUDIT_AND_MITIGATIONS.md` for source material feeding the discussion.
