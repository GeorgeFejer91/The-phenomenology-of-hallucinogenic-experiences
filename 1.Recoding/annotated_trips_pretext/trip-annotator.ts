// Pretext-based dynamic renderer for annotated trip reports.
//
// Uses pretext's canvas-based text measurement + explicit line-break layout
// to paint coloured rectangles behind scene spans with pixel-accurate
// positioning. No CSS text flow, no DOM measurement — pretext computes
// per-line text segments with exact x/width/line-index, and we render the
// highlight rectangles and then the text on top of them.
//
// Imports are relative to the sibling pretext_website repo under
// ../../pretext_website/src/layout.ts, which bun resolves natively.

import {
  prepareWithSegments,
  layoutWithLines,
  type PreparedTextWithSegments,
} from '../../pretext_website/src/layout.ts'

const FONT = '18px "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, serif'
const LINE_HEIGHT = 30
const PADDING_X = 0
const PADDING_Y = 0

const COLOURS: Record<string, string> = {
  AB:   '#b7e4c7',
  FRAG: '#ffd79a',
  AMP:  '#fff3a3',
  AMB:  '#d5c6e0',
  SOMA: '#f7c1d9',
  RCL:  '#f4b4b4',
}

const PRIORITY = ['RCL', 'SOMA', 'AMB', 'AMP', 'FRAG', 'AB']

type Scene = {
  scene_id: string
  rater_status: string
  driver: string
  parent_scene_id: string
  canonical_desc: string
  canonical_span_start: number | null
  canonical_span_end: number | null
  stage1_rationale: string
}

type TripData = {
  trip_id: string
  substance: string
  block: string
  coder_A: string
  coder_B: string
  dose_raw: string | null
  word_count: number
  narrative: string
  scenes: Scene[]
}

type TripIndexEntry = {
  trip_id: string
  substance: string
  coder_A: string
  coder_B: string
}

type SceneDrawInfo = {
  scene: Scene
  start: number
  end: number
  rects: Array<{ x: number; y: number; w: number; h: number }>
}

const statusEl = document.getElementById('status')!
const metaEl = document.getElementById('meta')!
const canvas = document.getElementById('narr-canvas') as HTMLCanvasElement
const tooltip = document.getElementById('tooltip')!
const indexEl = document.getElementById('scene-index')!
const select = document.getElementById('trip-select') as HTMLSelectElement

async function loadIndex(): Promise<TripIndexEntry[]> {
  const r = await fetch('./data/index.json')
  return r.json()
}

async function loadTrip(tripId: string): Promise<TripData> {
  const r = await fetch(`./data/${tripId}.json`)
  return r.json()
}

function getDriver(scene: Scene): string {
  return scene.driver || 'AB'
}

function parsePx(v: string): number {
  const m = v.match(/(\d+(?:\.\d+)?)/)
  return m ? parseFloat(m[1]) : 16
}

