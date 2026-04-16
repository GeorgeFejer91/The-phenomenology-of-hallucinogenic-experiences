"""Generate reliability figures for the preprint.

Produces four PNG figures in Preprint/figures/:

  fig_R1_scene_individuation.png
      Per-coder-pair stacked bar: n_both / n_only_A / n_only_B, with Jaccard
      annotated per pair. Shows individuation asymmetry visually.

  fig_R2_kappa_paradox.png
      Scatter of per-(pair, item) Cohen's kappa vs tag prevalence. The PABAK
      overlay (same points coloured by PABAK, or separate panel) illustrates
      the kappa paradox: extreme-prevalence items yield low kappa despite
      high observed agreement.

  fig_R3_section_heatmap.png
      Per-L1-section x coder-pair heatmap of weighted-mean Cohen's kappa.
      Compact overview of which taxonomic sections are reliably coded and
      which are not.

  fig_R4_per_scene_jaccard.png
      Violin + strip plot of per-scene tag-set Jaccard (J_s), split by
      substance. Shows the typical spread (~1/3 tag overlap) and the long
      tails (scenes fully converged vs fully divergent on attributes).

Inputs: 1.Recoding/analysis/reliability/*.csv (produced by script 19).
"""
# ======================================================================
# AI DIRECTIVE — read AI_DIRECTIVE.md at repo root
# Stage 1 of this project measures INTER-RATER CONSISTENCY ON SCENE
# INDIVIDUATION ONLY.  The attribute-level figures here (R2, R3, R4)
# are DESCRIPTIVE — they summarise reliability numbers, not resolve
# attribute disagreements.  Stage 2 (attribute reconciliation) remains
# deferred.  See AI_DIRECTIVE.md and 1.Recoding/STAGE1_SCOPE.json.
# ======================================================================
import os, csv
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RELI_DIR = "../analysis/reliability"
OUT_DIR  = "../../Preprint/figures"

# Project-fixed substance palette
SUB_COLOURS = {
    "brugmansia": "#1b4332",  # forest dark green
    "psilocybin": "#9b111e",  # ruby red
}

# Coder-pair colour — neutral, since pair identity is the grouping variable
PAIR_COLOURS = {
    "Brug 01-10: Brendan × Noah":        "#4a7c59",   # muted forest
    "Brug 11-20: Alessandra × Alessio":  "#1b4332",   # dark forest
    "Psil 01-10: Alessandra × Brendan":  "#c94b5c",   # muted ruby
    "Psil 11-20: Francesco × Susana":    "#9b111e",   # dark ruby
}


