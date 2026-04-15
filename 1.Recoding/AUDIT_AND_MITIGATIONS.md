# Audit of rater discrepancy + critical assessment of mitigation strategies

Produced from the consolidated recoding framework. This document is a critical
assessment — what does the data reveal about why raters disagreed, and how
should that be reconciled against the original PDF guidelines' intent?

---

## Part 1. Audit: all main sources of rater discrepancy, ranked

Total disagreement events in the dataset: **650**
- Individuation (scene-level): 125 events (19%)
- Classification (attribute-level on shared scenes): 525 events (81%)

### D1. Individuation-threshold mismatch (dominant individuation-level driver)

Only-one-rater scene counts by coder:

| Coder | Scenes individuated solo |
|---|---|
| Alessandra | **49** |
| Francesco | 23 |
| Susana | 22 |
| Brendan | 17 |
| Noah | 8 |
| Alessio | 6 |

Alessandra individuated **3× more solo scenes than her pair partners** on average, and **20× more than Brendan** on the Psilocybin 01–10 pair specifically. This is not random — it's a systematic rater-level difference in the threshold for "passage counts as a hallucinatory scene".

What Alessandra codes as scenes that others don't:
- brief perceptual amplifications ("everything glassy", "voices feel alien"),
- per-object fragments within already-shared scenes,
- metaphorical/visionary content ("mycelium visualisation"),
- ambient colour changes,
- introspective realisations.

**PDF rule violated:** Case 2 conservative rule (`Guidelines.pdf §5`). The instructions explicitly direct raters to *not* code unclear passages. Alessandra's bar for "clear evidence" is substantially lower than her peers'.

### D2. Taxonomy ambiguity in "Type of visual alteration"

The 4 leaves under this section (illusion / incrusted / detached / immersive) are mutually exclusive in theory but raters apply them inconsistently on the same scene (65% of shared-scene taxonomy rows under this section have A_ONLY or B_ONLY flags, not AGREE).

**PDF definition limitations:** the 4 definitions in `Description of items to be coded.pdf` are clearly written in the abstract but do not resolve realistic edge cases:
- Is a real screen with psychedelically-amplified colour-morphing an illusion (wrong property of real object) or incrusted (added content)?
- Is a breathing wall an illusion or a domain-violation?
- When the narrator describes a closed-eye visionary world, is it "detached" (superimposed) or "full-blown immersive" (replaces consensual world)?

### D3. Stylistic tag over-use (coding-discipline failure, not an instruction gap)

The 'Modal status' and 'Incrusted object' tags vary wildly in per-rater usage, producing A_ONLY/B_ONLY flags that are not semantic disagreements:

| Rater | modal-status uses | incrusted uses | illusion uses |
|---|---|---|---|
| Alessandra | 80 | 30 | 25 |
| Brendan | 59 | 35 | 37 |
| Francesco | 40 | 5 | 30 |
| Susana | 56 | 9 | 25 |
| Alessio | 42 | 29 | 1 |
| Noah | 1 | 14 | 9 |

Noah attaches modal-status 1 time across 10 trips; Alessandra attaches it 80 times across 20 trips. This is a ~8× per-trip rate difference. The PDF does not flag this as a risk or mandate a consistency check.

### D4. Scope-layer mismatch (scene-level vs trip-level)

Same passage coded at different taxonomy layers by different raters. The PDF taxonomy classifies items unambiguously (scene-level vs trip-level) but rater application blurs the boundary when a scene-level hallucination and a trip-level belief state describe the same passage:
- "Laws of physics had changed" — scene-level illusion or trip-level Delusional?
- "I visualised a mycelium" — scene-level hallucination or trip-level Insight?
- "I felt my body dissolve" — scene-level tactile hallucination or trip-level Ego-dissolution?

**PDF guidance gap:** no explicit rule for disambiguating when the same passage fits both scopes.

### D5. Per-object fragmentation style (row-inflation, not semantic disagreement)

Alessandra records separate scene-level rows for individual objects ("tree", "pen", "cigarette") when others record one row for the whole scene. This inflates her row count without changing what she actually reported. It is **not** a semantic disagreement — but it interacts with the agreement metrics at taxonomy depth 2 (leaf-level), making reliability at that depth look worse than the underlying agreement would justify.

**PDF guidance:** `Guidelines for individuating hallucinations in trip reports.pdf` says: count each object-class *once per scene* regardless of instances (the "3000 warriors = 1 row" rule). The rule is about column E counts, not excerpt cells; the instructions are silent on whether separate excerpt rows per object are allowed. Alessandra's style is *not strictly forbidden* but is inconsistent with the spirit of "one row per taxonomy item per scene".

### D6. Lump-vs-split of evolving scenes

When a hallucination morphs over time, some raters keep it as one scene; others split it into phases. The PDF explicitly favours lumping: "A scene can change a little and still remains the same scene." Splitting is thus a minor deviation.

**Impact:** small. Only 1 lump-split case was explicit enough in the adjudication to warrant the `LUMPA/SPLITB` convention; a few more may exist latently but the effect on the dataset is marginal.

