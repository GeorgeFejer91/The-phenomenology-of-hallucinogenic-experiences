"""Export each trip's narrative + scene metadata as JSON for the pretext-based
dynamic renderer.

Output: 1.Recoding/annotated_trips_pretext/data/<trip_id>.json
       + index.json listing all trips
"""
import os, csv, json
from collections import defaultdict

DATA = "../data"
TRIPS_DIR = "../data/trips"
OUT_DIR = "../annotated_trips_pretext/data"


def load(path):
    with open(os.path.join(os.path.dirname(__file__), DATA, path), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def extract_driver(scene_id):
    if scene_id.endswith("_AB") or "_AB_" in scene_id:
        return "AB"
    for k in ("FRAG", "AMP", "AMB", "SOMA", "RCL"):
        if scene_id.endswith("_" + k):
            return k
    return "AB"


def parse_int(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


def main():
    here = os.path.dirname(__file__)
    os.makedirs(os.path.join(here, OUT_DIR), exist_ok=True)

    trips = {t["trip_id"]: t for t in load("trips.csv")}
    scenes = load("scenes.csv")
    scenes_by_trip = defaultdict(list)
    for s in scenes:
        scenes_by_trip[s["trip_id"]].append(s)

    index_entries = []
    for trip_id, trip in trips.items():
        narr_path = os.path.join(here, TRIPS_DIR, f"{trip_id}.txt")
        if not os.path.exists(narr_path):
            continue
        with open(narr_path, encoding="utf-8") as f:
            narrative = f.read()

        trip_scenes = sorted(
            scenes_by_trip.get(trip_id, []),
            key=lambda s: parse_int(s["canonical_span_start"]) or 0,
        )
        scene_dicts = [{
            "scene_id": s["scene_id"],
            "rater_status": s["rater_status"],
            "driver": extract_driver(s["scene_id"]),
            "parent_scene_id": s.get("parent_scene_id", "") or "",
            "canonical_desc": s.get("canonical_desc", "") or "",
            "canonical_span_start": parse_int(s["canonical_span_start"]),
            "canonical_span_end": parse_int(s["canonical_span_end"]),
            "stage1_rationale": s.get("stage1_rationale", "") or "",
        } for s in trip_scenes]

        out = {
            "trip_id": trip_id,
            "substance": trip["substance"],
            "block": trip["block"],
            "coder_A": trip["coder_A"],
            "coder_B": trip["coder_B"],
            "dose_raw": trip["dose_raw"] or None,
            "word_count": int(trip["word_count"]),
            "narrative": narrative,
            "scenes": scene_dicts,
        }
        with open(os.path.join(here, OUT_DIR, f"{trip_id}.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

        index_entries.append({
            "trip_id": trip_id,
            "substance": trip["substance"],
            "coder_A": trip["coder_A"],
            "coder_B": trip["coder_B"],
        })

    # Sort index by substance + trip number
    index_entries.sort(key=lambda e: (e["trip_id"].split("_")[0], int(e["trip_id"].split("_")[1])))
    with open(os.path.join(here, OUT_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index_entries, f, ensure_ascii=False, indent=2)

    print(f"wrote {len(index_entries)} trip JSONs + index.json to {OUT_DIR}/")


if __name__ == "__main__":
    main()
