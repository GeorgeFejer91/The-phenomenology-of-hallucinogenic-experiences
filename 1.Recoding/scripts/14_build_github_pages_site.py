"""Build a single-page annotated trip-reports site at docs/index.html.

All 40 trip reports on one scrollable page with:
  - Fixed left sidebar: Brugmansia / Psilocybin groups, smooth-scroll links
  - Per-trip article with metadata, legend, and the narrative text
    with every individuated scene highlighted in its driver colour
  - Inline driver chips (e.g. [A: AMP]) at the start of each solo scene
  - Hover tooltip showing scene_id and driver rationale
  - Sticky top colour legend
  - Active-section highlighting in sidebar via IntersectionObserver

Output: docs/index.html  (plus minimal assets inline so GitHub Pages serves
it with no dependencies)
"""
import os, csv, html
from collections import defaultdict

DATA = "../data"
TRIPS_DIR = "../data/trips"
OUT_PATH = "../../docs/index.html"

DRIVER_ORDER = ["AB", "FRAG", "AMP", "AMB", "SOMA", "RCL"]
DRIVER_LABEL = {
    "AB":   "Both raters individuated (shared)",
    "FRAG": "Fragment — sub-scene of a holistic scene coded by the other rater",
    "AMP":  "Sensory amplification — ambient perceptual change, no discrete object",
    "AMB":  "Ambiguity — thought, memory, or metaphor coded as a hallucination",
    "SOMA": "Somatic — self-transformation or interoceptive content",
    "RCL":  "Reconciliation needed — likely genuine miss by the other rater",
}
DRIVER_SHORT = {
    "AB":   "SHARED",
    "FRAG": "FRAGMENT",
    "AMP":  "AMPLIFICATION",
    "AMB":  "AMBIGUITY",
    "SOMA": "SOMATIC",
    "RCL":  "RECONCILE",
}
DRIVER_COLOUR = {
    "AB":   "#b7e4c7",
    "FRAG": "#ffd79a",
    "AMP":  "#fff3a3",
    "AMB":  "#d5c6e0",
    "SOMA": "#f7c1d9",
    "RCL":  "#f4b4b4",
}


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


def build_narrative_html(narrative, scenes):
    """Build the HTML for a single trip's narrative with overlapping-span-safe
    highlights. Uses the standard sweep-line approach: emit one span per
    maximal segment where the same set of scenes is active.
    """
    # Collect segments with valid spans
    segs = []
    for s in scenes:
        a = parse_int(s["canonical_span_start"])
        b = parse_int(s["canonical_span_end"])
        if a is None or b is None or b <= a:
            continue
        b = min(b, len(narrative))
        if a >= len(narrative):
            continue
        segs.append({"start": a, "end": b, "scene": s, "driver": extract_driver(s["scene_id"])})
    if not segs:
        return html.escape(narrative)

    # Sweep events
    events = []
    for i, seg in enumerate(segs):
        events.append(("start", seg["start"], i))
        events.append(("end", seg["end"], i))
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

    # Render each piece
    priority = ["RCL", "SOMA", "AMB", "AMP", "FRAG", "AB"]
    out = []
    # Track scenes we've already emitted an opening chip for
    chipped = set()
    for start, end, active_idxs in pieces:
        text = html.escape(narrative[start:end])
        # Insert chips at the start of any scene that becomes active in this piece
        chips = ""
        for idx in sorted(active_idxs, key=lambda i: segs[i]["start"]):
            if idx in chipped:
                continue
            if segs[idx]["start"] == start:
                chipped.add(idx)
                s = segs[idx]["scene"]
                drv = segs[idx]["driver"]
                # Only show chip for solo scenes (drivers other than AB)
                if drv != "AB":
                    rater_letter = "A" if s["rater_status"] == "only_A" else "B"
                    chips += (
                        f'<span class="chip bg-{drv}" title="{html.escape(s["scene_id"])}: {html.escape(DRIVER_LABEL[drv])}">'
                        f'{rater_letter}: {DRIVER_SHORT[drv]}'
                        f'</span>'
                    )
        if not active_idxs:
            out.append(chips + text)
        else:
            active_drivers = [segs[i]["driver"] for i in active_idxs]
            colour_driver = next((d for d in priority if d in active_drivers), "AB")
            ids = ", ".join(segs[i]["scene"]["scene_id"] for i in active_idxs)
            drivers_str = " / ".join(sorted(set(active_drivers)))
            out.append(
                f'{chips}<span class="hl bg-{colour_driver}" '
                f'data-ids="{html.escape(ids)}" data-drivers="{html.escape(drivers_str)}" '
                f'title="{html.escape(ids)}">'
                f'{text}</span>'
            )
    return "".join(out)