### D7. Somatic/interoceptive sensations treated as scenes

Susana individuates embodied sensations (feather, stone, split body) as scenes. The PDF places Own-body-distortion, Arousal, Ego-dissolution at trip-level.

**PDF guidance gap:** somatic experiences do not have a scene-level equivalent in the taxonomy, yet they are clearly "hallucinatory" in the colloquial sense. Raters reasonably split over whether to force them into e.g. tactile-hallucination or to promote them to trip-level.

### D8. Cognitive insights / revelations treated as scenes

Raters inconsistently code insights ("I realised the universe is one") as scene-level visual hallucinations when they arrive with imagery. The PDF places Insight at trip-level, and the PDF-compliant reading is to code these at trip-level regardless of their imagistic quality. Alessandra violates this most often.

---

## Part 2. Critical assessment of mitigation strategies

### Evaluation rubric

Each candidate mitigation strategy is scored against four criteria:

- **PDF-fidelity**: does it operationalise the Guidelines' own stated intent?
- **Data loss**: does it discard information, and if so how much?
- **Bias risk**: does it systematically favour one kind of phenomenology over another?
- **Feasibility**: can it be done now, without re-engaging the original raters?

### Strategies considered

#### M1. Conservative consensus filter (`rater_status=both AND agreement=AGREE`)

- **What it does.** Retains only scenes both raters individuated AND items both raters attached to a shared scene.
- **PDF-fidelity.** HIGHEST. This is Case-2 applied at the dataset level: if at least one independent rater found the passage unclear enough to not code, treat it as not instantiated.
- **Data loss.** Significant — drops 125 of 305 scenes (41%) and 525 of 754 taxonomy rows (70%).
- **Bias risk.** Moderate. Systematically under-represents subtle/marginal phenomena (brief perceptual changes, embodied-somatic content) because precisely these phenomena have high rater-threshold variance. May bias the psilocybin-vs-brugmansia comparison toward the "easy" and well-defined hallucinations (classical hallucinogen iconography: geometric patterns, entity encounters, visual figures) and against the harder-to-code phenomenology (body distortion, insight, ambient perceptual amplification).
- **Feasibility.** Immediate. Pure dataset filter.

#### M2. Rater reconciliation meetings (the PDF's own prescribed method)

- **What it does.** The original `Project description.pdf` explicitly states: *"Once everyone will be done with the coding work, we will start to analyze the data and to compare cases in which two coders have coded trip reports differently. [...] coders having separately coded the same substances will meet (most likely through Skype) to discuss coding discrepancies and make final coding choices."*
- **PDF-fidelity.** HIGHEST — this is the original method. The scene-ID pipeline we built is infrastructure for exactly this step; it was not intended to replace it.
- **Data loss.** None — produces a consensus coding that integrates both raters' judgement.
- **Bias risk.** Low — raters reconcile against the source narrative, not against an external adjudicator.
- **Feasibility.** Time-intensive. Requires re-engaging 6 of the 8 coders (or a structured sub-sample). Post-hoc memory loss is a risk: raters may not remember why they made specific calls.

#### M3. LLM-assisted adjudication (what has been done so far)

