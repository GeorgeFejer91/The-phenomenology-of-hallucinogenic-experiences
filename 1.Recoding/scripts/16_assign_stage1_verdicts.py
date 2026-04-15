"""Assign MISS / AMBIGUITY-2a / AMBIGUITY-2b verdicts to every solo scene.

Output: 1.Recoding/data/stage1_verdicts.csv
Schema: scene_id, trip_id, rater_status, stage1_driver, verdict, verdict_flavour,
        verdict_source, rationale

Two passes:

 1. AUTO — the four structural driver categories map to AMBIGUITY defaults
    on the directive's logic (these are systematic Guideline edge-cases):
       _FRAG → AMBIGUITY-2a   (granularity edge-case: lump vs split)
       _AMP  → AMBIGUITY-2a   (ambient perceptual amplification w/o object)
       _AMB  → AMBIGUITY-2b   (thought/memory/metaphor = different phenomenon)
       _SOMA → AMBIGUITY-2b   (somatic self-transformation = different phenomenon)

 2. RCL residual — left as verdict=NEEDS_ADJUDICATION and flavour="".
    These require per-scene semantic judgement against the trip's _AB scenes
    (each rater's observed criterion). A subsequent manual pass updates the
    CSV with MISS vs AMBIGUITY-2a vs AMBIGUITY-2b verdicts.

Manual verdicts live in a SEPARATE tracked file:
  1.Recoding/data/stage1_manual_verdicts.csv
  schema: scene_id, verdict, flavour, rationale
Rows there override the auto/pending defaults for their scene_id. Running
this script merges them into stage1_verdicts.csv.
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
#                2a = under-specified rule; 2b = phenomenon outside current
#                hallucinatory-scene category (new category needed).
# The rater's subjective judgement about what is a hallucinatory scene is
# the PRIMARY DATA.  Preserve it.  Do NOT resolve attribute-level
# disagreement (illusion vs incrusted, object-class, etc.) — that is
# Stage 2, deferred.  See also 1.Recoding/STAGE1_SCOPE.json
# ======================================================================
import os, csv

DATA = "../data"
OUT = "stage1_verdicts.csv"

COLS = [
    "scene_id", "trip_id", "rater_status", "stage1_driver",
    "verdict", "verdict_flavour", "parent_scene_id", "verdict_source", "rationale",
]

# Verdicts: MISS | GRANULARITY | AMBIGUITY (flavour 2a/2b)
# Structural driver → default verdict mapping.  _FRAG maps to GRANULARITY
# (the fragment is a sub-scene of a larger encompassing scene; the parent
# is already recorded in scenes.csv.parent_scene_id).
AUTO_RULES = {
    "FRAG": ("GRANULARITY", "",
             "Fragment/sub-scene of a holistic scene coded by the other rater. Parent recorded "
             "in scenes.csv. Resolved by the data-coding rule: the encompassing scene is the "
             "canonical parent; the fragment pools under it for downstream attribute analysis."),
    "AMP":  ("AMBIGUITY", "2a",
             "Ambient perceptual amplification without a discrete hallucinatory object — the "
             "Guidelines do not rule cleanly on whether brightness/colour/shimmer changes alone "
             "constitute a scene."),
    "AMB":  ("AMBIGUITY", "2b",
             "Thought / memory / metaphor content individuated as a scene by one rater — the "
             "passage is phenomenologically real but arguably a different (non-perceptual) "
             "phenomenon the current taxonomy has no dedicated category for."),
    "SOMA": ("AMBIGUITY", "2b",
             "Somatic self-transformation / interoceptive content — the passage is "
             "phenomenologically real but may not be a hallucinatory SCENE in the "
             "external-object sense; would fit better in a body-schema / ego-dissolution "
             "category the current taxonomy lacks."),
}


def load(path):
    with open(os.path.join(os.path.dirname(__file__), DATA, path), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    here = os.path.dirname(__file__)
    scenes = load("scenes.csv")

    # Load manual verdict overrides (if present)
    manual_path = os.path.join(here, DATA, "stage1_manual_verdicts.csv")
    manual = {}
    if os.path.exists(manual_path):
        with open(manual_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("scene_id"):
                    manual[r["scene_id"]] = r

    out_path = os.path.join(here, DATA, OUT)

    rows = []
    for s in scenes:
        if s["rater_status"] == "both":
            continue  # only solo scenes get a verdict
        sid = s["scene_id"]
        drv = s.get("stage1_driver", "") or ""

        if sid in manual:
            m = manual[sid]
            rows.append({
                "scene_id": sid,
                "trip_id": s["trip_id"],
                "rater_status": s["rater_status"],
                "stage1_driver": drv,
                "verdict": m["verdict"],
                "verdict_flavour": m.get("flavour", ""),
                "parent_scene_id": m.get("parent_scene_id", "") or s.get("parent_scene_id", ""),
                "verdict_source": "manual",
                "rationale": m.get("rationale", ""),
            })
            continue

        if drv in AUTO_RULES:
            verdict, flavour, rationale = AUTO_RULES[drv]
            # For FRAG, carry parent_scene_id through from scenes.csv
            parent = s.get("parent_scene_id", "") if drv == "FRAG" else ""
            rows.append({
                "scene_id": sid,
                "trip_id": s["trip_id"],
                "rater_status": s["rater_status"],
                "stage1_driver": drv,
                "verdict": verdict,
                "verdict_flavour": flavour,
                "parent_scene_id": parent,
                "verdict_source": "auto",
                "rationale": rationale,
            })
        else:  # RCL or empty
            rows.append({
                "scene_id": sid,
                "trip_id": s["trip_id"],
                "rater_status": s["rater_status"],
                "stage1_driver": drv,
                "verdict": "NEEDS_ADJUDICATION",
                "verdict_flavour": "",
                "parent_scene_id": "",
                "verdict_source": "pending",
                "rationale": "",
            })

    # Sort: by trip_id, then scene_id
    rows.sort(key=lambda r: (r["trip_id"].split("_")[0],
                              int(r["trip_id"].split("_")[1]),
                              r["scene_id"]))

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # Summary
    from collections import Counter
    by_verdict = Counter(r["verdict"] for r in rows)
    by_source  = Counter(r["verdict_source"] for r in rows)
    print(f"wrote {out_path}")
    print(f"  {len(rows)} solo scenes")
    print(f"  verdicts: {dict(by_verdict)}")
    print(f"  sources:  {dict(by_source)}")


if __name__ == "__main__":
    main()
