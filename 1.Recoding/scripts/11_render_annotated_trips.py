"""Render one annotated HTML file per trip report, with scenes highlighted by
driver category using the scene-ID taxonomy.

Colour legend:
  _AB   (both raters individuated)       green
  _FRAG (fragment of a holistic scene)   orange
  _AMP  (sensory amplification)          yellow
  _AMB  (thought / memory / metaphor)    purple
  _SOMA (somatic / self-transformation)  pink
  _RCL  (genuine miss; flag human)       red

Each highlight shows the scene_id and, for fragments, the parent scene's id.
A header with a per-trip summary table and the full legend is added to each
page.  Output: 1.Recoding/annotated_trips/<trip_id>.html

To convert to PDF: open in browser and print, or use weasyprint / wkhtmltopdf.
"""
import os, csv, html, re
from collections import defaultdict

DATA = "../data"
TRIPS_DIR = "../data/trips"
OUT_DIR = "../annotated_trips"

COLOURS = {
    "AB":   "#b7e4c7",  # green
    "FRAG": "#ffd79a",  # orange
    "AMP":  "#fff3a3",  # yellow
    "AMB":  "#d5c6e0",  # purple
    "SOMA": "#f7c1d9",  # pink
    "RCL":  "#f4b4b4",  # red
}

DRIVER_NAMES = {
    "AB":   "SHARED (both raters individuated)",
    "FRAG": "FRAGMENT (child of a holistic scene coded by the other rater)",
    "AMP":  "SENSORY AMPLIFICATION (ambient perceptual change, no discrete object)",
    "AMB":  "AMBIGUITY (thought / memory / metaphor coded as a hallucination)",
    "SOMA": "SOMATIC (self-transformation or interoceptive content)",
    "RCL":  "RECONCILIATION NEEDED (likely genuine miss; requires human adjudication)",
}


