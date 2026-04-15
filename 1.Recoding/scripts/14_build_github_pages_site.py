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

# Verdict classes — the THREE-class Stage-1 framework (the primary analytical
# output the user is asked to inspect manually on this page).
VERDICT_ORDER = ["CONVERGENT", "MISS", "GRANULARITY", "AMBIGUITY-2a", "AMBIGUITY-2b"]
VERDICT_SHORT = {
    "CONVERGENT":   "CONVERGENT",
    "MISS":         "MISS",
    "GRANULARITY":  "GRAN",
    "AMBIGUITY-2a": "AMB-2a",
    "AMBIGUITY-2b": "AMB-2b",
}
VERDICT_LABEL = {
    "CONVERGENT":   "Both raters individuated this passage (shared scene)",
    "MISS":         "Rater-compliance gap — the other rater overlooked a passage they should have individuated by their own observed criterion",
    "GRANULARITY":  "Lump-vs-split disagreement — fragment of a larger scene the other rater individuated; pooled under its parent for downstream analysis",
    "AMBIGUITY-2a": "Instrument-design gap — the Guidelines under-specify this edge case (deferred: rewrite the Guidelines)",
    "AMBIGUITY-2b": "Instrument-design gap — the passage is phenomenologically real but outside the hallucinatory-scene category (deferred: add new non-scene taxonomy category)",
}
VERDICT_COLOUR = {
    "CONVERGENT":   "#16a34a",  # green — shared scene
    "MISS":         "#b91c1c",  # red — compliance gap
    "GRANULARITY":  "#1565c0",  # blue — lump/split
    "AMBIGUITY-2a": "#d97706",  # amber — clarify rule
    "AMBIGUITY-2b": "#6b21a8",  # purple — new category
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


def verdict_for_scene(scene, verdicts_by_scene):
    """Return the verdict class string for a scene: one of
    CONVERGENT / MISS / GRANULARITY / AMBIGUITY-2a / AMBIGUITY-2b.
    """
    if scene["rater_status"] == "both":
        return "CONVERGENT"
    v = verdicts_by_scene.get(scene["scene_id"])
    if not v:
        return "MISS"  # fallback; shouldn't happen in practice
    flavour = v.get("verdict_flavour", "") or ""
    verdict = v["verdict"]
    if verdict == "AMBIGUITY" and flavour:
        return f"AMBIGUITY-{flavour}"
    return verdict


def build_narrative_html(narrative, scenes, verdicts_by_scene):
    """Build the HTML for a single trip's narrative with overlapping-span-safe
    highlights. Uses the standard sweep-line approach: emit one span per
    maximal segment where the same set of scenes is active.
    Each highlighted span carries a data-verdict attribute for JS filtering.
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
    # Verdict priority for selecting the highlight colour when multiple scenes
    # overlap: divergence classes take visual precedence over CONVERGENT so
    # the reader sees the disagreement, not just the agreement.
    priority = ["AMBIGUITY-2b", "AMBIGUITY-2a", "MISS", "GRANULARITY", "CONVERGENT"]
    out = []
    chipped = set()
    for start, end, active_idxs in pieces:
        text = html.escape(narrative[start:end])
        chips = ""
        for idx in sorted(active_idxs, key=lambda i: segs[i]["start"]):
            if idx in chipped:
                continue
            if segs[idx]["start"] == start:
                chipped.add(idx)
                s = segs[idx]["scene"]
                verdict = verdict_for_scene(s, verdicts_by_scene)
                # Only chip for solo scenes (CONVERGENT highlights don't need a chip)
                if verdict != "CONVERGENT":
                    rater_letter = "A" if s["rater_status"] == "only_A" else "B"
                    v = verdicts_by_scene.get(s["scene_id"], {})
                    parent = v.get("parent_scene_id", "")
                    arrow = f"→{parent.rsplit('_S', 1)[-1].split('_')[0]}" if parent else ""
                    chip_label = VERDICT_SHORT[verdict] + arrow
                    rationale = v.get("rationale", "") or ""
                    tooltip = f"{s['scene_id']}: {VERDICT_LABEL[verdict]}"
                    if rationale:
                        tooltip += f"  —  {rationale}"
                    chips += (
                        f'<span class="chip chip-verdict v-{verdict}" '
                        f'data-verdict="{verdict}" '
                        f'title="{html.escape(tooltip)}">'
                        f'{rater_letter}: {chip_label}</span>'
                    )
        if not active_idxs:
            out.append(chips + text)
        else:
            active_verdicts = [verdict_for_scene(segs[i]["scene"], verdicts_by_scene) for i in active_idxs]
            # Pick highlight verdict by divergence priority (so CONVERGENT
            # overlapping a MISS shows the MISS colour to the reader)
            colour_verdict = next((d for d in priority if d in active_verdicts), "CONVERGENT")
            ids = ", ".join(segs[i]["scene"]["scene_id"] for i in active_idxs)
            verdict_str = " / ".join(sorted(set(active_verdicts)))
            # Build a rich tooltip with the verdict + scene_id(s) + rationale(s) of any solo scene
            tooltip_parts = []
            for i in active_idxs:
                s = segs[i]["scene"]
                v_cls = verdict_for_scene(s, verdicts_by_scene)
                if v_cls == "CONVERGENT":
                    tooltip_parts.append(f"{s['scene_id']}: CONVERGENT")
                else:
                    vobj = verdicts_by_scene.get(s["scene_id"], {})
                    rat = (vobj.get("rationale", "") or "")[:220]
                    parent = vobj.get("parent_scene_id", "")
                    ptxt = f" (parent: {parent})" if parent else ""
                    tooltip_parts.append(f"{s['scene_id']}: {v_cls}{ptxt}  —  {rat}")
            tooltip = "  ||  ".join(tooltip_parts)
            out.append(
                f'<span class="hl v-{colour_verdict}" '
                f'data-ids="{html.escape(ids)}" data-verdicts="{html.escape(verdict_str)}" '
                f'title="{html.escape(tooltip)}">'
                f'{chips}{text}</span>'
            )
    return "".join(out)


def build_scene_index_html(scenes, verdicts_by_scene):
    rows = []
    for s in sorted(scenes, key=lambda s: parse_int(s["canonical_span_start"]) or 0):
        verdict = verdict_for_scene(s, verdicts_by_scene)
        v = verdicts_by_scene.get(s["scene_id"], {}) or {}
        parent = v.get("parent_scene_id") or s.get("parent_scene_id", "") or ""
        parent_str = (f' <span class="index-parent">→ pooled under <a href="#scene-{html.escape(parent)}">'
                      f'<code>{html.escape(parent)}</code></a></span>') if parent else ""
        verdict_rationale = v.get("rationale", "") or ""
        scene_rationale   = s.get("stage1_rationale", "") or ""
        # Prefer the verdict rationale (newer, more analytically specific)
        rat = verdict_rationale or scene_rationale
        rat_str = f'<div class="index-rationale"><em>{html.escape(rat)}</em></div>' if rat else ""
        rows.append(
            f'<li class="scene-entry" id="scene-{html.escape(s["scene_id"])}" data-verdict="{verdict}">'
            f'<span class="chip chip-verdict v-{verdict}">{VERDICT_SHORT[verdict]}</span> '
            f'<code>{html.escape(s["scene_id"])}</code>{parent_str}'
            f'<div class="index-desc">{html.escape(s.get("canonical_desc", "") or "")}</div>'
            f'{rat_str}'
            f'</li>'
        )
    return "\n".join(rows)


def main():
    here = os.path.dirname(__file__)
    trips = load("trips.csv")
    scenes = load("scenes.csv")
    scenes_by_trip = defaultdict(list)
    for s in scenes:
        scenes_by_trip[s["trip_id"]].append(s)
    # Stage-1 verdicts (the primary analytical output — see AI_DIRECTIVE.md)
    try:
        verdict_rows = load("stage1_verdicts.csv")
    except FileNotFoundError:
        verdict_rows = []
    verdicts_by_scene = {v["scene_id"]: v for v in verdict_rows}

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
                   '<p class="subtle">40 trip reports, annotated with rater-agreement drivers</p>'
                   '<p class="nav-links"><a href="visualizations.html">→ Dynamic visualizations</a></p></div>')
    for sub in ("brugmansia", "psilocybin"):
        if not groups[sub]:
            continue
        sidebar.append(f'<h2 class="sidebar-group">{sub.title()} <span class="subtle">({len(groups[sub])})</span></h2>')
        sidebar.append('<ul class="sidebar-list">')
        for t in groups[sub]:
            n_scenes = len(scenes_by_trip[t["trip_id"]])
            n_shared = sum(1 for s in scenes_by_trip[t["trip_id"]]
                           if s["rater_status"] == "both")
            # Per-trip verdict counts (solo scenes only — divergence classes)
            v_counts = defaultdict(int)
            for s in scenes_by_trip[t["trip_id"]]:
                vc = verdict_for_scene(s, verdicts_by_scene)
                if vc != "CONVERGENT":
                    v_counts[vc] += 1
            v_dots = "".join(
                f'<span class="dot v-{vc}" title="{VERDICT_SHORT[vc]}:{n}"></span>'
                for vc in VERDICT_ORDER if vc != "CONVERGENT" for n in [v_counts[vc]] if n > 0
            )
            sidebar.append(
                f'<li><a href="#{t["trip_id"]}" data-trip="{t["trip_id"]}">'
                f'<span class="trip-id">{t["trip_id"]}</span>'
                f'<span class="trip-stats">{n_shared}/{n_scenes} shared '
                f'<span class="words">{t["word_count"]}w</span></span>'
                f'<span class="trip-drivers">{v_dots}</span>'
                f'</a></li>'
            )
        sidebar.append('</ul>')
    sidebar.append('</div></aside>')

    # Build main content
    main = ['<main class="main">']
    main.append('<header class="main-header">')
    main.append('<h1>Annotated trip reports</h1>')
    main.append('<div class="directive">'
                '<strong>Stage 1 scope — scene individuation only.</strong> '
                'This site measures whether <em>both</em> raters individuated the same narrative '
                'passages as hallucinatory scenes. For every only-one-rater scene the analytical '
                'question is MISS (the other rater overlooked it — rater-compliance gap) vs '
                'AMBIGUITY (PDF Guidelines do not cleanly cover the edge case — instruction-design gap). '
                'Rater subjective judgement on what counts as a hallucinatory scene is the PRIMARY DATA; '
                'attribute-level disagreement (illusion vs incrusted, object class, etc.) is Stage 2, deferred. '
                'See <code>AI_DIRECTIVE.md</code> and <code>1.Recoding/STAGE1_SCOPE.json</code> in the repo.'
                '</div>')
    main.append('<p class="subtle">Every individuated passage is highlighted and colour-coded by '
                'its Stage-1 <strong>verdict class</strong>. Hover a highlight for the full verdict '
                'rationale. Use the filter bar below to focus on one class at a time — e.g. show only '
                'MISS scenes to inspect the raw compliance-gap cases, or only AMBIGUITY-2b scenes to '
                'see phenomena that fall outside the current hallucinatory-scene category.</p>')
    # Verdict-class legend (THE primary analytical framework)
    main.append('<div class="legend">')
    main.append('<strong>Verdict classes (Stage 1):</strong><br>')
    for k in VERDICT_ORDER:
        main.append(
            f'<span class="legend-item"><span class="chip chip-verdict v-{k}">{VERDICT_SHORT[k]}</span> '
            f'{html.escape(VERDICT_LABEL[k])}</span>'
        )
    main.append('</div>')
    # Interactive filter bar
    main.append('<div class="filter-bar" id="filter-bar">')
    main.append('<strong>Show:</strong>')
    for k in VERDICT_ORDER:
        main.append(
            f'<label class="filter-item v-{k}">'
            f'<input type="checkbox" data-filter="{k}" checked> '
            f'<span class="filter-dot v-{k}"></span>{VERDICT_SHORT[k]}'
            f'</label>'
        )
    main.append('<button type="button" id="filter-only-div" class="filter-btn">'
                'Hide convergent (show divergences only)</button>')
    main.append('<button type="button" id="filter-all" class="filter-btn">Reset</button>')
    main.append('</div>')
    # Corpus-level summary: totals per verdict class and substance split
    corpus_counts = defaultdict(lambda: defaultdict(int))
    for s in scenes:
        vc = verdict_for_scene(s, verdicts_by_scene)
        corpus_counts["all"][vc] += 1
        # Look up substance from the trip
        tid = s["trip_id"]
        sub = next((t["substance"] for t in trips if t["trip_id"] == tid), "?")
        corpus_counts[sub][vc] += 1
    main.append('<div class="corpus-summary">')
    main.append('<strong>Corpus totals:</strong> ')
    main.append(f'<span>{sum(corpus_counts["all"].values())} scenes '
                f'= {corpus_counts["all"]["CONVERGENT"]} CONVERGENT '
                f'+ {sum(corpus_counts["all"][v] for v in VERDICT_ORDER if v != "CONVERGENT")} divergent</span>')
    for vc in VERDICT_ORDER:
        n = corpus_counts["all"][vc]
        if n:
            main.append(f'<span class="chip chip-verdict v-{vc}">{VERDICT_SHORT[vc]}: {n}</span>')
    main.append('<br><span style="color:#1b4332;font-weight:600;">brugmansia</span>: ')
    for vc in VERDICT_ORDER:
        n = corpus_counts["brugmansia"][vc]
        if n:
            main.append(f'<span class="chip chip-verdict v-{vc}">{VERDICT_SHORT[vc]}: {n}</span>')
    main.append(' <span style="color:#9b111e;font-weight:600;">psilocybin</span>: ')
    for vc in VERDICT_ORDER:
        n = corpus_counts["psilocybin"][vc]
        if n:
            main.append(f'<span class="chip chip-verdict v-{vc}">{VERDICT_SHORT[vc]}: {n}</span>')
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

        # Per-trip verdict counts
        v_counts = defaultdict(int)
        for s in trip_scenes:
            v_counts[verdict_for_scene(s, verdicts_by_scene)] += 1

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

        # Per-trip verdict strip (the primary analytical breakdown)
        main.append('<div class="trip-drivers-strip">')
        for k in VERDICT_ORDER:
            if v_counts[k]:
                main.append(f'<span class="chip chip-verdict v-{k}">{VERDICT_SHORT[k]}: {v_counts[k]}</span>')
        main.append('</div>')

        # Narrative
        main.append('<div class="narrative">')
        main.append(build_narrative_html(narrative, trip_scenes, verdicts_by_scene))
        main.append('</div>')

        # Per-trip scene index (collapsible, now with verdict rationales)
        main.append('<details class="scene-details"><summary>Scene index '
                    f'({len(trip_scenes)} scenes — click to expand)</summary>')
        main.append('<ul class="scene-index">')
        main.append(build_scene_index_html(trip_scenes, verdicts_by_scene))
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
    .sidebar-header .subtle { font-size: 0.75rem; color: #999; margin: 0 0 0.5rem; }
    .sidebar-header .nav-links a {
      display: inline-block;
      color: #ffd79a;
      text-decoration: none;
      font-size: 0.82rem;
      padding: 0.25rem 0.5rem;
      border: 1px solid #5a4e36;
      border-radius: 3px;
      margin-top: 0.2rem;
    }
    .sidebar-header .nav-links a:hover { background: #3a3a3a; }
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
    .directive {
      background: #fff9e6;
      border-left: 4px solid #c9a227;
      padding: 0.8rem 1rem;
      margin: 0.8rem 0 1rem;
      font-size: 0.82rem;
      line-height: 1.5;
      color: #3b3426;
      border-radius: 3px;
    }
    .directive strong { color: #6b4e00; }
    .directive code { background: #f0e4b8; padding: 1px 4px; border-radius: 2px; font-size: 0.9em; }
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

    /* ---- VERDICT CLASS STYLES ---- */
    /* Each verdict has a tinted background for highlights and a saturated border.
       The chip-verdict variant is the bold label used inline + in the index. */
    .v-CONVERGENT   { background-color: #d1fae5; border-left: 3px solid #16a34a; }
    .v-MISS         { background-color: #fee2e2; border-left: 3px solid #b91c1c; }
    .v-GRANULARITY  { background-color: #dbeafe; border-left: 3px solid #1565c0; }
    .v-AMBIGUITY-2a { background-color: #fef3c7; border-left: 3px solid #d97706; }
    .v-AMBIGUITY-2b { background-color: #ede9fe; border-left: 3px solid #6b21a8; }

    .hl.v-CONVERGENT,
    .hl.v-MISS,
    .hl.v-GRANULARITY,
    .hl.v-AMBIGUITY-2a,
    .hl.v-AMBIGUITY-2b {
      border-left: none;
      border-bottom: 2px solid;
      padding: 1px 3px;
    }
    .hl.v-CONVERGENT   { background-color: #d1fae5; border-bottom-color: #16a34a; }
    .hl.v-MISS         { background-color: #fee2e2; border-bottom-color: #b91c1c; }
    .hl.v-GRANULARITY  { background-color: #dbeafe; border-bottom-color: #1565c0; }
    .hl.v-AMBIGUITY-2a { background-color: #fef3c7; border-bottom-color: #d97706; }
    .hl.v-AMBIGUITY-2b { background-color: #ede9fe; border-bottom-color: #6b21a8; }

    .chip-verdict {
      color: #fff;
      padding: 1px 7px;
      border-radius: 3px;
      font-size: 0.72rem;
      letter-spacing: 0.02em;
    }
    .chip-verdict.v-CONVERGENT   { background-color: #16a34a; }
    .chip-verdict.v-MISS         { background-color: #b91c1c; }
    .chip-verdict.v-GRANULARITY  { background-color: #1565c0; }
    .chip-verdict.v-AMBIGUITY-2a { background-color: #d97706; }
    .chip-verdict.v-AMBIGUITY-2b { background-color: #6b21a8; }

    /* Sidebar dots */
    .dot.v-CONVERGENT   { background-color: #16a34a; }
    .dot.v-MISS         { background-color: #b91c1c; }
    .dot.v-GRANULARITY  { background-color: #1565c0; }
    .dot.v-AMBIGUITY-2a { background-color: #d97706; }
    .dot.v-AMBIGUITY-2b { background-color: #6b21a8; }

    /* ---- FILTER BAR ---- */
    .filter-bar {
      position: sticky;
      top: 0;
      background: #fff;
      border: 1px solid #e5dfd4;
      padding: 0.6rem 1rem;
      margin: 1rem 0 1rem;
      border-radius: 4px;
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem 0.8rem;
      align-items: center;
      font-size: 0.82rem;
      z-index: 40;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .filter-bar strong { margin-right: 0.5rem; }
    .filter-item { display: inline-flex; align-items: center; gap: 0.3rem; cursor: pointer; user-select: none; }
    .filter-item input { margin: 0; }
    .filter-dot {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin-right: 3px;
    }
    .filter-dot.v-CONVERGENT   { background-color: #16a34a; }
    .filter-dot.v-MISS         { background-color: #b91c1c; }
    .filter-dot.v-GRANULARITY  { background-color: #1565c0; }
    .filter-dot.v-AMBIGUITY-2a { background-color: #d97706; }
    .filter-dot.v-AMBIGUITY-2b { background-color: #6b21a8; }
    .filter-btn {
      font: inherit;
      padding: 3px 10px;
      border: 1px solid #ccc;
      background: #fafafa;
      border-radius: 3px;
      cursor: pointer;
    }
    .filter-btn:hover { background: #f0f0f0; }

    /* When a verdict class is filtered off, its highlight goes plain-text */
    .hl.filtered-off {
      background-color: transparent !important;
      border-bottom: none !important;
      padding: 0 !important;
    }
    .chip-verdict.filtered-off { display: none; }
    .scene-entry.filtered-off { display: none; }

    /* Corpus summary */
    .corpus-summary {
      background: #f8f6f2;
      border: 1px solid #e0d9ce;
      padding: 0.7rem 1rem;
      margin-top: 0.8rem;
      border-radius: 4px;
      font-size: 0.78rem;
      line-height: 1.9;
    }

    /* Scene index richer rendering */
    .scene-entry { margin-bottom: 0.7rem !important; padding: 0.55rem 0.8rem !important; }
    .scene-entry[data-verdict="CONVERGENT"]   { border-left-color: #16a34a !important; }
    .scene-entry[data-verdict="MISS"]         { border-left-color: #b91c1c !important; }
    .scene-entry[data-verdict="GRANULARITY"]  { border-left-color: #1565c0 !important; }
    .scene-entry[data-verdict="AMBIGUITY-2a"] { border-left-color: #d97706 !important; }
    .scene-entry[data-verdict="AMBIGUITY-2b"] { border-left-color: #6b21a8 !important; }
    .index-parent { font-size: 0.82em; color: #555; }
    .index-parent a { color: #1565c0; }
    .index-desc { margin: 0.25rem 0; color: #333; }
    .index-rationale { font-size: 0.88em; color: #555; margin-top: 0.25rem; }

    @media (max-width: 900px) {
      .sidebar { position: static; width: 100%; height: auto; max-height: 400px; }
      .main { margin-left: 0; padding: 1rem; }
      .filter-bar { position: static; }
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

      // -------- VERDICT FILTER --------
      const VERDICT_CLASSES = ['CONVERGENT','MISS','GRANULARITY','AMBIGUITY-2a','AMBIGUITY-2b'];
      const filterBoxes = document.querySelectorAll('.filter-bar input[data-filter]');
      function applyFilters() {
        const active = new Set();
        filterBoxes.forEach(b => { if (b.checked) active.add(b.dataset.filter); });
        // Highlights in narrative: span.hl has a v-X class — hide the tint/border when not active
        document.querySelectorAll('.hl').forEach(el => {
          // Determine primary verdict class
          const vc = VERDICT_CLASSES.find(v => el.classList.contains('v-' + v));
          if (vc && !active.has(vc)) el.classList.add('filtered-off');
          else el.classList.remove('filtered-off');
        });
        // Inline verdict chips
        document.querySelectorAll('.chip-verdict').forEach(el => {
          const vc = VERDICT_CLASSES.find(v => el.classList.contains('v-' + v));
          if (vc && !active.has(vc)) el.classList.add('filtered-off');
          else el.classList.remove('filtered-off');
        });
        // Scene index entries
        document.querySelectorAll('.scene-entry').forEach(el => {
          const vc = el.dataset.verdict;
          if (vc && !active.has(vc)) el.classList.add('filtered-off');
          else el.classList.remove('filtered-off');
        });
      }
      filterBoxes.forEach(b => b.addEventListener('change', applyFilters));
      const btnOnlyDiv = document.getElementById('filter-only-div');
      const btnAll = document.getElementById('filter-all');
      if (btnOnlyDiv) btnOnlyDiv.addEventListener('click', () => {
        filterBoxes.forEach(b => {
          b.checked = (b.dataset.filter !== 'CONVERGENT');
        });
        applyFilters();
      });
      if (btnAll) btnAll.addEventListener('click', () => {
        filterBoxes.forEach(b => { b.checked = true; });
        applyFilters();
      });
      applyFilters();

      // -------- SCENE-ID DEEP LINK --------
      // If an .index-parent link is clicked we jump to that scene's anchor;
      // this is already supported by the #anchors in the index.
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
