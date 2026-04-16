"""Rater-reliability pipeline.

Two questions answered in sequence:

(1) **Scene-individuation reliability.**
    Per coder pair: did both raters point to the same narrative passage as a
    hallucinatory scene? Metrics: Jaccard over scene sets, |A−B| count
    asymmetry, Cohen's κ approximated at the bin level (from scene_bins.csv
    if present; otherwise Jaccard + asymmetry alone).

(2) **Attribute-classification reliability** (conditional on shared scenes).
    For every scene-level taxonomy item, restricted to _AB (both-rater)
    scenes, compute Cohen's κ and prevalence-adjusted kappa (PABAK) on
    the binary A-coded vs B-coded decision.  Summaries: per L1 section,
    per coder pair, per substance, grand mean.  Per-scene Jaccard over
    tag sets gives a second, scene-centred view.

Outputs (1.Recoding/analysis/reliability/):
    scene_individuation.csv          — per coder pair
    attribute_kappa_by_item.csv      — per (coder_pair, item)
    attribute_kappa_by_section.csv   — per (coder_pair, L1 section)
    attribute_kappa_summary.csv      — per coder pair overall
    per_scene_jaccard.csv            — per _AB scene tag-set Jaccard
    RELIABILITY_REPORT.md            — narrative summary

Kappa interpretation (Landis & Koch 1977):
    <0    : worse than chance
    .00–.20 : slight
    .21–.40 : fair
    .41–.60 : moderate
    .61–.80 : substantial
    .81–1.00: almost perfect
Caveats: κ is known to collapse toward zero under very low prevalence even
when observed agreement is high ("kappa paradox"). We report observed
agreement and prevalence-adjusted kappa (PABAK) alongside κ so that
low-prevalence items are not unfairly penalised.
"""
# ======================================================================
# AI DIRECTIVE — read AI_DIRECTIVE.md at repo root
# Stage 1 of this project measures INTER-RATER CONSISTENCY ON SCENE
# INDIVIDUATION ONLY.  This reliability pipeline extends Stage 1 by
# quantifying (conditional on shared scenes) how often both raters
# agreed on attribute tags — a preview of Stage 2.  The attribute
# metrics here are DESCRIPTIVE.  They do not resolve or adjudicate
# which rater's tag is "correct" on a given scene; both rater
# subjective judgements remain the primary data.
# ======================================================================
import os, csv, math
from collections import defaultdict, Counter

DATA_DIR = "../data"
OUT_DIR  = "../analysis/reliability"


def load(name, base=DATA_DIR):
    path = os.path.join(os.path.dirname(__file__), base, name)
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def truthy(s):
    return str(s).strip().lower() in ("true", "1", "yes", "t")


# ---------------- metrics ----------------

def cohens_kappa(a, b, c, d):
    """2x2 agreement table: a=both-yes, b=A-yes-B-no, c=A-no-B-yes, d=both-no.
    Returns (kappa, observed_agreement, expected_agreement, n, prevalence,
             pabak, se_kappa).
    """
    n = a + b + c + d
    if n == 0:
        return (None, None, None, 0, None, None, None)
    p_o = (a + d) / n
    p_A_yes = (a + b) / n
    p_B_yes = (a + c) / n
    p_e = p_A_yes * p_B_yes + (1 - p_A_yes) * (1 - p_B_yes)
    if p_e == 1.0:
        kappa = 1.0 if p_o == 1.0 else 0.0
    else:
        kappa = (p_o - p_e) / (1 - p_e)
    # Prevalence-adjusted, bias-adjusted kappa: PABAK = 2*p_o - 1
    pabak = 2 * p_o - 1
    # Standard error of Cohen's kappa (Fleiss et al. 1969 approximation)
    if 0 < p_e < 1 and n > 0:
        var = (p_o * (1 - p_o)) / (n * (1 - p_e) ** 2)
        se = math.sqrt(var) if var > 0 else 0.0
    else:
        se = 0.0
    prevalence = (a * 2 + b + c) / (2 * n)  # mean tagging rate across both raters
    return (kappa, p_o, p_e, n, prevalence, pabak, se)


def jaccard(A_set, B_set):
    if not A_set and not B_set:
        return None
    union = A_set | B_set
    inter = A_set & B_set
    return len(inter) / len(union) if union else None


