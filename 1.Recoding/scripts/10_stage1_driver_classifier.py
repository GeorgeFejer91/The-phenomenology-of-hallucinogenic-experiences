"""Stage-1 driver classifier.

Every solo scene (rater_status != 'both') gets classified into one of six
driver categories based on why only one rater individuated it. The driver
category is appended to the scene_id as a suffix extension, creating a
data-structure-level taxonomy that encodes the source of inter-rater
discrepancy directly in the scene identifier:

  Shared scenes (unchanged):                {trip}_S{NN}_AB
  R1 Sensory amplification:                 {trip}_S{NN}_A_AMP   /  _B_AMP
  R2 / R5 Fragment of shared scene:         {trip}_S{NN}_A_FRAG  /  _B_FRAG
       (with parent_scene_id link to the other rater's encompassing scene)
  R3 Ambiguity (thought / memory / metaphor): {trip}_S{NN}_A_AMB  /  _B_AMB
  R4 Somatic-scope error:                   {trip}_S{NN}_A_SOMA  /  _B_SOMA
  R6 Genuine miss (reconciliation needed):  {trip}_S{NN}_A_RCL   /  _B_RCL

This is NOT a data mutation in the destructive sense — the canonical
scenes.csv is rewritten but scene_ids remain deterministic from the YAML
adjudications and classifier heuristics, so any regeneration reproduces
the same IDs.

Classification heuristics (applied in order, first match wins):
  1. Span overlap with a shared (_AB) scene in same trip → R2/R5 FRAG
     with parent_scene_id = that shared scene
  2. Span overlap with an opposite-rater solo scene in same trip → R5 FRAG
     with parent_scene_id = that solo scene (lump-split case)
  3. Metacognitive keywords in canonical_desc → R3 AMB
  4. Self-transformation / interoceptive keywords in canonical_desc AND
     rater coded it as tactile-hallucination → R4 SOMA
  5. Ambient perceptual-amplification keywords AND no explicit object → R1 AMP
  6. Otherwise → R6 RCL (flag for reconciliation)
"""
import os, csv, re
from collections import defaultdict

DATA = "../data"


def load(path):
    with open(os.path.join(os.path.dirname(__file__), DATA, path), encoding="utf-8") as f:
        return list(csv.DictReader(f))


# Keyword heuristics (lowercase)
R3_AMBIGUITY_PATTERNS = [
    r"\bpictured\b", r"\bimagined\b", r"\bimagining\b",
    r"\bremembered\b", r"\bmemory of\b", r"\bmemories\b",
    r"\brealised\b", r"\brealized\b",
    r"\bthought of\b", r"\bfancied\b", r"\bidea of\b",
    r"\bunderstood that\b", r"\bknew that\b",
    r"\bfelt like i was\b",  # covers "felt like I was at my funeral"
]

R4_SOMATIC_PATTERNS = [
    r"\bbecame a\b", r"\bbecome very\b", r"\bi was a\b",
    r"\bbody split\b", r"\bbody dissolv", r"\bbody was split\b",
    r"\bde-animate", r"\bdeanimate",
    r"\bsinking into (myself|my body)\b",
    r"\bheartbeat\b", r"\bheart was\b",
    r"\bbeing split into two\b", r"\bspread out\b.*\bfascia\b",
    r"\bbody schema", r"\bown body",
    r"\bhumpty dumpty\b",
    r"\bfeather\b.*\bblown\b",
    r"\bsensory perception.*off scale\b",
]

R1_AMPLIFICATION_PATTERNS = [
    r"\bgloss(y|iness)\b",
    r"\bshimmer", r"\btracers?\b",
    r"\bcolou?rs? (brighter|more|changing|pop|more vivid|saturated)",
    r"\bbrighter\b", r"\bmore defined\b", r"\bmore vivid\b",
    r"\bsparkles?\b", r"\bflicker",
    r"\bvision (?:was |became )?(blur|fuzz)",
    r"\bripples?\b", r"\bglow\b",
    r"\botherworldly glow\b",
    r"\beyes? (cannot|couldn'?t) focus\b",
    r"\bdepth perception\b",
    r"\bcolour-morph", r"\bcolor-morph",
    r"\bamplified (colour|color|sound)",
    r"\bkaleidoscope of colou?rs\b",
]


