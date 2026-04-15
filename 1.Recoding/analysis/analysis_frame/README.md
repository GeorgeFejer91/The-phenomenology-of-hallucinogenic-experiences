# Analysis-ready data frame bundle

*Stage 1 of the phenomenology-of-hallucinations pipeline — see
`../../AI_DIRECTIVE.md` at the repo root.*

This bundle re-shapes the canonical pipeline outputs (`1.Recoding/data/*.csv`)
into a single analytic scaffold where `scene_id` is the primary cross-reference
key, per-trip denominators are pre-computed, and the taxonomy hierarchy is
exposed for nested-level queries.

## Files (top level — Stage-1-clean)

| file | grain | rows | notes |
|---|---|---|---|
| `scenes.csv`/`.xlsx` | per canonical scene_id | 305 | all metadata + Stage-1 verdict + per-trip denominators |
| `scenes_x_raters.csv`/`.xlsx` | per (scene × rater who individuated it) | 485 | natural grain for rater-effect models |
| `codes.csv`/`.xlsx` | per (scene × rater × item) coding event | 1481 | long-format with scene-context joined |
| `trip_totals.csv`/`.xlsx` | per trip | 40 | scene-count + verdict-count + per-L1 prevalence |
| `taxonomy.csv`/`.xlsx` | per taxonomy item | 147 | pass-through convenience copy |
| `agreement_flags.csv`/`.xlsx` | per (scene × item) | 664 | AGREE / A_ONLY / B_ONLY at any taxonomy depth |
| `rater_style.csv`/`.xlsx` | per (trip × rater) | 80 | per-rater tagging density / leaf preferences |

**CSV is canonical.** XLSX is a convenience mirror with coloured verdict
cells, freeze-panes and auto-filter. If the two ever disagree, trust
the CSV.

## Stage-1 / Stage-2 boundary

This top-level bundle only exposes **scene individuation** state (Stage 1).
It reports each rater's tags but never adjudicates attribute disagreements.

Attribute-bearing wide matrices live separately under `stage2_preview/` and
are **descriptive only** — they present what each rater tagged without
implying that any single coding is "correct". Stage 2 (attribute-level
reliability) is deferred per `AI_DIRECTIVE.md`.

## Key columns on `scenes.csv`

- `scene_id`: unique code. Shared scenes end in `_AB` (one code, both
  raters individuated). Solo scenes end in rater-specific driver
  suffixes (`_A_RCL`, `_B_AMP`, etc.).
- `rater_status` ∈ `{both, only_A, only_B}`.
- `stage1_verdict` ∈ `{CONVERGENT, MISS, GRANULARITY, AMBIGUITY}`, with
  `verdict_flavour` ∈ `{2a, 2b}` for AMBIGUITY.
- `n_scenes_in_trip`, `n_convergent_in_trip`, `n_scenes_rater_A_in_trip`,
  `n_scenes_rater_B_in_trip`: denominators for proportion analyses.
- `scene_word_count`, `trip_word_count`: for per-1000-words normalisation.
- `parent_scene_id`: for GRANULARITY fragments, points to the larger
  canonical parent scene under which the fragment pools for downstream
  attribute analysis.

## Example queries

### A. "Proportion of individuated scenes (any rater) that include an animal-class hallucination, per substance, normalised per trip"

1. Start from `scenes.csv` joined with `stage2_preview/attributes_any.csv` on `scene_id`.
2. Sum any column matching `attr__visual_hallucination__animal*` per scene → a `has_animal` 0/1 flag.
3. Group by `trip_id`: `n_animal_scenes / n_scenes_in_trip` → per-trip rate.
4. Group by `substance`: take the mean (or median, or full distribution) of per-trip rates.

```python
import pandas as pd, re
scenes = pd.read_csv("scenes.csv")
attrs  = pd.read_csv("stage2_preview/attributes_any.csv")
animal_cols = [c for c in attrs.columns if c.startswith("attr__visual_hallucination__animal")]
attrs["has_animal"] = (attrs[animal_cols].sum(axis=1) > 0).astype(int)
df = scenes.merge(attrs[["scene_id", "has_animal"]], on="scene_id")
per_trip = df.groupby(["substance", "trip_id"]).agg(
    n_scenes=("scene_id", "count"),
    n_animal=("has_animal", "sum"),
).reset_index()
per_trip["rate"] = per_trip["n_animal"] / per_trip["n_scenes"]
per_trip.groupby("substance")["rate"].describe()
```

### B. "Same, but restricted to convergent scenes (raters agree on scene existence)"

Add `df = df[df["rater_status"] == "both"]` before the group-by, and use
`n_convergent_in_trip` as the denominator.

### C. "Same, but restricted to convergent scenes WHERE BOTH RATERS TAGGED IT AS ANIMAL"

Replace `attributes_any.csv` with `attributes_consensus.csv`. This filters
attribute agreement on top of scene-existence agreement.

### D. "Rate per 1000 words of narrative"

Divide `n_animal` by `trip_word_count / 1000` instead of scene count.

## Taxonomy hierarchy (nested analyses)

Every attribute column on the wide matrices is named
`attr__{L1_slug}__{L2_slug}__{L3_slug}`. Missing levels are omitted;
double-underscore is the separator; single-underscore only appears inside
a slug. To sum at any level, grep by prefix:

| cut | regex |
|---|---|
| all Visual-hallucination items | `^attr__visual_hallucination__` |
| all Visual-hallucination Animals | `^attr__visual_hallucination__animal__` |
| all Visual-hallucination Animal Insects | `^attr__visual_hallucination__animal__insect$` |

`stage2_preview/attributes_column_map.csv` gives the full lookup
(column_name → item_id, level_1/2/3, depth, is_leaf) for programmatic use.

## Regenerating the bundle

From `1.Recoding/scripts/`:

```sh
py 18_build_analysis_frame.py
```

The script is idempotent and purely additive — it never modifies the
canonical `data/*.csv` files.
