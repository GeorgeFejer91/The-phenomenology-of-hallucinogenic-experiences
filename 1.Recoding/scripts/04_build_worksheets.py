"""For each of the 40 trips, render a per-trip adjudication worksheet as
markdown. Shows: metadata, full narrative, and every scene-level excerpt
from each rater, with its approximate character position in the narrative
(computed by longest-common-substring / fuzzy match).

Output: 1.Recoding/worksheets/<trip_id>.md

The worksheet is the input I read when adjudicating. I produce
1.Recoding/adjudication/<trip_id>.yaml by hand afterwards.
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
import os, csv, re
from rapidfuzz import fuzz

RAW = "../data/raw_codings.csv"
TRIPS_INDEX = "../data/trips_index.csv"
TRIPS_DIR = "../data/trips"
OUT_DIR = "../worksheets"

PAIRS = {
    ("psilocybin", "01-10"): ("Alessandra", "Brendan"),
    ("psilocybin", "11-20"): ("Francesco",  "Susana"),
    ("brugmansia", "01-10"): ("Brendan",    "Noah"),
    ("brugmansia", "11-20"): ("Alessandra", "Alessio"),
}


def anchor(excerpt, narrative):
    """Return (start, end, score) best match of excerpt in narrative.
    Uses longest-common substring anchor first, then partial_ratio for the fallback window."""
    if not excerpt or not narrative:
        return None, None, 0
    # Try exact substring first (cheap and perfect)
    low_nar = narrative.lower()
    low_ex = excerpt.lower()
    idx = low_nar.find(low_ex)
    if idx != -1:
        return idx, idx + len(excerpt), 100
    # Try longest common substring of first 40 chars of excerpt
    probe = low_ex[:40]
    # Scan windows of length len(excerpt) +/- 20% using partial_ratio
    best_score = 0
    best_start = None
    L = len(excerpt)
    step = max(1, L // 8)
    for i in range(0, max(1, len(low_nar) - L + 1), step):
        win = low_nar[i:i + L]
        sc = fuzz.ratio(win, low_ex)
        if sc > best_score:
            best_score = sc
            best_start = i
    # refine by trying +/- step around best_start
    if best_start is not None:
        for i in range(max(0, best_start - step), min(len(low_nar) - L + 1, best_start + step + 1)):
            win = low_nar[i:i + L]
            sc = fuzz.ratio(win, low_ex)
            if sc > best_score:
                best_score = sc
                best_start = i
    if best_start is None:
        return None, None, 0
    return best_start, best_start + L, best_score


def load_rows(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    here = os.path.dirname(__file__)
    trips_idx = {r["trip_id"]: r for r in load_rows(os.path.join(here, TRIPS_INDEX))}
    raw = load_rows(os.path.join(here, RAW))
    outdir = os.path.join(here, OUT_DIR)
    os.makedirs(outdir, exist_ok=True)

    # Group raw by trip_id
    by_trip = {}
    for r in raw:
        by_trip.setdefault(r["trip_id"], []).append(r)

    # Order of trips
    ordered = sorted(trips_idx.keys(), key=lambda t: (t.split('_')[0], int(t.split('_')[1])))

    for tid in ordered:
        meta = trips_idx[tid]
        # Load narrative
        nar_path = os.path.join(here, TRIPS_DIR, f"{tid}.txt")
        narrative = open(nar_path, encoding="utf-8").read()
        rows = by_trip.get(tid, [])
        if not rows:
            print(f"  !! {tid}: no codings")
            continue
        substance = meta["substance"]
        block = rows[0]["block"]
        pair = PAIRS.get((substance, block))
        if not pair:
            print(f"  !! {tid}: no pair defined")
            continue
        coder_A, coder_B = pair
        rows_A = [r for r in rows if r["coder"] == coder_A]
        rows_B = [r for r in rows if r["coder"] == coder_B]

        # Build a compact list per rater: dedup excerpts (same excerpt may appear
        # under multiple items — we want to see it once, then list all items).
        def dedup(rows_r):
            by_ex = {}
            for r in rows_r:
                ex = (r["excerpt"] or "").strip()
                key = ex.lower() if ex else f"__no_excerpt_row_{r['source_row']}"
                entry = by_ex.setdefault(key, {"excerpt": ex, "items": [], "src_rows": set()})
                entry["items"].append(r["item_code"])
                entry["src_rows"].add(r["source_row"])
            # Anchor each
            out = []
            for e in by_ex.values():
                s, t, sc = anchor(e["excerpt"], narrative)
                e["span_start"] = s
                e["span_end"] = t
                e["score"] = sc
                out.append(e)
            # Sort by narrative position
            out.sort(key=lambda x: (x["span_start"] if x["span_start"] is not None else 10**9))
            return out

        A_list = dedup(rows_A)
        B_list = dedup(rows_B)

        # Split items into scene-level vs trip-level
        # Scene-level L1 sections
        SCENE_L1 = {
            "Type of visual alteration", "Visual hallucination", "Auditory hallucination",
            "Tactile hallucination", "Olfactory hallucination", "Gustatory hallucination",
            "Nonsensory hallucination", "Modal status of the hallucination",
            "Dynamics of hallucinations",
        }

        def is_scene_item(item_code):
            return item_code.split(" | ")[0] in SCENE_L1

        def classify(entries):
            scene, trip = [], []
            for e in entries:
                has_scene = any(is_scene_item(i) for i in e["items"])
                if has_scene:
                    scene.append(e)
                else:
                    trip.append(e)
            return scene, trip

        A_scene, A_trip = classify(A_list)
        B_scene, B_trip = classify(B_list)

        # Render worksheet
        out_lines = []
        out_lines.append(f"# Adjudication worksheet — {tid}")
        out_lines.append("")
        out_lines.append(f"- substance: **{substance}**  block: **{block}**")
        out_lines.append(f"- coder_A: **{coder_A}**  coder_B: **{coder_B}**")
        out_lines.append(f"- dose_raw: `{meta['dose_raw']}`   word_count: **{meta['word_count']}**")
        out_lines.append("")
        out_lines.append("## Narrative")
        out_lines.append("")
        out_lines.append("```")
        out_lines.append(narrative)
        out_lines.append("```")
        out_lines.append("")

        def render_list(title, entries, prefix):
            out_lines.append(f"## {title} ({len(entries)} distinct excerpts)")
            out_lines.append("")
            if not entries:
                out_lines.append("_none_"); out_lines.append(""); return
            for i, e in enumerate(entries, 1):
                pos = f"@{e['span_start']}" if e["span_start"] is not None else "@?"
                sc = f"sc={e['score']}"
                items = "; ".join(sorted(set(e["items"])))
                ex = (e["excerpt"] or "(no excerpt)").replace("\n", " ")
                if len(ex) > 400:
                    ex = ex[:400] + "…"
                out_lines.append(f"- **{prefix}{i:02d}** {pos} {sc}")
                out_lines.append(f"  - items: {items}")
                out_lines.append(f"  - excerpt: {ex!r}")
            out_lines.append("")

        render_list(f"Coder A ({coder_A}) — scene-level", A_scene, "A")
        render_list(f"Coder B ({coder_B}) — scene-level", B_scene, "B")
        render_list(f"Coder A ({coder_A}) — trip-level", A_trip, "a")
        render_list(f"Coder B ({coder_B}) — trip-level", B_trip, "b")

        out_path = os.path.join(outdir, f"{tid}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(out_lines))
        print(f"  wrote {out_path} (A:{len(A_scene)}s/{len(A_trip)}t  B:{len(B_scene)}s/{len(B_trip)}t)")


if __name__ == "__main__":
    main()
