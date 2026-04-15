# The phenomenology of hallucinogenic experiences

A psilocybin-vs-brugmansia mixed-methods comparison built from human-coded trip reports, with a two-stage scene-individuation and attribute-coding framework.

## Quick build

| Target | Command |
|---|---|
| Preprint PDF | `build_preprint.bat` |

The build reads `Preprint/main.tex`, compiles via `latexmk` (or a `pdflatex` / `bibtex` fallback), and writes the final PDF to `Preprint/main.pdf`.

## Repository layout

| Folder / file | Purpose |
|---|---|
| `Preprint/` | LaTeX manuscript (writing surface). See `Preprint/README.md`. |
| `1.Recoding/` | Stage 1 inter-rater consistency pipeline, scope docs, audit, final report. |
| `Coded Spread Sheets (All trips)/`, `Coding Instructions/` | Human-coding source corpus and coder-instruction PDFs. |
| `Brugmansia_source_coding/`, `Psilocybin_source_coding/` | Per-substance original coding worksheets. |
| `docs/` | GitHub Pages site (annotated trips, visualizations). |
| `AI_DIRECTIVE.md`, `AGENTS.md`, `CLAUDE.md` | Stage 1 directive — read before doing rater work. |

## Stage 1 directive

**Stage 1 measures inter-rater consistency on SCENE INDIVIDUATION only.** Read [AI_DIRECTIVE.md](AI_DIRECTIVE.md) before any rater work. Attribute-classification consistency is Stage 2 and is deferred.

## Substance colour palette (fixed)

| Substance | Hex | Name |
|---|---|---|
| brugmansia | `#1b4332` | forest dark green |
| psilocybin | `#9b111e` | ruby red |