function renderTrip(trip: TripData) {
  // Populate meta
  metaEl.innerHTML = `
    <div class="meta-row">
      <div class="meta-item"><strong>Trip:</strong> ${trip.trip_id}</div>
      <div class="meta-item"><strong>Substance:</strong> ${trip.substance}</div>
      <div class="meta-item"><strong>Block:</strong> ${trip.block}</div>
      <div class="meta-item"><strong>Coders:</strong> ${trip.coder_A} × ${trip.coder_B}</div>
      <div class="meta-item"><strong>Dose:</strong> ${trip.dose_raw || '—'}</div>
      <div class="meta-item"><strong>Words:</strong> ${trip.word_count}</div>
      <div class="meta-item"><strong>Scenes:</strong> ${trip.scenes.length}</div>
    </div>
  `

  // Scene index
  indexEl.innerHTML = trip.scenes.map(s => {
    const d = getDriver(s)
    const parent = s.parent_scene_id ? ` — parent <code>${s.parent_scene_id}</code>` : ''
    const rat = s.stage1_rationale ? `<br><em style="color:#666">${s.stage1_rationale}</em>` : ''
    return `<li><span class="legend-chip bg-${d}">${d}</span>
            <code>${s.scene_id}</code>${parent}<br>${s.canonical_desc || ''}${rat}</li>`
  }).join('')

  // Layout text with pretext
  const container = canvas.parentElement!
  const textWidth = Math.max(400, container.clientWidth - 4 * 16)  // 2rem padding
  const prepared: PreparedTextWithSegments = prepareWithSegments(trip.narrative, FONT, { whiteSpace: 'pre-wrap' })
  const { lines } = layoutWithLines(prepared, textWidth)

  // Each line has { text, segments: [{start, end, x, width, ...}], lineIndex }
  // We use the segments to locate character ranges for highlight rectangles.

  // Build per-line character ranges for the lines array.
  // lines[i] = { startChar, endChar, segments: [...] }
  type Line = { startChar: number; endChar: number; y: number; segments: Array<{ startChar: number; endChar: number; x: number; width: number }> }
  const normalisedLines: Line[] = []
  let charCursor = 0
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i] as any
    // Defensive: support varying shapes returned by pretext versions
    const lineText: string = line.text ?? ''
    const lineStartChar = line.startChar ?? charCursor
    const lineEndChar = line.endChar ?? (lineStartChar + lineText.length)
    const segs: Array<{ startChar: number; endChar: number; x: number; width: number }> = []
    if (Array.isArray(line.segments)) {
      for (const s of line.segments) {
        segs.push({
          startChar: s.startChar ?? s.start ?? 0,
          endChar:   s.endChar   ?? s.end   ?? 0,
          x:         s.x ?? 0,
          width:     s.width ?? s.w ?? 0,
        })
      }
    } else {
      // Fallback: a single segment spanning the whole line width
      segs.push({ startChar: lineStartChar, endChar: lineEndChar, x: 0, width: textWidth })
    }
    normalisedLines.push({
      startChar: lineStartChar,
      endChar: lineEndChar,
      y: i * LINE_HEIGHT,
      segments: segs,
    })
    charCursor = lineEndChar
  }

  const totalHeight = normalisedLines.length * LINE_HEIGHT + 2 * PADDING_Y
  const dpr = window.devicePixelRatio || 1
  canvas.width = (textWidth + 2 * PADDING_X) * dpr
  canvas.height = totalHeight * dpr
  canvas.style.width = (textWidth + 2 * PADDING_X) + 'px'
  canvas.style.height = totalHeight + 'px'
  const ctx = canvas.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  // Compute highlight rectangles per scene
  const sceneDraws: SceneDrawInfo[] = []
  for (const scene of trip.scenes) {
    if (scene.canonical_span_start == null || scene.canonical_span_end == null) continue
    const ss = scene.canonical_span_start
    const se = Math.min(scene.canonical_span_end, trip.narrative.length)
    if (se <= ss) continue
    const rects: Array<{ x: number; y: number; w: number; h: number }> = []
    for (const line of normalisedLines) {
      const ovStart = Math.max(ss, line.startChar)
      const ovEnd = Math.min(se, line.endChar)
      if (ovEnd <= ovStart) continue
      // Find x range on this line for [ovStart, ovEnd]
      let xStart = 0, xEnd = 0
      for (const seg of line.segments) {
        // Segment covers [seg.startChar, seg.endChar] at [seg.x, seg.x+seg.width]
        if (seg.endChar <= seg.startChar) continue
        const segChars = seg.endChar - seg.startChar || 1
        const perChar = seg.width / segChars
        if (ovStart >= seg.startChar && ovStart < seg.endChar) {
          xStart = seg.x + (ovStart - seg.startChar) * perChar
        } else if (seg.startChar >= ovStart && seg.endChar <= ovEnd) {
          // segment entirely within overlap — contributes nothing new
        }
        if (ovEnd > seg.startChar && ovEnd <= seg.endChar) {
          xEnd = seg.x + (ovEnd - seg.startChar) * perChar
        } else if (seg.endChar <= ovEnd && seg.startChar >= ovStart) {
          xEnd = Math.max(xEnd, seg.x + seg.width)
        }
      }
      if (xEnd === 0 && line.segments.length > 0) {
        const last = line.segments[line.segments.length - 1]
        xEnd = last.x + last.width
      }
      rects.push({
        x: xStart + PADDING_X,
        y: line.y + PADDING_Y,
        w: Math.max(xEnd - xStart, 4),
        h: LINE_HEIGHT,
      })
    }
    sceneDraws.push({ scene, start: ss, end: se, rects })
  }

  // Sort sceneDraws by driver priority (so higher-priority drivers paint on top)
  sceneDraws.sort((a, b) => {
    const pa = PRIORITY.indexOf(getDriver(a.scene))
    const pb = PRIORITY.indexOf(getDriver(b.scene))
    return pb - pa  // RCL (priority 0) draws last → on top? We want it visible
  })

  // Paint highlights
  for (const sd of sceneDraws) {
    ctx.fillStyle = COLOURS[getDriver(sd.scene)] || '#ddd'
    for (const r of sd.rects) {
      ctx.fillRect(r.x, r.y, r.w, r.h)
    }
  }

  // Paint text on top, line by line
  ctx.font = FONT
  ctx.textBaseline = 'alphabetic'
  ctx.fillStyle = '#1a1a1a'
  for (let i = 0; i < normalisedLines.length; i++) {
    const line = normalisedLines[i]
    const text = trip.narrative.slice(line.startChar, line.endChar)
    ctx.fillText(text, PADDING_X, line.y + LINE_HEIGHT * 0.75 + PADDING_Y)
  }

  // Tooltip: map click/mousemove to scene via simple hit test
  canvas.onmousemove = (e) => {
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const hits: string[] = []
    for (const sd of sceneDraws) {
      for (const r of sd.rects) {
        if (x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h) {
          hits.push(`${getDriver(sd.scene)} ${sd.scene.scene_id}`)
          break
        }
      }
    }
    if (hits.length) {
      tooltip.style.display = 'block'
      tooltip.textContent = hits.join('  |  ')
      tooltip.style.left = `${e.clientX - rect.left + canvas.offsetLeft + 10}px`
      tooltip.style.top = `${e.clientY - rect.top + canvas.offsetTop + 10}px`
    } else {
      tooltip.style.display = 'none'
    }
  }
  canvas.onmouseleave = () => { tooltip.style.display = 'none' }
}

async function main() {
  statusEl.textContent = 'loading index…'
  const idx = await loadIndex()
  select.innerHTML = idx.map(t =>
    `<option value="${t.trip_id}">${t.trip_id} (${t.substance})</option>`
  ).join('')
  select.onchange = async () => {
    statusEl.textContent = `loading ${select.value}…`
    const trip = await loadTrip(select.value)
    renderTrip(trip)
    statusEl.textContent = `rendered ${trip.trip_id}`
  }
  statusEl.textContent = 'loading first trip…'
  const first = await loadTrip(idx[0].trip_id)
  select.value = idx[0].trip_id
  renderTrip(first)
  statusEl.textContent = `rendered ${first.trip_id}`
}

main().catch((err) => {
  console.error(err)
  statusEl.textContent = `error: ${err.message}`
})
