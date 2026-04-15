# Annotated trip reports — pretext-based dynamic renderer

Colour-highlights every individuated hallucinatory scene directly on the
trip-report narrative, using the pretext layout engine for pixel-precise
line-breaking and text measurement (canvas rendering, no DOM reflow).

## Driver-category colour legend

| Suffix | Meaning | Colour |
|---|---|---|
| `_AB` | Both raters individuated the scene | green |
| `_FRAG` | Fragment of a holistic scene coded by the other rater | orange |
| `_AMP` | Sensory amplification (no discrete object content) | yellow |
| `_AMB` | Ambiguity — thought, memory, or metaphor coded as a hallucination | purple |
| `_SOMA` | Somatic / self-transformation | pink |
| `_RCL` | Genuine miss by the other rater — flagged for reconciliation | red |

## Layout

```
annotated_trips_pretext/
├── package.json
├── index.html
├── trip-annotator.ts         entry point; imports pretext from ../../../pretext_website/src
└── data/
    ├── index.json            list of all trips with coder metadata
    ├── Brugmansia_01.json    narrative + scene spans + drivers for this trip
    ├── …
    └── Psilocybe_20.json
```

The renderer imports pretext's layout engine by relative path:

```ts
import { prepareWithSegments, layoutWithLines } from '../../pretext_website/src/layout.ts'
```

This assumes the sibling checkout
`C:/Users/cogpsy-vrlab/Documents/GitHub/pretext_website/` exists — if you
move either repo, update the import path.

## Run locally

Requires [bun](https://bun.sh/) (which handles both dev-server duty and native
TypeScript compilation for the browser; no separate bundler needed).

```sh
cd 1.Recoding/annotated_trips_pretext
bun install                   # (no external deps, but sets up bun state)
bun run start                 # starts bun dev server on http://localhost:3000
```

Open `http://localhost:3000` in a browser. The trip selector at the top lets
you switch between all 40 trip reports; each renders with colour-highlighted
scenes using pretext's canvas-based layout.

### Without bun

Any dev server that can compile TypeScript on the fly (vite, parcel, esbuild)
will work — update `package.json` scripts accordingly. The static fallback
`../annotated_trips/` contains plain HTML versions of the same annotations
that open directly in a browser with no build step required.

## How the renderer uses pretext

1. Fetches `data/<trip_id>.json` containing the narrative text and an array of
   scenes with `canonical_span_start` / `canonical_span_end` character offsets
   and a `driver` tag.
2. Calls `prepareWithSegments(narrative, FONT, { whiteSpace: 'pre-wrap' })` to
   segment the text and measure each segment's width using canvas.
3. Calls `layoutWithLines(prepared, textWidth)` to compute the final line
   breaks and per-segment x/width positions.
4. For each scene, maps its character range onto the resulting lines,
   computing one rectangle per line it spans.
5. Paints the coloured rectangles first, then draws the text on top via
   `ctx.fillText()`. Result is per-line accurate highlights that move with
   the text when the container is resized.
6. A lightweight hit-test on `mousemove` drives the tooltip that shows which
   scene IDs are active at the cursor position.

Regenerate the JSON data files at any time with:

```sh
py scripts/13_export_trip_json.py
```

The JSON schema matches the canonical `scenes.csv` — any re-run of the Stage-1
driver classifier propagates automatically to the rendered views.
