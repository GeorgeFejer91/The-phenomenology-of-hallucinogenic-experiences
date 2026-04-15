# Recoding data-structure rules

Goal: a single consistent set of naming/formatting conventions that makes
every known source of inter-rater inconsistency queryable from the data alone.

These rules are iterative — new patterns get added here as they are spotted
during adjudication, and the consolidator script applies them across the
full dataset.

**Scope note.** The current pipeline stage addresses **scene individuation
consistency only** — did both raters treat the same narrative passage as a
hallucinatory scene? Attribute-classification consistency (did they tag the
same scene as illusion vs incrusted, same object-class, same modal status,
etc.) is deliberately **out of scope** and is left as recorded rater
judgement. See [STAGE1_SCOPE.md](STAGE1_SCOPE.md) for the full scope
definition and [STAGE1_SCOPE.json](STAGE1_SCOPE.json) for the
machine-readable version.

---

## 1. Scene ID convention

Every scene has an ID of the form `{trip_id}_S{NN}[.k]_{STATUS}[_MOD]`.

| Part | Meaning | Example |
|------|---------|---------|
| `trip_id` | normalised trip identifier | `Psilocybe_04` |
| `S{NN}` | two-digit sequential scene number in narrative order, per trip | `S07` |
| `.k` | optional child-scene index; present only for scenes that are a sub-portion of a larger scene individuated by the other rater | `.1`, `.2`, `.3` |
| `STATUS` | rater-status suffix (see §2) | `AB`, `A`, `B` |
| `MOD` | optional modifier flags for structural nuances (see §3) | `LUMP`, `SPLIT` |

Examples:
- `Psilocybe_04_S03_AB` — scene 3 of trip Psilocybe_04, both raters individuated it identically
- `Psilocybe_04_S05_A` — scene 5, only rater A individuated (rater B did not code this passage as a scene)
- `Psilocybe_04_S07_B` — scene 7, only rater B individuated
- `Brugmansia_12_S08_AB_LUMPA` — shared scene where rater A lumped what rater B split
- `Brugmansia_12_S08.1_AB_SPLITB` — child of the above; one of rater B's split scenes that falls under rater A's lump
- `Brugmansia_12_S08.2_AB_SPLITB` — second child of the lump

---

## 2. Rater-status suffix

Primary flag encoding whether each rater individuated the scene:

| Suffix | Meaning | Guaranteed invariants |
|--------|---------|-----------------------|
| `AB` | Both raters individuated this scene (co-extensive in narrative span) | both `rater_A_refs` and `rater_B_refs` non-empty |
| `A` | Only rater A individuated it | `rater_B_refs` empty |
| `B` | Only rater B individuated it | `rater_A_refs` empty |

Filtering on this suffix alone answers "what is the consensus subset?"
(filter `scene_id` ending in `_AB`), "what is in rater-A's view only?"
(filter `_A`), etc.

---

## 3. Structural modifier flags

These capture structural disagreements about scene boundaries — separate
from attribute disagreements.

