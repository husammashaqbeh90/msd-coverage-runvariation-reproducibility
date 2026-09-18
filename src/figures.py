#!/usr/bin/env python3
"""
Stage 4 — Figures 1-3, regenerated from outputs/ (v3 numbers).

Print constraints: vector PDF + 300 dpi PNG, serif, greyscale-safe. Identity is
never carried by colour alone — every category also differs in marker shape,
fill, or line style, so the figures survive greyscale printing and CVD.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PKG, "outputs")
FIG = os.path.join(PKG, "figures")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "grid.linewidth": 0.4,
    "lines.linewidth": 1.4,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

INK = "#1a1a1a"
MUTED = "#6b6b6b"
GRID = "#d9d9d9"
REF = "#8c8c8c"


def save(fig, name):
    # CreationDate is suppressed so the PDFs are byte-reproducible across runs.
    meta = {"pdf": {"CreationDate": None, "Producer": "matplotlib", "Creator": "figures.py"},
            "png": {"Software": "figures.py"}}
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=300,
                    bbox_inches="tight", facecolor="white", metadata=meta[ext])
    plt.close(fig)
    print(f"  wrote figures/{name}.pdf and .png")


# ------------------------------------------------------------------ Figure 1
def figure1(rep):
    fig, ax = plt.subplots(figsize=(7.1, 5.0))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    LH = 5.2          # line height
    PADV = 3.4        # vertical padding inside a box

    def box(x, ytop, w, lines, bold_first=True, fill="#f4f4f4", fs=7.4):
        """Draw a box whose top edge is at ytop; height follows the line count."""
        h = 2 * PADV + LH * len(lines)
        y = ytop - h
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=1.2",
                                    linewidth=0.8, edgecolor=INK, facecolor=fill))
        first = ytop - PADV - LH / 2
        for i, ln in enumerate(lines):
            ax.text(x + w / 2, first - i * LH, ln, ha="center", va="center",
                    fontsize=fs, color=INK,
                    fontweight="bold" if (i == 0 and bold_first) else "normal")
        return y   # bottom edge

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=8, linewidth=0.8, color=INK))

    b1 = box(26, 99, 48, ["Released MSD benchmark results",
                          "6 source archives, 1160 executions",
                          "14 derived evaluation groups"])
    b2 = box(26, b1 - 6, 48, ["Five analysed evaluation groups",
                              "968 released source records"])
    arrow(50, b1, 50, b1 - 6)
    b3 = box(26, b2 - 6, 48, ["Evaluable records",
                              f"ATE, C and S available: n = {rep['evaluable']}"])
    arrow(50, b2, 50, b2 - 6)

    split = b3 - 5
    arrow(50, b3, 50, split)
    ax.text(51.8, b3 - 2.6, "split into two analyses", fontsize=6.8, color=MUTED, va="center")

    b4 = box(2, split - 3, 45, ["RQ1  Trajectory error at high coverage",
                                f"C ≥ 0.99 and S ≥ 0.99: n = {rep['primary_high_coverage']}",
                                "outcome: ATE distribution and the",
                                "ATE ≥ 1 m and ATE ≥ 10 m proportions"], fill="#ececec")
    b5 = box(53, split - 3, 45, ["RQ2  Run-to-run variation",
                                 "ORB-SLAM3 and OKVIS2, three runs each",
                                 "triplets with all three runs high coverage:",
                                 f"{rep['orb_triplets']} and {rep['okvis_triplets']} of 64"],
             fill="#ececec")
    arrow(50, split, 24.5, split - 3); arrow(50, split, 75.5, split - 3)

    b6 = box(2, b4 - 6, 96, ["Sensitivity and uncertainty",
                             "coverage threshold  |  equal-sequence weighting",
                             "released run-selection rule  |  leave-one-system-out",
                             "sequence-cluster bootstrap, 30 000 replicates"], fill="#f9f9f9")
    arrow(24.5, b4, 24.5, b4 - 6); arrow(75.5, b5, 75.5, b5 - 6)

    ax.text(50, b6 - 4.5,
            "The repeated-run analysis is a subset and reanalysis of the released benchmark "
            "results, not an independent validation sample.",
            ha="center", fontsize=6.6, color=MUTED, style="italic")
    ax.set_ylim(b6 - 8, 100)
    save(fig, "Figure1_study_design")


# ------------------------------------------------------------------ Figure 2
def figure2(hc):
    a = np.sort(hc.ate.to_numpy())
    n = a.size
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.9))

    ax = axes[0]
    ax.step(a, np.arange(1, n + 1) / n * 100, where="post", color=INK, linewidth=1.4)
    ax.set_xscale("log")
    XMAX = 1e3
    n_above = int((a > XMAX).sum())
    ax.set_xlim(10 ** np.floor(np.log10(a.min())), XMAX)
    ax.set_xlabel("Absolute trajectory error [m], log scale")
    ax.set_ylabel("Records at or below [%]")
    ax.set_title(f"A  Empirical cumulative distribution (n = {n})", loc="left")
    ax.grid(True, which="major", color=GRID, linewidth=0.4)
    ax.set_ylim(0, 103)
    for x, lab in ((1, "1 m"), (10, "10 m")):
        ax.axvline(x, color=REF, linewidth=0.9, linestyle="--", dashes=(4, 3))
        ax.text(x, 101.5, lab, fontsize=6.6, color=MUTED, ha="center", va="bottom")
    if n_above:
        ax.annotate(f"{n_above} records lie above {XMAX:.0f} m and are\n"
                    f"outside the drawn range; all are retained\nin every reported estimate",
                    xy=(XMAX, 46), xytext=(-6, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=6.4, color=MUTED)

    ax = axes[1]
    grid = np.logspace(np.log10(0.05), np.log10(20), 260)
    pct = [(a >= t).sum() / n * 100 for t in grid]
    ax.plot(grid, pct, color=INK, linewidth=1.4)
    ax.set_xscale("log")
    ax.set_xlabel("ATE threshold [m], log scale")
    ax.set_ylabel("Records at or above threshold [%]")
    ax.set_title("B  Upper tail", loc="left")
    ax.grid(True, which="major", color=GRID, linewidth=0.4)
    for x in (1, 10):
        ax.axvline(x, color=REF, linewidth=0.9, linestyle="--", dashes=(4, 3))
    for x, y, lab, dx, ha in (
            (1, (a >= 1).sum() / n * 100, f"{(a>=1).sum()/n*100:.1f}% at 1 m", 8, "left"),
            (10, (a >= 10).sum() / n * 100, f"{(a>=10).sum()/n*100:.1f}% at 10 m", -8, "right")):
        ax.plot([x], [y], marker="o", markersize=4.5, color=INK,
                markerfacecolor="white", markeredgewidth=1.2, zorder=5)
        ax.annotate(lab, (x, y), textcoords="offset points", xytext=(dx, 9),
                    fontsize=6.8, color=INK, ha=ha)
    ax.set_ylim(bottom=0)
    fig.text(0.5, -0.07,
             "Both panels are drawn over a truncated abscissa for legibility. No record is excluded "
             "from any computation:\nevery reported percentile, count and proportion uses all "
             f"{n} records.",
             ha="center", fontsize=6.6, color=MUTED, style="italic")
    fig.tight_layout()
    save(fig, "Figure2_high_coverage_ATE_distribution")


# ------------------------------------------------------------------ Figure 3
def figure3(det):
    # greyscale-safe: category is carried by marker shape + fill, colour is secondary
    CAT = [("neither", "none", "o", "white", INK),
           ("crossed 1 m", "1 m", "s", "#9e9e9e", INK),
           ("crossed 10 m", "10 m", "D", INK, INK)]
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 6.4), sharex=True)
    for ax, (lab, sub) in zip(axes, det.groupby("system", sort=False)):
        sub = sub.copy()
        sub["mid"] = np.sqrt(sub.ate_min * sub.ate_max)
        sub = sub.sort_values("mid").reset_index(drop=True)
        for i, r in sub.iterrows():
            cat = 2 if r.cross10 else (1 if r.cross1 else 0)
            _, _, mk, mfc, mec = CAT[cat]
            ax.hlines(i, r.ate_min, r.ate_max, color=MUTED, linewidth=0.9, zorder=1)
            runs = [r.ate_run1, r.ate_run2, r.ate_run3]
            ax.plot(runs, [i] * 3, linestyle="none", marker=mk,
                    markersize=4.0, markerfacecolor=mfc, markeredgecolor=mec,
                    markeredgewidth=0.8, zorder=3)
        ax.set_xscale("log")
        ax.set_yticks(range(len(sub)))
        ax.set_yticklabels(sub.sequence, fontsize=5.2)
        ax.set_ylim(-1, len(sub))
        ax.set_title(f"{'A' if lab=='ORB-SLAM3' else 'B'}  {lab}  "
                     f"({len(sub)} eligible triplets)", loc="left")
        ax.set_xlabel("Absolute trajectory error [m], log scale")
        ax.grid(True, axis="x", which="major", color=GRID, linewidth=0.4)
        for x in (1, 10):
            ax.axvline(x, color=REF, linewidth=0.9, linestyle="--", dashes=(4, 3))
    LEG = {"none": "no threshold crossed", "1 m": "1 m threshold crossed",
           "10 m": "10 m threshold crossed"}
    handles = [plt.Line2D([], [], linestyle="none", marker=mk, markersize=4.5,
                          markerfacecolor=mfc, markeredgecolor=mec, markeredgewidth=0.8,
                          label=LEG[short])
               for _, short, mk, mfc, mec in CAT]
    handles.append(plt.Line2D([], [], color=MUTED, linewidth=0.9,
                              label="within-triplet min–max span"))
    fig.tight_layout(rect=(0, 0.055, 1, 1))
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, 0.028))
    fig.text(0.5, 0.002,
             "Each row is one sequence for which all three released runs satisfied C ≥ 0.99 "
             "and S ≥ 0.99; rows sorted by within-triplet geometric mean ATE.\n"
             "Markers show the three individual ATE values. Vertical reference lines mark 1 m "
             "and 10 m.",
             ha="center", fontsize=6.6, color=MUTED, style="italic")
    save(fig, "Figure3_repeated_run_ATE_ranges")


if __name__ == "__main__":
    import json
    rep = json.load(open(os.path.join(OUT, "analysis_report.json")))
    d = pd.read_csv(os.path.join(OUT, "records_primary.csv"))
    ev = d.dropna(subset=["ate", "completion", "success"])
    hc = ev[(ev.completion >= 0.99) & (ev.success >= 0.99)]
    det = pd.read_csv(os.path.join(OUT, "Supplement_repeated_triplet_details.csv"))
    print("Regenerating figures:")
    figure1(rep)
    figure2(hc)
    figure3(det)