def load(name):
    with open(os.path.join(os.path.dirname(__file__), RELI_DIR, name),
              encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f(s, default=None):
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


# ------------------------------------------------------------
# Figure R1: scene-individuation per coder pair
# ------------------------------------------------------------
def fig_R1(out_path):
    rows = load("scene_individuation.csv")
    # Order: brug first, then psil, within each by block
    rows.sort(key=lambda r: (0 if r["substance"] == "brugmansia" else 1, r["block"]))
    pair_labels = [r["coder_pair"] for r in rows]
    both  = [int(r["n_both"])   for r in rows]
    oa    = [int(r["n_only_A"]) for r in rows]
    ob    = [int(r["n_only_B"]) for r in rows]
    jacc  = [float(r["jaccard_scenes"]) for r in rows]
    asym  = [float(r["asymmetry_ratio"]) for r in rows]
    conv  = [float(r["percent_convergent"]) for r in rows]

    # horizontal stacked bar
    y = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(9.5, 3.8))
    ax.barh(y, both, color="#1f7a3a", label="both raters individuated",
            edgecolor="white", height=0.65)
    ax.barh(y, oa, left=both, color="#c46a1c", label="only rater A",
            edgecolor="white", height=0.65)
    ax.barh(y, ob, left=[b+a for b,a in zip(both,oa)], color="#6e4fa6",
            label="only rater B", edgecolor="white", height=0.65)
    for i, (J, A, C) in enumerate(zip(jacc, asym, conv)):
        total = both[i] + oa[i] + ob[i]
        ax.text(total + 1.5, i,
                f"  J={J:.2f}   asym={A:.2f}   n={total}",
                va="center", fontsize=8.5, color="#333")
    ax.set_yticks(y)
    ax.set_yticklabels(pair_labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("number of scenes")
    ax.set_title("Scene-individuation per coder pair\n"
                 "both-rater (consensus) vs only-A vs only-B scenes",
                 fontsize=10.5)
    ax.legend(loc="lower right", fontsize=8.5, framealpha=0.95)
    ax.set_xlim(0, max(sum(xs) for xs in zip(both, oa, ob)) * 1.35)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


# ------------------------------------------------------------
# Figure R2: kappa paradox
# ------------------------------------------------------------
def fig_R2(out_path):
    rows = load("attribute_kappa_by_item.csv")
    prev   = []
    kappa  = []
    pabak  = []
    obs    = []
    pairs  = []
    for r in rows:
        p = f(r["prevalence"])
        k = f(r["cohens_kappa"])
        pb = f(r["pabak"])
        o = f(r["observed_agreement"])
        n = int(r["n_shared_scenes"]) if r["n_shared_scenes"] else 0
        if p is None or k is None or n < 3:
            continue
        prev.append(p)
        kappa.append(k)
        pabak.append(pb)
        obs.append(o)
        pairs.append(r["coder_pair"])

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=False)

    # Left panel: kappa vs prevalence
    ax = axes[0]
    sc = ax.scatter(prev, kappa,
                    c=obs, cmap="viridis", s=35, alpha=0.78,
                    edgecolor="white", linewidth=0.5, vmin=0.5, vmax=1.0)
    ax.axhline(0.0, color="#555", lw=0.7, linestyle="--")
    ax.axhline(0.40, color="#aaa", lw=0.5, linestyle=":", alpha=0.6)
    ax.axhline(0.60, color="#aaa", lw=0.5, linestyle=":", alpha=0.6)
    ax.set_xlabel("tag prevalence (mean A-tag / B-tag rate on AB scenes)")
    ax.set_ylabel("Cohen's $\\kappa$")
    ax.set_title("Cohen's $\\kappa$ vs tag prevalence", fontsize=10.5)
    cb = plt.colorbar(sc, ax=ax, shrink=0.9, label="observed agreement")
    cb.ax.tick_params(labelsize=8)
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.15, 1.02)

    # Right panel: kappa vs PABAK
    ax = axes[1]
    ax.scatter(pabak, kappa,
               c=[PAIR_COLOURS.get(p, "#888") for p in pairs],
               s=35, alpha=0.78, edgecolor="white", linewidth=0.5)
    ax.plot([-0.1, 1.05], [-0.1, 1.05], color="#aaa", lw=0.6, linestyle="--",
            label="identity")
    ax.axhline(0.0, color="#555", lw=0.7, linestyle="--")
    ax.set_xlabel("PABAK (prevalence- and bias-adjusted $\\kappa$)")
    ax.set_ylabel("Cohen's $\\kappa$")
    ax.set_title("The kappa paradox\n(many items: PABAK $\\gg$ $\\kappa$)",
                 fontsize=10.5)
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.set_xlim(-0.1, 1.05)
    ax.set_ylim(-0.15, 1.05)
    # Coder-pair legend
    handles = [plt.Line2D([0], [0], marker="o", color="w", markersize=7,
                          markerfacecolor=c, markeredgecolor="white",
                          label=p.split(": ", 1)[-1])
               for p, c in PAIR_COLOURS.items()]
    ax.legend(handles=handles, loc="lower right", fontsize=7.5, framealpha=0.9)

    plt.suptitle("Attribute-classification reliability: items are "
                 "low-prevalence by nature, so Cohen's $\\kappa$ under-states "
                 "agreement", fontsize=10.8, y=1.02)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


