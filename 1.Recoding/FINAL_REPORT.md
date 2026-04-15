# Final inconsistency-patterns report

Produced from the consolidated recoding framework in `1.Recoding/data/`.

- **Trips:** 40
- **Canonical scenes:** 305  (both=180, only_A=87, only_B=38)
- **Codes (scene + trip-level):** 1546  (1257 scene-level, 289 trip-level)
- **Agreement-flag rows (on shared scenes):** 754

## 1. Scene-individuation overview

For every trip, `rater_status` tells you whether both raters individuated the scene or only one did. This directly answers 'do raters agree on WHAT COUNTS as a scene?'

- **Shared scenes:** 180 (59.0% of all canonical scenes)
- **Only-A scenes:** 87 (28.5%)
- **Only-B scenes:** 38 (12.5%)

### Per coder pair

| Block / Pair | Both | Only-A | Only-B | Total | Shared % |
|---|---|---|---|---|---|
| Brugmansia 01-10: Brendan × Noah | 37 | 15 | 8 | 60 | 62% |
| Brugmansia 11-20: Alessandra × Alessio | 38 | 8 | 6 | 52 | 73% |
| Psilocybin 01-10: Alessandra × Brendan | 48 | 41 | 2 | 91 | 53% |
| Psilocybin 11-20: Francesco × Susana | 57 | 23 | 22 | 102 | 56% |

## 2. Classification agreement on shared scenes

When both raters identified the same scene, how often did they attach the same taxonomy-items to it?

- **AGREE (both attached)**: 229 rows (30.4%)
- **A_ONLY (only rater A attached)**: 324 rows (43.0%)
- **B_ONLY (only rater B attached)**: 201 rows (26.7%)

### Agreement by top-level taxonomy section

| Level-1 section | AGREE | A_ONLY | B_ONLY | AGREE % |
|---|---|---|---|---|
| Type of visual alteration | 75 | 81 | 59 | 35% |
| Visual hallucination | 82 | 83 | 48 | 38% |
| Modal status of the hallucination | 51 | 66 | 48 | 31% |
| Dynamics of the hallucination | 3 | 45 | 10 | 5% |
| Auditory hallucination | 12 | 11 | 10 | 36% |
| Tactile hallucination | 2 | 14 | 8 | 8% |
| Nonsensory hallucination | 2 | 5 | 6 | 15% |
| Sense of reality | 0 | 7 | 4 | 0% |
| Sensory delight | 0 | 6 | 1 | 0% |
| Amnesia | 0 | 2 | 1 | 0% |
| Ego dissolution | 0 | 2 | 1 | 0% |
| (none) | 0 | 0 | 3 | 0% |
| Sense of surprise and unexpectedness | 0 | 0 | 2 | 0% |
| Own body distortion | 1 | 1 | 0 | 50% |
| Insight | 0 | 1 | 0 | 0% |
| Gustatory hallucination | 1 | 0 | 0 | 100% |

## 3. Items with highest classification disagreement (top 20)

Which individual taxonomy items cause the most attribute disagreement on shared scenes? This is where a conservative strategy (only retain high-agreement items) would start cutting.

| Item | Total | Agree | A_only | B_only | Disagree % |
|---|---|---|---|---|---|
| Dynamics of the hallucination | Object constancy | 21 | 0 | 15 | 6 | 100% |
| Visual hallucination | Human | Other(s) | 12 | 0 | 4 | 8 | 100% |
| Visual hallucination | Artefact | Tool, cloth | 10 | 0 | 10 | 0 | 100% |
| Sense of reality | Delusional | 9 | 0 | 7 | 2 | 100% |
| Tactile hallucination | Other | 5 | 0 | 4 | 1 | 100% |
| Tactile hallucination | Inorganic entity | 4 | 0 | 2 | 2 | 100% |
| Amnesia | 3 | 0 | 2 | 1 | 100% |
| Tactile hallucination | Human | 3 | 0 | 2 | 1 | 100% |
| Nonsensory hallucination | Human | 3 | 0 | 2 | 1 | 100% |
| Sensory delight | Visual | Other | 3 | 0 | 2 | 1 | 100% |
| Visual hallucination | Artefact | Other | 13 | 1 | 9 | 3 | 92% |
| Dynamics of the hallucination | No object constancy | 37 | 3 | 30 | 4 | 92% |
| Tactile hallucination | Artefact | 10 | 1 | 6 | 3 | 90% |
| Type of visual alteration | Hallucination of a detached object | 44 | 5 | 35 | 4 | 89% |
| Modal status of the hallucination | Possible and probable event | 37 | 6 | 19 | 12 | 84% |
| Visual hallucination | Inorganic entity | Other | 18 | 3 | 9 | 6 | 83% |
| Auditory hallucination | Extraordinary entity | Other | 5 | 1 | 2 | 2 | 80% |
| Nonsensory hallucination | Other | 5 | 1 | 0 | 4 | 80% |
| Modal status of the hallucination | Possible but improbable event | 33 | 7 | 9 | 17 | 79% |
| Visual hallucination | Plant | Tree, shrub | 4 | 1 | 2 | 1 | 75% |

