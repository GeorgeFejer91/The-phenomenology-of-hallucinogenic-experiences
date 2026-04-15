"""Conservative-consensus view (analytical, does NOT modify canonical data).

Writes analysis/consensus_codes.csv containing only codings that pass the
minimum conservative consensus filter — the dataset-level analogue of the
PDF Guidelines' Case-2 rule:

  A scene-level code is retained if
      scenes.rater_status == 'both' AND
      agreement_flags.agreement == 'AGREE' for that (scene, item)

  A trip-level code is retained if both raters attached the same item_id
  to the same trip_id at trip-level.

Everything else is dropped. Single-rater codings are excluded — they are
by construction Case-2 passages under the conservative rule.

This view is regenerated from canonical scenes.csv / codes.csv /
agreement_flags.csv; it is a read-only derived artefact.
"""
import os, csv
from collections import defaultdict

DATA = "../data"
OUT_DIR = "../analysis"


def load(path):
    with open(os.path.join(os.path.dirname(__file__), DATA, path), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    here = os.path.dirname(__file__)
    scenes = load("scenes.csv")
    codes = load("codes.csv")
    flags = load("agreement_flags.csv")

    scene_status = {s["scene_id"]: s["rater_status"] for s in scenes}

    # Build set of (scene_id, item_id) pairs where agreement=AGREE
    scene_agree_pairs = {
        (f["scene_id"], f["item_id"])
        for f in flags
        if f["agreement"] == "AGREE"
    }

    # Identify trip-level consensus items: both A and B attached same item_id to same trip
    trip_items = defaultdict(lambda: {"A": False, "B": False})
    for c in codes:
        if c["is_scene_level"] == "False":
            trip_items[(c["trip_id"], c["item_id"])][c["rater"]] = True
    trip_consensus_pairs = {k for k, v in trip_items.items() if v["A"] and v["B"]}

    # Filter codes
    out_rows = []
    kept_scene = 0
    kept_trip = 0
    for c in codes:
        if c["is_scene_level"] == "True":
            if scene_status.get(c["scene_id"]) == "both" and (c["scene_id"], c["item_id"]) in scene_agree_pairs:
                # Mark as consensus — attach once per (scene, item) not per rater row
                # We'll dedup after
                out_rows.append(dict(c, consensus_level="scene"))
                kept_scene += 1
        else:
            if (c["trip_id"], c["item_id"]) in trip_consensus_pairs:
                out_rows.append(dict(c, consensus_level="trip"))
                kept_trip += 1

    # Dedup — one row per (scene|trip, item_id), drop the rater-redundant pair
    seen = set()
    final = []
    for r in out_rows:
        if r["consensus_level"] == "scene":
            key = ("scene", r["scene_id"], r["item_id"])
        else:
            key = ("trip", r["trip_id"], r["item_id"])
        if key in seen:
            continue
        seen.add(key)
        # Strip rater-specific fields since this is a consensus row
        r["rater"] = "consensus"
        r["coder_name"] = ""
        r["code_id"] = r["code_id"]  # keep traceability to one of the original rows
        final.append(r)

    os.makedirs(os.path.join(here, OUT_DIR), exist_ok=True)
    out_path = os.path.join(here, OUT_DIR, "consensus_codes.csv")
    cols = ["code_id","consensus_level","scene_id","trip_id","substance","block",
            "item_id","item_path","level_1","level_2","level_3","is_scene_level"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in final:
            w.writerow(r)

    # Summary
    total_scene_codes_pre = sum(1 for c in codes if c["is_scene_level"] == "True")
    total_trip_codes_pre = sum(1 for c in codes if c["is_scene_level"] == "False")
    scene_consensus = sum(1 for r in final if r["consensus_level"] == "scene")
    trip_consensus = sum(1 for r in final if r["consensus_level"] == "trip")
    total_shared_scenes = sum(1 for s in scenes if s["rater_status"] == "both")
    total_scenes = len(scenes)

    print("Conservative consensus view (minimum-consensus filter applied)")
    print("-" * 68)
    print(f"Scenes:             {total_shared_scenes} / {total_scenes} kept ({100*total_shared_scenes/total_scenes:.0f}%)")
    print(f"Scene-level codes:  {scene_consensus} / {total_scene_codes_pre} kept ({100*scene_consensus/max(1,total_scene_codes_pre):.0f}%)")
    print(f"Trip-level codes:   {trip_consensus} / {total_trip_codes_pre} kept ({100*trip_consensus/max(1,total_trip_codes_pre):.0f}%)")
    print(f"Wrote: {out_path}")

    # Per substance breakdown
    sub_scene = defaultdict(int)
    sub_trip = defaultdict(int)
    for r in final:
        sub = r.get("substance", "")
        if r["consensus_level"] == "scene":
            sub_scene[sub] += 1
        else:
            sub_trip[sub] += 1
    print()
    print("By substance:")
    for sub in sorted(set(list(sub_scene.keys())+list(sub_trip.keys()))):
        print(f"  {sub:<12}  scene_consensus={sub_scene[sub]:>4}  trip_consensus={sub_trip[sub]:>3}")


if __name__ == "__main__":
    main()
