# CLAUDE.md — auto-loaded project memory

This file is loaded by Claude Code at the start of every session in this
repository. Its only purpose is to make the project's standing directive
impossible to miss.

---

## READ THIS FIRST: [AI_DIRECTIVE.md](AI_DIRECTIVE.md)

> **Stage 1 of this project measures inter-rater consistency on SCENE
> INDIVIDUATION only.** The atomic question is: *for every narrative passage,
> did both raters individuate it as a hallucinatory scene?*
>
> **Core analytical question** — for every scene only one rater individuated:
>
> 1. **MISS** — did the other rater overlook a clearly hallucinatory passage they should have coded per the PDF Guidelines (rater-compliance gap)?
> 2. **AMBIGUITY** — do the PDF rules not cleanly cover this edge case (instruction-design gap)?
>
> The rater's subjective judgement about what is a hallucinatory scene is the **primary data**. Preserve it. Do not silently drop individuations that "shouldn't have been coded". Do not override attribute tags on shared scenes (Stage 2, deferred).

---

## Do and don't

- **Do** treat each rater's individuation as primary data.
- **Do** classify only-one-rater scenes via the driver taxonomy (`_AB / _FRAG / _AMP / _AMB / _SOMA / _RCL`) — this is *diagnostic, not resolution*.
- **Do** preserve both raters' attribute tags on shared scenes as-is.
- **Don't** resolve "illusion vs incrusted vs detached vs immersive" or any other attribute-level disagreement. That is Stage 2, out of scope.
- **Don't** quietly filter out scenes one rater individuated because they seem to violate the PDF rules. Classify the driver instead.
- **Don't** merge shared scenes with only-one-rater scenes based on your own reading of the narrative. The rater's own individuation span is the source of truth.

## Key files

| File | Purpose |
|---|---|
| [AI_DIRECTIVE.md](AI_DIRECTIVE.md) | Canonical directive. Read first. |
| [AGENTS.md](AGENTS.md) | Same directive, agent-file convention. |
| [1.Recoding/STAGE1_SCOPE.json](1.Recoding/STAGE1_SCOPE.json) | Machine-readable scope. Load programmatically if a script needs to check scope. |
| [1.Recoding/STAGE1_SCOPE.md](1.Recoding/STAGE1_SCOPE.md) | Human-readable scope companion. |
| [1.Recoding/RULES.md](1.Recoding/RULES.md) | Data-structure rules (scene-ID conventions, column schemas). |
| [1.Recoding/AUDIT_AND_MITIGATIONS.md](1.Recoding/AUDIT_AND_MITIGATIONS.md) | The 8-source audit of rater discrepancy and mitigation strategies. |
| [1.Recoding/FINAL_REPORT.md](1.Recoding/FINAL_REPORT.md) | Pipeline synthesis, regenerable. |
| `Coding Instructions/*.pdf` | The original coder instructions. Reference these when judging MISS vs AMBIGUITY. |

## Current pipeline order

```
scripts/01_extract_taxonomy.py       → data/taxonomy.csv
scripts/02_load_codings.py           → data/raw_codings.csv
scripts/03_extract_narratives.py     → data/trips/*.txt + trips_index.csv
scripts/04_build_worksheets.py       → worksheets/*.md (adjudication scaffolds)
scripts/05_consolidate.py            → data/scenes.csv, data/codes.csv, data/agreement_flags.csv, data/rater_style.csv  (D4 scope-layer normalisation + D5 dedup applied here)
scripts/06_patterns_report.py        → FINAL_REPORT.md
scripts/07_binning.py                → analysis/scene_bins.csv + bins_summary.csv  (derived view; does NOT modify scenes.csv)
scripts/08_validate.py               → integrity + cross-condition sanity checks
scripts/09_consensus_view.py         → analysis/consensus_codes.csv  (scene-level AGREE filter)
scripts/10_stage1_driver_classifier  → rewrites scene_ids with driver suffix  (_AB / _FRAG / _AMP / _AMB / _SOMA / _RCL)
scripts/11_render_annotated_trips.py → annotated_trips/*.html (static)
scripts/12_visualize_drivers.py      → figures/*.png (static)
scripts/13_export_trip_json.py       → annotated_trips_pretext/data/*.json
scripts/14_build_github_pages_site.py → docs/index.html (single-page trip report view)
scripts/15_build_visualizations_page.py → docs/visualizations.html (Chart.js dashboards)
```

Canonical data is `data/*.csv`. `analysis/*.csv` is derived, regenerable, non-canonical. `docs/*.html` is the GitHub Pages output.

## Substance colour palette (fixed)

| Substance | Hex | Name |
|---|---|---|
| brugmansia | `#1b4332` | forest dark green |
| psilocybin | `#9b111e` | ruby red |

Use these consistently whenever the two substances are directly compared.

---

## One-line reminder — copy into code headers

```
# Stage 1: scene-individuation consistency only. For every only-one-rater
# scene, classify MISS vs AMBIGUITY. Preserve rater subjective judgement.
# Do not resolve attribute-level disagreement. See AI_DIRECTIVE.md.
```