# ------------------------------------------------------------
# Figure R3: per-L1-section x coder-pair heatmap
# ------------------------------------------------------------
def fig_R3(out_path):
    rows = load("attribute_kappa_by_section.csv")
    # Build matrix
    pairs_order = [
        "Brug 01-10: Brendan × Noah",
        "Brug 11-20: Alessandra × Alessio",
        "Psil 01-10: Alessandra × Brendan",
        "Psil 11-20: Francesco × Susana",
    ]
    # Sections: take those that appear at least twice to declutter
    from collections import Counter
    sec_count = Counter(r["level_1"] for r in rows)
    sections = [s for s, c in sec_count.most_common() if c >= 2]
    # Enforce a sensible order (modality + taxonomic)
    preferred_order = [
        "Visual hallucination",
        "Type of visual alteration",
        "Auditory hallucination",
        "Tactile hallucination",
        "Nonsensory hallucination",
        "Modal status of the hallucination",
    ]
    sections = [s for s in preferred_order if s in sections] + \
               [s for s in sections if s not in preferred_order]

    M = np.full((len(sections), len(pairs_order)), np.nan)
    N = np.full_like(M, fill_value=0, dtype=int)
    for r in rows:
        if r["level_1"] not in sections or r["coder_pair"] not in pairs_order:
            continue
        i = sections.index(r["level_1"])
        j = pairs_order.index(r["coder_pair"])
        k = f(r["weighted_mean_kappa"])
        ni = int(r["n_items_active"]) if r["n_items_active"] else 0
        if k is not None:
            M[i, j] = k
            N[i, j] = ni

    fig, ax = plt.subplots(figsize=(9.5, 3.8))
    cmap = plt.get_cmap("RdYlGn")
    im = ax.imshow(M, cmap=cmap, vmin=0.0, vmax=0.8, aspect="auto")
    ax.set_xticks(np.arange(len(pairs_order)))
    ax.set_xticklabels([p.split(": ", 1)[-1] for p in pairs_order],
                       fontsize=8.5, rotation=12, ha="right")
    ax.set_yticks(np.arange(len(sections)))
    ax.set_yticklabels(sections, fontsize=8.5)
    # Substance-band colour above x-tick labels
    for i, p in enumerate(pairs_order):
        sub = "brugmansia" if p.startswith("Brug") else "psilocybin"
        ax.add_patch(plt.Rectangle((i-0.5, len(sections)-0.4),
                                    1.0, 0.12,
                                    transform=ax.transData,
                                    facecolor=SUB_COLOURS[sub],
                                    clip_on=False))
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            n = N[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center",
                        fontsize=9, color="#888")
            else:
                colour = "black" if 0.2 < v < 0.6 else "white"
                ax.text(j, i, f"{v:.2f}\nn={n}", ha="center", va="center",
                        fontsize=7.5, color=colour)
    ax.set_title("Weighted $\\kappa$ per L1 section × coder pair",
                 fontsize=10.5)
    cb = plt.colorbar(im, ax=ax, shrink=0.85,
                      label="weighted Cohen's $\\kappa$ (cell value)")
    cb.ax.tick_params(labelsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


# ------------------------------------------------------------
# Figure R4: per-scene Jaccard distribution
# ------------------------------------------------------------
def fig_R4(out_path):
    rows = load("per_scene_jaccard.csv")
    brug = [f(r["jaccard"]) for r in rows if r["substance"] == "brugmansia" and r["jaccard"]]
    psil = [f(r["jaccard"]) for r in rows if r["substance"] == "psilocybin" and r["jaccard"]]
    brug = [x for x in brug if x is not None]
    psil = [x for x in psil if x is not None]

    fig, ax = plt.subplots(figsize=(8, 4.2))
    parts = ax.violinplot([brug, psil], positions=[1, 2],
                          widths=0.75, showmeans=False, showextrema=False,
                          showmedians=False)
    for i, pc in enumerate(parts["bodies"]):
        sub = "brugmansia" if i == 0 else "psilocybin"
        pc.set_facecolor(SUB_COLOURS[sub])
        pc.set_edgecolor("black")
        pc.set_alpha(0.35)
    # Overlaid strip
    rng = np.random.default_rng(0)
    for i, (vals, sub) in enumerate(zip([brug, psil], ["brugmansia", "psilocybin"]), start=1):
        xs = rng.normal(loc=i, scale=0.05, size=len(vals))
        ax.scatter(xs, vals, s=12, color=SUB_COLOURS[sub],
                   alpha=0.55, edgecolor="white", linewidth=0.3)
    # Box inside
    bp = ax.boxplot([brug, psil], positions=[1, 2], widths=0.18,
                    patch_artist=True, showfliers=False)
    for i, box in enumerate(bp["boxes"]):
        box.set_facecolor("white")
        box.set_edgecolor("#333")
        box.set_alpha(0.95)
    for median in bp["medians"]:
        median.set_color("#333")
        median.set_linewidth(1.8)
    for whisker in bp["whiskers"]:
        whisker.set_color("#333")
    for cap in bp["caps"]:
        cap.set_color("#333")

    # Annotations
    for i, vals in enumerate([brug, psil], start=1):
        if vals:
            mean = float(np.mean(vals))
            ax.annotate(f"mean={mean:.3f}\nmedian={np.median(vals):.3f}\nn={len(vals)}",
                        xy=(i + 0.33, 0.85), fontsize=8.2, color="#333")

    ax.set_xticks([1, 2])
    ax.set_xticklabels(["brugmansia", "psilocybin"], fontsize=10)
    ax.set_ylabel("per-scene tag-set Jaccard, $J_s$")
    ax.set_ylim(-0.05, 1.05)
    ax.axhline(1.0, color="#888", lw=0.5, linestyle=":")
    ax.axhline(0.5, color="#888", lw=0.5, linestyle=":")
    ax.set_title("Scene-level agreement on attribute tags (shared scenes only)\n"
                 "$J_s = |T_A^s \\cap T_B^s| / |T_A^s \\cup T_B^s|$",
                 fontsize=10.3)
    ax.grid(axis="y", linestyle=":", alpha=0.35)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


def main():
    here = os.path.dirname(__file__)
    out = os.path.abspath(os.path.join(here, OUT_DIR))
    os.makedirs(out, exist_ok=True)
    fig_R1(os.path.join(out, "fig_R1_scene_individuation.png"))
    fig_R2(os.path.join(out, "fig_R2_kappa_paradox.png"))
    fig_R3(os.path.join(out, "fig_R3_section_heatmap.png"))
    fig_R4(os.path.join(out, "fig_R4_per_scene_jaccard.png"))
    for fn in ("fig_R1_scene_individuation.png",
               "fig_R2_kappa_paradox.png",
               "fig_R3_section_heatmap.png",
               "fig_R4_per_scene_jaccard.png"):
        p = os.path.join(out, fn)
        print(f"  {fn:<38} {os.path.getsize(p)//1024} KB")


if __name__ == "__main__":
    main()