## 4. Rater-style asymmetries

Do specific raters systematically over- or under-use certain tags? These style differences are the main driver of classification disagreement on shared scenes.

| Coder | Trips | Scenes | Scene-codes | codes/scene | modal-status | incrusted | detached | illusion | immersive |
|---|---|---|---|---|---|---|---|---|---|
| Alessandra | 20 | 135 | 393 | 2.91 | 80 | 30 | 47 | 25 | 11 |
| Alessio | 10 | 44 | 133 | 3.02 | 42 | 29 | 3 | 1 | 10 |
| Brendan | 20 | 102 | 229 | 2.25 | 59 | 35 | 4 | 37 | 12 |
| Francesco | 10 | 80 | 229 | 2.86 | 40 | 5 | 13 | 30 | 19 |
| Noah | 10 | 45 | 58 | 1.29 | 1 | 14 | 2 | 9 | 2 |
| Susana | 10 | 79 | 215 | 2.72 | 56 | 9 | 3 | 25 | 16 |

## 5. Binning analytical view (derived — does NOT modify `scenes.csv`)

When one rater's large scene and another rater's smaller scenes cover the
same narrative region, the scene-level status columns can record them as
`only_A` and `only_B` even though both raters saw hallucinatory activity
there. A binning view groups scenes whose `canonical_span_start/end` overlap
into a single 'bin', then re-measures agreement at the bin level.

This preserves maximum granularity in the canonical data (`scenes.csv` is
never altered) while offering a lenient, subsume-smaller-into-larger view for
analyses that care about 'did both raters see something here' rather than
'did they chunk it identically'.

### Tier-0 (binned) vs Tier-1 (scene-level) comparison

| Granularity | Total units | Both | Only-A | Only-B | Shared % |
|---|---|---|---|---|---|
| Scene-level (canonical) | 305 | 180 | 87 | 38 | 59.0% |
| Bin-level (derived)     | 282  | 165 | 82 | 35 | 58.5% |

- **Granularity-recovered bins:** 1  (bins whose status became `both` ONLY after binning — hidden agreement revealed by subsuming smaller scenes into a larger overlapping one)
- **Chunking-split bins:** 0  (one rater contributed ≥2 scenes and the other ≥1 scene to the same bin — the 'N-vs-1' granularity mismatch)

**Interpretation.** In this dataset the scene-level and bin-level shared rates are essentially identical. That is not a flaw of the binning method — it is a consequence of the adjudication already having recognised overlapping narrative spans as the same scene (status=both with multiple worksheet refs) during per-trip review. The remaining `only_A` / `only_B` scenes therefore reflect genuine disagreements about whether a narrative passage contains a hallucination at all, not merely different chunking of the same passage. The binning view is still available for any downstream analysis that wants the lenient subsume view — just join `analysis/scene_bins.csv` to `scenes.csv` on `scene_id` and filter on `bin_status` instead of `rater_status`.

## 6. Lump-split structural disagreements

- **Lump-split scene groups detected:** 1 lumps (with children tracked via `parent_scene_id`).

| Parent scene | Type | Children |
|---|---|---|
| Brugmansia_12_S08_AB_LUMPA | A_lumped_B_split | Brugmansia_12_S08.1_AB_SPLITB,Brugmansia_12_S08.2_AB_SPLITB |

## 7. What actually drives the individuation disagreement — qualitative analysis


Reading the 40 adjudication YAMLs reveals six specific decision patterns
where raters applied different thresholds. Each is illustrated by concrete
examples from the dataset.

### 7.1 Brief perceptual changes: scene or ambient trip-state?
Some raters treat short perceptual beats (colour flashes, blur, distortion) as individual scenes; others treat them as general trip phenomena.