| Flag | Meaning | Applied to |
|------|---------|------------|
| `LUMPA` | Rater A treated this as one scene, rater B split it into ≥2 parts | The parent scene (A's single individuation) |
| `LUMPB` | Rater B treated this as one scene, rater A split it into ≥2 parts | The parent scene |
| `SPLITA` | This child scene is one of multiple that rater A produced from rater B's single lumped scene | A child scene |
| `SPLITB` | This child scene is one of multiple that rater B produced from rater A's single lumped scene | A child scene |

When present, `parent_scene_id` in scenes.csv links the child back to the
lump it belongs to. The lump and its children share the `.N` stem (e.g.
`S08` is parent of `S08.1`, `S08.2`).

---

## 4. scenes.csv schema

| Column | Type | Description |
|--------|------|-------------|
| scene_id | str | Primary key, formatted per §1 |
| trip_id | str | FK to trips.csv |
| rater_status | enum | `both`, `only_A`, `only_B` — redundant with suffix but easier for filtering |
| parent_scene_id | str? | For child scenes, the lump's scene_id |
| lump_split_type | enum? | `none`, `A_lumped_B_split`, `B_lumped_A_split` |
| canonical_desc | str | Short human-readable label |
| canonical_span_start | int? | Character offset in narrative (.docx body) |
| canonical_span_end | int? | |
| rater_A_refs | str | Comma-separated worksheet excerpt refs (e.g. `A01,A02`) |
| rater_B_refs | str | Comma-separated worksheet excerpt refs |
| adjudicator_note | str | Free-text rationale |

---

## 5. codes.csv schema

Every attribute/item that any rater attached to a scene or at trip level.

| Column | Type | Description |
|--------|------|-------------|
| code_id | str | Surrogate key (C000001…) |
| scene_id | str? | FK to scenes.csv, null for trip-level items |
| trip_id | str | Always present |
| rater | enum | `A` or `B` |
| coder_name | str | e.g. `Alessandra` |
| item_id | str | FK to taxonomy.csv |
| item_path | str | Human-readable (e.g. `Visual hallucination \| Animal \| Insect`) |
| level_1, level_2, level_3 | str? | Hierarchy at each depth |
| is_scene_level | bool | True for scene items, False for trip-level items |
| excerpt | str? | Verbatim text snippet (trip-level codes carry their own) |

---

## 6. agreement_flags.csv (derived)

For every shared scene (status=`both`), every taxonomy item that EITHER
rater attached gets one row stating which raters attached it. Lets you
compute agreement at any taxonomy level by filtering on depth.

| Column | Type | Description |
|--------|------|-------------|
| scene_id | str | FK |
| trip_id | str | FK |
| item_id, item_path, level_1/2/3, depth | — | From taxonomy |
| A_coded, B_coded | bool | Presence flags |
| agreement | enum | `AGREE` (both), `A_ONLY`, `B_ONLY` |

Derived queries that become trivial:
- "L1-only agreement on shared scenes" → filter `depth=0`, compute `AGREE/(AGREE+A_ONLY+B_ONLY)`
- "Which items do raters disagree on most?" → group by `item_id`, count `A_ONLY+B_ONLY`
- "Which level-1 categories have the most classification disagreement?" → group by `level_1`

---

## 7. rater_style.csv (derived)

Per-trip, per-rater counts that quantify style asymmetries already observed
in the data. These are the levers for later correction strategies.

| Column | Description |
|--------|-------------|
| n_scenes_individuated | How many scenes this rater individuated in this trip |
| n_scene_codes | Total scene-level item codings attached |
| n_trip_codes | Total trip-level item codings |
| codes_per_scene | Density: scene-items / scenes |
| modal_status_uses | How often this rater tags modal-status |
| incrusted_uses, detached_uses, illusion_uses, immersive_uses | Counts per type-of-visual-alteration leaf |

---

## 8. Known inconsistency patterns currently captured by the framework

| Pattern | How the framework flags it |
|---------|---------------------------|
| Rater omits a scene another rater individuated | `rater_status` = `only_A` or `only_B` |
| Raters individuate the same passage but classify its attributes differently | `rater_status` = `both` + `agreement_flags.agreement` = `A_ONLY` or `B_ONLY` per item |
| One rater lumps what the other splits | Structural modifiers `LUMPA/LUMPB/SPLITA/SPLITB` + `parent_scene_id` links |
| Rater systematically over-uses a tag (e.g. modal-status) | `rater_style.modal_status_uses` skewed per-rater |
| Rater codes a passage at trip-level while the other codes it scene-level | Same `trip_id` appears in both scope layers; comparison requires joining codes on trip with `is_scene_level` flag |
| Attribute disagreement only at the leaf (level-3) while agreeing at level-1 | `agreement_flags` grouped at depth 0 agrees while depth 2 disagrees |

---

## 9. Binning (analytical view, not a data mutation)

`scenes.csv` is always stored at the finest granularity each rater
individuated. Binning is a separate **analytical view** on top of that
granularity, for questions like "did both raters see SOMETHING in this
narrative region, regardless of how they chunked it?"

### Principle

- The canonical data (`scenes.csv`, `codes.csv`) retains maximum detail and
  maximum transparency. No scene is ever merged or destroyed.
- When a coarser view is needed, the binning script groups scenes whose
  `canonical_span_start/end` overlap into a `bin_id`, and computes a
  bin-level `bin_status` (both / only_A / only_B).
- The bin annotation lives in `analysis/scene_bins.csv` and
  `analysis/bins_summary.csv`. These files are **derived** — they can be
  regenerated at any time from scenes.csv and deleted without loss.

### Three tiers of agreement

| Tier | Question | Where it lives |
|------|----------|----------------|
| 0 (binned) | Did both raters see anything at all in this narrative region? | `analysis/bins_summary.csv:bin_status` |
| 1 (scene) | Did they individuate it with the same boundaries? | `scenes.csv:rater_status` (the canonical column) |
| 2 (classify) | Given a matched scene, did they tag the same attributes? | `data/agreement_flags.csv` |

### Flags the binning script emits

| Flag | Meaning |
|------|---------|
| `granularity_recovered` | True if a bin's status is `both`, but its constituent scenes are all `only_A` or `only_B`. This is a genuine hidden agreement — recovered only when you zoom out. |
| `chunking_split` | True if one rater contributed ≥2 scenes and the other rater contributed ≥1 scene to the same bin, i.e. one rater split what the other (in part) lumped. |

These flags let any downstream analysis switch between a strict scene-level
view and a lenient bin-level view simply by joining `scenes.csv` to
`analysis/scene_bins.csv` on `scene_id`.

## 10. Iteration

When new patterns are discovered during adjudication, this file is updated
and (if needed) new columns/tags are added to scenes/codes. The consolidator
script re-runs idempotently over the YAML adjudications. Analytical views
(like binning) are always derived in `analysis/` and can be regenerated at
any time — they never modify the canonical data.
