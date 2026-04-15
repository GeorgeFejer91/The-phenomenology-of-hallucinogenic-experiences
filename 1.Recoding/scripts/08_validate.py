"""Validate the consolidated dataset for cross-condition analysis.

Checks:
  - every scene_id in codes.csv exists in scenes.csv
  - every trip_id in codes.csv / scenes.csv exists in trips.csv
  - every item_id in codes.csv exists in taxonomy.csv
  - every scene_id in agreement_flags.csv is status='both' in scenes.csv
  - every trip in trips.csv has both codes AND scenes
  - substance values are canonical {psilocybin, brugmansia}
  - block values are canonical {01-10, 11-20}
  - rater values are canonical {A, B}
  - is_scene_level has no scene-level items that are taxonomy trip-level
    (post-D4 normalisation invariant)
  - no duplicate (trip_id, rater, item_id) at trip-level (post-D5 dedup invariant)

Also prints cross-condition sanity statistics:
  - n trips per (substance, block)
  - n scenes per (substance, rater_status)
  - n codes per (substance, is_scene_level, rater)
  - % scope_normalised rows per trip-level section
"""
# ======================================================================
# AI DIRECTIVE — read AI_DIRECTIVE.md at repo root
# Stage 1 of this project measures INTER-RATER CONSISTENCY ON SCENE
# INDIVIDUATION ONLY.  The atomic question is:
#   For every narrative passage, did BOTH raters individuate it as a
#   hallucinatory scene?
# Core analytical question for every only-one-rater scene:
#   MISS       - the other rater overlooked a clearly hallucinatory passage
#                they should have coded (rater-compliance gap), OR
#   AMBIGUITY  - the PDF Guidelines do not cleanly cover this edge case,
#                so both decisions are defensible (instruction-design gap).
# The rater's subjective judgement about what is a hallucinatory scene is
# the PRIMARY DATA.  Preserve it.  Do NOT resolve attribute-level
# disagreement (illusion vs incrusted, object-class, etc.) — that is
# Stage 2, deferred.  See also 1.Recoding/STAGE1_SCOPE.json
# ======================================================================
import os, csv
from collections import defaultdict, Counter

DATA = "../data"