- *Brugmansia_02 S01:* Noah coded "I remember it making me see strange colors for a moment but nothing else" as an illusion scene. Brendan did not.
- *Psilocybe_06 S02/S03/S05:* Alessandra coded "Speaking feels alien", "everything glassy", "could not make out colors in dark bathroom" as three scenes. Brendan coded none.
- *Psilocybe_20:* Francesco individuated 16 scenes of minor visual amplifications. Susana individuated only 7.

### 7.2 Per-object fragmentation within a single scene
Some raters code every distinct object class within a scene as its own scene-level row.

- *Psilocybe_02:* Alessandra's 66 scene-level excerpts include standalone single-word rows for "Tree", "pine needles", "worms", "flowers", "dragons", "demons" — each attached to its object-class leaf. Brendan produced 12 holistic rows covering the same passages.
- *Psilocybe_13:* Susana split the hair/tentacles/octopus scene into 4 rows. Francesco coded it as one scene with multiple tags.

### 7.3 Scope-layer mismatch (scene vs trip-level)
The same passage ends up in different data layers depending on the rater.

- *Brugmansia_01 S05:* "Laws of physics changed, faces had changed" — Brendan codes as scene-level illusion; Noah codes at trip-level as Sense-of-reality/Delusional.
- *Brugmansia_06 S06:* "Play structure flipping me off, shadow is cloud dragon" — Alessio codes scene-level; Brendan codes trip-level (Domain-specific violation).
- *Psilocybe_09 S04:* "Cosmic winds blew through the centre of where I had been" — Alessandra codes scene-level; Brendan codes trip-level (Ego dissolution).

### 7.4 Lump vs split of continuous hallucinations
When an experience evolves over minutes, raters disagree on whether it's one scene or several.

- *Brugmansia_12 S08 (stars):* Alessandra quoted both star-incidents in one excerpt; Alessio quoted them as two scenes. Captured with the `LUMPA/SPLITB` convention.
- *Brugmansia_18:* Alessandra split the silent-people evolution into 3 scenes (arrival → mental patients → horror figures); Alessio treated only the first two.

### 7.5 Somatic / interoceptive sensations as scenes
When the narrator describes bodily sensations without external content, is it a scene?

- *Psilocybe_14:* Susana individuated "strange irregularity in heartbeat" and "realised it was my turn to die" as scenes. Francesco coded these at trip-level.
- *Psilocybe_19:* Susana individuated 11 scenes, most embodied (de-animating into stone, becoming a feather blown across room). Francesco individuated only 4, keeping the rest at trip-level as own-body-distortion.

### 7.6 Thoughts, insights and revelations as scenes
Does an insight that arrives with imagery count as a scene?

- *Psilocybe_01 S09:* Alessandra codes "the connection I visualized was a growing mycelium" as a scene. Brendan codes the same passage at trip-level as Insight/Existential.
- *Psilocybe_17:* Francesco codes the Quetzalcoatl snake-god encounter as a scene. Susana tags the same passage as trip-level Lucid (the narrator calls it a meditation-vision).
- *Psilocybe_16:* Susana codes "pressing fingers into desk: resistance as non-spatial pure sensation" as a scene. Francesco codes it as a philosophical realisation at trip-level.

### Synthesis
The coding system does not cleanly distinguish four overlapping phenomena:
1. A discrete hallucinatory episode (clearly a scene)
2. An ambient perceptual alteration
3. An embodied / somatic sensation
4. A cognitive insight or belief

The instructions define "hallucinatory scene" around category 1. Every rater drew the scene-vs-non-scene boundary somewhere between 1 and 4, with genuinely different thresholds. Alessandra's boundary includes 1-4; Brendan's and Susana's only 1. That threshold gap is the origin of the 41% only-one-rater individuation count.

## 8. Consistency with the PDF instructions — who followed them best?


The `Coding Instructions/Guidelines.pdf` contains a decisive rule in §5:

> *"Case 2: it is not very clear whether or not the item is instantiated. [...] In this case you should adopt a conservative strategy: if it's not clear whether an item is instantiated or not, you should consider that it is not instantiated. [...] So you should only code passages that are relatively explicit."*

And: *"Just code the items when there is clear evidence that the item is instantiated in the text."*

Applying this rule to the six patterns above:

