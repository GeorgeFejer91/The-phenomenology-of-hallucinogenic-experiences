"""Visualize distribution of Stage-1 driver categories across substances.

Produces four figures in 1.Recoding/figures/:
  - driver_counts_by_substance.png      bar chart (absolute counts)
  - driver_proportion_by_substance.png  stacked bar (proportions)
  - driver_by_pair.png                  per-coder-pair breakdown
  - driver_per_trip_heatmap.png         heatmap, trips × driver counts
"""
import os, csv
from collections import defaultdict, Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA = "../data"
OUT_DIR = "../figures"

DRIVERS_ORDER = ["AB", "FRAG", "AMP", "AMB", "SOMA", "RCL"]
DRIVER_LABELS = {
    "AB":   "Shared (both)",
    "FRAG": "Fragment",
    "AMP":  "Sensory amplification",
    "AMB":  "Ambiguity (thought/memory)",
    "SOMA": "Somatic / self-transform",
    "RCL":  "Genuine miss (reconcile)",
}
DRIVER_COLOURS = {
    "AB":   "#4caf50",
    "FRAG": "#ff9800",
    "AMP":  "#ffc107",
    "AMB":  "#9c27b0",
    "SOMA": "#e91e63",
    "RCL":  "#f44336",
}
# Substance palette — used wherever brugmansia and psilocybin are directly compared.
SUBSTANCE_COLOURS = {
    "brugmansia": "#1b4332",  # forest dark green
    "psilocybin": "#9b111e",  # ruby red
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


def main():
    here = os.path.dirname(__file__)
    os.makedirs(os.path.join(here, OUT_DIR), exist_ok=True)

    scenes = load("scenes.csv")
    trips = {t["trip_id"]: t for t in load("trips.csv")}

    # --- 1. Absolute counts by substance ---
    counts_by_sub = defaultdict(Counter)
    for s in scenes:
        counts_by_sub[s["substance"]][extract_driver(s["scene_id"])] += 1

    substances = sorted(counts_by_sub.keys())
    x = np.arange(len(DRIVERS_ORDER))
    width = 0.38
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for i, sub in enumerate(substances):
        vals = [counts_by_sub[sub][d] for d in DRIVERS_ORDER]
        bars = ax.bar(x + (i - (len(substances)-1)/2) * width, vals, width,
                      label=sub.title(), color=SUBSTANCE_COLOURS[sub])
        for b, v in zip(bars, vals):
            if v:
                ax.text(b.get_x() + b.get_width()/2, v + 1, str(v), ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([DRIVER_LABELS[d] for d in DRIVERS_ORDER], rotation=20, ha="right")
    ax.set_ylabel("Number of scenes")
    ax.set_title("Stage-1 driver categories per substance (absolute counts)")
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(here, OUT_DIR, "driver_counts_by_substance.png"), dpi=140)
    plt.close()

    # --- 2. Stacked-bar proportions by substance ---
    fig, ax = plt.subplots(figsize=(8, 5))
    bottoms = np.zeros(len(substances))
    totals = [sum(counts_by_sub[sub].values()) for sub in substances]
    for d in DRIVERS_ORDER:
        vals = np.array([counts_by_sub[sub][d] for sub in substances], dtype=float)
        props = vals / np.array(totals)
        ax.bar(substances, props, bottom=bottoms, color=DRIVER_COLOURS[d],
               label=DRIVER_LABELS[d], edgecolor="white")
        # Annotate non-trivial
        for i, (v, p) in enumerate(zip(vals, props)):
            if p >= 0.03:
                ax.text(i, bottoms[i] + p/2, f"{int(v)}\n({p*100:.0f}%)",
                        ha="center", va="center", fontsize=8, color="white" if d in ("AB", "RCL", "SOMA", "AMB") else "black")
        bottoms += props
    ax.set_ylabel("Proportion of scenes")
    ax.set_title("Stage-1 driver proportions by substance")
    ax.set_ylim(0, 1.02)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(here, OUT_DIR, "driver_proportion_by_substance.png"), dpi=140)
    plt.close()

    # --- 3. Per coder-pair breakdown ---
    pair_key = lambda t: f"{t['substance'][:4].title()} {t['block']}: {t['coder_A']} × {t['coder_B']}"
    pair_counts = defaultdict(Counter)
    for s in scenes:
        t = trips[s["trip_id"]]
        pair_counts[pair_key(t)][extract_driver(s["scene_id"])] += 1
    pair_names = sorted(pair_counts.keys())
    fig, ax = plt.subplots(figsize=(11, 5))
    bottoms = np.zeros(len(pair_names))
    totals = [sum(pair_counts[p].values()) for p in pair_names]
    for d in DRIVERS_ORDER:
        vals = np.array([pair_counts[p][d] for p in pair_names], dtype=float)
        props = vals / np.array(totals)
        ax.bar(pair_names, props, bottom=bottoms, color=DRIVER_COLOURS[d],
               label=DRIVER_LABELS[d], edgecolor="white")
        for i, (v, p) in enumerate(zip(vals, props)):
            if p >= 0.04:
                ax.text(i, bottoms[i] + p/2, f"{int(v)}",
                        ha="center", va="center", fontsize=8, color="white" if d in ("AB", "RCL", "SOMA", "AMB") else "black")
        bottoms += props
    ax.set_ylabel("Proportion of scenes")
    ax.set_title("Stage-1 driver proportions by coder pair")
    ax.set_ylim(0, 1.02)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    plt.setp(ax.get_xticklabels(), rotation=18, ha="right")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(here, OUT_DIR, "driver_by_pair.png"), dpi=140)
    plt.close()

    # --- 4. Per-trip driver heatmap ---
    trip_counts = defaultdict(Counter)
    for s in scenes:
        trip_counts[s["trip_id"]][extract_driver(s["scene_id"])] += 1
    ordered_trips = sorted(trip_counts.keys(), key=lambda t: (t.split('_')[0], int(t.split('_')[1])))
    M = np.array([[trip_counts[t][d] for d in DRIVERS_ORDER] for t in ordered_trips])
    fig, ax = plt.subplots(figsize=(7, 11))
    im = ax.imshow(M, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(np.arange(len(DRIVERS_ORDER)))
    ax.set_xticklabels([DRIVER_LABELS[d] for d in DRIVERS_ORDER], rotation=25, ha="right", fontsize=9)
    ax.set_yticks(np.arange(len(ordered_trips)))
    ax.set_yticklabels(ordered_trips, fontsize=8)
    # Annotate cells
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if M[i, j]:
                ax.text(j, i, int(M[i, j]), ha="center", va="center",
                        color="white" if M[i, j] > M.max()/2 else "black", fontsize=7)
    # Separator between substances
    split_idx = next((i for i, t in enumerate(ordered_trips) if t.startswith("Psilocybe")), None)
    if split_idx is not None:
        ax.axhline(split_idx - 0.5, color="blue", linewidth=1.5)
    ax.set_title("Driver category counts per trip")
    fig.colorbar(im, ax=ax, shrink=0.6, label="count")
    plt.tight_layout()
    plt.savefig(os.path.join(here, OUT_DIR, "driver_per_trip_heatmap.png"), dpi=140)
    plt.close()

    print(f"wrote 4 figures to {OUT_DIR}/")
    for fn in ("driver_counts_by_substance.png", "driver_proportion_by_substance.png",
               "driver_by_pair.png", "driver_per_trip_heatmap.png"):
        print(f"  {fn}")


if __name__ == "__main__":
    main()
