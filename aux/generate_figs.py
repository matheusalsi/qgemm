import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = "./"
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.size": 12,
    "font.family": "serif",
    "axes.labelsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.axisbelow": True,
    "figure.dpi": 120,
})

configs = ["INT8", "INT16", "INT4/acc32", "INT4/acc16"]
x = np.arange(len(configs))

# Consistent, colorblind-friendly (Okabe-Ito) colors per configuration
cfg_colors = {
    "INT8": "#6E6E6E",        # neutral gray = baseline
    "INT16": "#D55E00",       # vermillion
    "INT4/acc32": "#0072B2",  # blue
    "INT4/acc16": "#009E73",  # bluish green
}

def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(OUT, name + ".png"), bbox_inches="tight", dpi=200)
    plt.close(fig)

# ----------------------------------------------------------------------
# 1) AREA  (stacked, absolute, in mm^2)
# ----------------------------------------------------------------------
area = {
    "Mesh":            [0.4924, 0.9494, 0.2569, 0.2506],
    "Scratchpad SRAM": [1.6989, 1.7387, 1.6988, 1.6988],
    "Accumulator":     [0.5407, 0.5407, 0.5407, 0.5298],
    "Acc. scale":      [0.1283, 0.1340, 0.1251, 0.0823],
    "Acc. adders":     [0.0085, 0.0085, 0.0085, 0.0041],
    "Other":           [0.5510, 0.6432, 0.5222, 0.5039],
}
totals_area = [3.4198, 4.0145, 3.1522, 3.0695]
area_colors = {
    "Mesh":            "#D55E00",
    "Scratchpad SRAM": "#56B4E9",
    "Accumulator":     "#009E73",
    "Acc. scale":      "#E69F00",
    "Acc. adders":     "#CC79A7",
    "Other":           "#BBBBBB",
}
order = ["Mesh", "Scratchpad SRAM", "Accumulator", "Acc. scale", "Acc. adders", "Other"]

fig, ax = plt.subplots(figsize=(7.2, 4.7))
bottom = np.zeros(4)
for mod in order:
    vals = np.array(area[mod], float)
    ax.bar(x, vals, bottom=bottom, width=0.62, label=mod,
           color=area_colors[mod], edgecolor="white", linewidth=0.6)
    bottom += vals
for i in range(4):                      # label the mesh band (the precision-driven part)
    mv = area["Mesh"][i]
    ax.text(x[i], mv / 2, f"{mv:.2f}", ha="center", va="center",
            color="white", fontsize=9, fontweight="bold")
for i, t in enumerate(totals_area):     # total on top of each stack
    ax.text(x[i], t + 0.07, f"{t:.2f}", ha="center", va="bottom",
            fontsize=10, fontweight="bold", color="#222222")
ax.set_xticks(x); ax.set_xticklabels(configs)
ax.set_ylabel(r"Cell area (mm$^2$)")
ax.set_ylim(0, max(totals_area) * 1.13)
ax.grid(axis="y", alpha=0.3, linewidth=0.6)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=3, frameon=False)
save(fig, "res-area")

# ----------------------------------------------------------------------
# 2) POWER  (stacked, mW)
# ----------------------------------------------------------------------
power = {
    "Mesh":                 [48.2, 100.2, 23.4, 22.2],
    "Scratchpad subsystem": [35.0, 36.5, 33.6, 25.6],
    "Other":                [20.6, 20.2, 20.7, 20.6],
}
totals_power = [103.8, 156.9, 77.7, 68.4]
power_colors = {"Mesh": "#D55E00", "Scratchpad subsystem": "#56B4E9", "Other": "#BBBBBB"}
porder = ["Mesh", "Scratchpad subsystem", "Other"]

fig, ax = plt.subplots(figsize=(6.6, 4.5))
bottom = np.zeros(4)
for blk in porder:
    vals = np.array(power[blk], float)
    ax.bar(x, vals, bottom=bottom, width=0.6, label=blk,
           color=power_colors[blk], edgecolor="white", linewidth=0.6)
    bottom += vals
for i in range(4):
    mv = power["Mesh"][i]
    ax.text(x[i], mv / 2, f"{mv:.1f}", ha="center", va="center",
            color="white", fontsize=9, fontweight="bold")
for i, t in enumerate(totals_power):
    ax.text(x[i], t + 3, f"{t:.1f}", ha="center", va="bottom",
            fontsize=10, fontweight="bold", color="#222222")
ax.set_xticks(x); ax.set_xticklabels(configs)
ax.set_ylabel("Power (mW)")
ax.set_ylim(0, max(totals_power) * 1.15)
ax.grid(axis="y", alpha=0.3, linewidth=0.6)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=3, frameon=False)
save(fig, "res-power")

# ----------------------------------------------------------------------
# 3) THROUGHPUT  (normalized bars)
# ----------------------------------------------------------------------
thr = [1.000, 0.415, 1.072, 1.247]
fig, ax = plt.subplots(figsize=(6.6, 4.4))
ax.bar(x, thr, width=0.58, color=[cfg_colors[c] for c in configs],
       edgecolor="white", linewidth=0.6)
ax.axhline(1.0, color="#444444", linestyle="--", linewidth=1.0, zorder=3)
ax.text(1.0, 1.0 + 0.015, "INT8 baseline", ha="center", va="bottom",
        fontsize=9, color="#444444")
for i, v in enumerate(thr):
    ax.text(x[i], v + 0.025, f"{v:.2f}\u00d7", ha="center", va="bottom", fontsize=10)
ax.set_xticks(x); ax.set_xticklabels(configs)
ax.set_ylabel("Throughput (normalized to INT8)")
ax.set_ylim(0, 1.45)
ax.grid(axis="y", alpha=0.3, linewidth=0.6)
ax.text(0.015, 0.97, "higher is better", transform=ax.transAxes,
        ha="left", va="top", fontsize=9, color="#666666", style="italic")
save(fig, "res-throughput")

# ----------------------------------------------------------------------
# 4) ENERGY  (normalized bars)
# ----------------------------------------------------------------------
energy = [1.000, 2.549, 0.759, 0.597]
fig, ax = plt.subplots(figsize=(6.6, 4.4))
ax.bar(x, energy, width=0.58, color=[cfg_colors[c] for c in configs],
       edgecolor="white", linewidth=0.6)
ax.axhline(1.0, color="#444444", linestyle="--", linewidth=1.0, zorder=3)
ax.text(2.5, 1.0 + 0.025, "INT8 baseline", ha="center", va="bottom",
        fontsize=9, color="#444444")
for i, v in enumerate(energy):
    ax.text(x[i], v + 0.04, f"{v:.2f}\u00d7", ha="center", va="bottom", fontsize=10)
ax.set_xticks(x); ax.set_xticklabels(configs)
ax.set_ylabel("Energy per inference (normalized to INT8)")
ax.set_ylim(0, 2.85)
ax.grid(axis="y", alpha=0.3, linewidth=0.6)
ax.text(0.015, 0.97, "lower is better", transform=ax.transAxes,
        ha="left", va="top", fontsize=9, color="#666666", style="italic")
save(fig, "res-energy")

print("done:", sorted(os.listdir(OUT)))