def match_any(text, patterns):
    low = (text or "").lower()
    return any(re.search(p, low) for p in patterns)


def parse_span(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


def spans_overlap(a0, a1, b0, b1):
    if None in (a0, a1, b0, b1):
        return False
    return max(a0, b0) < min(a1, b1)


def classify_solo(scene, trip_scenes, codes_for_scene):
    """Return (driver_code, parent_scene_id_or_empty, rationale)."""
    sid = scene["scene_id"]
    status = scene["rater_status"]
    rater_letter = "A" if status == "only_A" else "B"
    other_letter = "B" if rater_letter == "A" else "A"
    a0 = parse_span(scene["canonical_span_start"])
    a1 = parse_span(scene["canonical_span_end"])
    desc = (scene["canonical_desc"] or "").lower()

    # Rule 1+2: span-overlap fragments
    best_parent = None
    best_parent_status = None
    for other in trip_scenes:
        if other["scene_id"] == sid:
            continue
        b0 = parse_span(other["canonical_span_start"])
        b1 = parse_span(other["canonical_span_end"])
        if not spans_overlap(a0, a1, b0, b1):
            continue
        # Prefer shared parent, then opposite-rater solo parent
        if other["rater_status"] == "both" and best_parent_status != "both":
            best_parent = other; best_parent_status = "both"
        elif other["rater_status"] == f"only_{other_letter}" and best_parent_status is None:
            best_parent = other; best_parent_status = other["rater_status"]
    if best_parent is not None:
        return ("FRAG", best_parent["scene_id"],
                f"Span overlaps {best_parent_status} parent scene; treated as fragment")

    # Rule 3: ambiguity (thought/memory/metaphor)
    if match_any(desc, R3_AMBIGUITY_PATTERNS):
        return ("AMB", "", "Metacognitive keywords — thought/memory/metaphor content")

    # Rule 4: somatic scope error (keywords + tactile-hallucination tag)
    has_tactile_code = any(c.get("level_1", "") == "Tactile hallucination" for c in codes_for_scene)
    if match_any(desc, R4_SOMATIC_PATTERNS):
        # Even without tactile tag, if the keywords are strongly somatic, call it SOMA
        return ("SOMA", "", "Self-transformation / interoceptive content")
    if has_tactile_code and any(re.search(r"\bbody\b|\bi was\b|\bbecame\b", desc) for _ in [0]):
        return ("SOMA", "", "Tactile-hallucination tagged for body/self-transformation")

    # Rule 5: sensory amplification
    if match_any(desc, R1_AMPLIFICATION_PATTERNS):
        return ("AMP", "", "Ambient perceptual-amplification content, no explicit object")

    # Rule 6: residual — genuine miss
    return ("RCL", "", "No automatic classification; likely genuine miss by other rater")


def build_new_scene_id(base_scene_id, status, driver_code):
    """Convert existing scene_id to include driver suffix.

    Existing shared scenes keep their _AB suffix unchanged.
    Solo scenes get an additional _DRIVER suffix appended to _A or _B.
    """
    if status == "both":
        return base_scene_id
    # base_scene_id already ends in _A or _B (or modifier like _LUMPA)
    # Append driver
    return f"{base_scene_id}_{driver_code}"


def main():
    here = os.path.dirname(__file__)
    scenes = load("scenes.csv")
    codes = load("codes.csv")

    # Group codes by scene_id for quick lookup
    codes_by_scene = defaultdict(list)
    for c in codes:
        if c["scene_id"]:
            codes_by_scene[c["scene_id"]].append(c)

    # Group scenes by trip for span-overlap checks
    by_trip = defaultdict(list)
    for s in scenes:
        by_trip[s["trip_id"]].append(s)

    # Classify every solo scene
    driver_assignments = {}  # scene_id -> (driver, parent, rationale)
    for s in scenes:
        if s["rater_status"] == "both":
            driver_assignments[s["scene_id"]] = (None, "", "")
            continue
        driver, parent, rationale = classify_solo(
            s, by_trip[s["trip_id"]], codes_by_scene[s["scene_id"]])
        driver_assignments[s["scene_id"]] = (driver, parent, rationale)

    # Rewrite scene_ids with driver suffix
    id_map = {}  # old_scene_id -> new_scene_id
    for s in scenes:
        driver, parent, rationale = driver_assignments[s["scene_id"]]
        if driver is None:
            id_map[s["scene_id"]] = s["scene_id"]
        else:
            id_map[s["scene_id"]] = build_new_scene_id(s["scene_id"], s["rater_status"], driver)

    # Apply renames to scenes, codes, agreement_flags, scene_bins
    for s in scenes:
        old = s["scene_id"]
        s["scene_id"] = id_map[old]
        # If FRAG, also rewrite parent_scene_id
        driver, parent, rationale = driver_assignments[old]
        if driver == "FRAG" and parent:
            # parent may or may not have been renamed (both-status parents keep their id)
            s["parent_scene_id"] = id_map.get(parent, parent)
        # Add stage1_driver and rationale columns
        s["stage1_driver"] = driver or ""
        s["stage1_rationale"] = rationale

    for c in codes:
        if c["scene_id"]:
            c["scene_id"] = id_map.get(c["scene_id"], c["scene_id"])
        if c.get("original_scene_id"):
            c["original_scene_id"] = id_map.get(c["original_scene_id"], c["original_scene_id"])

    # Rewrite scenes.csv with stage1_driver column
    scenes_cols = ["scene_id","trip_id","substance","block","rater_status",
                   "stage1_driver","stage1_rationale",
                   "parent_scene_id","lump_split_type",
                   "canonical_desc","canonical_span_start","canonical_span_end",
                   "rater_A_refs","rater_B_refs","adjudicator_note"]
    with open(os.path.join(here, DATA, "scenes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=scenes_cols, extrasaction="ignore")
        w.writeheader()
        for r in scenes:
            w.writerow(r)

    # Rewrite codes.csv (same cols + preserve existing)
    codes_cols = ["code_id","scene_id","original_scene_id","trip_id","substance","block",
                  "rater","coder_name",
                  "item_id","item_path","level_1","level_2","level_3",
                  "is_scene_level","scope_normalised","trip_level_multiplicity","excerpt"]
    with open(os.path.join(here, DATA, "codes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=codes_cols, extrasaction="ignore")
        w.writeheader()
        for r in codes:
            w.writerow(r)

    # Also update agreement_flags.csv scene_ids (they only reference shared scenes which don't get renamed)
    # scene_bins.csv + bins_summary.csv likewise reference scene_ids
    for path in ("agreement_flags.csv",):
        rows = load(path)
        for r in rows:
            if r.get("scene_id"):
                r["scene_id"] = id_map.get(r["scene_id"], r["scene_id"])
        if rows:
            with open(os.path.join(here, DATA, path), "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                for r in rows:
                    w.writerow(r)

    # Update analysis/scene_bins.csv + bins_summary.csv if present
    for ap in ("scene_bins.csv", "bins_summary.csv"):
        ap_path = os.path.join(here, "../analysis", ap)
        if os.path.exists(ap_path):
            with open(ap_path, encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            for r in rows:
                if r.get("scene_id"):
                    r["scene_id"] = id_map.get(r["scene_id"], r["scene_id"])
                if r.get("member_scene_ids"):
                    parts = [id_map.get(sid, sid) for sid in r["member_scene_ids"].split(";") if sid]
                    r["member_scene_ids"] = ";".join(parts)
            with open(ap_path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                for r in rows:
                    w.writerow(r)

    # Summary
    drivers = [d for (d, _, _) in driver_assignments.values() if d]
    from collections import Counter
    counts = Counter(drivers)
    print("Stage-1 driver classification summary")
    print("=" * 52)
    for driver in ("FRAG", "AMP", "AMB", "SOMA", "RCL"):
        n = counts.get(driver, 0)
        print(f"  {driver:<6}  n={n}")
    print(f"  TOTAL solo scenes classified: {sum(counts.values())}")

    # Per substance
    sub_counts = defaultdict(lambda: Counter())
    for s in scenes:
        if s["stage1_driver"]:
            sub_counts[s["substance"]][s["stage1_driver"]] += 1
    print()
    print("By substance:")
    for sub in sorted(sub_counts.keys()):
        print(f"  {sub}")
        for driver, n in sub_counts[sub].most_common():
            print(f"    {driver:<6} n={n}")


if __name__ == "__main__":
    main()
