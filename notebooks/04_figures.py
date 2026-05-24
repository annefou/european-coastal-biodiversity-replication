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
per_site = pd.read_csv(RESULTS_DIR / "per_site_delta.csv")

n_panels = len(ACTIVE_STORMS)
fig, axes = plt.subplots(
    1, n_panels,
    figsize=(7 * n_panels, 6),
    subplot_kw={"projection": ccrs.PlateCarree()},
    squeeze=False,
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
    cb = fig.colorbar(pcm, ax=ax, shrink=0.7, label="Peak Hs regional (m)")
    cs = peak_waverys.plot.contour(
        ax=ax, transform=ccrs.PlateCarree(),
        colors="white", linewidths=0.6, alpha=0.9, levels=6,
    )
    ax.clabel(cs, fontsize=7, fmt="%.1f")

    sites = gpd.read_file(CLEAN_DIR / f"{storm}_n2000_sites.geojson")
    site_col = next(c for c in sites.columns if c.upper() == "SITECODE")
    df = per_site[per_site["storm"] == storm].set_index("site_code")
    sites = sites.merge(df, left_on=site_col, right_index=True, how="left")
    # Diverging fill = signed delta (regional - waverys); edge ∝ biodiversity weight.
    vmax = max(0.5, float(sites["delta_hs"].abs().max() if len(sites) else 0.5))
    sites.plot(
        ax=ax, transform=ccrs.PlateCarree(),
        column="delta_hs", cmap="RdBu_r", vmin=-vmax, vmax=vmax,
        edgecolor="black",
        linewidth=(sites["weight"].fillna(0) / max(1.0, sites["weight"].max()) * 1.5 + 0.3),
        alpha=0.7, legend=False,
    )

    ax.add_feature(cfeature.LAND, facecolor="#f3f0e8", zorder=1)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, zorder=2)
    # Frame to the wave bbox so cartopy doesn't auto-expand to far-offshore polygons.
    x0, x1, y0, y1 = STORM_BBOXES[storm]
    ax.set_extent([x0, x1, y0, y1], crs=ccrs.PlateCarree())
    ax.set_title(STORM_LABELS[storm], fontsize=10)
    ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)

fig.suptitle(
    "WAVERYS vs regional CMEMS peak Hs around Natura 2000 marine sites",
    fontsize=12, y=1.02,
)
fig.tight_layout()
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
ax.set_xlabel("Biodiversity weight  w = log1p(habitats × species)")
ax.set_ylabel("|Δ Hs|  (m)   regional − WAVERYS,  at storm-window peak")
ax.set_title("Biodiversity richness vs inter-product wave-height delta")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(FIGURES_DIR / "biodiversity_vs_delta.png", dpi=150, bbox_inches="tight")
plt.show()
