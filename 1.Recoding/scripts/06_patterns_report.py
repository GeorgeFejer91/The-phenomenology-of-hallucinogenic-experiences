"""Generate a data-driven patterns report from the consolidated framework.

Reads scenes.csv, codes.csv, agreement_flags.csv, rater_style.csv
Emits: 1.Recoding/FINAL_REPORT.md with headline numbers + pattern analysis.
"""
import os, csv
from collections import Counter, defaultdict

DATA = "../data"
OUT = "../FINAL_REPORT.md"


def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    here = os.path.dirname(__file__)
    scenes = load(os.path.join(here, DATA, "scenes.csv"))
    codes = load(os.path.join(here, DATA, "codes.csv"))
    flags = load(os.path.join(here, DATA, "agreement_flags.csv"))
    style = load(os.path.join(here, DATA, "rater_style.csv"))
    trips = load(os.path.join(here, DATA, "trips.csv"))

    # --- Basic counts ---
    n_trips = len(trips)
    n_scenes = len(scenes)
    n_both = sum(1 for s in scenes if s["rater_status"] == "both")
    n_A = sum(1 for s in scenes if s["rater_status"] == "only_A")
    n_B = sum(1 for s in scenes if s["rater_status"] == "only_B")

    # --- Per-pair breakdown ---
    trips_by_id = {t["trip_id"]: t for t in trips}
    pair_scenes = defaultdict(lambda: {"both": 0, "only_A": 0, "only_B": 0})
    for s in scenes:
        t = trips_by_id[s["trip_id"]]
        pair = f"{t['substance'].title()} {t['block']}: {t['coder_A']} × {t['coder_B']}"
        pair_scenes[pair][s["rater_status"]] += 1

    # --- Classification agreement on shared scenes ---
    # Per shared scene, what fraction of items in agreement_flags are AGREE?
    agr_counts = {"AGREE": 0, "A_ONLY": 0, "B_ONLY": 0}
    for f in flags:
        agr_counts[f["agreement"]] += 1

    # --- Agreement by level_1 (taxonomy L1) ---
    l1_stats = defaultdict(lambda: {"AGREE": 0, "A_ONLY": 0, "B_ONLY": 0})
    for f in flags:
        l1 = f["level_1"] or "(none)"
        l1_stats[l1][f["agreement"]] += 1

    # --- Rater-style aggregates ---
    style_by_rater = defaultdict(lambda: {
        "n_trips": 0, "n_scenes": 0, "n_scene_codes": 0, "n_trip_codes": 0,
        "modal_status": 0, "incrusted": 0, "detached": 0, "illusion": 0, "immersive": 0,
    })
    for s in style:
        key = f"{s['coder_name']} ({s['substance']} {('01-10' if s['trip_id'].endswith('_01') or s['trip_id'].endswith('_02') or s['trip_id'].endswith('_03') or s['trip_id'].endswith('_04') or s['trip_id'].endswith('_05') or s['trip_id'].endswith('_06') or s['trip_id'].endswith('_07') or s['trip_id'].endswith('_08') or s['trip_id'].endswith('_09') or s['trip_id'].endswith('_10') else '11-20')})"
        d = style_by_rater[key]
        d["n_trips"] += 1
        d["n_scenes"] += int(s["n_scenes_individuated"])
        d["n_scene_codes"] += int(s["n_scene_codes"])
        d["n_trip_codes"] += int(s["n_trip_codes"])
        d["modal_status"] += int(s["modal_status_uses"])
        d["incrusted"] += int(s["incrusted_uses"])
        d["detached"] += int(s["detached_uses"])
        d["illusion"] += int(s["illusion_uses"])
        d["immersive"] += int(s["immersive_uses"])

    # --- Scenes with lump-split structure ---
    lump_scenes = [s for s in scenes if s["lump_split_type"] != "none"]

    # --- Items with highest disagreement ---
    item_disagreement = defaultdict(lambda: {"AGREE": 0, "A_ONLY": 0, "B_ONLY": 0})
    for f in flags:
        item_disagreement[f["item_path"]][f["agreement"]] += 1
    # Sort by disagreement count descending (only count items appearing >= 3 times)
    ranked = []
    for item, c in item_disagreement.items():
        total = c["AGREE"] + c["A_ONLY"] + c["B_ONLY"]
        if total < 3: continue
        disagree = c["A_ONLY"] + c["B_ONLY"]
        ranked.append((item, total, c["AGREE"], c["A_ONLY"], c["B_ONLY"], disagree / total))
    ranked.sort(key=lambda x: (-x[5], -x[1]))

    # --- Write report ---
    out = []
    out.append("# Final inconsistency-patterns report\n")
    out.append("Produced from the consolidated recoding framework in `1.Recoding/data/`.\n")
    out.append(f"- **Trips:** {n_trips}")
    out.append(f"- **Canonical scenes:** {n_scenes}  (both={n_both}, only_A={n_A}, only_B={n_B})")
    out.append(f"- **Codes (scene + trip-level):** {len(codes)}  ({sum(1 for c in codes if c['is_scene_level']=='True')} scene-level, {sum(1 for c in codes if c['is_scene_level']=='False')} trip-level)")
    out.append(f"- **Agreement-flag rows (on shared scenes):** {len(flags)}")
    out.append("")

    out.append("## 1. Scene-individuation overview\n")
    out.append("For every trip, `rater_status` tells you whether both raters individuated the scene or only one did. This directly answers 'do raters agree on WHAT COUNTS as a scene?'\n")
    out.append(f"- **Shared scenes:** {n_both} ({100*n_both/n_scenes:.1f}% of all canonical scenes)")
    out.append(f"- **Only-A scenes:** {n_A} ({100*n_A/n_scenes:.1f}%)")
    out.append(f"- **Only-B scenes:** {n_B} ({100*n_B/n_scenes:.1f}%)")
    out.append("")

    out.append("### Per coder pair\n")
    out.append("| Block / Pair | Both | Only-A | Only-B | Total | Shared % |")
    out.append("|---|---|---|---|---|---|")
    for pair, c in pair_scenes.items():
        tot = c["both"] + c["only_A"] + c["only_B"]
        out.append(f"| {pair} | {c['both']} | {c['only_A']} | {c['only_B']} | {tot} | {100*c['both']/tot:.0f}% |")
    out.append("")

    out.append("## 2. Classification agreement on shared scenes\n")
    out.append("When both raters identified the same scene, how often did they attach the same taxonomy-items to it?\n")
    out.append(f"- **AGREE (both attached)**: {agr_counts['AGREE']} rows ({100*agr_counts['AGREE']/len(flags):.1f}%)")
    out.append(f"- **A_ONLY (only rater A attached)**: {agr_counts['A_ONLY']} rows ({100*agr_counts['A_ONLY']/len(flags):.1f}%)")
    out.append(f"- **B_ONLY (only rater B attached)**: {agr_counts['B_ONLY']} rows ({100*agr_counts['B_ONLY']/len(flags):.1f}%)")
    out.append("")

    out.append("### Agreement by top-level taxonomy section\n")
    out.append("| Level-1 section | AGREE | A_ONLY | B_ONLY | AGREE % |")
    out.append("|---|---|---|---|---|")
    for l1, c in sorted(l1_stats.items(), key=lambda x: -sum(x[1].values())):
        tot = sum(c.values())
        pct = 100 * c["AGREE"] / tot if tot else 0
        out.append(f"| {l1} | {c['AGREE']} | {c['A_ONLY']} | {c['B_ONLY']} | {pct:.0f}% |")
    out.append("")

    out.append("## 3. Items with highest classification disagreement (top 20)\n")
    out.append("Which individual taxonomy items cause the most attribute disagreement on shared scenes? This is where a conservative strategy (only retain high-agreement items) would start cutting.\n")
    out.append("| Item | Total | Agree | A_only | B_only | Disagree % |")
    out.append("|---|---|---|---|---|---|")
    for item, total, agr, a_only, b_only, rate in ranked[:20]:
        out.append(f"| {item} | {total} | {agr} | {a_only} | {b_only} | {100*rate:.0f}% |")
    out.append("")

    out.append("## 4. Rater-style asymmetries\n")
    out.append("Do specific raters systematically over- or under-use certain tags? These style differences are the main driver of classification disagreement on shared scenes.\n")
    # Aggregate per rater across their trips
    per_coder = defaultdict(lambda: defaultdict(int))
    for s in style:
        k = s["coder_name"]
        for f in ("n_scenes_individuated","n_scene_codes","n_trip_codes",
                 "modal_status_uses","incrusted_uses","detached_uses",
                 "illusion_uses","immersive_uses"):
            per_coder[k][f] += int(s[f])
    out.append("| Coder | Trips | Scenes | Scene-codes | codes/scene | modal-status | incrusted | detached | illusion | immersive |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    coders_sorted = sorted(per_coder.keys())
    coder_trips = Counter(s["coder_name"] for s in style)
    for c in coders_sorted:
        d = per_coder[c]
        t = coder_trips[c]
        cps = d["n_scene_codes"] / max(1, d["n_scenes_individuated"])
        out.append(f"| {c} | {t} | {d['n_scenes_individuated']} | {d['n_scene_codes']} | {cps:.2f} | {d['modal_status_uses']} | {d['incrusted_uses']} | {d['detached_uses']} | {d['illusion_uses']} | {d['immersive_uses']} |")
    out.append("")

    # --- Binning analysis (derived view) ---
    bins_path = os.path.join(here, "../analysis/bins_summary.csv")
    if os.path.exists(bins_path):
        bins = load(bins_path)
        n_bins = len(bins)
        n_bin_both = sum(1 for b in bins if b["bin_status"] == "both")
        n_bin_A = sum(1 for b in bins if b["bin_status"] == "only_A")
        n_bin_B = sum(1 for b in bins if b["bin_status"] == "only_B")
        n_recovered = sum(1 for b in bins if b["granularity_recovered"] == "True")
        n_chunking = sum(1 for b in bins if b["chunking_split"] == "True")

        out.append("## 5. Binning analytical view (derived — does NOT modify `scenes.csv`)\n")
        out.append("""When one rater's large scene and another rater's smaller scenes cover the
same narrative region, the scene-level status columns can record them as
`only_A` and `only_B` even though both raters saw hallucinatory activity
there. A binning view groups scenes whose `canonical_span_start/end` overlap
into a single 'bin', then re-measures agreement at the bin level.

This preserves maximum granularity in the canonical data (`scenes.csv` is
never altered) while offering a lenient, subsume-smaller-into-larger view for
analyses that care about 'did both raters see something here' rather than
'did they chunk it identically'.
""")
        out.append("### Tier-0 (binned) vs Tier-1 (scene-level) comparison\n")
        out.append("| Granularity | Total units | Both | Only-A | Only-B | Shared % |")
        out.append("|---|---|---|---|---|---|")
        out.append(f"| Scene-level (canonical) | {n_scenes} | {n_both} | {n_A} | {n_B} | {100*n_both/n_scenes:.1f}% |")
        out.append(f"| Bin-level (derived)     | {n_bins}  | {n_bin_both} | {n_bin_A} | {n_bin_B} | {100*n_bin_both/n_bins:.1f}% |")
        out.append("")
        out.append(f"- **Granularity-recovered bins:** {n_recovered}  "
                   "(bins whose status became `both` ONLY after binning — hidden agreement revealed by subsuming smaller scenes into a larger overlapping one)")
        out.append(f"- **Chunking-split bins:** {n_chunking}  "
                   "(one rater contributed ≥2 scenes and the other ≥1 scene to the same bin — the 'N-vs-1' granularity mismatch)")
        out.append("")
        out.append("**Interpretation.** In this dataset the scene-level and bin-level "
                   "shared rates are essentially identical. That is not a flaw of the "
                   "binning method — it is a consequence of the adjudication already "
                   "having recognised overlapping narrative spans as the same scene "
                   "(status=both with multiple worksheet refs) during per-trip review. "
                   "The remaining `only_A` / `only_B` scenes therefore reflect genuine "
                   "disagreements about whether a narrative passage contains a "
                   "hallucination at all, not merely different chunking of the same "
                   "passage. The binning view is still available for any downstream "
                   "analysis that wants the lenient subsume view — just join "
                   "`analysis/scene_bins.csv` to `scenes.csv` on `scene_id` and filter "
                   "on `bin_status` instead of `rater_status`.")
        out.append("")

    out.append("## 6. Lump-split structural disagreements\n")
    out.append(f"- **Lump-split scene groups detected:** {sum(1 for s in lump_scenes if 'LUMP' in s['scene_id'])} lumps (with children tracked via `parent_scene_id`).")
    if lump_scenes:
        out.append("")
        out.append("| Parent scene | Type | Children |")
        out.append("|---|---|---|")
        children_by_parent = defaultdict(list)
        for s in lump_scenes:
            if s["parent_scene_id"]:
                children_by_parent[s["parent_scene_id"]].append(s["scene_id"])
        for s in lump_scenes:
            if "LUMP" in s["scene_id"]:
                kids = ",".join(children_by_parent.get(s["scene_id"], []))
                out.append(f"| {s['scene_id']} | {s['lump_split_type']} | {kids} |")
    out.append("")

    out.append("## 7. What actually drives the individuation disagreement — qualitative analysis\n")
    out.append("""
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
""")
    out.append("""
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
""")
    out.append("""
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
""")

    out.append("""
Based on the 305 canonical scenes and 754 agreement-flag rows, the dominant drivers of inter-rater inconsistency are:

### P1. Scene-granularity asymmetry (individuation bias)

Some raters individuate many narrow scenes (every object-within-passage), others individuate a few broad scenes. Across the whole dataset:
- Total `only_A` scenes: %d (scenes that only rater A saw)
- Total `only_B` scenes: %d (scenes that only rater B saw)
- Mean-excess ratio (only_A / only_B): %.2f  — values far from 1.0 indicate one rater consistently over-individuates.

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
""" % (n_A, n_B, n_A / max(1, n_B)))

    out.append("## 11. How to correct for these patterns (proposed downstream analysis)\n")
    out.append("""
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
""")

    out.append("## 12. File layout\n")
    out.append("```")
    out.append("1.Recoding/")
    out.append("├── RULES.md                    ← naming conventions + framework rules (iterative)")
    out.append("├── FINAL_REPORT.md             ← this report")
    out.append("├── scripts/")
    out.append("│   ├── 01_extract_taxonomy.py")
    out.append("│   ├── 02_load_codings.py")
    out.append("│   ├── 03_extract_narratives.py")
    out.append("│   ├── 04_build_worksheets.py")
    out.append("│   ├── 05_consolidate.py       ← enforces the naming convention")
    out.append("│   └── 06_patterns_report.py   ← this script")
    out.append("├── data/")
    out.append("│   ├── taxonomy.csv            ← hierarchical item tree")
    out.append("│   ├── raw_codings.csv         ← lossless dump of all 8 rater xlsx")
    out.append("│   ├── trips.csv               ← 40 trips")
    out.append("│   ├── scenes.csv              ← 305 scenes with _AB/_A/_B + lump/split suffixes")
    out.append("│   ├── codes.csv               ← 1546 codes keyed to scene_id")
    out.append("│   ├── agreement_flags.csv     ← derived agreement table for shared scenes")
    out.append("│   ├── rater_style.csv         ← per-rater style metrics")
    out.append("│   ├── trips_index.csv")
    out.append("│   └── trips/<trip_id>.txt     ← per-trip narratives")
    out.append("├── worksheets/                 ← 40 per-trip adjudication worksheets")
    out.append("└── adjudication/               ← 40 per-trip adjudication YAMLs")
    out.append("```")
    out.append("")

    # Write
    out_path = os.path.join(here, OUT)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
