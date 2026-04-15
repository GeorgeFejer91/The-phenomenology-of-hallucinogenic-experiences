# Preprint

LaTeX manuscript for the psilocybin-vs-brugmansia mixed-methods paper.

## Build

From the repository root:

```
build_preprint.bat
```

The compiled PDF is written to `Preprint/build/main.pdf` and copied to `Preprint/main.pdf` for easy access. Build artifacts (`.aux`, `.log`, `.bbl`, `.fls`, `.fdb_latexmk`, `.synctex.gz`) live in `Preprint/build/` and are gitignored.

`build_preprint.bat` uses `latexmk` if available, otherwise falls back to a `pdflatex` / `bibtex` / `pdflatex` / `pdflatex` sequence.

## Layer structure

```
Preprint/
├── main.tex              Master document (preamble + section inputs)
├── references.bib        BibTeX entries
├── sections/
│   ├── introduction.tex  Introduction (skeleton)
│   ├── methods.tex       Methods (complete)
│   ├── results.tex       Results (skeleton)
│   └── discussion.tex    Discussion (partial)
├── figures/              Manuscript figures (currently empty placeholder)
└── build/                Compile outputs (gitignored)
```

A writer can locate any prose file two clicks under `Preprint/`. Editing one section means opening one file in `sections/` without touching the master document or the preamble.

## Status

- **methods.tex** — complete, describes the source corpus, original human coding procedure, and the post-hoc LLM-assisted consistency pipeline (stages 1-6), plus the conservative consensus filter.
- **discussion.tex** — inter-rater audit section complete; phenomenology and limitations sections to be written after results are finalised.
- **introduction.tex, results.tex** — skeletons only.

See also `../1.Recoding/FINAL_REPORT.md` and `../1.Recoding/AUDIT_AND_MITIGATIONS.md` for source material feeding the discussion.