def load(path):
    with open(os.path.join(os.path.dirname(__file__), DATA, path), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def extract_driver(scene_id):
    """Return driver suffix code for a scene_id."""
    if scene_id.endswith("_AB") or "_AB_" in scene_id:
        return "AB"
    for k in ("FRAG", "AMP", "AMB", "SOMA", "RCL"):
        if scene_id.endswith("_" + k):
            return k
    return "AB"  # fallback


def parse_span(s):
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

    for trip_id, trip in trips.items():
        narr_path = os.path.join(here, TRIPS_DIR, f"{trip_id}.txt")
        if not os.path.exists(narr_path):
            print(f"  !! missing narrative: {trip_id}")
            continue
        with open(narr_path, encoding="utf-8") as f:
            narrative = f.read()

        trip_scenes = sorted(
            [s for s in scenes_by_trip.get(trip_id, []) if parse_span(s["canonical_span_start"]) is not None],
            key=lambda s: parse_span(s["canonical_span_start"]),
        )

        # Build list of (start, end, scene) with driver category, for highlight
        # If two scenes overlap, the later one's highlight will visually overlay
        # the earlier — for clarity we sort by start ascending and nest via
        # CSS (later tooltip wins).
        segments = []
        for s in trip_scenes:
            a = parse_span(s["canonical_span_start"])
            b = parse_span(s["canonical_span_end"])
            if a is None or b is None or b <= a or b > len(narrative) + 500:
                continue
            # clamp end
            b = min(b, len(narrative))
            if a >= len(narrative):
                continue
            driver = extract_driver(s["scene_id"])
            segments.append({
                "start": a, "end": b, "scene": s, "driver": driver,
            })

        # Build HTML with highlights. Since spans can overlap, merge them into
        # a linear list of text-pieces where each piece carries the set of
        # scene_ids active at that character position.
        events = []
        for i, seg in enumerate(segments):
            events.append(("start", seg["start"], i))
            events.append(("end",   seg["end"],   i))
        events.sort(key=lambda e: (e[1], 0 if e[0] == "end" else 1))

        active = set()
        pieces = []
        cursor = 0
        for kind, pos, idx in events:
            if pos > cursor:
                pieces.append((cursor, pos, set(active)))
                cursor = pos
            if kind == "start":
                active.add(idx)
            else:
                active.discard(idx)
        if cursor < len(narrative):
            pieces.append((cursor, len(narrative), set(active)))

        # Render
        out_html = []
        out_html.append(f"<!doctype html><html><head><meta charset='utf-8'>")
        out_html.append(f"<title>{html.escape(trip_id)} — annotated trip report</title>")
        out_html.append("<style>")
        out_html.append("""
        body { font-family: Georgia, serif; max-width: 900px; margin: 2em auto; padding: 0 2em; line-height: 1.55; color: #222; }
        h1 { border-bottom: 2px solid #333; padding-bottom: .3em; }
        h2 { margin-top: 2em; color: #444; }
        .legend { background: #f5f5f5; border: 1px solid #ccc; padding: 1em; margin: 1em 0; border-radius: 4px; font-size: 0.9em; }
        .legend-item { display: inline-block; padding: 2px 8px; margin: 2px 4px; border-radius: 3px; }
        .summary { font-size: 0.9em; background: #fafafa; border: 1px solid #ddd; padding: 1em; border-radius: 4px; }
        .summary table { border-collapse: collapse; }
        .summary td, .summary th { padding: 3px 10px; }
        .narr { white-space: pre-wrap; border: 1px solid #eee; padding: 1.5em; background: #fcfcfc; border-radius: 4px; }
        .seg { border-radius: 2px; padding: 1px 2px; cursor: help; position: relative; }
        .seg-ids { display: none; position: absolute; top: 100%; left: 0; background: #222; color: #fff; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; white-space: nowrap; z-index: 10; }
        .seg:hover .seg-ids { display: block; }
        .scene-list { font-size: 0.85em; }
        .scene-list li { margin: 3px 0; }
        """)
        for k, col in COLOURS.items():
            out_html.append(f".bg-{k} {{ background-color: {col}; }}")
        out_html.append("</style></head><body>")

        # Header
        out_html.append(f"<h1>{html.escape(trip_id)}</h1>")
        out_html.append(f"<div class='summary'>")
        out_html.append(f"<table>")
        out_html.append(f"<tr><th>substance</th><td>{html.escape(trip['substance'])}</td>")
        out_html.append(f"<th>block</th><td>{html.escape(trip['block'])}</td></tr>")
        out_html.append(f"<tr><th>coder A</th><td>{html.escape(trip['coder_A'])}</td>")
        out_html.append(f"<th>coder B</th><td>{html.escape(trip['coder_B'])}</td></tr>")
        out_html.append(f"<tr><th>dose</th><td>{html.escape(trip['dose_raw'] or '')}</td>")
        out_html.append(f"<th>word count</th><td>{html.escape(trip['word_count'])}</td></tr>")
        out_html.append(f"</table>")
        # Per-trip scene counts by driver
        counts = defaultdict(int)
        for s in trip_scenes:
            counts[extract_driver(s["scene_id"])] += 1
        out_html.append("<p><b>Scene counts by driver:</b> ")
        for k in ("AB", "FRAG", "AMP", "AMB", "SOMA", "RCL"):
            if counts[k]:
                out_html.append(f"<span class='legend-item bg-{k}'>{k}: {counts[k]}</span>")
        out_html.append("</p>")
        out_html.append("</div>")

        # Legend
        out_html.append("<div class='legend'><b>Colour legend (driver categories)</b><br>")
        for k, name in DRIVER_NAMES.items():
            out_html.append(f"<span class='legend-item bg-{k}'>{k}</span> {html.escape(name)}<br>")
        out_html.append("</div>")

        # Annotated narrative
        out_html.append("<h2>Annotated trip report</h2>")
        out_html.append("<div class='narr'>")
        for start, end, active_idxs in pieces:
            text = html.escape(narrative[start:end])
            if not active_idxs:
                out_html.append(text)
            else:
                # Pick the most specific driver for the background colour.
                # Priority: RCL > SOMA > AMB > AMP > FRAG > AB  (flag solos first)
                priority = ["RCL", "SOMA", "AMB", "AMP", "FRAG", "AB"]
                active_drivers = [segments[i]["driver"] for i in active_idxs]
                colour_driver = next((d for d in priority if d in active_drivers), "AB")
                ids_list = ", ".join(segments[i]["scene"]["scene_id"] for i in active_idxs)
                out_html.append(
                    f"<span class='seg bg-{colour_driver}'>{text}"
                    f"<span class='seg-ids'>{html.escape(ids_list)}</span>"
                    f"</span>"
                )
        out_html.append("</div>")

        # Scene-by-scene index
        out_html.append("<h2>Scene index</h2>")
        out_html.append("<ul class='scene-list'>")
        for s in trip_scenes:
            drv = extract_driver(s["scene_id"])
            parent = s["parent_scene_id"]
            parent_str = f" — parent: <code>{html.escape(parent)}</code>" if parent else ""
            rationale = s.get("stage1_rationale", "")
            rat_str = f"<br><i>{html.escape(rationale)}</i>" if rationale else ""
            out_html.append(
                f"<li><span class='legend-item bg-{drv}'>{drv}</span> "
                f"<code>{html.escape(s['scene_id'])}</code>{parent_str}<br>"
                f"{html.escape(s['canonical_desc'] or '')}{rat_str}</li>"
            )
        out_html.append("</ul>")

        out_html.append("</body></html>")
        out_path = os.path.join(here, OUT_DIR, f"{trip_id}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(out_html))

    # Index page
    idx = ["<!doctype html><html><head><meta charset='utf-8'><title>Annotated trip reports</title>",
           "<style>body{font-family:Georgia,serif;max-width:900px;margin:2em auto;padding:0 2em;} "
           "table{border-collapse:collapse;width:100%;} td,th{padding:6px 12px;border:1px solid #ddd;}</style>",
           "</head><body><h1>Annotated trip reports</h1>",
           "<p>Each trip report is highlighted with driver-category colours. Hover a highlighted segment to see scene IDs.</p>",
           "<table><tr><th>Trip</th><th>Substance</th><th>Coders</th><th>Words</th></tr>"]
    for tid in sorted(trips.keys(), key=lambda x: (x.split('_')[0], int(x.split('_')[1]))):
        t = trips[tid]
        idx.append(f"<tr><td><a href='{tid}.html'>{tid}</a></td>"
                   f"<td>{t['substance']}</td>"
                   f"<td>{t['coder_A']} × {t['coder_B']}</td>"
                   f"<td>{t['word_count']}</td></tr>")
    idx.append("</table></body></html>")
    with open(os.path.join(here, OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(idx))

    print(f"wrote {len(trips)} annotated trip HTMLs to {OUT_DIR}/")
    print(f"   index: {OUT_DIR}/index.html")


if __name__ == "__main__":
    main()