def build_scene_index_html(scenes):
    rows = []
    for s in sorted(scenes, key=lambda s: parse_int(s["canonical_span_start"]) or 0):
        drv = extract_driver(s["scene_id"])
        parent = s.get("parent_scene_id", "")
        parent_str = f' — parent: <code>{html.escape(parent)}</code>' if parent else ""
        rat = s.get("stage1_rationale") or ""
        rat_str = f'<br><em>{html.escape(rat)}</em>' if rat else ""
        rows.append(
            f'<li><span class="chip bg-{drv}">{DRIVER_SHORT[drv]}</span> '
            f'<code>{html.escape(s["scene_id"])}</code>{parent_str}<br>'
            f'<small>{html.escape(s.get("canonical_desc", "") or "")}</small>{rat_str}</li>'
        )
    return "\n".join(rows)


def main():
    here = os.path.dirname(__file__)
    trips = load("trips.csv")
    scenes = load("scenes.csv")
    scenes_by_trip = defaultdict(list)
    for s in scenes:
        scenes_by_trip[s["trip_id"]].append(s)

    # Sort trips substance-first
    trips.sort(key=lambda t: (
        0 if t["substance"] == "brugmansia" else 1,
        int(t["trip_id"].split("_")[-1]),
    ))

    # Sidebar groups
    groups = {"brugmansia": [], "psilocybin": []}
    for t in trips:
        groups[t["substance"]].append(t)

    # Build sidebar
    sidebar = ['<aside class="sidebar"><div class="sidebar-inner">']
    sidebar.append('<div class="sidebar-header"><h1>Trip reports</h1>'
                   '<p class="subtle">40 trip reports, annotated with rater-agreement drivers</p></div>')
    for sub in ("brugmansia", "psilocybin"):
        if not groups[sub]:
            continue
        sidebar.append(f'<h2 class="sidebar-group">{sub.title()} <span class="subtle">({len(groups[sub])})</span></h2>')
        sidebar.append('<ul class="sidebar-list">')
        for t in groups[sub]:
            n_scenes = len(scenes_by_trip[t["trip_id"]])
            n_shared = sum(1 for s in scenes_by_trip[t["trip_id"]]
                           if s["rater_status"] == "both")
            # Per-trip driver counts (solo only)
            drv_counts = defaultdict(int)
            for s in scenes_by_trip[t["trip_id"]]:
                d = extract_driver(s["scene_id"])
                if d != "AB":
                    drv_counts[d] += 1
            drv_dots = "".join(
                f'<span class="dot bg-{d}" title="{DRIVER_SHORT[d]}:{n}"></span>'
                for d in DRIVER_ORDER if d != "AB" for n in [drv_counts[d]] if n > 0
            )
            sidebar.append(
                f'<li><a href="#{t["trip_id"]}" data-trip="{t["trip_id"]}">'
                f'<span class="trip-id">{t["trip_id"]}</span>'
                f'<span class="trip-stats">{n_shared}/{n_scenes} shared '
                f'<span class="words">{t["word_count"]}w</span></span>'
                f'<span class="trip-drivers">{drv_dots}</span>'
                f'</a></li>'
            )
        sidebar.append('</ul>')
    sidebar.append('</div></aside>')

    # Build main content
    main = ['<main class="main">']
    main.append('<header class="main-header">')
    main.append('<h1>Annotated trip reports</h1>')
    main.append('<p class="subtle">Every individuated hallucinatory scene is highlighted on the narrative. '
                'Solo scenes (individuated by only one rater) carry an inline chip showing which rater '
                '(A/B) and the discrepancy driver (AMP / AMB / SOMA / FRAG / RCL). '
                'Hover a highlight for the scene ID.</p>')
    main.append('<div class="legend">')
    main.append('<strong>Driver colours:</strong><br>')
    for k in DRIVER_ORDER:
        main.append(
            f'<span class="legend-item"><span class="chip bg-{k}">{DRIVER_SHORT[k]}</span> '
            f'{html.escape(DRIVER_LABEL[k])}</span>'
        )
    main.append('</div>')
    main.append('</header>')

    for t in trips:
        trip_id = t["trip_id"]
        narr_path = os.path.join(here, TRIPS_DIR, f"{trip_id}.txt")
        if not os.path.exists(narr_path):
            continue
        with open(narr_path, encoding="utf-8") as f:
            narrative = f.read()
        trip_scenes = scenes_by_trip[trip_id]

        # Per-trip counts
        drv_counts = defaultdict(int)
        for s in trip_scenes:
            drv_counts[extract_driver(s["scene_id"])] += 1

        main.append(f'<article class="trip" id="{trip_id}">')
        main.append(f'<h2>{trip_id}</h2>')
        main.append('<div class="trip-meta">')
        main.append(f'<span><strong>substance:</strong> {t["substance"]}</span>')
        main.append(f'<span><strong>block:</strong> {t["block"]}</span>')
        main.append(f'<span><strong>coders:</strong> {t["coder_A"]} × {t["coder_B"]}</span>')
        main.append(f'<span><strong>dose:</strong> {t["dose_raw"] or "—"}</span>')
        main.append(f'<span><strong>words:</strong> {t["word_count"]}</span>')
        main.append(f'<span><strong>scenes:</strong> {len(trip_scenes)}</span>')
        main.append('</div>')

        # Driver breakdown strip
        main.append('<div class="trip-drivers-strip">')
        for k in DRIVER_ORDER:
            if drv_counts[k]:
                main.append(f'<span class="chip bg-{k}">{DRIVER_SHORT[k]}: {drv_counts[k]}</span>')
        main.append('</div>')

        # Narrative
        main.append('<div class="narrative">')
        main.append(build_narrative_html(narrative, trip_scenes))
        main.append('</div>')

        # Per-trip scene index (collapsible)
        main.append('<details class="scene-details"><summary>Scene index '
                    f'({len(trip_scenes)} scenes)</summary>')
        main.append('<ul class="scene-index">')
        main.append(build_scene_index_html(trip_scenes))
        main.append('</ul></details>')

        main.append('</article>')

    main.append('</main>')

    # CSS (inline)
    css = """
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; scroll-padding-top: 1rem; }
    body {
      margin: 0;
      font-family: 'Iowan Old Style', 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
      background: #f7f5f2;
      color: #1a1a1a;
      line-height: 1.6;
    }
    .sidebar {
      position: fixed;
      top: 0; left: 0; bottom: 0;
      width: 280px;
      background: #2b2b2b;
      color: #e8e6e1;
      overflow-y: auto;
      border-right: 1px solid #111;
      z-index: 50;
    }
    .sidebar-inner { padding: 1.2rem 0.9rem; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .sidebar-header h1 { font-size: 1.05rem; margin: 0 0 0.3rem; }
    .sidebar-header .subtle { font-size: 0.75rem; color: #999; margin: 0 0 1rem; }
    .sidebar-group {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #9a9690;
      margin: 1.2rem 0.3rem 0.3rem;
      padding-bottom: 0.2rem;
      border-bottom: 1px solid #3a3a3a;
    }
    .sidebar-list { list-style: none; padding: 0; margin: 0; }
    .sidebar-list li a {
      display: block;
      padding: 0.35rem 0.5rem;
      color: #e8e6e1;
      text-decoration: none;
      font-size: 0.8rem;
      border-left: 2px solid transparent;
      transition: background 0.12s, border-color 0.12s;
    }
    .sidebar-list li a:hover { background: #3a3a3a; }
    .sidebar-list li a.active {
      background: #3a3a3a;
      border-left-color: #ffd79a;
      color: #fff;
    }
    .trip-id { display: block; font-weight: 600; }
    .trip-stats { display: block; font-size: 0.7rem; color: #aaa; }
    .trip-drivers { margin-top: 2px; display: block; }
    .dot {
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      margin-right: 2px;
    }
    .words { color: #777; }
    .main {
      margin-left: 300px;
      padding: 2rem 2.5rem;
      max-width: 900px;
    }
    .main-header {
      padding-bottom: 1.5rem;
      border-bottom: 1px solid #ddd;
      margin-bottom: 2rem;
    }
    .main-header h1 { margin: 0 0 0.5rem; font-size: 1.8rem; }
    .subtle { color: #666; font-size: 0.9rem; }
    .legend {
      background: #fff;
      border: 1px solid #e0d9ce;
      padding: 0.9rem 1rem;
      border-radius: 4px;
      margin-top: 1rem;
      font-size: 0.85rem;
      line-height: 2;
    }
    .legend-item { display: inline-block; margin-right: 1.5rem; }
    .chip {
      display: inline-block;
      padding: 1px 6px;
      border-radius: 3px;
      font-family: 'SF Mono', Menlo, monospace;
      font-size: 0.75rem;
      font-weight: 700;
      color: #333;
      margin: 0 2px;
      vertical-align: baseline;
    }
    .trip {
      background: #fff;
      border: 1px solid #e5dfd4;
      border-radius: 6px;
      padding: 1.6rem 1.8rem;
      margin-bottom: 2rem;
      scroll-margin-top: 1.5rem;
    }
    .trip h2 {
      margin: 0 0 0.3rem;
      font-size: 1.4rem;
      font-weight: 600;
    }
    .trip-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 0.3rem 1.1rem;
      font-size: 0.82rem;
      color: #555;
      margin-bottom: 0.8rem;
    }
    .trip-meta strong { color: #333; }
    .trip-drivers-strip {
      margin: 0.3rem 0 1rem;
      font-size: 0.7rem;
    }
    .narrative {
      white-space: pre-wrap;
      background: #fdfcf9;
      padding: 1.2rem 1.4rem;
      border-radius: 4px;
      border: 1px solid #eee5d2;
      font-size: 1rem;
      line-height: 1.75;
    }
    .hl {
      border-radius: 2px;
      padding: 1px 2px;
      cursor: help;
      border-bottom: 1px dotted rgba(0,0,0,0.15);
    }
    .scene-details {
      margin-top: 1.2rem;
      font-size: 0.85rem;
    }
    .scene-details summary {
      cursor: pointer;
      color: #555;
      font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
      padding: 0.3rem 0;
    }
    .scene-index {
      list-style: none;
      padding: 0.5rem 0 0;
      margin: 0;
    }
    .scene-index li {
      margin-bottom: 0.6rem;
      padding: 0.4rem 0.6rem;
      background: #faf8f4;
      border-left: 3px solid #ddd;
      border-radius: 2px;
    }
    .scene-index code {
      background: #eee;
      padding: 1px 4px;
      border-radius: 2px;
      font-size: 0.85em;
    }
    .scene-index em { color: #666; }

    .bg-AB   { background-color: #b7e4c7; }
    .bg-FRAG { background-color: #ffd79a; }
    .bg-AMP  { background-color: #fff3a3; }
    .bg-AMB  { background-color: #d5c6e0; }
    .bg-SOMA { background-color: #f7c1d9; }
    .bg-RCL  { background-color: #f4b4b4; }

    @media (max-width: 900px) {
      .sidebar { position: static; width: 100%; height: auto; max-height: 400px; }
      .main { margin-left: 0; padding: 1rem; }
    }
    """

    # JS (minimal — active link + IntersectionObserver)
    js = """
    (function () {
      const links = document.querySelectorAll('.sidebar-list a');
      const sectionMap = new Map();
      links.forEach(a => {
        const id = a.getAttribute('data-trip');
        const sec = document.getElementById(id);
        if (sec) sectionMap.set(sec, a);
      });
      const setActive = (link) => {
        links.forEach(a => a.classList.remove('active'));
        link.classList.add('active');
        // Scroll sidebar to keep active link visible
        const sidebar = document.querySelector('.sidebar');
        const linkRect = link.getBoundingClientRect();
        const sideRect = sidebar.getBoundingClientRect();
        if (linkRect.top < sideRect.top || linkRect.bottom > sideRect.bottom) {
          link.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
      };
      const io = new IntersectionObserver((entries) => {
        // pick the entry nearest the top that is intersecting
        let best = null, bestTop = Infinity;
        entries.forEach(e => {
          if (e.isIntersecting && e.boundingClientRect.top >= 0 && e.boundingClientRect.top < bestTop) {
            best = e; bestTop = e.boundingClientRect.top;
          }
        });
        if (best) {
          const link = sectionMap.get(best.target);
          if (link) setActive(link);
        }
      }, { rootMargin: '-10% 0px -70% 0px', threshold: 0 });
      sectionMap.forEach((_, sec) => io.observe(sec));
      // Initial active state based on hash or first
      if (location.hash) {
        const target = document.querySelector(location.hash);
        if (target && sectionMap.has(target)) setActive(sectionMap.get(target));
      } else if (links.length) {
        setActive(links[0]);
      }
    })();
    """

    # Assemble
    doc = [
        '<!doctype html>',
        '<html lang="en"><head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>Annotated trip reports — the phenomenology of hallucinogenic experiences</title>',
        f'<style>{css}</style>',
        '</head>',
        '<body>',
        *sidebar,
        *main,
        f'<script>{js}</script>',
        '</body></html>',
    ]
    out_full = "\n".join(doc)

    out_path = os.path.abspath(os.path.join(here, OUT_PATH))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out_full)
    size_kb = len(out_full.encode("utf-8")) / 1024
    print(f"wrote {out_path}  ({size_kb:.0f} KB)")
    print(f"  {len(trips)} trips, {len(scenes)} scenes highlighted")


if __name__ == "__main__":
    main()