def kappa_label(k):
    if k is None:
        return "n/a"
    if k < 0:       return "worse-than-chance"
    if k < 0.20:    return "slight"
    if k < 0.40:    return "fair"
    if k < 0.60:    return "moderate"
    if k < 0.80:    return "substantial"
    return "almost-perfect"


# ---------------- main ----------------

def main():
    here = os.path.dirname(__file__)
    os.makedirs(os.path.join(here, OUT_DIR), exist_ok=True)

    trips      = load("trips.csv")
    scenes     = load("scenes.csv")
    codes      = load("codes.csv")
    taxonomy   = load("taxonomy.csv")

    trips_by_id     = {t["trip_id"]: t for t in trips}
    scenes_by_id    = {s["scene_id"]: s for s in scenes}
    taxonomy_by_id  = {t["item_id"]: t for t in taxonomy}

    # Coder pair label
    def pair_key(trip_id):
        t = trips_by_id.get(trip_id, {})
        sub = t.get("substance", "?")
        blk = t.get("block", "?")
        return f"{sub.title()[:4]} {blk}: {t.get('coder_A','?')} × {t.get('coder_B','?')}"

    # Group scenes by pair
    scenes_by_pair = defaultdict(list)
    for s in scenes:
        scenes_by_pair[pair_key(s["trip_id"])].append(s)

    # ============== (1) Scene-individuation reliability ==============
    INDIV_COLS = [
        "coder_pair", "substance", "block", "coder_A", "coder_B",
        "n_trips", "n_scenes_total", "n_both", "n_only_A", "n_only_B",
        "n_scenes_A", "n_scenes_B",
        "jaccard_scenes", "asymmetry_ratio",
        "percent_convergent",
    ]
    indiv_rows = []
    for pair, ss in sorted(scenes_by_pair.items()):
        t0 = trips_by_id.get(ss[0]["trip_id"], {})
        n_both = sum(1 for s in ss if s["rater_status"] == "both")
        n_A    = sum(1 for s in ss if s["rater_status"] == "only_A")
        n_B    = sum(1 for s in ss if s["rater_status"] == "only_B")
        n_tot  = n_both + n_A + n_B
        n_sc_A = n_both + n_A
        n_sc_B = n_both + n_B
        union  = n_tot
        jacc   = n_both / union if union else None
        asym   = abs(n_A - n_B) / n_tot if n_tot else None
        pct    = 100.0 * n_both / n_tot if n_tot else None
        n_trips = len({s["trip_id"] for s in ss})
        indiv_rows.append({
            "coder_pair": pair,
            "substance": t0.get("substance", ""),
            "block": t0.get("block", ""),
            "coder_A": t0.get("coder_A", ""),
            "coder_B": t0.get("coder_B", ""),
            "n_trips": n_trips,
            "n_scenes_total": n_tot,
            "n_both": n_both, "n_only_A": n_A, "n_only_B": n_B,
            "n_scenes_A": n_sc_A, "n_scenes_B": n_sc_B,
            "jaccard_scenes": round(jacc, 4) if jacc is not None else "",
            "asymmetry_ratio": round(asym, 4) if asym is not None else "",
            "percent_convergent": round(pct, 2) if pct is not None else "",
        })
    with open(os.path.join(here, OUT_DIR, "scene_individuation.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=INDIV_COLS)
        w.writeheader()
        for r in indiv_rows:
            w.writerow(r)

    # ============== (2) Attribute-classification reliability ==============
    # Universe per coder pair: the set of _AB scenes (both individuated).
    ab_scenes_by_pair = defaultdict(list)
    for s in scenes:
        if s["rater_status"] == "both":
            ab_scenes_by_pair[pair_key(s["trip_id"])].append(s["scene_id"])

    # For each (scene_id, item_id), which raters coded it
    coded = defaultdict(set)   # (scene_id, item_id) -> set of {"A","B"}
    for c in codes:
        if truthy(c.get("is_scene_level", "False")) and c.get("scene_id"):
            coded[(c["scene_id"], c["item_id"])].add(c["rater"])

    # Scene-level taxonomy items only
    scene_level_items = [t for t in taxonomy if truthy(t["is_scene_level"])]

    # For each (coder_pair, item), tabulate the 2x2 across AB scenes
    ITEM_COLS = [
        "coder_pair", "substance", "block", "item_id",
        "level_1", "level_2", "level_3",
        "n_shared_scenes", "n_A_coded", "n_B_coded",
        "both_yes", "A_only", "B_only", "both_no",
        "observed_agreement", "expected_agreement",
        "prevalence", "cohens_kappa", "kappa_SE", "pabak",
        "kappa_label",
    ]
    item_rows = []
    pair_substance = {p: next((r["substance"] for r in indiv_rows if r["coder_pair"] == p), "")
                      for p in ab_scenes_by_pair}
    pair_block = {p: next((r["block"] for r in indiv_rows if r["coder_pair"] == p), "")
                  for p in ab_scenes_by_pair}

    for pair, ab_sids in sorted(ab_scenes_by_pair.items()):
        for it in scene_level_items:
            a_yes = b_yes = ab_cell = ao_cell = bo_cell = bn_cell = 0
            for sid in ab_sids:
                raters = coded.get((sid, it["item_id"]), set())
                A = "A" in raters
                B = "B" in raters
                if A: a_yes += 1
                if B: b_yes += 1
                if A and B: ab_cell += 1
                elif A:     ao_cell += 1
                elif B:     bo_cell += 1
                else:       bn_cell += 1
            n = ab_cell + ao_cell + bo_cell + bn_cell
            # Only emit rows where at least one rater coded this item on at least one AB scene
            if a_yes == 0 and b_yes == 0:
                continue
            k, po, pe, _, prev, pabak, se = cohens_kappa(ab_cell, ao_cell, bo_cell, bn_cell)
            item_rows.append({
                "coder_pair": pair,
                "substance":  pair_substance.get(pair, ""),
                "block":      pair_block.get(pair, ""),
                "item_id":    it["item_id"],
                "level_1":    it["level_1"],
                "level_2":    it["level_2"],
                "level_3":    it["level_3"],
                "n_shared_scenes": n,
                "n_A_coded":  a_yes,
                "n_B_coded":  b_yes,
                "both_yes":   ab_cell,
                "A_only":     ao_cell,
                "B_only":     bo_cell,
                "both_no":    bn_cell,
                "observed_agreement": round(po, 4) if po is not None else "",
                "expected_agreement": round(pe, 4) if pe is not None else "",
                "prevalence":         round(prev, 4) if prev is not None else "",
                "cohens_kappa":       round(k, 4) if k is not None else "",
                "kappa_SE":           round(se, 4) if se is not None else "",
                "pabak":              round(pabak, 4) if pabak is not None else "",
                "kappa_label":        kappa_label(k),
            })
    with open(os.path.join(here, OUT_DIR, "attribute_kappa_by_item.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ITEM_COLS)
        w.writeheader()
        for r in item_rows:
            w.writerow(r)

    # ---- Per (coder_pair, L1 section) rollup ----
    SEC_COLS = [
        "coder_pair", "substance", "level_1",
        "n_items_active", "n_shared_scenes",
        "mean_observed_agreement", "mean_pabak",
        "weighted_mean_kappa", "kappa_label",
        "n_items_above_0_4_kappa", "n_items_above_0_6_kappa",
    ]
    sec_rows = []
    from collections import defaultdict as dd
    by_pair_sec = dd(list)
    for r in item_rows:
        by_pair_sec[(r["coder_pair"], r["level_1"])].append(r)
    for (pair, L1), items in sorted(by_pair_sec.items()):
        ks = [r["cohens_kappa"] for r in items if r["cohens_kappa"] != ""]
        pos = [r["observed_agreement"] for r in items if r["observed_agreement"] != ""]
        pabaks = [r["pabak"] for r in items if r["pabak"] != ""]
        ns  = [r["n_shared_scenes"] for r in items]
        # weighted mean kappa by n_shared_scenes
        total_n = sum(ns) if ns else 0
        if ks and total_n:
            weights = [r["n_shared_scenes"] for r in items if r["cohens_kappa"] != ""]
            wkappa = sum(k * w for k, w in zip(ks, weights)) / sum(weights)
        else:
            wkappa = None
        above_04 = sum(1 for k in ks if k >= 0.40)
        above_06 = sum(1 for k in ks if k >= 0.60)
        sec_rows.append({
            "coder_pair": pair,
            "substance":  pair_substance.get(pair, ""),
            "level_1":    L1,
            "n_items_active": len(items),
            "n_shared_scenes": max(ns) if ns else 0,
            "mean_observed_agreement": round(sum(pos)/len(pos), 4) if pos else "",
            "mean_pabak":              round(sum(pabaks)/len(pabaks), 4) if pabaks else "",
            "weighted_mean_kappa":     round(wkappa, 4) if wkappa is not None else "",
            "kappa_label":             kappa_label(wkappa),
            "n_items_above_0_4_kappa": above_04,
            "n_items_above_0_6_kappa": above_06,
        })
    with open(os.path.join(here, OUT_DIR, "attribute_kappa_by_section.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SEC_COLS)
        w.writeheader()
        for r in sec_rows:
            w.writerow(r)

    # ---- Per coder-pair overall ----
    PAIR_COLS = [
        "coder_pair", "substance", "block", "coder_A", "coder_B",
        "n_shared_scenes", "n_items_active",
        "mean_observed_agreement", "weighted_mean_kappa", "mean_pabak",
        "kappa_label",
        "n_items_above_0_4", "n_items_above_0_6", "n_items_below_0_2",
    ]
    pair_rows = []
    by_pair = defaultdict(list)
    for r in item_rows:
        by_pair[r["coder_pair"]].append(r)
    for pair, items in sorted(by_pair.items()):
        t0 = next(iter(trips_by_id[s["trip_id"]]
                       for s in scenes if pair_key(s["trip_id"]) == pair), None)
        # extract coder info from indiv_rows
        indiv = next((r for r in indiv_rows if r["coder_pair"] == pair), {})
        ks = [r["cohens_kappa"] for r in items if r["cohens_kappa"] != ""]
        pos = [r["observed_agreement"] for r in items if r["observed_agreement"] != ""]
        pabaks = [r["pabak"] for r in items if r["pabak"] != ""]
        ns  = [r["n_shared_scenes"] for r in items]
        total_n = sum(ns) if ns else 0
        if ks and total_n:
            weights = [r["n_shared_scenes"] for r in items if r["cohens_kappa"] != ""]
            wkappa = sum(k * w for k, w in zip(ks, weights)) / sum(weights)
        else:
            wkappa = None
        pair_rows.append({
            "coder_pair": pair,
            "substance":  indiv.get("substance", ""),
            "block":      indiv.get("block", ""),
            "coder_A":    indiv.get("coder_A", ""),
            "coder_B":    indiv.get("coder_B", ""),
            "n_shared_scenes": max(ns) if ns else 0,
            "n_items_active":  len(items),
            "mean_observed_agreement": round(sum(pos)/len(pos), 4) if pos else "",
            "weighted_mean_kappa":     round(wkappa, 4) if wkappa is not None else "",
            "mean_pabak":              round(sum(pabaks)/len(pabaks), 4) if pabaks else "",
            "kappa_label":             kappa_label(wkappa),
            "n_items_above_0_4": sum(1 for k in ks if k >= 0.40),
            "n_items_above_0_6": sum(1 for k in ks if k >= 0.60),
            "n_items_below_0_2": sum(1 for k in ks if k < 0.20),
        })
    with open(os.path.join(here, OUT_DIR, "attribute_kappa_summary.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=PAIR_COLS)
        w.writeheader()
        for r in pair_rows:
            w.writerow(r)

    # ---- Per-scene Jaccard on tag sets ----
    SCENE_JAC_COLS = [
        "scene_id", "trip_id", "substance", "coder_pair",
        "n_A_tags", "n_B_tags", "n_shared_tags", "n_union_tags", "jaccard",
    ]
    scene_jac_rows = []
    for pair, ab_sids in sorted(ab_scenes_by_pair.items()):
        for sid in ab_sids:
            A_items = {it for (s, it), rs in coded.items() if s == sid and "A" in rs}
            B_items = {it for (s, it), rs in coded.items() if s == sid and "B" in rs}
            union = A_items | B_items
            inter = A_items & B_items
            jac = len(inter) / len(union) if union else None
            trip = trips_by_id.get(scenes_by_id[sid]["trip_id"], {})
            scene_jac_rows.append({
                "scene_id": sid,
                "trip_id":  scenes_by_id[sid]["trip_id"],
                "substance": trip.get("substance", ""),
                "coder_pair": pair,
                "n_A_tags": len(A_items),
                "n_B_tags": len(B_items),
                "n_shared_tags": len(inter),
                "n_union_tags":  len(union),
                "jaccard":  round(jac, 4) if jac is not None else "",
            })
    with open(os.path.join(here, OUT_DIR, "per_scene_jaccard.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SCENE_JAC_COLS)
        w.writeheader()
        for r in scene_jac_rows:
            w.writerow(r)

    # ============== RELIABILITY_REPORT.md ==============
    md = []
    md.append("# Rater reliability report")
    md.append("")
    md.append("*Generated by `1.Recoding/scripts/19_rater_reliability.py`.*")
    md.append("")
    md.append("Two levels of rater reliability, measured independently:")
    md.append("")
    md.append("1. **Scene-individuation reliability** — Stage 1 question: "
              "did both raters point at the same narrative passage as a hallucinatory scene?")
    md.append("2. **Attribute-classification reliability** — Stage-2 preview: "
              "conditional on both raters having individuated a scene, "
              "did they assign the same taxonomy tags (modality, object class, "
              "modal status, dynamics, illusion vs incrusted, etc.)? "
              "Reported per (coder pair × item) as Cohen's κ with observed "
              "agreement and prevalence-adjusted kappa (PABAK) alongside.")
    md.append("")

    # Individuation table
    md.append("## Scene-individuation reliability — per coder pair")
    md.append("")
    md.append("| coder pair | n trips | n scenes | both | only A | only B | Jaccard | % convergent | count asymmetry |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in indiv_rows:
        md.append(f"| {r['coder_pair']} | {r['n_trips']} | {r['n_scenes_total']} | "
                  f"{r['n_both']} | {r['n_only_A']} | {r['n_only_B']} | "
                  f"{r['jaccard_scenes']} | {r['percent_convergent']}% | {r['asymmetry_ratio']} |")
    md.append("")
    md.append("*Jaccard(scenes) = n_both / (n_both + n_only_A + n_only_B). "
              "Asymmetry = |n_only_A − n_only_B| / n_total — flags pairs where "
              "one rater individuated systematically more than the other.*")
    md.append("")

    # Coder-pair overall attribute table
    md.append("## Attribute-classification reliability — per coder pair (overall)")
    md.append("")
    md.append("Weighted across all scene-level taxonomy items that were "
              "actually used by either rater on at least one _AB scene. "
              "Universe per pair = the consensus-individuated (_AB) scenes.")
    md.append("")
    md.append("| coder pair | n AB scenes | n items | obs. agreement | weighted κ | PABAK | κ label | items κ≥0.6 | items κ≥0.4 | items κ<0.2 |")
    md.append("|---|---:|---:|---:|---:|---:|---|---:|---:|---:|")
    for r in pair_rows:
        md.append(f"| {r['coder_pair']} | {r['n_shared_scenes']} | {r['n_items_active']} | "
                  f"{r['mean_observed_agreement']} | {r['weighted_mean_kappa']} | "
                  f"{r['mean_pabak']} | {r['kappa_label']} | "
                  f"{r['n_items_above_0_6']} | {r['n_items_above_0_4']} | {r['n_items_below_0_2']} |")
    md.append("")

    # Section rollup
    md.append("## Attribute reliability — per L1 section × coder pair")
    md.append("")
    md.append("Items grouped by top-level taxonomic section (e.g. Visual hallucination, "
              "Type of visual alteration, Modal status, Emotion). "
              "Weighted-κ interpretation: slight / fair / moderate / substantial / almost-perfect.")
    md.append("")
    md.append("| coder pair | section | n items | obs. agreement | weighted κ | PABAK | label |")
    md.append("|---|---|---:|---:|---:|---:|---|")
    for r in sec_rows:
        md.append(f"| {r['coder_pair']} | {r['level_1']} | {r['n_items_active']} | "
                  f"{r['mean_observed_agreement']} | {r['weighted_mean_kappa']} | "
                  f"{r['mean_pabak']} | {r['kappa_label']} |")
    md.append("")

    # Per-scene Jaccard summary
    md.append("## Per-scene tag-set Jaccard (shared scenes)")
    md.append("")
    sub_stats = defaultdict(list)
    pair_stats = defaultdict(list)
    for r in scene_jac_rows:
        if r["jaccard"] != "":
            sub_stats[r["substance"]].append(r["jaccard"])
            pair_stats[r["coder_pair"]].append(r["jaccard"])
    md.append("Scene-centred view: for each _AB scene, Jaccard over the two raters' tag sets "
              "(|A ∩ B| / |A ∪ B|). Complement of the item-level view. High mean Jaccard means "
              "raters tag each shared scene with largely overlapping labels; low mean means they "
              "agree a scene exists but classify it differently.")
    md.append("")
    md.append("| grouping | n scenes | mean Jaccard | median Jaccard | min | max |")
    md.append("|---|---:|---:|---:|---:|---:|")
    for sub, vals in sorted(sub_stats.items()):
        vals_s = sorted(vals)
        md.append(f"| substance: {sub} | {len(vals)} | {sum(vals)/len(vals):.3f} | "
                  f"{vals_s[len(vals_s)//2]:.3f} | {min(vals):.3f} | {max(vals):.3f} |")
    for pair, vals in sorted(pair_stats.items()):
        vals_s = sorted(vals)
        md.append(f"| pair: {pair} | {len(vals)} | {sum(vals)/len(vals):.3f} | "
                  f"{vals_s[len(vals_s)//2]:.3f} | {min(vals):.3f} | {max(vals):.3f} |")
    md.append("")

    # Top best and worst items
    items_with_kappa = [r for r in item_rows if r["cohens_kappa"] != ""]
    md.append("## Best-agreeing items (highest κ, any pair, n_shared_scenes ≥ 5)")
    md.append("")
    md.append("| coder pair | item | level_1 | n AB | A_tagged | B_tagged | κ | PABAK | label |")
    md.append("|---|---|---|---:|---:|---:|---:|---:|---|")
    best = [r for r in items_with_kappa if r["n_shared_scenes"] >= 5]
    best.sort(key=lambda r: -r["cohens_kappa"])
    for r in best[:15]:
        md.append(f"| {r['coder_pair']} | `{r['item_id']}` | {r['level_1']} | "
                  f"{r['n_shared_scenes']} | {r['n_A_coded']} | {r['n_B_coded']} | "
                  f"{r['cohens_kappa']} | {r['pabak']} | {r['kappa_label']} |")
    md.append("")
    md.append("## Worst-agreeing items (lowest κ, any pair, n_shared_scenes ≥ 5)")
    md.append("")
    md.append("| coder pair | item | level_1 | n AB | A_tagged | B_tagged | κ | PABAK | label |")
    md.append("|---|---|---|---:|---:|---:|---:|---:|---|")
    worst = sorted(best, key=lambda r: r["cohens_kappa"])
    for r in worst[:15]:
        md.append(f"| {r['coder_pair']} | `{r['item_id']}` | {r['level_1']} | "
                  f"{r['n_shared_scenes']} | {r['n_A_coded']} | {r['n_B_coded']} | "
                  f"{r['cohens_kappa']} | {r['pabak']} | {r['kappa_label']} |")
    md.append("")
    md.append("## Caveats")
    md.append("")
    md.append("- **Kappa paradox:** low-prevalence items (e.g. a tag used on only 1 or 2 AB scenes) "
              "can yield low κ even when raters agree on all but one case. Read κ together with "
              "observed agreement and PABAK.")
    md.append("- **Small n per pair:** each coder pair has at most ~10 trips and ~45 AB scenes, so "
              "κ standard errors per item are large. Use pair-level summaries to discuss patterns, "
              "individual items only when n_shared_scenes is ≥ 10.")
    md.append("- **Scope:** attribute metrics use only the _AB (consensus-individuated) scenes. "
              "Solo-scene attribute disagreement is not tested here — it is 100% by construction "
              "(the other rater tagged nothing) and would conflate individuation with classification.")
    md.append("")

    with open(os.path.join(here, OUT_DIR, "RELIABILITY_REPORT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # ---- stdout summary ----
    print("wrote:", os.path.abspath(os.path.join(here, OUT_DIR)))
    for fn in ("scene_individuation.csv", "attribute_kappa_by_item.csv",
               "attribute_kappa_by_section.csv", "attribute_kappa_summary.csv",
               "per_scene_jaccard.csv", "RELIABILITY_REPORT.md"):
        p = os.path.join(here, OUT_DIR, fn)
        print(f"  {fn:<40} {os.path.getsize(p)//1024} KB")


if __name__ == "__main__":
    main()