- **What it does.** A large language model reads the worksheet (narrative + both rater's excerpts) and proposes a canonical scene set with provenance. A human reviewer confirms or corrects.
- **PDF-fidelity.** MODERATE. The LLM is a plausible proxy for the reconciliation step, but it is not one of the original raters — it cannot recover the rater's original intent in ambiguous cases, only infer it from their recorded excerpt. In practice this tends to accept whichever rater's reading is more explicitly evidenced in the text.
- **Data loss.** None — produces a richer schema than the original spreadsheets had.
- **Bias risk.** The LLM has its own threshold for scene-individuation. It must be anchored to the PDF's conservative rule explicitly (which we did in the iterative RULES.md).
- **Feasibility.** Already done — 40/40 trips adjudicated.

#### M4. Weighted Cohen's κ / Krippendorff's α by taxonomy level

- **What it does.** Report per-item inter-rater reliability coefficients at each taxonomy depth, identify items with unacceptable κ, and drop them.
- **PDF-fidelity.** LOW — the PDF framework is rule-based, not psychometric. Applying κ thresholds is a post-hoc quality gate, not an instruction-consistent rule.
- **Data loss.** Variable. Depends on the κ cutoff.
- **Bias risk.** Very high — κ conflates random agreement baseline with content-driven agreement, which on rare items produces spurious low scores.
- **Feasibility.** Immediate if numeric.

#### M5. Third-rater tiebreaker

- **What it does.** For every item where A and B disagree, a third rater reads the passage and adjudicates.
- **PDF-fidelity.** MODERATE — the PDF allows for this in principle but does not prescribe it.
- **Data loss.** None.
- **Bias risk.** The third rater inherits the same threshold-variance problem as the original two.
- **Feasibility.** Expensive — would require re-coding ~650 disagreement events.

#### M6. Scope-layer normalisation (rule-based)

- **What it does.** For every item in the `Sense of reality`, `Insight`, `Ego dissolution`, `Own body distortion`, `Domain-specific violation` sections, force the coding to trip-level regardless of where the rater put it. Applied mechanically at consolidation time.
- **PDF-fidelity.** HIGH — the PDF taxonomy unambiguously places these at trip-level.
- **Data loss.** None — only reassigns.
- **Bias risk.** Low but non-zero: raters occasionally have a good reason to place one of these at scene-level (e.g. a specific visual incident of ego dissolution). Losing that granularity is a minor cost.
- **Feasibility.** Immediate — add a normalisation pass to the consolidator.

#### M7. Taxonomy collapse for ambiguous sections

- **What it does.** Collapse the 4 "Type of visual alteration" leaves into a single binary "visual alteration present / not present" indicator. Optionally do the same for the 3 "Modal status" leaves.
- **PDF-fidelity.** LOW — loses categories the PDF explicitly defines.
- **Data loss.** Significant at the taxonomy level.
- **Bias risk.** Low — the collapse is conservative.
- **Feasibility.** Immediate.

#### M8. Per-rater calibration re-analysis

- **What it does.** Estimate each rater's personal threshold for scene individuation (e.g.\ via their total scenes-per-word ratio across all their trips). Compute rater-adjusted probabilities of inclusion and apply them as weights.
- **PDF-fidelity.** LOW — no PDF precedent for this.
- **Data loss.** None — probabilistic.
- **Bias risk.** Unclear. Requires an assumed model of rater threshold.
- **Feasibility.** Moderate — requires principled threshold estimation.

---

## Part 3. Recommended strategy

### Primary recommendation: tiered application of M1 + M2 + M6

A single mitigation strategy is insufficient. We recommend a tiered approach that uses each mitigation for the kind of disagreement it best handles.

**Tier A — mechanical pre-processing (do this first, no rater involvement).**
1. **M6 scope-layer normalisation.** Force `Sense of reality`, `Insight`, `Ego dissolution`, `Own body distortion`, `Domain-specific violation` items to trip-level regardless of where raters placed them. This eliminates source D4 entirely and recovers ~20–30 false disagreement flags.
2. **Within-rater object-row deduplication.** Collapse Alessandra's per-object excerpt rows to one row per taxonomy-leaf per scene. This removes D5 without changing semantic content.

**Tier B — analysis-time filters.**
3. **M1 conservative consensus** as the primary analysis base for all between-substance comparisons. This is the single filter most consistent with the PDF's Case-2 rule.
4. **Parallel liberal analysis** reported alongside: include single-rater items as exploratory observations with provenance, so the paper does not silently discard the "harder" phenomenology.

**Tier C — targeted rater reconciliation (the PDF's intended path).**
5. **Prioritised reconciliation list.** The pipeline has already identified the Alessandra × Brendan pair (Psilocybin 01–10) as the single worst pair, responsible for 41 of 87 only-A scenes dataset-wide. Reconciliation effort should be concentrated there first. Next priority: the 49 Alessandra-solo scenes across all her blocks, which are where the individuation-threshold mismatch is most concentrated.
6. **Structured reconciliation worksheet.** The existing per-trip adjudication YAMLs, with their worksheet-level provenance, are the ideal input for this step — they present each disagreement as a discrete item with the original excerpts and the narrative context, supporting a focused 10–15 minute discussion per trip.

### What NOT to do

- **Do not use weighted κ as the headline reliability measure.** κ systematically underestimates agreement on rare items and gives misleading results when raters' base rates differ (which is the case here for Noah's modal-status rate of 1/10 vs Alessandra's 80/20). The PDF's conservative rule is the more principled baseline.
- **Do not add a third-rater tiebreaker.** The threshold problem repeats itself; you end up with three opinions instead of two.
- **Do not abandon the pipeline and re-code from scratch.** The scene-ID framework and its agreement-flags derivation is a net improvement over the original spreadsheet structure; it's the scaffolding for any further reconciliation.

---

## Part 4. Summary positions

1. **The main source of individuation discrepancy is a rater-threshold mismatch** (D1) concentrated almost entirely in one coder pair (Psilocybin 01–10). The PDF's Case-2 rule is explicit but was unevenly applied.

2. **The main source of classification discrepancy is taxonomy ambiguity + stylistic tag over-use** (D2, D3) concentrated in the "Type of visual alteration", "Modal status", and "Dynamics" sections. The PDF definitions are clear in principle but do not resolve edge cases.

3. **The conservative consensus filter is the best single mitigation for a paper-ready analysis**, because it is the dataset-level analogue of the PDF's own Case-2 rule. It should be combined with mechanical scope-layer normalisation (M6) and, ideally, a targeted reconciliation pass (M2) on the Alessandra × Brendan block.

4. **The recoding framework is the scaffolding, not the solution.** The scene-ID convention and the `agreement_flags.csv` table make the problem visible and filterable; they do not resolve the semantic disagreements by themselves. The PDF's original intent — that raters would meet and reconcile — remains the most faithful endpoint, and the pipeline's purpose is to make that reconciliation tractable, not to substitute for it.
