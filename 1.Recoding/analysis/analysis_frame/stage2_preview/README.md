# stage2_preview — attribute-bearing artefacts (DESCRIPTIVE ONLY)

**Read `AI_DIRECTIVE.md` at the repo root first.**

Everything in this folder is a convenience view over each rater's
attribute tags. Stage 1 measures *scene-individuation* reliability only;
attribute-level reliability (Stage 2) is explicitly deferred. These
files report what each rater tagged without adjudicating.

## Files

| file | value semantics | rows × cols | notes |
|---|---|---|---|
| `attributes_count.csv` / `.xlsx` | number of raters (0/1/2) who tagged this scene with this item | 305 × 68 | primary, information-preserving |
| `attributes_any.csv` / `.xlsx` | 1 if ≥1 rater tagged it, else 0 | 305 × 68 | convenience (≥1 rater) |
| `attributes_consensus.csv` / `.xlsx` | 1 if BOTH raters tagged it, else 0 | 305 × 68 | convenience (consensus filter) |
| `trip_attributes_count.csv` / `.xlsx` | 0/1/2 for trip-level items | 40 × 38 | separate grain — never duplicate into scene sheets |
| `attributes_column_map.csv` | column_name → taxonomy lookup | 92 × 10 | use this when parsing column names programmatically |

## Column naming

`attr__{L1_slug}__{L2_slug}__{L3_slug}`.
- Double underscore separates levels.
- Single underscore only appears inside a slug.
- Parsing: `colname.removeprefix("attr__").split("__")`.

## Carried-context columns on every wide sheet

`scene_id, trip_id, substance, block, rater_status, stage1_verdict,
verdict_flavour` — so substance-level proportions don't require joining
back to `scenes.csv`.

## What these sheets DO NOT give you

- Reliability of attribute choices on a given scene. Two raters disagreeing
  about illusion-vs-incrusted-object is recorded in `attributes_count` as
  each having tagged their own preferred leaf; neither choice is endorsed.
- Consensus on modal-status / dynamics / object-class. Those require
  Stage-2 adjudication (out of scope).
