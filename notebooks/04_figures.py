# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 04 — Figures
#
# Three figures, all saved as PNG (display) and also published inline (so
# MyST renders them in the Jupyter Book — `docs/cicd-conventions.md`):
#
# 1. **Regional storm-panel map** — one panel per active storm. WAVERYS peak
#    Hs as background contours, regional peak Hs colored on its native grid,
#    Natura 2000 marine polygons overlaid with fill = `delta_hs` (diverging
#    colormap) and edge-weight ∝ biodiversity weight.
# 2. **Headline bar chart** — weighted fraction of sites exceeding threshold X
#    per storm + aggregated.
# 3. **Biodiversity vs delta scatter** — diagnostic: are bio-rich sites
#    systematically more affected by the inter-product choice?
#
# **Inline display rule** (`DOMAIN.md`): always `plt.show()` after
# `fig.savefig()`. Never set `matplotlib.use('Agg')` — it suppresses inline
# rendering, which silently breaks the Jupyter Book build.

# %%
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

plt.style.use("seaborn-v0_8-whitegrid")

# %%
CLEAN_DIR = Path("../data/clean")
RESULTS_DIR = Path("../results")
FIGURES_DIR = Path("../figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ACTIVE_STORMS = ["xynthia"]
ACTIVE_STORMS = ["xynthia", "xaver", "gloria"]

STORM_LABELS = {
    "xynthia": "Xynthia (French Atlantic, Feb 2010 — IBI)",
    "xaver": "Xaver (North Sea, Dec 2013 — NWS)",
    "gloria": "Gloria (NW Mediterranean, Jan 2020 — MED)",
}

# Wave bbox per storm (mirror 01/02) — used to frame each map panel so cartopy
# doesn't auto-expand to fit far-offshore polygons.
STORM_BBOXES = {
    "xynthia": (-10.5, 0.0, 43.0, 49.5),
    "xaver":   (1.5, 10.5, 50.5, 57.0),
    "gloria":  (-2.75, 5.5, 37.0, 44.5),
}

# %% [markdown]
# ## Figure 1 — regional storm-panel map

# %%
import matplotlib as mpl  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

per_site = pd.read_csv(RESULTS_DIR / "per_site_delta.csv")

# Shared scales across panels so the polygons are comparable storm-to-storm:
# - delta fill: symmetric diverging, capped at the 95th percentile of |delta|
#   (extend='both' flags the few larger outliers, e.g. the Xaver 4.9 m site).
# - edge width: normalised by the global max biodiversity weight.
DELTA_VMAX = float(np.ceil(np.nanpercentile(per_site["abs_delta_hs"], 95) * 2) / 2)
WEIGHT_MAX = float(max(1.0, per_site["weight"].max()))
delta_norm = mpl.colors.Normalize(vmin=-DELTA_VMAX, vmax=DELTA_VMAX)


def _edge_lw(weights):
    return weights.fillna(0) / WEIGHT_MAX * 2.0 + 0.3


n_panels = len(ACTIVE_STORMS)
fig, axes = plt.subplots(
    1, n_panels,
    figsize=(7 * n_panels, 6.5),
    subplot_kw={"projection": ccrs.PlateCarree()},
    squeeze=False,
    layout="constrained",  # behaves with cartopy GeoAxes where tight_layout does not
)
axes = axes.ravel()

for ax, storm in zip(axes, ACTIVE_STORMS):
    aligned = xr.open_dataset(CLEAN_DIR / f"{storm}_aligned.nc")
    regional_native = xr.open_dataset(CLEAN_DIR / f"{storm}_regional_native.nc")

    peak_waverys = aligned["waverys_hs"].max(dim="time")
    peak_regional = regional_native["regional_hs_native"].max(dim="time")

    pcm = peak_regional.plot.pcolormesh(
        ax=ax, transform=ccrs.PlateCarree(),
        cmap="viridis", add_colorbar=False, alpha=0.85,
    )
    fig.colorbar(pcm, ax=ax, shrink=0.6, label="Peak Hs regional (m)")
    cs = peak_waverys.plot.contour(
        ax=ax, transform=ccrs.PlateCarree(),
        colors="white", linewidths=0.6, alpha=0.9, levels=6,
    )
    ax.clabel(cs, fontsize=7, fmt="%.1f")

    sites = gpd.read_parquet(CLEAN_DIR / f"{storm}_n2000_sites.parquet")
    site_col = next(c for c in sites.columns if c.upper() == "SITECODE")
    df = per_site[per_site["storm"] == storm].set_index("site_code")
    sites = sites.merge(df, left_on=site_col, right_index=True, how="left")
    # Polygon fill = signed Hs delta (regional − WAVERYS); edge thickness ∝
    # biodiversity weight. Both scales are shared across panels (see above).
    sites.plot(
        ax=ax, transform=ccrs.PlateCarree(),
        column="delta_hs", cmap="RdBu_r", norm=delta_norm,
        edgecolor="black", linewidth=_edge_lw(sites["weight"]),
        alpha=0.75, legend=False,
    )

    ax.add_feature(cfeature.LAND, facecolor="#f3f0e8", zorder=1)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, zorder=2)
    # Frame to the wave bbox so cartopy doesn't auto-expand to far-offshore polygons.
    x0, x1, y0, y1 = STORM_BBOXES[storm]
    ax.set_extent([x0, x1, y0, y1], crs=ccrs.PlateCarree())
    ax.set_title(STORM_LABELS[storm], fontsize=10)
    ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)

