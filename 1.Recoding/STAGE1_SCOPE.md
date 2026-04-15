# Stage 1 scope — scene individuation only

This document makes explicit what the current pipeline stage is and is **not** measuring.

## The single question Stage 1 answers

> **For every narrative passage in a trip report, did both raters individuate it as a hallucinatory scene?**

That is the only question. The machine-readable version of this scope lives at [STAGE1_SCOPE.json](STAGE1_SCOPE.json) and is loaded by analysis scripts.

## Why this matters

The *Guidelines for individuating hallucinations in trip reports.pdf* names the atomic unit of coding: **the hallucinatory scene**. It instructs:

> *"Every time you read a trip report, you have to wonder: how many hallucinatory scenes are there in this trip report?"*

Agreement at this atomic unit is logically prior to any other reliability measure. Two raters cannot be said to disagree *about* a scene if they haven't both individuated one to begin with.

## What Stage 1 does measure

- Whether rater A individuated a given passage as a scene.
- Whether rater B individuated the same passage as a scene.
- Whether their individuations refer to the same narrative passage (overlap of `canonical_span_start / canonical_span_end`).
- **Why** only-one-rater individuations happened — the six-category driver taxonomy encoded as `scene_id` suffixes (`_AB / _FRAG / _AMP / _AMB / _SOMA / _RCL`).

## What Stage 1 explicitly does **not** measure

The PDF taxonomy provides many *attribute tags* that each rater then attaches to each individuated scene. These attribute decisions are **not** adjudicated, normalised, or resolved by Stage 1. They are recorded in `data/codes.csv` and `data/agreement_flags.csv` for transparency only.

Attribute categories left untouched at Stage 1:

| Attribute group | Example leaves | Why out of scope |
|---|---|---|
| Type of visual alteration | illusion / incrusted / detached / immersive | Rater's subjective judgement call on ambient-versus-object-centred alteration |
| Visual-hallucination object class | Human / Artefact / Animal / Plant / Inorganic entity / Extraordinary entity | Rater's taxonomic classification of the hallucinated content |
| Modality | Visual / Auditory / Tactile / Olfactory / Gustatory / Nonsensory | Rater's choice of modality tag for the same scene |
| Modal status | Possible-probable / Possible-improbable / Impossible | Rater's judgement on event plausibility |
| Dynamics | Object constancy / No object constancy | Rater's observation about scene dynamics |

If rater A tags a scene as "illusion" and rater B tags the same scene as "hallucination of an incrusted object", that is not a Stage-1 concern. Stage 1 only cares that they both individuated the scene.

Similarly, if one rater codes a passage scene-level while the other codes the same passage as a trip-level item (e.g. one codes an anthropomorphised object as an illusion, the other as domain-specific-violation at trip-level), Stage 1 treats each rater's placement as their honest reading of the passage. The one who put it at scene-level individuated a scene; the one who put it at trip-level did not. That is the disagreement we record.

## Driver suffixes: diagnosis, not resolution

The six scene-ID driver suffixes classify *why* only-one-rater individuations happened. They are diagnostic:

- `_AB` — both raters individuated. Chronological shared id.
- `_FRAG` — one rater's sub-scene of the other's holistic scene. Parent linked via `parent_scene_id`.
- `_AMP` — ambient perceptual amplification without a discrete object; a Case-2 borderline.
- `_AMB` — thought / memory / metaphor content that one rater read as a hallucination.
- `_SOMA` — self-transformation or interoceptive content.
- `_RCL` — no automatic match; likely genuine miss; flagged for human reconciliation.

A scene flagged with any of these stays in the dataset. The suffix tells downstream analyses *why* only one rater saw it as a scene, nothing more.

## When attribute consistency gets addressed

A future Stage 2 analysis would ask: *given that both raters individuated a scene (`_AB`), how often do they attach the same attribute tags to it?* That work is out of scope here. The framework already supports it — `data/agreement_flags.csv` carries per-(scene, item) AGREE / A_ONLY / B_ONLY flags for every attribute on every shared scene — but it is not resolved or interpreted at Stage 1.

## Practical implication for the conservative-consensus filter

The conservative-consensus filter applied at analysis time has two nested levels, corresponding to Stage 1 and the eventual Stage 2:

1. **Scene level (Stage 1):** keep only scenes where `rater_status == 'both'`. This is the filter the Project description paper-writing plan should use. It is PDF-faithful (implements the Case-2 rule at the dataset level) and does not conflate attribute disagreements into the individuation question.

2. **Attribute level (Stage 2, future):** further filter to `agreement == 'AGREE'` on shared scenes. This is only applicable once Stage 2 is explicitly opened.

Until Stage 2 is started, analyses of Stage-1-filtered data should retain *both raters' attribute tags* side-by-side and treat attribute divergence as content for the paper, not as noise to be cleaned.