def load(path):
    with open(os.path.join(os.path.dirname(__file__), DATA, path), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    trips = load("trips.csv")
    scenes = load("scenes.csv")
    codes = load("codes.csv")
    flags = load("agreement_flags.csv")
    style = load("rater_style.csv")
    tax = load("taxonomy.csv")

    trip_ids = {t["trip_id"] for t in trips}
    scene_ids = {s["scene_id"] for s in scenes}
    item_ids = {t["item_id"] for t in tax}
    trip_scene_status = {s["scene_id"]: s["rater_status"] for s in scenes}
    taxonomy_is_trip_level = {t["item_id"]: (t["is_trip_level"] == "True") for t in tax}

    errors = []
    warnings = []

    # 1. scene_id integrity
    for c in codes:
        if c["scene_id"] and c["scene_id"] not in scene_ids:
            errors.append(f"codes.scene_id {c['scene_id']} missing from scenes.csv")

    # 2. trip_id integrity
    for c in codes:
        if c["trip_id"] not in trip_ids:
            errors.append(f"codes.trip_id {c['trip_id']} missing from trips.csv")
    for s in scenes:
        if s["trip_id"] not in trip_ids:
            errors.append(f"scenes.trip_id {s['trip_id']} missing from trips.csv")

    # 3. item_id integrity
    for c in codes:
        if c["item_id"] not in item_ids:
            errors.append(f"codes.item_id {c['item_id']} missing from taxonomy.csv")

    # 4. agreement_flags invariant: only shared scenes
    for f in flags:
        if trip_scene_status.get(f["scene_id"]) != "both":
            errors.append(f"agreement_flags.scene_id {f['scene_id']} is not status=both")

    # 5. every trip has at least one scene
    trips_with_scenes = {s["trip_id"] for s in scenes}
    missing_scenes = trip_ids - trips_with_scenes
    if missing_scenes:
        warnings.append(f"trips without scenes: {missing_scenes}")

    # 6. canonical substance / block / rater
    canonical_sub = {"psilocybin", "brugmansia"}
    canonical_blk = {"01-10", "11-20"}
    for t in trips:
        if t["substance"] not in canonical_sub:
            errors.append(f"trips.substance {t['substance']!r} not canonical")
        if t["block"] not in canonical_blk:
            errors.append(f"trips.block {t['block']!r} not canonical")
    for c in codes:
        if c["rater"] not in ("A", "B"):
            errors.append(f"codes.rater {c['rater']!r} not canonical")

    # 7. D4 post-normalisation invariant: no scene-level row carrying a taxonomy-trip-level item
    for c in codes:
        if c["is_scene_level"] == "True" and taxonomy_is_trip_level.get(c["item_id"]):
            errors.append(
                f"D4 VIOLATION: code {c['code_id']} is_scene_level=True but item {c['item_id']} is taxonomy-trip-level")

    # 8. D5 post-dedup invariant: no duplicate (trip_id, rater, item_id) at trip level
    trip_keys = Counter((c["trip_id"], c["rater"], c["item_id"]) for c in codes if c["is_scene_level"] == "False")
    dup_trip_keys = {k: v for k, v in trip_keys.items() if v > 1}
    if dup_trip_keys:
        errors.append(f"D5 VIOLATION: duplicate trip-level (trip,rater,item) rows: {len(dup_trip_keys)}")
        for k, n in list(dup_trip_keys.items())[:5]:
            errors.append(f"  e.g. {k} count={n}")

    # -- Cross-condition sanity stats --
    print("=" * 72)
    print("CROSS-CONDITION SANITY STATS (for between-substance comparison)")
    print("=" * 72)

    # Trips per (substance, block)
    sub_blk = Counter((t["substance"], t["block"]) for t in trips)
    print("\nTrips per (substance, block):")
    for (sub, blk), n in sorted(sub_blk.items()):
        print(f"  {sub:<11} {blk:<6}  n_trips={n}")

    # Scenes per (substance, rater_status)
    trip_sub = {t["trip_id"]: t["substance"] for t in trips}
    sub_status = Counter((trip_sub[s["trip_id"]], s["rater_status"]) for s in scenes)
    print("\nScenes per (substance, rater_status):")
    for (sub, st), n in sorted(sub_status.items()):
        print(f"  {sub:<11} {st:<8}  n_scenes={n}")

    # Codes per (substance, is_scene_level, rater)
    sub_codes = Counter((trip_sub[c["trip_id"]], c["is_scene_level"], c["rater"]) for c in codes)
    print("\nCodes per (substance, is_scene_level, rater):")
    for (sub, isl, r), n in sorted(sub_codes.items()):
        lvl = "scene" if isl == "True" else "trip"
        print(f"  {sub:<11} {lvl:<6} rater={r}  n_codes={n}")

    # Scope-normalised rows per section
    norm_by_section = Counter()
    for c in codes:
        if c["scope_normalised"] == "True":
            norm_by_section[c["level_1"]] += 1
    if norm_by_section:
        print("\nCodes rescued by D4 scope-layer normalisation, by section:")
        for sec, n in norm_by_section.most_common():
            print(f"  {sec:<40}  n={n}")

    # Trip-level multiplicity: which items got collapsed from multiple scenes?
    multi = [c for c in codes if c["is_scene_level"] == "False" and int(c["trip_level_multiplicity"]) > 1]
    print(f"\nTrip-level rows that collapsed ≥2 scene-level rows: {len(multi)}")
    if multi:
        top_ex = Counter(c["item_id"] for c in multi).most_common(5)
        print("  top collapsed items:")
        for item, n in top_ex:
            print(f"    {item}  {n}")

    # -- Report errors/warnings --
    print()
    print("=" * 72)
    print("INTEGRITY CHECK")
    print("=" * 72)
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors[:20]:
            print(f"  {e}")
        if len(errors) > 20:
            print(f"  ... and {len(errors)-20} more")
    else:
        print("OK — no integrity errors")
    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")


if __name__ == "__main__":
    main()