# Shared diverging colorbar for the polygon delta fill — this is the headline
# quantity, so it gets its own scale spanning all three panels.
delta_sm = mpl.cm.ScalarMappable(norm=delta_norm, cmap="RdBu_r")
cbar = fig.colorbar(
    delta_sm, ax=axes, orientation="horizontal",
    fraction=0.04, pad=0.06, extend="both", aspect=40,
)
cbar.set_label("Natura 2000 site fill: Hs delta, regional − WAVERYS (m)")

# Proxy legend for the edge-width = biodiversity-weight encoding.
legend_weights = [1.0, WEIGHT_MAX / 2, WEIGHT_MAX]
handles = [
    Line2D([0], [0], color="black", lw=_edge_lw(pd.Series([w])).iloc[0],
           label=f"w ≈ {w:.1f}")
    for w in legend_weights
]
axes[-1].legend(
    handles=handles, title="Site edge: biodiversity\nweight log1p(hab.+sp.)",
    loc="lower right", fontsize=7, title_fontsize=7, framealpha=0.9,
)

fig.suptitle(
    "WAVERYS vs regional CMEMS peak Hs around Natura 2000 marine sites",
    fontsize=13,
)
fig.savefig(FIGURES_DIR / "main_result.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Figure 2 — headline bar chart

# %%
headline = pd.read_csv(RESULTS_DIR / "headline_stats.csv")
fig, ax = plt.subplots(figsize=(7, 4.5))
colors = ["#2b6cb0" if s != "aggregated" else "#c05621" for s in headline["storm"]]
ax.bar(
    headline["storm"],
    headline["weighted_frac_exceeds_X_headline"],
    color=colors,
)
threshold_str = (
    headline.loc[0, "threshold_X_headline_m"]
    if len(headline) else 0.4
)
ax.set_ylabel(f"Biodiversity-weighted fraction\n|Δ Hs| > {threshold_str} m")
ax.set_title(
    "Inter-product wave-height delta at Natura 2000 marine sites\n"
    "(WAVERYS global vs CMEMS regional)"
)
ax.set_ylim(0, 1)
for i, row in headline.iterrows():
    ax.text(
        i, row["weighted_frac_exceeds_X_headline"] + 0.02,
        f"n={row['n_sites']}", ha="center", fontsize=8,
    )
fig.tight_layout()
fig.savefig(FIGURES_DIR / "headline_stats_bars.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Figure 3 — biodiversity vs delta scatter (diagnostic)

# %%
fig, ax = plt.subplots(figsize=(6.5, 5))
for storm, sub in per_site.groupby("storm"):
    ax.scatter(
        sub["weight"], sub["abs_delta_hs"],
        label=STORM_LABELS.get(storm, storm), alpha=0.7, s=22,
    )
ax.axhline(0.4, linestyle="--", color="gray", linewidth=0.8, label="X = 0.4 m")
ax.set_xlabel("Biodiversity weight  w = log1p(habitats + species)")
ax.set_ylabel("|Δ Hs|  (m)   regional − WAVERYS,  at storm-window peak")
ax.set_title("Biodiversity richness vs inter-product wave-height delta")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(FIGURES_DIR / "biodiversity_vs_delta.png", dpi=150, bbox_inches="tight")
plt.show()