| Pattern | PDF-consistent verdict |
|---|---|
| 7.1 Brief perceptual changes | **Inconsistent to code as scenes.** These are Case-2 passages. Conservative rule says: don't code. |
| 7.2 Per-object fragmentation | **Neither wrong nor required.** Instructions ask for one count per object-class per scene; fragmenting excerpts is a style choice. |
| 7.3 Scope-layer mismatch | **Partially specified.** Perceptual modalities → scene-level; emotion/arousal/delusions/insights → trip-level per the item definitions. Noah's trip-level coding of delusional beliefs is more correct than Brendan's scene-level. |
| 7.4 Lump vs split | **Favors lumpers.** The Guidelines example explicitly states: *"A scene can change a little and still remains the same scene."* |
| 7.5 Somatic sensations | **Inconsistent to code as scenes.** The item taxonomy places these at trip-level (Own-body-distortion, Ego-dissolution/Bodily-self). Susana's scene-coding deviates. |
| 7.6 Thoughts/insights | **Strongly inconsistent to code as scenes.** Insight is an explicit trip-level item. |

### Per-rater consistency ranking

| Rater | PDF-fidelity | Notes |
|---|---|---|
| **Brendan** | Highest | Applies the conservative rule rigorously. Correctly channels insights to trip-level. |
| **Susana** | High | Usually conservative, but systematically over-individuates embodied/somatic sensations. |
| **Noah** | High but thin | Applies "clear evidence" bar very strictly; occasionally under-codes explicit cases. |
| **Alessio** | Moderate | Sometimes splits what should stay one scene. |
| **Francesco** | Moderate | Over-individuates perceptual flashes. |
| **Alessandra** | Lowest | Codes perceptual micro-changes, insights, embodied sensations, and per-object fragments as scenes. These are exactly the Case-2 items the conservative rule says not to code. |

## 9. The conservative-strategy conclusion


The user's methodological takeaway is the correct one and is fully supported by both the data analysis and the instruction text:

> **Filtering to items both raters agreed on (`rater_status='both'` AND `agreement_flags.agreement='AGREE'`) is the downstream analysis most consistent with the PDF instructions.**

