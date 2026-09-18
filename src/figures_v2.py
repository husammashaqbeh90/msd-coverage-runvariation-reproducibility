#!/usr/bin/env python3
"""
Revised Figures 1-3.

Changes against src/figures.py:
  Fig 1  PRISMA-style flow with explicit exclusion boxes; the sensitivity box is
         attached to the RQ1 arm only (it does not apply to RQ2).
  Fig 2  A: aggregate ECDF plus a per-system ECDF, so the aggregate is not read
            as a property of "benchmarks" when its tail is carried by DM-VIO and
            ORB-SLAM3.  Truncated panel title fixed.
         B: replaces the old panel B (which was panel A re-plotted as 100-F).
            New panel shows coverage shortfall against ATE over all 861 evaluable
            records - the figure that actually carries the paper's claim.
  Fig 3  A: ECDF of the within-triplet max/min ratio, ATE and RTE, per system.
         B: only the 11 threshold-crossing triplets, at readable size.
         The 122-row dot chart moves to the supplement (Figure S1).

Print constraints inherited from figures.py: vector PDF + 300 dpi PNG, serif,
greyscale-safe (identity via marker shape / fill / dash, never colour alone).
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PKG, "outputs")
FIG = os.environ.get("FIGDIR", os.path.join(PKG, "figures"))
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 6.8,
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

# marker shape + fill carry identity; nothing depends on colour
SYS_STYLE = {
    "Basalt":     dict(marker="o", mfc="white",   mec=INK,   ms=3.2, dash=(5, 2)),
    "OKVIS2":     dict(marker="s", mfc="#bdbdbd", mec=INK,   ms=3.0, dash=(1.6, 1.6)),
    "ORB-SLAM3":  dict(marker="D", mfc=INK,       mec=INK,   ms=2.9, dash=(4, 1.5, 1, 1.5)),
    "DM-VIO":     dict(marker="^", mfc="white",   mec=INK,   ms=3.6, dash=(2.5, 1.2, 0.8, 1.2)),
    "Snake-SLAM": dict(marker="v", mfc="#6b6b6b", mec=INK,   ms=3.4, dash=(1, 1.4)),
}
SYS_ORDER = ["Basalt", "OKVIS2", "ORB-SLAM3", "DM-VIO", "Snake-SLAM"]


def save(fig, name):
    meta = {"pdf": {"CreationDate": None, "Producer": "matplotlib", "Creator": "figures_v2.py"},
            "png": {"Software": "figures_v2.py"}}
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=300,
                    bbox_inches="tight", facecolor="white", metadata=meta[ext])
    plt.close(fig)
    print(f"  wrote {name}.pdf / .png")


def _first(v):
    return v[0] if isinstance(v, (list, tuple)) else v


def ecdf(values):
    v = np.sort(np.asarray(values, dtype=float))
    return v, np.arange(1, v.size + 1) / v.size * 100.0


# ------------------------------------------------------------------ Figure 1
def figure1(rep, exc):
    fig, ax = plt.subplots(figsize=(7.1, 6.2))
    ax.set_xlim(0, 100)
    ax.axis("off")
    LH, PADV = 4.6, 3.0

    def box(x, ytop, w, lines, bold_first=True, fill="#f4f4f4", fs=7.2, align="center"):
        h = 2 * PADV + LH * len(lines)
        y = ytop - h
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=1.2",
                                    linewidth=0.8, edgecolor=INK, facecolor=fill))
        first = ytop - PADV - LH / 2
        for i, ln in enumerate(lines):
            if align == "left":
                ax.text(x + 2.0, first - i * LH, ln, ha="left", va="center", fontsize=fs,
                        color=INK, fontweight="bold" if (i == 0 and bold_first) else "normal")
            else:
                ax.text(x + w / 2, first - i * LH, ln, ha="center", va="center", fontsize=fs,
                        color=INK, fontweight="bold" if (i == 0 and bold_first) else "normal")
        return y

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=8, linewidth=0.8, color=INK))

    MAIN_X, MAIN_W = 8, 50          # main column
    EXC_X, EXC_W = 63, 35           # exclusion column

    b1 = box(MAIN_X, 99, MAIN_W, ["Released MSD benchmark package",
                                  "6 source archives, 1160 runs",
                                  "14 derived evaluation groups"])
    b2 = box(MAIN_X, b1 - 5, MAIN_W, ["Five analysed evaluation groups",
                                      "one causal group per system family",
                                      "968 released source records"])
    arrow(MAIN_X + MAIN_W / 2, b1, MAIN_X + MAIN_W / 2, b1 - 5)

    # exclusion 1
    e1 = box(EXC_X, b2 - 1, EXC_W,
             [f"Excluded: {exc['to_evaluable']} records",
              "98  DM-VIO, no released",
              "      scaled trajectory artifact",
              "  9  Snake-SLAM, no released",
              "      trajectory-error value"],
             fill="#ffffff", fs=6.8, align="left")
    b3 = box(MAIN_X, b2 - 11, MAIN_W, ["Evaluable records",
                                       f"ATE, C and S all available: n = {rep['evaluable']}"])
    arrow(MAIN_X + MAIN_W / 2, b2, MAIN_X + MAIN_W / 2, b2 - 11)
    arrow(MAIN_X + MAIN_W / 2, b2 - 6.5, EXC_X, b2 - 6.5)

    split = b3 - 4.5
    arrow(MAIN_X + MAIN_W / 2, b3, MAIN_X + MAIN_W / 2, split)
    ax.text(MAIN_X + MAIN_W / 2 + 1.8, b3 - 2.3, "two analyses", fontsize=6.6,
            color=MUTED, va="center")

    LX, LW = 2, 44
    RX, RW = 52, 46
    b4 = box(LX, split - 3, LW,
             ["RQ1  Trajectory error at high coverage",
              f"C ≥ 0.99 and S ≥ 0.99:  n = {rep['primary_high_coverage']}",
              f"excluded {exc['to_high_cov']} records below threshold",
              "outcome: ATE distribution and the",
              "ATE ≥ 1 m and ATE ≥ 10 m proportions"], fill="#ececec", fs=7.0)
    b5 = box(RX, split - 3, RW,
             ["RQ2  Run-to-run variation",
              "ORB-SLAM3 and OKVIS2, three runs each",
              "128 system-sequence triplets",
              "excluded 5 and 1 triplet, not all three",
              "runs at high coverage",
              f"eligible: {rep['orb_triplets']} and {rep['okvis_triplets']} of 64"],
             fill="#ececec", fs=7.0)
    arrow(MAIN_X + MAIN_W / 2, split, LX + LW / 2, split - 3)
    arrow(MAIN_X + MAIN_W / 2, split, RX + RW / 2, split - 3)

    b6 = box(LX, b4 - 5, LW,
             ["Sensitivity and uncertainty  (RQ1)",
              "coverage threshold  |  equal-sequence weighting",
              "released run-selection rule",
              "leave-one-system-out",
              "sequence-cluster bootstrap, 30,000 replicates"], fill="#f9f9f9", fs=6.9)
    arrow(LX + LW / 2, b4, LX + LW / 2, b4 - 5)

    b7 = box(RX, b5 - 5, RW,
             ["Secondary condition  (RQ2)",
              "exact coverage C = S = 1.0 in all three runs",
              f"{_first(rep['exact_triplets_ORB-SLAM3'])} ORB-SLAM3 and "
              f"{_first(rep['exact_triplets_OKVIS2'])} OKVIS2 triplets"], fill="#f9f9f9", fs=6.9)
    arrow(RX + RW / 2, b5, RX + RW / 2, b5 - 5)

    bot = min(b6, b7)
    ax.set_ylim(bot - 3, 100)
    save(fig, "Figure1_study_design")


# ------------------------------------------------------------------ Figure 2
def figure2(ev, hc):
    n = len(hc)
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.2))

    # ---- Panel A: aggregate ECDF + per-system ECDF
    ax = axes[0]
    for s in SYS_ORDER:
        sub = hc[hc.system == s]
        if len(sub) == 0:
            continue
        st = SYS_STYLE[s]
        x, y = ecdf(sub.ate)
        ax.step(x, y, where="post", color=MUTED, linewidth=0.85,
                dashes=st["dash"], zorder=2)
    x, y = ecdf(hc.ate)
    ax.step(x, y, where="post", color=INK, linewidth=1.7, zorder=4)

    ax.set_xscale("log")
    XMAX = 1e3
    n_above = int((hc.ate > XMAX).sum())
    ax.set_xlim(10 ** np.floor(np.log10(hc.ate.min())), XMAX)
    ax.set_ylim(0, 104)
    ax.set_xlabel("Absolute trajectory error [m], log scale")
    ax.set_ylabel("Cumulative percentage of records")
    ax.set_title(f"A  ATE at high output coverage (n = {n})", loc="left")
    ax.grid(True, which="major", color=GRID, linewidth=0.4)
    for xv, lab in ((1, "1 m"), (10, "10 m")):
        ax.axvline(xv, color=REF, linewidth=0.9, linestyle="--", dashes=(4, 3), zorder=1)
        ax.text(xv, 102, lab, fontsize=6.6, color=MUTED, ha="center", va="bottom")

    med = float(np.median(hc.ate))
    ax.plot([med], [50], marker="o", markersize=4.4, color=INK,
            markerfacecolor="white", markeredgewidth=1.2, zorder=6)
    ax.annotate(f"median {med:.3f} m", (med, 50), textcoords="offset points",
                xytext=(7, -10), fontsize=6.8, color=INK, ha="left")
    if n_above:
        ax.text(XMAX * 0.85, 4, f"{n_above} records above {XMAX:.0f} m lie outside\n"
                                "the drawn range and are retained\nin every reported estimate",
                ha="right", va="bottom", fontsize=6.3, color=MUTED)

    # ---- Panel B: coverage against ATE, all evaluable records
    ax = axes[1]
    EXACT_LO, EXACT_HI = 1.8e-6, 5.2e-6
    BREAK_X = 8.5e-6
    LEFT, RIGHT = 1.4e-6, 1.4
    YLO, YHI = 1e-3, 1e4

    rng = np.random.default_rng(7)
    sf = (1.0 - ev["cov"]).to_numpy()
    xs = np.where(sf <= 0,
                  np.exp(rng.uniform(np.log(EXACT_LO), np.log(EXACT_HI), size=sf.size)),
                  np.maximum(sf, 1.15e-5))
    ys = ev.ate.to_numpy()

    for s in SYS_ORDER:
        m = (ev.system == s).to_numpy()
        if not m.any():
            continue
        st = SYS_STYLE[s]
        ax.plot(xs[m], ys[m], linestyle="none", marker=st["marker"],
                markersize=st["ms"] * 0.85, markerfacecolor=st["mfc"],
                markeredgecolor=st["mec"], markeredgewidth=0.5, alpha=0.85, zorder=3)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(LEFT, RIGHT)
    ax.set_ylim(YLO, YHI)
    ax.axvline(BREAK_X, color=INK, linewidth=0.6, linestyle=":", zorder=1)
    ax.axvline(1e-2, color=INK, linewidth=1.0, linestyle="--", dashes=(4, 3), zorder=4)
    for yv, lab in ((1, "1 m"), (10, "10 m")):
        ax.axhline(yv, color=REF, linewidth=0.9, linestyle="--", dashes=(4, 3), zorder=2)
        ax.text(RIGHT * 0.62, yv * 1.3, lab, fontsize=6.4, color=MUTED, ha="right", va="bottom")

    ticks = [np.sqrt(EXACT_LO * EXACT_HI), 1e-4, 1e-3, 1e-2, 1e-1, 1e0]
    labels = ["exact", "0.9999", "0.999", "0.99", "0.9", "0"]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=6.1)
    ax.set_xlabel("Output coverage  min(C, S)      \u2190 better coverage")
    ax.set_ylabel("Absolute trajectory error [m], log scale")
    ax.set_title(f"B  Coverage against ATE (n = {len(ev)})", loc="left")
    ax.grid(True, which="major", axis="y", color=GRID, linewidth=0.4, zorder=0)

    n_elig = int((ev["cov"] >= 0.99).sum())
    n_elig_1m = int(((ev["cov"] >= 0.99) & (ev.ate >= 1)).sum())
    n_off = int((ev.ate > YHI).sum())
    ax.annotate("eligibility\nthreshold", xy=(1e-2, YLO), xytext=(-4, 4),
                textcoords="offset points", fontsize=6.3, color=INK,
                ha="right", va="bottom", linespacing=1.1)

    # one shared legend for both panels
    handles = [Line2D([], [], color=INK, linewidth=1.7, label="all systems")]
    for s in SYS_ORDER:
        st = SYS_STYLE[s]
        k = int((hc.system == s).sum())
        handles.append(Line2D([], [], color=MUTED, linewidth=0.85, dashes=st["dash"],
                              marker=st["marker"], markersize=st["ms"],
                              markerfacecolor=st["mfc"], markeredgecolor=st["mec"],
                              markeredgewidth=0.6,
                              label=f"{s} ({k} at high coverage)"))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.115),
               ncol=3, frameon=False, handlelength=3.0, columnspacing=1.6,
               labelspacing=0.3)

    fig.text(0.5, -0.24,
             "Panel B plots every evaluable record against min(C, S); coverage improves "
             "to the left, while ATE spans several orders of magnitude.\nExact coverage cannot be placed "
             "on a logarithmic axis and is drawn in the separate band at the far left. "
             f"{n_elig} records meet the\n0.99 threshold and {n_elig_1m} of those exceed 1 m. "
             f"{n_off} records above 10$^4$ m lie outside the drawn range and are retained in "
             "every estimate.",
             ha="center", fontsize=6.5, color=MUTED, style="italic")
    fig.tight_layout()
    save(fig, "Figure2_coverage_and_ATE")


# ------------------------------------------------------------------ Figure 3
def figure3(det):
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.2),
                             gridspec_kw={"width_ratios": [1.0, 1.15]})

    # ---- Panel A: ECDF of within-triplet max/min ratio
    ax = axes[0]
    spec = [("ORB-SLAM3", "ate_ratio", INK, (None, None), 1.6, "ORB-SLAM3, ATE"),
            ("ORB-SLAM3", "rte_ratio", INK, (3, 1.6), 1.0, "ORB-SLAM3, RTE"),
            ("OKVIS2", "ate_ratio", MUTED, (None, None), 1.6, "OKVIS2, ATE"),
            ("OKVIS2", "rte_ratio", MUTED, (3, 1.6), 1.0, "OKVIS2, RTE")]
    for sysname, col, colour, dash, lw, lab in spec:
        sub = det[det.system == sysname]
        x, y = ecdf(sub[col])
        kw = dict(where="post", color=colour, linewidth=lw, label=lab)
        if dash[0] is not None:
            kw["dashes"] = dash
        ax.step(x, y, **kw)

    ax.set_xscale("log")
    ax.set_xlim(1, 4e3)
    ax.set_ylim(0, 104)
    ax.set_xlabel("Within-triplet max/min ratio, log scale")
    ax.set_ylabel("Cumulative percentage of triplets")
    ax.set_title("A  Repeated-run variation", loc="left")
    ax.grid(True, which="major", color=GRID, linewidth=0.4)
    ax.axhline(90, color=REF, linewidth=0.8, linestyle="--", dashes=(4, 3), zorder=1)
    ax.text(3.5e3, 91, "90th percentile", fontsize=6.4, color=MUTED,
            va="bottom", ha="right")
    for sysname, col, marker, off in (("OKVIS2", "ate_ratio", "s", (6, -12)),
                                      ("ORB-SLAM3", "ate_ratio", "D", (6, -12))):
        v = float(np.percentile(det[det.system == sysname][col], 90))
        ax.plot([v], [90], marker=marker, markersize=4.4, color=INK,
                markerfacecolor="white", markeredgewidth=1.1, zorder=6)
        ax.annotate(f"{v:.2f}", (v, 90), textcoords="offset points", xytext=off,
                    fontsize=6.8, color=INK,
                    ha="right" if off[0] < 0 else "left")
    ax.legend(loc="lower right", frameon=False, handlelength=2.6, labelspacing=0.28)

    # ---- Panel B: only the threshold-crossing triplets
    ax = axes[1]
    cr = det[det.cross1 | det.cross10].copy()
    cr["mid"] = np.sqrt(cr.ate_min * cr.ate_max)
    cr = cr.sort_values(["system", "mid"], ascending=[False, True]).reset_index(drop=True)

    for i, r in cr.iterrows():
        mk, mfc = ("D", INK) if r.cross10 else ("s", "#bdbdbd")
        ax.hlines(i, r.ate_min, r.ate_max, color=MUTED, linewidth=1.0, zorder=1)
        ax.plot([r.ate_run1, r.ate_run2, r.ate_run3], [i] * 3, linestyle="none",
                marker=mk, markersize=4.4, markerfacecolor=mfc, markeredgecolor=INK,
                markeredgewidth=0.8, zorder=3)

    ax.set_xscale("log")
    ax.set_yticks(range(len(cr)))
    ax.set_yticklabels(cr.sequence, fontsize=6.6)
    ax.set_ylim(-0.8, len(cr) - 0.2)
    ax.set_xlim(0.08, 5e3)
    ax.set_xlabel("Absolute trajectory error [m], log scale")
    ax.set_title(f"B  Triplets crossing a threshold ({len(cr)} of {len(det)})", loc="left")
    ax.grid(True, which="major", axis="x", color=GRID, linewidth=0.4, zorder=0)
    for xv, lab in ((1, "1 m"), (10, "10 m")):
        ax.axvline(xv, color=REF, linewidth=0.9, linestyle="--", dashes=(4, 3), zorder=2)
        ax.text(xv, len(cr) - 0.55, lab, fontsize=6.5, color=MUTED, ha="center", va="bottom")

    nswitch = int((cr.system == "ORB-SLAM3").sum())
    ax.plot([0.085, 0.4], [nswitch - 0.5] * 2, color=INK, linewidth=0.6,
            zorder=2, clip_on=False)
    ax.text(0.095, nswitch / 2 - 0.5, "ORB-SLAM3", fontsize=6.6, color=INK,
            rotation=90, va="center", ha="left")
    ax.text(0.095, nswitch + (len(cr) - nswitch) / 2 - 0.5, "OKVIS2", fontsize=6.6,
            color=INK, rotation=90, va="center", ha="left")

    ax.legend(handles=[
        Line2D([], [], linestyle="none", marker="s", markersize=4.4,
               markerfacecolor="#bdbdbd", markeredgecolor=INK, label="crosses 1 m"),
        Line2D([], [], linestyle="none", marker="D", markersize=4.4,
               markerfacecolor=INK, markeredgecolor=INK, label="crosses 10 m"),
        Line2D([], [], color=MUTED, linewidth=1.0, label="min–max span"),
    ], loc="lower right", frameon=False, handletextpad=0.5, labelspacing=0.3)

    fig.text(0.5, -0.07,
             "Each row in panel B represents one three-run sequence triplet under a fixed configuration, "
             "with every run at high coverage.\nThe full 122-triplet chart is Figure S1 in "
             "the supplement.",
             ha="center", fontsize=6.5, color=MUTED, style="italic")
    fig.tight_layout()
    save(fig, "Figure3_repeated_run_variation")


def figureS1(det):
    """The 122-row triplet chart from v4.0.0, now the supplementary figure.

    Reuses figure3() in figures.py rather than duplicating it, and saves under the
    supplementary name.
    """
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("figures_v1", os.path.join(here, "figures.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["figures_v1"] = mod
    spec.loader.exec_module(mod)
    mod.FIG = FIG
    mod.figure3(det)
    for ext in ("pdf", "png"):
        old = os.path.join(FIG, f"Figure3_repeated_run_ATE_ranges.{ext}")
        new = os.path.join(FIG, f"FigureS1_repeated_run_ATE_ranges.{ext}")
        if os.path.exists(old):
            os.replace(old, new)
    print("  wrote FigureS1_repeated_run_ATE_ranges.pdf / .png")


def main():
    import json
    rep = json.load(open(os.path.join(OUT, "analysis_report.json")))
    ev = pd.read_csv(os.path.join(OUT, "records_primary.csv"))
    ev["cov"] = ev[["completion", "success"]].min(axis=1)
    hc = ev[ev["cov"] >= 0.99].copy()
    det = pd.read_csv(os.path.join(OUT, "Supplement_repeated_triplet_details.csv"))

    exc = {"to_evaluable": 968 - int(rep["evaluable"]),
           "to_high_cov": int(rep["evaluable"]) - int(rep["primary_high_coverage"])}

    print(f"evaluable={len(ev)}  high-coverage={len(hc)}  triplets={len(det)}")
    figure1(rep, exc)
    figure2(ev, hc)
    figure3(det)
    figureS1(det)


if __name__ == "__main__":
    main()
