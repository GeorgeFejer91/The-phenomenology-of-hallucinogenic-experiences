"""Build docs/visualizations.html — a dynamic charts subpage.

Embeds scenes + codes + trips as compact JSON, wires them to Chart.js
charts with client-side filters. No server, no build step.

Charts included:
  1. Scene counts by driver category (grouped by substance/pair/coder)
  2. Shared-vs-solo proportions
  3. Top taxonomy items (configurable depth + consensus filter)
  4. Rater-style comparison (codes/scene, tag-specific usage)
  5. Trip-level driver heatmap
"""
import os, csv, json

DATA = "../data"
OUT = "../../docs/visualizations.html"


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
    try: return int(s)
    except (ValueError, TypeError): return None


def main():
    here = os.path.dirname(__file__)
    trips = load("trips.csv")
    scenes = load("scenes.csv")
    codes = load("codes.csv")
    flags = load("agreement_flags.csv")

    # Trip metadata by id
    trip_by_id = {t["trip_id"]: t for t in trips}

    # Compact scenes
    scenes_js = []
    for s in scenes:
        t = trip_by_id.get(s["trip_id"], {})
        scenes_js.append({
            "scene_id": s["scene_id"],
            "trip_id": s["trip_id"],
            "substance": t.get("substance", ""),
            "block": t.get("block", ""),
            "coder_A": t.get("coder_A", ""),
            "coder_B": t.get("coder_B", ""),
            "rater_status": s["rater_status"],
            "driver": extract_driver(s["scene_id"]),
        })

    # Compact codes (scene-level only is enough for the aggregations we need,
    # plus keep trip-level so Rater-style can count them)
    codes_js = []
    for c in codes:
        t = trip_by_id.get(c["trip_id"], {})
        codes_js.append({
            "scene_id": c.get("scene_id") or None,
            "trip_id": c["trip_id"],
            "substance": t.get("substance", ""),
            "block": t.get("block", ""),
            "coder_pair": f"{t.get('coder_A', '')}×{t.get('coder_B', '')}",
            "coder_name": c.get("coder_name", ""),
            "rater": c["rater"],
            "item_id": c["item_id"],
            "level_1": c.get("level_1", ""),
            "level_2": c.get("level_2", ""),
            "level_3": c.get("level_3", ""),
            "is_scene_level": c.get("is_scene_level", "") == "True",
        })

    # Flags — which (scene, item) rows AGREE
    flags_js = []
    for f in flags:
        flags_js.append({
            "scene_id": f["scene_id"],
            "item_id": f["item_id"],
            "level_1": f.get("level_1", ""),
            "agreement": f["agreement"],
        })

    trips_js = [{
        "trip_id": t["trip_id"],
        "substance": t["substance"],
        "block": t["block"],
        "coder_A": t["coder_A"],
        "coder_B": t["coder_B"],
        "word_count": int(t["word_count"]),
        "dose_raw": t.get("dose_raw", "") or "",
    } for t in trips]

    payload = {
        "trips": trips_js,
        "scenes": scenes_js,
        "codes": codes_js,
        "flags": flags_js,
    }
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)

    # ---- HTML ----
    css = """
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; scroll-padding-top: 0.5rem; }
    body {
      margin: 0;
      font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
      background: #f7f5f2;
      color: #1a1a1a;
      line-height: 1.5;
    }
    header.top {
      position: sticky;
      top: 0;
      background: #2b2b2b;
      color: #e8e6e1;
      padding: 0.8rem 1.5rem;
      z-index: 40;
      display: flex;
      align-items: center;
      gap: 1.5rem;
      flex-wrap: wrap;
      border-bottom: 1px solid #111;
    }
    header.top h1 { font-size: 1.05rem; margin: 0; font-weight: 600; }
    header.top a { color: #ffd79a; text-decoration: none; font-size: 0.9rem; }
    header.top a:hover { text-decoration: underline; }
    .subnav a { margin-right: 1rem; font-size: 0.85rem; color: #bbb; }
    .subnav a:hover { color: #fff; }
    main {
      max-width: 1100px;
      margin: 0 auto;
      padding: 1.5rem;
    }
    .filters {
      background: #fff;
      border: 1px solid #e0d9ce;
      border-radius: 6px;
      padding: 1rem 1.2rem;
      margin-bottom: 1.2rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      flex-wrap: wrap;
    }
    .filters label {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 0.85rem;
      color: #444;
    }
    .filters select, .filters input[type=checkbox] {
      font: inherit;
    }
    .filters select {
      padding: 0.25rem 0.5rem;
      border: 1px solid #ccc;
      border-radius: 3px;
      background: #fafafa;
    }
    section.card {
      background: #fff;
      border: 1px solid #e5dfd4;
      border-radius: 6px;
      padding: 1.4rem 1.6rem;
      margin-bottom: 1.5rem;
    }
    section.card h2 { margin: 0 0 0.4rem; font-size: 1.1rem; font-weight: 600; }
    section.card p.desc {
      color: #666;
      font-size: 0.85rem;
      margin: 0 0 1rem;
    }
    .chart-holder {
      position: relative;
      height: 380px;
    }
    .chart-holder.tall { height: 600px; }
    .note {
      font-size: 0.75rem;
      color: #888;
      margin-top: 0.5rem;
    }
    .legend-row {
      font-size: 0.75rem;
      color: #555;
      margin-top: 0.4rem;
    }
    .legend-row span { display: inline-block; padding: 1px 5px; border-radius: 2px; margin-right: 5px; font-weight: 600; }
    .bg-AB   { background-color: #b7e4c7; }
    .bg-FRAG { background-color: #ffd79a; }
    .bg-AMP  { background-color: #fff3a3; }
    .bg-AMB  { background-color: #d5c6e0; }
    .bg-SOMA { background-color: #f7c1d9; }
    .bg-RCL  { background-color: #f4b4b4; }
    """

    js = """
    const DATA = window.__VIZ_DATA__;
    const DRIVERS = ['AB','FRAG','AMP','AMB','SOMA','RCL'];
    const DRIVER_COLOUR = {
      AB: '#4caf50', FRAG: '#ff9800', AMP: '#ffc107',
      AMB: '#9c27b0', SOMA: '#e91e63', RCL: '#f44336',
    };
    const DRIVER_LABEL = {
      AB:'Shared', FRAG:'Fragment', AMP:'Amplification',
      AMB:'Ambiguity', SOMA:'Somatic', RCL:'Reconcile',
    };

    // ---------------- helpers ----------------
    function groupCount(items, keyFn, valueFn) {
      const m = new Map();
      for (const it of items) {
        const k = keyFn(it);
        m.set(k, (m.get(k) || 0) + (valueFn ? valueFn(it) : 1));
      }
      return m;
    }
    function filterScenes(substance, pair) {
      return DATA.scenes.filter(s => {
        if (substance !== 'all' && s.substance !== substance) return false;
        if (pair !== 'all' && (s.coder_A + '×' + s.coder_B) !== pair) return false;
        return true;
      });
    }
    function allPairs() {
      const set = new Set();
      DATA.trips.forEach(t => set.add(t.coder_A + '×' + t.coder_B));
      return Array.from(set).sort();
    }

    // ---------------- chart renderers ----------------
    const charts = {};
    function render(id, cfg) {
      if (charts[id]) { charts[id].destroy(); delete charts[id]; }
      charts[id] = new Chart(document.getElementById(id), cfg);
    }

    // Chart 1: driver distribution grouped
    function renderDriverDist() {
      const groupBy = document.getElementById('d1-groupby').value;
      const substance = document.getElementById('d1-substance').value;
      const showMode = document.getElementById('d1-showmode').value; // absolute|proportion

      const scenes = filterScenes(substance, 'all');
      // buckets
      let bucketKey;
      if (groupBy === 'substance')      bucketKey = s => s.substance;
      else if (groupBy === 'block')     bucketKey = s => s.substance + ' ' + s.block;
      else if (groupBy === 'pair')      bucketKey = s => s.coder_A + '×' + s.coder_B;
      else                               bucketKey = () => 'all';

      const buckets = [...new Set(scenes.map(bucketKey))].sort();
      const datasets = DRIVERS.map(drv => {
        const vals = buckets.map(b => scenes.filter(s => bucketKey(s) === b && s.driver === drv).length);
        return { label: DRIVER_LABEL[drv], data: vals, backgroundColor: DRIVER_COLOUR[drv] };
      });

      if (showMode === 'proportion') {
        // normalise per bucket
        const totals = buckets.map(b => scenes.filter(s => bucketKey(s) === b).length || 1);
        datasets.forEach(ds => ds.data = ds.data.map((v, i) => v / totals[i]));
      }

      render('chart-drivers', {
        type: 'bar',
        data: { labels: buckets, datasets },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: {
            tooltip: { mode: 'index', intersect: false },
            legend: { position: 'top' },
          },
          scales: {
            x: { stacked: true },
            y: {
              stacked: true,
              beginAtZero: true,
              ticks: {
                callback: v => (showMode === 'proportion' ? Math.round(v*100)+'%' : v),
              },
            },
          },
        },
      });
    }

    // Chart 2: shared vs solo over trips
    function renderSharedVsSolo() {
      const substance = document.getElementById('d2-substance').value;
      const scenes = filterScenes(substance, 'all');
      const trips = [...new Set(scenes.map(s => s.trip_id))].sort((a, b) => {
        const [sa, na] = [a.split('_')[0], parseInt(a.split('_')[1])];
        const [sb, nb] = [b.split('_')[0], parseInt(b.split('_')[1])];
        if (sa !== sb) return sa < sb ? -1 : 1;
        return na - nb;
      });
      const shared = trips.map(t => scenes.filter(s => s.trip_id === t && s.rater_status === 'both').length);
      const onlyA  = trips.map(t => scenes.filter(s => s.trip_id === t && s.rater_status === 'only_A').length);
      const onlyB  = trips.map(t => scenes.filter(s => s.trip_id === t && s.rater_status === 'only_B').length);
      render('chart-shared', {
        type: 'bar',
        data: {
          labels: trips,
          datasets: [
            { label: 'Shared (both)', data: shared, backgroundColor: '#4caf50' },
            { label: 'Only rater A', data: onlyA, backgroundColor: '#ffb74d' },
            { label: 'Only rater B', data: onlyB, backgroundColor: '#9575cd' },
          ],
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { tooltip: { mode: 'index', intersect: false } },
          scales: { x: { stacked: true, ticks: { autoSkip: false, maxRotation: 60 } }, y: { stacked: true } },
        },
      });
    }

    // Chart 3: top taxonomy items — always brugmansia vs psilocybin side-by-side
    function renderTopItems() {
      const depth = document.getElementById('d3-depth').value; // 1 | 2 | 3
      const consensus = document.getElementById('d3-consensus').checked;
      const onlyScene = document.getElementById('d3-onlyscene').checked;
      const normalise = document.getElementById('d3-normalise').checked;

      let items = DATA.codes;
      if (onlyScene) items = items.filter(c => c.is_scene_level);

      // Consensus filter: keep only items where both raters attached the same
      // (scene, item) on a shared scene, OR both attached the same item at
      // trip-level within the same trip.
      if (consensus) {
        const agreePairs = new Set();
        DATA.flags.forEach(f => { if (f.agreement === 'AGREE') agreePairs.add(f.scene_id + '|' + f.item_id); });
        const tripPairs = new Map();
        DATA.codes.forEach(c => {
          if (!c.is_scene_level) {
            const k = c.trip_id + '|' + c.item_id;
            const rec = tripPairs.get(k) || { A: false, B: false };
            rec[c.rater] = true;
            tripPairs.set(k, rec);
          }
        });
        items = items.filter(c => {
          if (c.is_scene_level) return agreePairs.has(c.scene_id + '|' + c.item_id);
          const r = tripPairs.get(c.trip_id + '|' + c.item_id);
          return r && r.A && r.B;
        });
      }

      const keyFn = depth === '1' ? (c => c.level_1)
                  : depth === '2' ? (c => c.level_1 + ' | ' + (c.level_2 || ''))
                                  : (c => c.level_1 + ' | ' + (c.level_2 || '') + ' | ' + (c.level_3 || ''));

      // Split by substance, count, merge, rank by combined
      const brug = groupCount(items.filter(c => c.substance === 'brugmansia'), keyFn);
      const psil = groupCount(items.filter(c => c.substance === 'psilocybin'), keyFn);
      const allKeys = new Set([...brug.keys(), ...psil.keys()]);
      const combined = [...allKeys].map(k => ({
        key: k,
        brug: brug.get(k) || 0,
        psil: psil.get(k) || 0,
        total: (brug.get(k) || 0) + (psil.get(k) || 0),
      })).sort((a, b) => b.total - a.total).slice(0, 20);

      let brugVals = combined.map(r => r.brug);
      let psilVals = combined.map(r => r.psil);
      let xLabel = 'count';
      if (normalise) {
        const n_brug = DATA.trips.filter(t => t.substance === 'brugmansia').length || 1;
        const n_psil = DATA.trips.filter(t => t.substance === 'psilocybin').length || 1;
        brugVals = brugVals.map(v => v / n_brug);
        psilVals = psilVals.map(v => v / n_psil);
        xLabel = 'count per trip (normalised by n trips per substance)';
      }

      render('chart-items', {
        type: 'bar',
        data: {
          labels: combined.map(r => r.key),
          datasets: [
            { label: 'brugmansia', data: brugVals, backgroundColor: '#1b4332' },
            { label: 'psilocybin', data: psilVals, backgroundColor: '#9b111e' },
          ],
        },
        options: {
          indexAxis: 'y',
          responsive: true, maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top' },
            tooltip: { mode: 'index', intersect: false },
          },
          scales: {
            x: { beginAtZero: true, title: { display: true, text: xLabel } },
          },
        },
      });
    }

    // Chart 4: rater style
    function renderRaterStyle() {
      const substance = document.getElementById('d4-substance').value;
      const metric = document.getElementById('d4-metric').value;
      // metric options: n_scenes, n_scene_codes, n_trip_codes,
      // modal_status, incrusted, detached, illusion, immersive
      const trips = substance === 'all' ? DATA.trips : DATA.trips.filter(t => t.substance === substance);
      const tripIds = new Set(trips.map(t => t.trip_id));
      const relevantScenes = DATA.scenes.filter(s => tripIds.has(s.trip_id));
      const relevantCodes = DATA.codes.filter(c => tripIds.has(c.trip_id));

      // per coder_name
      const coders = [...new Set([
        ...relevantCodes.map(c => c.coder_name),
      ].filter(Boolean))].sort();

      const countFor = (coder, metric) => {
        if (metric === 'n_scenes') {
          return new Set(relevantCodes.filter(c => c.coder_name === coder && c.is_scene_level && c.scene_id).map(c => c.scene_id)).size;
        }
        if (metric === 'n_scene_codes') {
          return relevantCodes.filter(c => c.coder_name === coder && c.is_scene_level).length;
        }
        if (metric === 'n_trip_codes') {
          return relevantCodes.filter(c => c.coder_name === coder && !c.is_scene_level).length;
        }
        if (metric === 'modal_status') {
          return relevantCodes.filter(c => c.coder_name === coder && c.level_1 === 'Modal status of the hallucination').length;
        }
        if (metric === 'incrusted') {
          return relevantCodes.filter(c => c.coder_name === coder && c.item_id === 'type_of_visual_alteration_hallucination_of_an_incrusted_object').length;
        }
        if (metric === 'detached') {
          return relevantCodes.filter(c => c.coder_name === coder && c.item_id === 'type_of_visual_alteration_hallucination_of_a_detached_object').length;
        }
        if (metric === 'illusion') {
          return relevantCodes.filter(c => c.coder_name === coder && c.item_id === 'type_of_visual_alteration_illusion').length;
        }
        if (metric === 'immersive') {
          return relevantCodes.filter(c => c.coder_name === coder && c.item_id === 'type_of_visual_alteration_full_blown_immersive_hallucination').length;
        }
        return 0;
      };

      const vals = coders.map(c => countFor(c, metric));
      render('chart-rater-style', {
        type: 'bar',
        data: {
          labels: coders,
          datasets: [{ label: metric, data: vals, backgroundColor: '#009688' }],
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true } },
        },
      });
    }

    // Chart 5: trip × driver heatmap-ish stacked bar
    function renderTripHeatmap() {
      const substance = document.getElementById('d5-substance').value;
      const scenes = filterScenes(substance, 'all');
      const trips = [...new Set(scenes.map(s => s.trip_id))].sort((a, b) => {
        const [sa, na] = [a.split('_')[0], parseInt(a.split('_')[1])];
        const [sb, nb] = [b.split('_')[0], parseInt(b.split('_')[1])];
        if (sa !== sb) return sa < sb ? -1 : 1;
        return na - nb;
      });
      const datasets = DRIVERS.map(drv => ({
        label: DRIVER_LABEL[drv],
        data: trips.map(t => scenes.filter(s => s.trip_id === t && s.driver === drv).length),
        backgroundColor: DRIVER_COLOUR[drv],
      }));
      render('chart-trip-heatmap', {
        type: 'bar',
        data: { labels: trips, datasets },
        options: {
          indexAxis: 'y',
          responsive: true, maintainAspectRatio: false,
          plugins: { tooltip: { mode: 'index', intersect: false } },
          scales: {
            x: { stacked: true, beginAtZero: true },
            y: { stacked: true, ticks: { autoSkip: false, font: { size: 10 } } },
          },
        },
      });
    }

    // ---------------- init ----------------
    function init() {
      // Populate pair dropdowns
      const pairs = allPairs();
      // all filter selects
      ['d1-substance','d2-substance','d4-substance','d5-substance'].forEach(id => {
        const el = document.getElementById(id);
        el.addEventListener('change', rerender);
      });
      ['d1-groupby','d1-showmode','d3-depth','d3-consensus','d3-onlyscene','d3-normalise','d4-metric']
        .forEach(id => document.getElementById(id).addEventListener('change', rerender));
      rerender();
    }
    function rerender() {
      renderDriverDist();
      renderSharedVsSolo();
      renderTopItems();
      renderRaterStyle();
      renderTripHeatmap();
    }

    // Expose under DOMContentLoaded
    document.addEventListener('DOMContentLoaded', init);
    """

    # Subnav anchor section ids
    doc = [
        '<!doctype html>',
        '<html lang="en"><head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>Visualizations — phenomenology of hallucinogenic experiences</title>',
        f'<style>{css}</style>',
        '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>',
        '</head>',
        '<body>',
        '<header class="top">',
        '<h1>Visualizations</h1>',
        '<span class="subnav">',
        '<a href="index.html">← trip reports</a>',
        '<a href="#drivers">Drivers</a>',
        '<a href="#shared">Shared vs solo</a>',
        '<a href="#items">Top items</a>',
        '<a href="#rater">Rater style</a>',
        '<a href="#tripheat">Per-trip heatmap</a>',
        '</span>',
        '</header>',
        '<main>',

        # --- Chart 1: driver distribution ---
        '<section class="card" id="drivers">',
        '<h2>Scene counts by driver category</h2>',
        '<p class="desc">Distribution of Stage-1 driver categories. '
        'Group by substance / block / coder pair; toggle between absolute counts and proportions.</p>',
        '<div class="filters">',
        '<label>Group by <select id="d1-groupby">'
        '<option value="substance">substance</option>'
        '<option value="block">substance + block</option>'
        '<option value="pair">coder pair</option>'
        '</select></label>',
        '<label>Substance <select id="d1-substance">'
        '<option value="all">all</option>'
        '<option value="brugmansia">brugmansia</option>'
        '<option value="psilocybin">psilocybin</option>'
        '</select></label>',
        '<label>Show <select id="d1-showmode">'
        '<option value="absolute">absolute count</option>'
        '<option value="proportion">proportion</option>'
        '</select></label>',
        '</div>',
        '<div class="chart-holder"><canvas id="chart-drivers"></canvas></div>',
        '<div class="legend-row">'
        '<span class="bg-AB">AB</span>shared '
        '<span class="bg-FRAG">FRAG</span>fragment '
        '<span class="bg-AMP">AMP</span>amplification '
        '<span class="bg-AMB">AMB</span>ambiguity '
        '<span class="bg-SOMA">SOMA</span>somatic '
        '<span class="bg-RCL">RCL</span>reconcile'
        '</div>',
        '</section>',

        # --- Chart 2: shared vs solo per trip ---
        '<section class="card" id="shared">',
        '<h2>Shared vs solo scenes per trip</h2>',
        '<p class="desc">Per-trip stacked bars: how many scenes were individuated by both raters vs by only one.</p>',
        '<div class="filters">',
        '<label>Substance <select id="d2-substance">'
        '<option value="all">all</option>'
        '<option value="brugmansia">brugmansia</option>'
        '<option value="psilocybin">psilocybin</option>'
        '</select></label>',
        '</div>',
        '<div class="chart-holder tall"><canvas id="chart-shared"></canvas></div>',
        '</section>',

        # --- Chart 3: top items ---
        '<section class="card" id="items">',
        '<h2>Top 20 taxonomy items — brugmansia vs psilocybin</h2>',
        '<p class="desc">The 20 most-coded taxonomy items, always shown side-by-side '
        'for the two substances (this is the primary comparison the paper is about). '
        'Choose depth (L1 section / L2 category / L3 leaf); restrict to scene-level only; '
        'toggle the consensus filter (keep only items both raters attached); or normalise '
        'counts per trip so the substances (20 trips each) are directly comparable.</p>',
        '<div class="filters">',
        '<label>Depth <select id="d3-depth">'
        '<option value="1">L1 section</option>'
        '<option value="2" selected>L2 category</option>'
        '<option value="3">L3 leaf</option>'
        '</select></label>',
        '<label><input type="checkbox" id="d3-onlyscene"> scene-level only</label>',
        '<label><input type="checkbox" id="d3-consensus" checked> consensus only (both raters)</label>',
        '<label><input type="checkbox" id="d3-normalise"> normalise per trip</label>',
        '</div>',
        '<div class="chart-holder tall"><canvas id="chart-items"></canvas></div>',
        '</section>',

        # --- Chart 4: rater style ---
        '<section class="card" id="rater">',
        '<h2>Rater style comparison</h2>',
        '<p class="desc">Per-coder counts for various tag-usage metrics. Reveals systematic over-/under-use patterns.</p>',
        '<div class="filters">',
        '<label>Substance <select id="d4-substance">'
        '<option value="all">all</option>'
        '<option value="brugmansia">brugmansia</option>'
        '<option value="psilocybin">psilocybin</option>'
        '</select></label>',
        '<label>Metric <select id="d4-metric">'
        '<option value="n_scenes">scenes individuated</option>'
        '<option value="n_scene_codes">total scene-level codes</option>'
        '<option value="n_trip_codes">total trip-level codes</option>'
        '<option value="modal_status">modal status attachments</option>'
        '<option value="incrusted">"incrusted object" tag</option>'
        '<option value="detached">"detached object" tag</option>'
        '<option value="illusion">"illusion" tag</option>'
        '<option value="immersive">"full-blown immersive" tag</option>'
        '</select></label>',
        '</div>',
        '<div class="chart-holder"><canvas id="chart-rater-style"></canvas></div>',
        '</section>',

        # --- Chart 5: trip heatmap ---
        '<section class="card" id="tripheat">',
        '<h2>Per-trip driver breakdown</h2>',
        '<p class="desc">Each trip shown as a horizontal stacked bar of driver categories. Gives a trip-by-trip view of where disagreement is concentrated.</p>',
        '<div class="filters">',
        '<label>Substance <select id="d5-substance">'
        '<option value="all">all</option>'
        '<option value="brugmansia">brugmansia</option>'
        '<option value="psilocybin">psilocybin</option>'
        '</select></label>',
        '</div>',
        '<div class="chart-holder tall"><canvas id="chart-trip-heatmap"></canvas></div>',
        '</section>',

        '</main>',
        f'<script>window.__VIZ_DATA__ = {payload_json};</script>',
        f'<script>{js}</script>',
        '</body></html>',
    ]

    out_path = os.path.abspath(os.path.join(here, OUT))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    out_html = "\n".join(doc)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out_html)

    size_kb = len(out_html.encode("utf-8")) / 1024
    print(f"wrote {out_path}  ({size_kb:.0f} KB)")
    print(f"  data: {len(trips_js)} trips, {len(scenes_js)} scenes, {len(codes_js)} codes, {len(flags_js)} flags")


if __name__ == "__main__":
    main()