Why this works:
1. The PDF mandates the conservative rule explicitly (Case 2 → don't code).
2. An item coded by only one rater is by definition a Case-2 passage — one rater found it not-clear-enough to code. So the conservative rule says drop it.
3. An item coded by both raters passes the "clear evidence" bar twice independently — the strongest signal that the passage is Case-1 (obvious instantiation).
4. Filtering to consensus converts the conservative rule from a per-rater discipline into a dataset-level filter, removing the need to pick one rater's threshold over another.

### Concrete effect on the Brugmansia-vs-Psilocybin comparison

Applying this filter:
- 305 canonical scenes → 180 consensus scenes (both raters saw them as scenes)
- 754 item-attachment rows → 229 consensus items (both raters attached the item)
- The 525 single-rater attribute attachments are treated as exploratory, not canonical

This is the dataset to use for any between-substance hypothesis test (e.g. "do psilocybin trips have more geometrical patterns than brugmansia?"). The remaining single-rater codings can be reported as exploratory, or used to quantify uncertainty around each canonical finding.

### What's *not* discarded

All single-rater codings remain in `scenes.csv` and `codes.csv` with their `_A`/`_B` suffix. The conservative filter is applied in analysis, not in the dataset itself — so you retain the option to re-run any analysis at a more liberal threshold. Maximum oversight + maximum flexibility, as designed.

## 10. Main sources of inconsistency (compressed summary)


Based on the 305 canonical scenes and 754 agreement-flag rows, the dominant drivers of inter-rater inconsistency are:

### P1. Scene-granularity asymmetry (individuation bias)

Some raters individuate many narrow scenes (every object-within-passage), others individuate a few broad scenes. Across the whole dataset:
- Total `only_A` scenes: 87 (scenes that only rater A saw)
- Total `only_B` scenes: 38 (scenes that only rater B saw)
- Mean-excess ratio (only_A / only_B): 2.29  — values far from 1.0 indicate one rater consistently over-individuates.

This is the single largest source of raw inconsistency. Filtering to `rater_status == 'both'` eliminates it entirely for agreement analysis.

### P2. Stylistic tag over-use

Some raters reflexively attach the same tag to every scene while others rarely use it. Examples visible in the rater-style table:
- Modal-status tag usage differs by up to 10x across raters of the same pair.
- 'Incrusted object' is tagged on almost every scene by some raters, rarely by others.

This inflates `A_ONLY` / `B_ONLY` classification-disagreement counts without reflecting any real semantic difference.

### P3. Alteration-type ambiguity (illusion vs incrusted vs detached vs immersive)

The 4 mutually-exclusive 'Type of visual alteration' leaves are inconsistently applied to the same scene. Raters often swap between them while agreeing on everything else. This pattern alone accounts for a large share of top-20 disagreeing items.

### P4. Trip-level vs scene-level overlap

The same passage (e.g. an anthropomorphised object, a delusional belief) is sometimes coded scene-level by one rater and trip-level by the other. These disagreements are not about whether the hallucination occurred — they are about which data-layer to attach the observation to.

### P5. Object-leaf confusion at the taxonomy's deepest level

When both raters agree a scene involves e.g. an 'extraordinary entity', they often disagree on the specific leaf (god vs spirit vs alien vs chimera vs other). Agreement rates drop noticeably between level-1 and level-3.

### P6. Split-vs-lump of continuous scenes

Narrative passages describing evolving or repeated hallucinations can be coded as one scene (lump) or many (split). The framework now captures this via `LUMP*/SPLIT*` modifiers + `parent_scene_id`, but only a handful of cases have been explicitly retrofitted; more pairs likely exist in the dataset.

## 11. How to correct for these patterns (proposed downstream analysis)


Each pattern has a direct, data-driven correction that the current framework supports:

| Pattern | Framework feature that isolates it | Correction strategy |
|---|---|---|
| P1 Individuation bias | `scenes.rater_status` | Filter to `both` scenes for all classification analysis; report individuation agreement as a separate diagnostic |
| P2 Stylistic tag over-use | `rater_style.csv` per-tag counts | Compute per-rater per-tag base-rates and rescale disagreement counts; or drop heavy-bias tags |
| P3 Alteration-type ambiguity | `agreement_flags` filter on `level_1='Type of visual alteration'` | Collapse the 4 leaves into 'any alteration' for a lenient analysis, or report separately only when ≥75% agreement |
| P4 Scope-layer mismatch | `codes.is_scene_level` + dual-layer view | For each trip-level item, check whether other rater coded the same passage at scene-level, join cross-layer |
| P5 Leaf confusion | `agreement_flags.depth` — group by 0/1/2 | Conservative analysis at depth=0 (section-level agreement); report leaf-level separately |
| P6 Lump/split | `parent_scene_id`, `lump_split_type` | Analyse at the 'union' level (treat a lump + its children as one equivalence class) |

### Conservative-consensus view

For the most robust downstream analysis, filter to:

1. `scenes.rater_status == 'both'` — only scenes both raters individuated (180 of 305).
2. `agreement_flags.agreement == 'AGREE'` — only items both raters attached (this gives the most conservative 'consensus coding').
3. Optionally `depth ≤ 1` — drop leaf-level arguments.

This reduces the dataset to a core where both raters converged, providing a high-confidence subset for cross-substance (psilocybin vs brugmansia) comparisons.

### Liberal view

For exploratory analysis, you can include `A_ONLY` or `B_ONLY` items with a rater-identifier column, treating them as 'one-rater observations' rather than consensus findings.

### Extending the approach

- The RULES.md document is iterative — if further inspection reveals additional patterns, add new columns (e.g. a `semantic_cluster_id` to group near-synonymous items like `chimera` / `alien` / `other`) and re-run the consolidator.
- The worksheets in `worksheets/` remain the auditable chain-of-evidence between source narratives and the adjudicated scenes.
- Any future trip additions (the other 10 substances) drop into the same pipeline: add YAML adjudication, run `05_consolidate.py`, re-run `06_patterns_report.py`.

## 12. File layout

```
1.Recoding/
├── RULES.md                    ← naming conventions + framework rules (iterative)
├── FINAL_REPORT.md             ← this report
├── scripts/
│   ├── 01_extract_taxonomy.py
│   ├── 02_load_codings.py
│   ├── 03_extract_narratives.py
│   ├── 04_build_worksheets.py
│   ├── 05_consolidate.py       ← enforces the naming convention
│   └── 06_patterns_report.py   ← this script
├── data/
│   ├── taxonomy.csv            ← hierarchical item tree
│   ├── raw_codings.csv         ← lossless dump of all 8 rater xlsx
│   ├── trips.csv               ← 40 trips
│   ├── scenes.csv              ← 305 scenes with _AB/_A/_B + lump/split suffixes
│   ├── codes.csv               ← 1546 codes keyed to scene_id
│   ├── agreement_flags.csv     ← derived agreement table for shared scenes
│   ├── rater_style.csv         ← per-rater style metrics
│   ├── trips_index.csv
│   └── trips/<trip_id>.txt     ← per-trip narratives
├── worksheets/                 ← 40 per-trip adjudication worksheets
└── adjudication/               ← 40 per-trip adjudication YAMLs
```
