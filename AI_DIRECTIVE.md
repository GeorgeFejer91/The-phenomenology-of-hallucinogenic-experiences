# AI DIRECTIVE — read this first, every session

> This file is the canonical statement of the project's goal. Every AI
> agent working on this repository — Claude, Cursor, Copilot, any future
> tool — should read this before acting. The directive is repeated in
> [CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md), in script headers, in
> [1.Recoding/STAGE1_SCOPE.json](1.Recoding/STAGE1_SCOPE.json), and in
> [1.Recoding/STAGE1_SCOPE.md](1.Recoding/STAGE1_SCOPE.md). The repetition
> is intentional.

## Primary goal (now, and in every future session)

**Ascertain inter-rater consistency on SCENE INDIVIDUATION in hallucinogen trip reports.**

The atomic question: *for every narrative passage, did both raters individuate it as a hallucinatory scene?*

The rater's **subjective judgement** about what counts as a hallucinatory scene is the **primary data**. Any analysis of agreement must be anchored in what the raters actually individuated, not in what we think they should have individuated. If the instructions to the raters left ambiguity, that ambiguity is part of the phenomenon under study — it is not a bug to be silently fixed.

## What "individuating a scene" means

Scene **individuation** is the atomic act of pointing to a passage in a trip report and asserting: *"a hallucinatory scene happened here."* It is the precursor to every other coding step. Before a rater can assign a modality, an object class, an illusion-vs-incrusted tag, a modal status, or a dynamics flag, they must first decide that there is a scene to tag at all.

Individuation is therefore the **more objective** of the two coding steps:

- **Individuation** (Stage 1, the current question) — *is this passage a hallucinatory scene, yes or no?* A dichotomous decision grounded in the PDF *Guidelines for individuating hallucinations in trip reports*.
- **Classification** (Stage 2, deferred) — *given the scene exists, what kind of hallucination is it?* A multi-attribute taxonomic decision where rater subjective judgement dominates (illusion vs incrusted object vs detached vs immersive; animal vs artefact vs extraordinary entity; possible vs impossible; etc.).

Individuation is not perfectly objective — two raters may draw the "scene vs not-scene" line differently — but the disagreement is of a **different kind** than classification disagreement. The subjective residue in individuation is exactly what Stage 1 measures; classification subjectivity is preserved in the data untouched and deferred to Stage 2.

## Core analytical question

For every passage individuated by only ONE of the two raters (not both), determine whether the discrepancy is driven by:

1. **A MISS** — the other rater overlooked a passage that, by their own demonstrated criterion (see next section), they should have individuated. This is a rater-compliance gap, resolvable by reconciliation.
2. **AN AMBIGUITY** — the PDF rules do not cleanly cover this edge case, so both the individuation and the omission are defensible readings. This is an instruction-design gap, resolvable only by rewriting the Guidelines. AMBIGUITY splits into two flavours worth distinguishing in the write-up:
   - **2a. Edge case under-specified** — the Guidelines need a clarifying rule that decides, one way or the other, whether passages of this type are hallucinatory scenes.
   - **2b. Phenomenon outside the current category** — the passage may not belong under "hallucinatory scene" at all under any reasonable reading, but it is phenomenologically relevant (a sensation, a mood shift, an autobiographical memory without imagery, a somatic intensification, etc.) and the taxonomy would need an additional non-hallucinatory-scene category to handle it properly.

Generalising from what both raters agreed on gives the consistent core of the dataset. Classifying the drivers of disagreement as MISS vs AMBIGUITY tells us whether the remaining inconsistency is a rater-compliance problem (fixable by reconciliation) or an instruction-design problem (fixable only by clarifying or extending the Guidelines).

This is the **ultimate and only** overarching question of the current pipeline stage. All infrastructure (scene-ID taxonomy, driver suffixes, annotated trip-report pages, visualizations) exists in service of it.

## How to judge MISS vs AMBIGUITY — use the shared scenes as the reference

The "truth" against which a solo scene is judged is **not** the PDF Guidelines read in isolation and applied from scratch. It is each rater's *demonstrated* application of the PDF Guidelines on the scenes both raters individuated. The shared (`_AB`) scenes are where the two raters converged; they reveal the **operational criterion** each rater was actually using when they coded this corpus.

### Procedure

1. **Establish each rater's observed criterion from the `_AB` scenes of the same trip (and the same coder pair).** These are the scenes both raters agreed were hallucinatory. They are the empirical expression of "scene" as these two raters, in this coding effort, actually used the term.
2. **Read the solo scene in context.** Look at the narrative passage, the rater's canonical excerpt, and the rationale recorded in `stage1_rationale`.
3. **Apply the observed criterion.**
   - If the solo passage clearly matches the kinds of passages both raters individuated on the shared scenes — same kind of content, same level of specificity, same degree of perceptual concreteness — and one rater simply did not annotate it, the verdict is **MISS** (rater-compliance gap; the omitting rater overlooked it by their own standard).
   - If the solo passage sits at a kind of content the shared scenes do *not* establish a clear rule for — ambient perceptual amplification with no object, thought/memory/metaphor content, somatic self-transformation, a fragment of a holistic scene — the two raters are not disagreeing because one missed something; they are disagreeing because the Guidelines do not settle the case. Verdict is **AMBIGUITY**.
