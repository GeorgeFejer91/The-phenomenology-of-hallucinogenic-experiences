# Stage 1 scope — scene individuation only

> **Directive reminder (read [AI_DIRECTIVE.md](../AI_DIRECTIVE.md) first).**
> Stage 1 of this project addresses scene-individuation consistency **only**.
> Do **not** resolve or adjudicate attribute-level disagreements on shared
> scenes (illusion vs incrusted, object-class choices, modal status,
> dynamics). Those reflect rater subjective judgement and are preserved
> in the data unresolved. Attribute-classification consistency is Stage 2,
> deferred.

This document makes explicit what the current pipeline stage is and is **not** measuring.

## The single question Stage 1 answers

> **For every narrative passage in a trip report, did both raters individuate it as a hallucinatory scene?**

That is the only question. The machine-readable version of this scope lives at [STAGE1_SCOPE.json](STAGE1_SCOPE.json) and is loaded by analysis scripts.

## What "individuating a scene" means

Scene **individuation** is the atomic act of pointing to a passage in a trip report and asserting *"a hallucinatory scene happened here."* It is the precursor to every other coding step; before a rater can assign a modality, an object class, an illusion-vs-incrusted tag, a modal status, or a dynamics flag, they must first decide that there is a scene to tag at all.

Individuation is the **more objective** of the two coding steps:

- **Individuation** (Stage 1, the question this project is answering) — *is this passage a hallucinatory scene, yes or no?* A dichotomous decision grounded in the PDF *Guidelines for individuating hallucinations in trip reports*.
- **Classification** (Stage 2, deferred) — *given the scene exists, what kind of hallucination is it?* A multi-attribute taxonomic decision where rater subjective judgement dominates.

Individuation is not perfectly objective — two raters can draw the "scene vs not-scene" line differently — but the disagreement is of a different kind than classification disagreement. The subjective residue in individuation is exactly what Stage 1 measures; classification subjectivity is preserved in the data untouched and deferred to Stage 2.

## Core analytical question — three verdict classes

For every narrative passage **individuated by only one** of the two raters, the pipeline classifies the discrepancy into one of **three** distinct classes. The classes differ in kind and in how they are remedied:

| Verdict | Meaning | Fix |
|---|---|---|
| **MISS** | By this rater's *observed* criterion (the _AB scenes of the same trip), they should have individuated this passage too — they simply overlooked it. | Rater reconciliation (per Project description §7). Instrument untouched. |
| **GRANULARITY** | Raters agree something happened in this narrative region but split it differently: one holistic scene vs several sub-scenes. | **Data-coding rule, immediate.** Default to the more conservative (larger-scope) individuation; the larger scene is the parent; fragments get `parent_scene_id` pointing to it. Downstream analysis can collapse fragments into the parent and pool attributes. |
| **AMBIGUITY — 2a** | The PDF Guidelines under-specify this edge case. Both individuation and omission are defensible; the Guidelines need a clarifying rule. | Deferred. Rewrite the Guidelines with explicit edge-case rules. |
| **AMBIGUITY — 2b** | The passage is phenomenologically real but not a hallucinatory scene under any reasonable reading. It is a different phenomenon (dissociative state, inner imagery, ego-dissolution metaphor, existential belief, altered somatosensory phenomenology, post-trip cognitive residue). | Deferred. Add new non-hallucinatory-scene categories to the taxonomy. |

Classifying every only-one-rater scene as MISS / GRANULARITY / AMBIGUITY-2a / AMBIGUITY-2b is the primary analytical output of Stage 1. The tri-partite framing matters: *granularity is its own class*, not an ambiguity. It has a clean technical fix at the data layer and should not be bundled with unresolved AMBIGUITY cases.

**This is the ONE question the project exists to answer at this stage.** All infrastructure — scene-ID driver suffixes, annotated trip-report pages, visualizations, pretext renderer, Chart.js dashboards — exists in service of it.

### Granularity coding strategy (default rule)

When a solo scene's canonical span overlaps an `_AB` scene or an opposite-rater solo scene in the same trip, the verdict is **GRANULARITY**. Apply this default:

- The larger-scope individuation is the **parent**. Usually the `_AB` shared scene is the parent because both raters agreed at that level of scope; the fragment is the minority split.
- The fragment scene keeps its `scene_id` but sets `parent_scene_id` to the parent's `scene_id`.
- The driver suffix `_FRAG` marks these structurally (already present in the pipeline from the auto-classifier).
- Downstream analyses may either collapse fragments into the parent and pool the attributes of both raters onto the parent scene, OR retain fragments as annotated sub-units. Both views are supported.
- **Default when in doubt:** prefer the conservative (larger-scope) reading. If only one rater fragmented the scene, the other rater's holistic individuation is the canonical scope.

This is a decision rule, not adjudication of rater judgement. The fragment rater's individuation is preserved (scene_id, status, canonical_desc, spans remain untouched); only the canonical scope for downstream aggregation is committed.

## How to judge MISS vs AMBIGUITY — use the shared scenes as the reference

The "truth" against which a solo scene is judged is **not** the PDF Guidelines read in isolation. It is each rater's *demonstrated* application of the PDF Guidelines on the scenes both raters individuated. The shared (`_AB`) scenes are where the two raters converged; they reveal the **operational criterion** each rater was actually using in this coding effort.

### Procedure

1. **Establish each rater's observed criterion** from the `_AB` scenes of the same trip (and same coder pair). These are the empirical expression of "scene" as the two raters, in this effort, actually used the term.
2. **Read the solo scene in context** — narrative passage, rater's canonical excerpt, `stage1_rationale`.
3. **Apply the observed criterion.**
   - If the solo passage matches the kind of content both raters individuated on shared scenes and one rater simply did not annotate it → **MISS**.
   - If the solo passage sits at a kind of content the shared scenes do not establish a clear rule for (ambient amplification, thought/memory/metaphor, somatic transformation, fragment-of-holistic) → **AMBIGUITY**; decide whether flavour 2a (clarify existing rule) or 2b (add new non-scene category).

### Why shared scenes, not the PDF in the abstract

The PDF is not self-interpreting. Two competent raters reading the same PDF can land at different operational criteria; that is exactly how inter-rater disagreement arises. Using each rater's `_AB` scenes as the reference grounds the judgement in *what they actually did*, not in a theoretical ideal. A MISS verdict then means "by the criterion this rater used elsewhere in this trip, they should have individuated this too" — a far more defensible claim than "by my reading of the PDF, they should have."

The driver suffixes are the first-pass expression of this procedure:
- `_FRAG`, `_AMP`, `_AMB`, `_SOMA` are content types where the Guidelines are systematically under-specified — strong AMBIGUITY candidates.
- `_RCL` scenes have no automatic rule fit — these need human MISS-vs-AMBIGUITY adjudication against each trip's own `_AB` scenes.

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
