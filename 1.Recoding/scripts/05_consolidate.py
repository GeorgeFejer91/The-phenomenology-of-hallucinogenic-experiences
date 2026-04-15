"""Consolidate per-trip adjudication YAMLs into framework tables.

This is the data-structure framework. Five long-format CSVs:

  trips.csv             one row per trip
  scenes.csv            one row per canonical scene (scene_id encodes rater status)
  codes.csv             one row per (scene|trip, rater, item) attribute
  agreement_flags.csv   derived: per shared scene, per taxonomy path, who coded it
  rater_style.csv       derived: per trip per rater, style metrics

Scene-ID naming convention:
  {trip_id}_S{NN}_AB   — both raters individuated this scene
  {trip_id}_S{NN}_A    — only rater A individuated
  {trip_id}_S{NN}_B    — only rater B individuated

Why the suffix: after loading scenes.csv you can filter on the suffix alone
to isolate consensus vs disputed scenes, which is the core downstream question.

The codes table lets you trace every attribute each rater attached to each
scene, and the agreement_flags table makes per-item A/B overlap filterable
at any taxonomy level.
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
import os, csv, re, glob
try:
    import yaml
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "--quiet"])
    import yaml

ADJ_DIR = "../adjudication"
DATA_DIR = "../data"
TAX_PATH = "../data/taxonomy.csv"


def load_taxonomy(path):
    """item_id -> (level_1, level_2, level_3, path, depth, is_scene_level)."""
    out = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["item_id"]] = row
    return out


def normalise_item_id(item_id):
    """Normalise hyphens to underscores so YAML item refs match taxonomy IDs."""
    if item_id is None:
        return None
    return item_id.replace("-", "_")


def is_trip_level_item(tax_row):
    """True if the taxonomy item's section is trip-level (per taxonomy.csv).

    Used to implement the D4 scope-layer normalisation: when a rater attaches
    a trip-level-taxonomy item to a scene, we move it to trip-level at
    consolidation time, recording the original scene_id for audit.
    """
    if not tax_row:
        return False
    return tax_row.get("is_trip_level") == "True"


def norm_suffix(status):
    return {"both": "AB", "only_A": "A", "only_B": "B"}[status]


def build_scene_id(trip_id, scene_num, child_k, status, lump_split_type, is_child):
    """Apply the naming convention from RULES.md §1.

    scene_num: int (1-based)  → "S07"
    child_k:   int or None    → ".2" if child else ""
    status:    "both"/"only_A"/"only_B"
    lump_split_type: None | "A_lumped_B_split" | "B_lumped_A_split"
    is_child:  bool — True if this is a sub-scene under a parent lump
    """
    base = f"{trip_id}_S{scene_num:02d}"
    if is_child and child_k is not None:
        base = f"{base}.{child_k}"
    suffix = norm_suffix(status)
    mod = ""
    if lump_split_type == "A_lumped_B_split":
        mod = "_SPLITB" if is_child else "_LUMPA"
    elif lump_split_type == "B_lumped_A_split":
        mod = "_SPLITA" if is_child else "_LUMPB"
    return f"{base}_{suffix}{mod}"


SCENE_ID_RE = re.compile(
    r"^(?P<trip>[A-Z][a-z]+_\d{2})_S(?P<num>\d{2})"
    r"(?:\.(?P<child>\d+))?"
    r"_(?P<status>AB|A|B)"
    r"(?:_(?P<mod>LUMPA|LUMPB|SPLITA|SPLITB))?$"
)


def validate_scene_id(sid):
    return bool(SCENE_ID_RE.match(sid))


def main():
    here = os.path.dirname(__file__)
    adj_dir = os.path.join(here, ADJ_DIR)
    data_dir = os.path.join(here, DATA_DIR)
    tax = load_taxonomy(os.path.join(here, TAX_PATH))

    trips = []               # rows for trips.csv
    scenes = []              # rows for scenes.csv
    codes = []               # rows for codes.csv
    code_id_counter = 0

    for yaml_path in sorted(glob.glob(os.path.join(adj_dir, "*.yaml"))):
        with open(yaml_path, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        trip_id = doc["trip_id"]
        substance = doc["substance"]
        block = doc["block"]
        coder_A = doc["coder_A"]
        coder_B = doc["coder_B"]
        dose_raw = doc.get("dose_raw")
        word_count = doc.get("word_count")

        trips.append({
            "trip_id": trip_id,
            "substance": substance,
            "block": block,
            "coder_A": coder_A,
            "coder_B": coder_B,
            "dose_raw": dose_raw,
            "word_count": word_count,
        })

        # -- scene-level adjudication rows --
        for sc in doc.get("scenes", []):
            status = sc["status"]
            # Reconstruct scene_id per RULES §1 — two paths:
            #  (a) legacy YAML already provides scene_id like "Psilocybe_04_S03" (no suffix) → add suffix
            #  (b) YAML provides scene_num / child_k / lump fields → build from scratch
            base = sc["scene_id"]
            # If it's already fully-formed per the regex, keep it
            if validate_scene_id(base):
                scene_id = base
            else:
                # Legacy: only has Stub like "Psilocybe_04_S03" — append suffix
                suffix = norm_suffix(status)
                mod = ""
                lst = sc.get("lump_split_type")
                if sc.get("is_child"):
                    if lst == "A_lumped_B_split": mod = "_SPLITB"
                    elif lst == "B_lumped_A_split": mod = "_SPLITA"
                else:
                    if lst == "A_lumped_B_split": mod = "_LUMPA"
                    elif lst == "B_lumped_A_split": mod = "_LUMPB"
                # Include dotted child suffix if declared
                if sc.get("child_k") is not None and ".".__add__ not in base[-3:]:
                    # add .k before the suffix
                    base = f"{base}.{sc['child_k']}"
                scene_id = f"{base}_{suffix}{mod}"
                if not validate_scene_id(scene_id):
                    print(f"  WARN: scene_id does not match convention: {scene_id}  (from {base!r}, trip {trip_id})")

            scenes.append({
                "scene_id": scene_id,
                "trip_id": trip_id,
                "rater_status": status,
                "parent_scene_id": sc.get("parent_scene_id") or "",
                "lump_split_type": sc.get("lump_split_type") or "none",
                "canonical_desc": sc.get("canonical_desc"),
                "canonical_span_start": sc.get("canonical_span_start"),
                "canonical_span_end": sc.get("canonical_span_end"),
                "rater_A_refs": ",".join(sc.get("rater_A", {}).get("worksheet_refs", [])) if sc.get("rater_A") else "",
                "rater_B_refs": ",".join(sc.get("rater_B", {}).get("worksheet_refs", [])) if sc.get("rater_B") else "",
                "adjudicator_note": sc.get("rationale"),
            })

            # -- per-scene rater codes (with D4 scope-layer normalisation) --
            for rater_label, rater_blob, coder_name in (
                ("A", sc.get("rater_A"), coder_A),
                ("B", sc.get("rater_B"), coder_B),
            ):
                if not rater_blob:
                    continue
                # D5 dedup safety: within one (scene, rater) use a set
                seen_items = set()
                for raw_item in rater_blob.get("items", []):
                    item = normalise_item_id(raw_item)
                    if item in seen_items:
                        continue
                    seen_items.add(item)
                    t = tax.get(item)
                    code_id_counter += 1
                    # D4 normalisation: if the item is trip-level per the taxonomy,
                    # attach it at trip level (scene_id=NULL) and record the
                    # originating scene_id for audit transparency.
                    if is_trip_level_item(t):
                        final_scene_id = None
                        original_scene_id = scene_id
                        is_scene_lvl = False
                        scope_normalised = True
                    else:
                        final_scene_id = scene_id
                        original_scene_id = ""
                        is_scene_lvl = True
                        scope_normalised = False
                    codes.append({
                        "code_id": f"C{code_id_counter:06d}",
                        "scene_id": final_scene_id,
                        "original_scene_id": original_scene_id,
                        "trip_id": trip_id,
                        "rater": rater_label,
                        "coder_name": coder_name,
                        "item_id": item,
                        "item_path": t["path"] if t else item,
                        "level_1": t["level_1"] if t else None,
                        "level_2": t["level_2"] if t else None,
                        "level_3": t["level_3"] if t else None,
                        "is_scene_level": is_scene_lvl,
                        "scope_normalised": scope_normalised,
                        "excerpt": None,
                    })

        # -- trip-level codes --
        for rater_key, coder_name_for_rater in (("rater_A", coder_A), ("rater_B", coder_B)):
            rater_label = "A" if rater_key == "rater_A" else "B"
            for entry in doc.get("trip_level_codes", {}).get(rater_key, []) or []:
                if not isinstance(entry, dict):
                    continue
                item = normalise_item_id(entry.get("item"))
                if not item:
                    continue
                t = tax.get(item)
                code_id_counter += 1
                codes.append({
                    "code_id": f"C{code_id_counter:06d}",
                    "scene_id": None,
                    "original_scene_id": "",
                    "trip_id": trip_id,
                    "rater": rater_label,
                    "coder_name": coder_name_for_rater,
                    "item_id": item,
                    "item_path": t["path"] if t else item,
                    "level_1": t["level_1"] if t else None,
                    "level_2": t["level_2"] if t else None,
                    "level_3": t["level_3"] if t else None,
                    "is_scene_level": False,
                    "scope_normalised": False,
                    "excerpt": entry.get("excerpt"),
                })

    # Write tables
    trips_cols = ["trip_id","substance","block","coder_A","coder_B","dose_raw","word_count"]
    with open(os.path.join(data_dir, "trips.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=trips_cols); w.writeheader(); [w.writerow(r) for r in trips]

    # scenes.csv is written below, after substance/block denormalisation

    # D4 post-pass: dedup trip-level rows that arose from multiple scenes
    # getting normalised to the same (trip_id, rater, item_id) bucket.
    # We keep one row and remember how many scenes it was normalised from.
    trip_key_counts = {}
    for c in codes:
        if c["is_scene_level"] is False:
            k = (c["trip_id"], c["rater"], c["item_id"])
            trip_key_counts[k] = trip_key_counts.get(k, 0) + 1
    seen = set()
    deduped = []
    for c in codes:
        if c["is_scene_level"] is False:
            k = (c["trip_id"], c["rater"], c["item_id"])
            if k in seen:
                continue
            seen.add(k)
            c["trip_level_multiplicity"] = trip_key_counts[k]
        else:
            c["trip_level_multiplicity"] = 1
        deduped.append(c)
    codes = deduped

    # Denormalise substance / block onto scenes and codes so cross-condition
    # filters can be expressed without a join. This is a routine analytics
    # denormalisation — the canonical source is still trips.csv.
    trip_meta = {t["trip_id"]: t for t in trips}
    for s in scenes:
        t = trip_meta.get(s["trip_id"], {})
        s["substance"] = t.get("substance", "")
        s["block"] = t.get("block", "")
    for c in codes:
        t = trip_meta.get(c["trip_id"], {})
        c["substance"] = t.get("substance", "")
        c["block"] = t.get("block", "")

    # Rewrite scenes.csv with denormalised columns
    scenes_cols = ["scene_id","trip_id","substance","block","rater_status",
                   "parent_scene_id","lump_split_type",
                   "canonical_desc","canonical_span_start","canonical_span_end",
                   "rater_A_refs","rater_B_refs","adjudicator_note"]
    with open(os.path.join(data_dir, "scenes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=scenes_cols); w.writeheader(); [w.writerow(r) for r in scenes]

    codes_cols = ["code_id","scene_id","original_scene_id","trip_id","substance","block",
                  "rater","coder_name",
                  "item_id","item_path","level_1","level_2","level_3",
                  "is_scene_level","scope_normalised","trip_level_multiplicity","excerpt"]
    with open(os.path.join(data_dir, "codes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=codes_cols); w.writeheader(); [w.writerow(r) for r in codes]

    # ------ Derived: agreement_flags.csv ------
    # For each shared scene (rater_status == "both"), list every (taxonomy leaf
    # that either rater attached to it) and note A_coded / B_coded.
    # Also compute agreement-at-level for L1, L2, L3 roll-ups.
    scene_status = {s["scene_id"]: s["rater_status"] for s in scenes}
    # codes grouped by scene
    by_scene_rater = {}
    for c in codes:
        if not c["scene_id"]:
            continue
        by_scene_rater.setdefault((c["scene_id"], c["rater"]), set()).add(c["item_id"])
    shared_scenes = [s for s in scenes if s["rater_status"] == "both"]
    agreement_rows = []
    for sc in shared_scenes:
        sid = sc["scene_id"]
        a_items = by_scene_rater.get((sid, "A"), set())
        b_items = by_scene_rater.get((sid, "B"), set())
        all_items = a_items | b_items
        for item in sorted(all_items):
            t = tax.get(item, {})
            A = item in a_items; B = item in b_items
            agreement_rows.append({
                "scene_id": sid,
                "trip_id": sc["trip_id"],
                "item_id": item,
                "item_path": t.get("path", item),
                "level_1": t.get("level_1"),
                "level_2": t.get("level_2"),
                "level_3": t.get("level_3"),
                "depth": t.get("depth"),
                "A_coded": A,
                "B_coded": B,
                "agreement": "AGREE" if (A and B) else ("A_ONLY" if A else "B_ONLY"),
            })
    # Denormalise substance/block onto agreement_flags
    for r in agreement_rows:
        t = trip_meta.get(r["trip_id"], {})
        r["substance"] = t.get("substance", "")
        r["block"] = t.get("block", "")
    ag_cols = ["scene_id","trip_id","substance","block",
               "item_id","item_path","level_1","level_2","level_3",
               "depth","A_coded","B_coded","agreement"]
    with open(os.path.join(data_dir, "agreement_flags.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ag_cols); w.writeheader(); [w.writerow(r) for r in agreement_rows]

    # ------ Derived: rater_style.csv ------
    # Per (trip, rater): counts that capture style differences.
    style_rows = []
    trips_by_id = {t["trip_id"]: t for t in trips}
    scenes_by_trip = {}
    for s in scenes:
        scenes_by_trip.setdefault(s["trip_id"], []).append(s)
    codes_by_trip_rater = {}
    for c in codes:
        codes_by_trip_rater.setdefault((c["trip_id"], c["rater"]), []).append(c)
    for tid, tmeta in trips_by_id.items():
        for rater in ("A", "B"):
            scenes_t = scenes_by_trip.get(tid, [])
            # scenes this rater individuated (both + only_this)
            if rater == "A":
                my_status = {"both", "only_A"}
            else:
                my_status = {"both", "only_B"}
            my_scenes = [s for s in scenes_t if s["rater_status"] in my_status]
            codes_r = codes_by_trip_rater.get((tid, rater), [])
            scene_codes = [c for c in codes_r if c["is_scene_level"]]
            trip_codes = [c for c in codes_r if not c["is_scene_level"]]
            modal_uses = sum(1 for c in scene_codes if c["level_1"] == "Modal status of the hallucination")
            incrusted_uses = sum(1 for c in scene_codes if c["item_id"] == "type_of_visual_alteration_hallucination_of_an_incrusted_object")
            detached_uses = sum(1 for c in scene_codes if c["item_id"] == "type_of_visual_alteration_hallucination_of_a_detached_object")
            illusion_uses = sum(1 for c in scene_codes if c["item_id"] == "type_of_visual_alteration_illusion")
            immersive_uses = sum(1 for c in scene_codes if c["item_id"] == "type_of_visual_alteration_full-blown_immersive_hallucination")
            style_rows.append({
                "trip_id": tid,
                "substance": tmeta["substance"],
                "rater": rater,
                "coder_name": tmeta["coder_A" if rater=="A" else "coder_B"],
                "n_scenes_individuated": len(my_scenes),
                "n_scene_codes": len(scene_codes),
                "n_trip_codes": len(trip_codes),
                "codes_per_scene": round(len(scene_codes) / max(1, len(my_scenes)), 2),
                "modal_status_uses": modal_uses,
                "incrusted_uses": incrusted_uses,
                "detached_uses": detached_uses,
                "illusion_uses": illusion_uses,
                "immersive_uses": immersive_uses,
            })
    st_cols = ["trip_id","substance","rater","coder_name",
               "n_scenes_individuated","n_scene_codes","n_trip_codes","codes_per_scene",
               "modal_status_uses","incrusted_uses","detached_uses","illusion_uses","immersive_uses"]
    with open(os.path.join(data_dir, "rater_style.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=st_cols); w.writeheader(); [w.writerow(r) for r in style_rows]

    # Summary to stdout
    n_both = sum(1 for s in scenes if s["rater_status"] == "both")
    n_A = sum(1 for s in scenes if s["rater_status"] == "only_A")
    n_B = sum(1 for s in scenes if s["rater_status"] == "only_B")
    print(f"trips:  {len(trips)}")
    print(f"scenes: {len(scenes)} (both={n_both}  only_A={n_A}  only_B={n_B})")
    print(f"codes:  {len(codes)} (scene={sum(1 for c in codes if c['is_scene_level'])}  trip={sum(1 for c in codes if not c['is_scene_level'])})")
    print(f"agreement_flags rows: {len(agreement_rows)}")
    print(f"rater_style rows: {len(style_rows)}")
    print(f"wrote {data_dir}/{{trips,scenes,codes,agreement_flags,rater_style}}.csv")


if __name__ == "__main__":
    main()