4. **If AMBIGUITY, decide which flavour.** Is this a passage that *should* be a hallucinatory scene once the Guidelines clarify the edge case (flavour 2a)? Or is it a phenomenon the coding taxonomy is missing a category for, and would be better handled by a new non-hallucinatory-scene classification (flavour 2b)?

### Why the shared scenes, not the PDF in the abstract

The PDF is not self-interpreting. Two competent raters reading the same PDF can land at different operational criteria; that is precisely how inter-rater disagreement arises. Using each rater's `_AB` scenes as the reference grounds the judgement in *what they actually did*, not in a theoretical ideal. A MISS verdict therefore means "by the criterion this rater used elsewhere in this trip, they should have individuated this too" — a much more defensible claim than "by my reading of the PDF, they should have."

Practically, the driver suffix system is the first-pass expression of this procedure:

- `_FRAG`, `_AMP`, `_AMB`, `_SOMA` correspond to content types where the Guidelines are systematically under-specified — these are strong AMBIGUITY candidates (usually flavour 2a or 2b).
- `_RCL` corresponds to scenes with no automatic rule fit — these are the ones a human needs to read against the trip's `_AB` scenes and verdict individually (likely MISS, possibly AMBIGUITY).

## What is explicitly OUT OF SCOPE at this stage

- **Attribute classification** on shared scenes — illusion vs incrusted vs detached vs immersive, object-class tags (Human / Artefact / Animal / etc.), modality tags, modal-status, dynamics. These record rater subjective judgement and are preserved in the data **unresolved**. A future Stage 2 analysis may address them; it is deferred.
- **Adjudicating** whether a rater's scope-layer choice (scene-level vs trip-level) was "correct". If a rater individuated a passage, the passage is in that rater's scene list. If they placed it at trip-level, it is not.
- **Merging** or **overriding** any rater's subjective taxonomic choice.

## Checklist before any code change

If you are ever about to do any of the following, **stop** and re-read this directive:

- [ ] Quietly drop or hide a scene one rater individuated because "it shouldn't have been coded according to the rules." The rater's individuation is data. Preserve it; classify the **driver** of why only-one-rater individuated it.
- [ ] Override a rater's choice of attribute tag on a scene both raters individuated. That is Stage 2, explicitly deferred.
- [ ] Treat attribute-disagreement on shared scenes as the primary reliability question. Stage 1 is about individuation only.
- [ ] Introduce analysis that conflates "only one rater individuated this" with "only one rater tagged this item at this depth" — these are two orthogonal questions.

## Driver taxonomy (diagnostic, not resolution)

Every scene has a status suffix encoded in its `scene_id`:

| Suffix | Interpretation |
|---|---|
| `_AB` | Both raters individuated this scene. Chronological shared ID. |
| `_FRAG` | One rater's sub-scene of a holistic scene coded by the other. Parent via `parent_scene_id`. |
| `_AMP` | Ambient perceptual amplification, no discrete object. Case-2 borderline. |
| `_AMB` | Thought / memory / metaphor treated as a hallucination by one rater. |
| `_SOMA` | Self-transformation or interoceptive content. |
| `_RCL` | No automatic classification — likely genuine miss, flagged for human reconciliation. |

These suffixes do not resolve anything. They classify *why* only-one-rater individuated the passage, so the core analytical question (miss vs ambiguity) can be answered.

## Authoritative sources

- `Coding Instructions/Guidelines for individuating hallucinations in trip reports.pdf` — the definition of "scene"
- `Coding Instructions/Description of items to be coded.pdf` — the taxonomy
- `Coding Instructions/Guidelines.pdf` — the per-item coding procedure (Case 1 / 2 / 3 rule)
- `Coding Instructions/The phenomenology of hallucinogenic experiences - Project description.pdf` — the project plan including the §7 reconciliation procedure
- `1.Recoding/STAGE1_SCOPE.json` — machine-readable scope
- `1.Recoding/STAGE1_SCOPE.md` — human-readable scope
- `1.Recoding/RULES.md` — the data-structure rules
- `1.Recoding/FINAL_REPORT.md` — the synthesis

## One-line reminder (for code headers)

> *Stage 1: scene-individuation consistency only. For every only-one-rater scene, classify MISS vs AMBIGUITY. Preserve rater subjective judgement. Do not resolve attribute-level disagreement.*
