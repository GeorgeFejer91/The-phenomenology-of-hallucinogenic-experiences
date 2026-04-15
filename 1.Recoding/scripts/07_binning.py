"""Bin-level agreement (ANALYTICAL VIEW — does not modify scenes.csv).

When one rater's scene subsumes the other rater's sub-scenes, currently the
sub-scenes show up as only_A / only_B even though BOTH raters saw
hallucinatory activity in that narrative region. This script groups scenes
whose canonical character-spans overlap into a "bin" and re-classifies
status at the bin level.

Three tiers of agreement become measurable:
  Tier 0 (binned)  — did both raters see SOMETHING in this narrative region?
                     bin_status = both | only_A | only_B
  Tier 1 (scene)   — did they individuate it with the same boundaries?
                     scene.rater_status (already in scenes.csv — unchanged)
  Tier 2 (classify)— given a matched scene, did they tag the same attributes?
                     agreement_flags.csv

Outputs live in 1.Recoding/analysis/ (NOT in data/) to signal that bins are
a derived view, not part of the canonical scene dataset.

Output:
  analysis/scene_bins.csv     one row per scene, with bin_id + bin_status
  analysis/bins_summary.csv   one row per bin: span, scenes-in-bin, tier-0 status
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
import os, csv
from collections import defaultdict

DATA = "../data"
OUT_DIR = "../analysis"


def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def spans_overlap(a0, a1, b0, b1):
    return max(a0, b0) < min(a1, b1)


class UF:
    """Union-find for bin grouping."""
    def __init__(self, items):
        self.p = {x: x for x in items}
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def main():
    here = os.path.dirname(__file__)
    scenes = load(os.path.join(here, DATA, "scenes.csv"))

    # Parse spans — only scenes with numeric spans can be binned
    scenes_usable = []
    for s in scenes:
        try:
            a = int(s["canonical_span_start"]) if s["canonical_span_start"] else None
            b = int(s["canonical_span_end"]) if s["canonical_span_end"] else None
            if a is not None and b is not None and b > a:
                s["_span"] = (a, b)
                scenes_usable.append(s)
        except (ValueError, TypeError):
            pass

    # Skip child scenes for binning — they are already in a parent-lump relationship.
    # We bin at the parent level; children inherit their parent's bin.
    is_child = {s["scene_id"]: bool(s["parent_scene_id"]) for s in scenes}

    # Group scenes per trip
    by_trip = defaultdict(list)
    for s in scenes_usable:
        by_trip[s["trip_id"]].append(s)

    # Per trip: union-find over scenes whose spans overlap (lumps excluded from union)
    bin_assignment = {}  # scene_id -> bin_id
    bin_id_counter = 0
    bins_info = []  # list of dicts

    for trip_id, trip_scenes in by_trip.items():
        # Only root scenes (not children) participate in binning
        roots = [s for s in trip_scenes if not is_child[s["scene_id"]]]
        uf = UF([s["scene_id"] for s in roots])
        for i, s1 in enumerate(roots):
            a0, a1 = s1["_span"]
            for s2 in roots[i+1:]:
                b0, b1 = s2["_span"]
                if spans_overlap(a0, a1, b0, b1):
                    uf.union(s1["scene_id"], s2["scene_id"])
        # Collect bins
        groups = defaultdict(list)
        for s in roots:
            groups[uf.find(s["scene_id"])].append(s)
        # Emit bins in narrative order
        sorted_groups = sorted(groups.values(), key=lambda g: min(s["_span"][0] for s in g))
        for grp in sorted_groups:
            bin_id_counter += 1
            bin_id = f"{trip_id}_B{bin_id_counter:03d}"
            # Bin span = union of all group spans
            bin_start = min(s["_span"][0] for s in grp)
            bin_end = max(s["_span"][1] for s in grp)
            # Who individuated scenes in this bin?
            statuses = set(s["rater_status"] for s in grp)
            # For child scenes with the same parent, assign the parent's bin
            member_scene_ids = [s["scene_id"] for s in grp]
            # Include any children whose parent is in this group
            for sc in trip_scenes:
                if is_child[sc["scene_id"]] and sc["parent_scene_id"] in member_scene_ids:
                    member_scene_ids.append(sc["scene_id"])
                    statuses.add(sc["rater_status"])
            # Determine bin-level status
            has_A = any(st in ("both", "only_A") for st in statuses)
            has_B = any(st in ("both", "only_B") for st in statuses)
            if has_A and has_B:
                bin_status = "both"
            elif has_A:
                bin_status = "only_A"
            else:
                bin_status = "only_B"
            # Is this bin "granularity-split"? True if the bin has scenes
            # contributed only by one rater AND scenes contributed only by the
            # other rater — meaning the two raters' individuations were
            # internally disjoint but overlap within the bin.
            all_A_counts = sum(1 for sid in member_scene_ids
                               for sc in scenes if sc["scene_id"] == sid and sc["rater_status"] == "only_A")
            all_B_counts = sum(1 for sid in member_scene_ids
                               for sc in scenes if sc["scene_id"] == sid and sc["rater_status"] == "only_B")
            bin_both_counts = sum(1 for sid in member_scene_ids
                                  for sc in scenes if sc["scene_id"] == sid and sc["rater_status"] == "both")
            # "granularity-recovered" = bin is `both` in bin view, but contains
            # only_A and only_B scenes, i.e. agreement only visible AFTER binning.
            granularity_recovered = (bin_status == "both" and bin_both_counts == 0
                                     and all_A_counts > 0 and all_B_counts > 0)

            # "chunking-split" = one rater's N scenes overlap the other rater's 1 scene
            chunking_split = (all_A_counts >= 2 and all_B_counts == 0 and bin_both_counts >= 1) or \
                             (all_B_counts >= 2 and all_A_counts == 0 and bin_both_counts >= 1) or \
                             (all_A_counts >= 2 and all_B_counts >= 1) or \
                             (all_B_counts >= 2 and all_A_counts >= 1)

            bins_info.append({
                "bin_id": bin_id,
                "trip_id": trip_id,
                "bin_span_start": bin_start,
                "bin_span_end": bin_end,
                "bin_status": bin_status,
                "n_scenes_in_bin": len(member_scene_ids),
                "n_both_scenes": bin_both_counts,
                "n_only_A_scenes": all_A_counts,
                "n_only_B_scenes": all_B_counts,
                "granularity_recovered": granularity_recovered,
                "chunking_split": chunking_split,
                "member_scene_ids": ";".join(member_scene_ids),
            })
            for sid in member_scene_ids:
                bin_assignment[sid] = bin_id

    # Write per-scene bin_id to ANALYSIS dir (derived view, not canonical data)
    os.makedirs(os.path.join(here, OUT_DIR), exist_ok=True)
    out_scene_bins = os.path.join(here, OUT_DIR, "scene_bins.csv")
    with open(out_scene_bins, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scene_id", "trip_id", "rater_status", "bin_id"])
        for s in scenes:
            w.writerow([s["scene_id"], s["trip_id"], s["rater_status"],
                        bin_assignment.get(s["scene_id"], "")])

    # Write bins summary to ANALYSIS dir
    out_bins = os.path.join(here, OUT_DIR, "bins_summary.csv")
    fields = list(bins_info[0].keys())
    with open(out_bins, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in bins_info:
            w.writerow(r)

    # Summary to stdout
    n_bins = len(bins_info)
    n_bin_both = sum(1 for b in bins_info if b["bin_status"] == "both")
    n_bin_A = sum(1 for b in bins_info if b["bin_status"] == "only_A")
    n_bin_B = sum(1 for b in bins_info if b["bin_status"] == "only_B")
    n_recovered = sum(1 for b in bins_info if b["granularity_recovered"])
    n_chunking = sum(1 for b in bins_info if b["chunking_split"])

    # Scene-level comparison
    n_scene_both = sum(1 for s in scenes if s["rater_status"] == "both")
    n_scene_A = sum(1 for s in scenes if s["rater_status"] == "only_A")
    n_scene_B = sum(1 for s in scenes if s["rater_status"] == "only_B")
    n_scene_total = len(scenes)

    print(f"Scenes: {n_scene_total}  (both={n_scene_both}, only_A={n_scene_A}, only_B={n_scene_B})")
    print(f"        Scene-level shared rate: {100*n_scene_both/n_scene_total:.1f}%")
    print(f"")
    print(f"Bins:   {n_bins}  (both={n_bin_both}, only_A={n_bin_A}, only_B={n_bin_B})")
    print(f"        Bin-level shared rate:   {100*n_bin_both/n_bins:.1f}%")
    print(f"")
    print(f"Granularity-recovered bins: {n_recovered}")
    print(f"  (bins where raters AGREE something happened but individuated disjointly)")
    print(f"Chunking-split bins:        {n_chunking}")
    print(f"  (one rater N scenes, other rater >=1 overlapping scene)")
    print(f"")
    print(f"Wrote:")
    print(f"  {out_scene_bins}")
    print(f"  {out_bins}")


if __name__ == "__main__":
    main()
