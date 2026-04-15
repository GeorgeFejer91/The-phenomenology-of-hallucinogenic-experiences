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

## Core analytical question

For every passage individuated by only ONE of the two raters (not both), determine whether the discrepancy is driven by:

1. **A MISS** — the other rater overlooked a clearly hallucinatory passage that per the PDF Guidelines they *should* have coded. This is a rater-compliance gap.
2. **AN AMBIGUITY** — the PDF rules do not cleanly cover this edge case, so both the individuation and the omission are defensible readings. This is an instruction-design gap.

Generalising from what both raters agreed on gives the consistent core of the dataset. Understanding *why* they disagreed — miss vs ambiguity — tells us whether the remaining disagreement is a rater-compliance problem (fixable by reconciliation) or an instruction-design problem (needs disambiguation for any future coding project).

This is the **ultimate and only** overarching question of the current pipeline stage. All infrastructure (scene-ID taxonomy, driver suffixes, annotated trip-report pages, visualizations) exists in service of it.

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
