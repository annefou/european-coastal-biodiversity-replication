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
# # 03 — Analysis
#
# Computes the headline statistic: the biodiversity-weighted fraction of
# Natura 2000 marine sites where the WAVERYS-vs-regional peak-Hs delta exceeds
# threshold X during the storm window. Per `docs/phase1-plan.md` § 3-4.
#
# **Per-site exposure metric:** spatial mean of grid cells inside the polygon
# at the temporal max (= peak Hs at the site during the storm window).
# Secondary metric: integrated wave action ∫ Hs² dt over the window.
#
# **Threshold X:** region-specific, derived from CMEMS QUID joint observational
# noise floors (`docs/phase1-plan.md` § A3). Headline = `0.4 m` rounded;
# sensitivity = region-specific `{xynthia: 0.46, xaver: 0.39, gloria: 0.41}`.
#
# **Biodiversity weight:** `w_site = log1p(n_annex1_habitats + n_annex2_species)`.
# Additive, not multiplicative: a multiplicative `habitats × species` collapses
# to zero whenever either count is zero, which zeroed 91% of bird SPAs (Special
# Protection Areas carry Annex II species but no Annex I habitat listing) — 31%
# of all sites, including a 298-species SPA. The additive form counts a site as
# long as it protects either habitats or species. `log1p` still damps the
# mega-biodiverse sites (Wadden Sea 100+; small islets 2–3). See
# `docs/phase1-plan.md` § 5.3 (decision revised 2026-05-24).
#
# **Verify before drafting nanopubs:** the FORRT Replication Study's
# Methodology field is drafted *from this code* — do not extrapolate. See
# `docs/verify-before-drafting.md`.

# %%
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import box

# np.trapz was renamed np.trapezoid in numpy 2.0; bind whichever exists.
_trapezoid = getattr(np, "trapezoid", None) or np.trapz

# %%
CLEAN_DIR = Path("../data/clean")
RESULTS_DIR = Path("../results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ACTIVE_STORMS = ["xynthia"]
ACTIVE_STORMS = ["xynthia", "xaver", "gloria"]

# Headline threshold (m, see § A3): one rounded value for the aggregated stat.
THRESHOLD_X_HEADLINE = 0.4
# Per-region thresholds (sqrt(RMSE_WAVERYS² + RMSE_regional²) from CMEMS QUIDs):
THRESHOLD_X_PER_REGION = {"xynthia": 0.46, "xaver": 0.39, "gloria": 0.41}


# %% [markdown]
# ## Per-site exposure extraction
#
# For each polygon: pick the grid cells whose centres fall inside the polygon,
# compute the temporal max of Hs over the storm window per cell, then take the
# spatial mean. Falls back to the nearest single cell if the polygon is too
# small to enclose any grid centre (typical for some <0.04° N2000 islets at
# WAVERYS 0.2° resolution).

# %%
def _grid_cells_in_polygon(
    ds: xr.Dataset, polygon
) -> tuple[np.ndarray, np.ndarray]:
    """Return (lat_idx, lon_idx) of grid cells whose centres fall in polygon.

    If none, return the single nearest-centre cell so the site is never
    silently dropped from the statistic.
    """
    lons = ds["longitude"].values
    lats = ds["latitude"].values
    minx, miny, maxx, maxy = polygon.bounds
    lon_in = np.where((lons >= minx) & (lons <= maxx))[0]
    lat_in = np.where((lats >= miny) & (lats <= maxy))[0]
    if len(lon_in) == 0 or len(lat_in) == 0:
        # Polygon falls between grid centres — nearest neighbour.
        cx, cy = polygon.centroid.x, polygon.centroid.y
        return (
            np.array([int(np.argmin(np.abs(lats - cy)))]),
            np.array([int(np.argmin(np.abs(lons - cx)))]),
        )
    # Vectorised point-in-polygon check against the candidate centres.
    lo_grid, la_grid = np.meshgrid(lons[lon_in], lats[lat_in])
    pts = gpd.GeoSeries(gpd.points_from_xy(lo_grid.ravel(), la_grid.ravel()))
    inside = pts.within(polygon).values.reshape(la_grid.shape)
    if not inside.any():
        cx, cy = polygon.centroid.x, polygon.centroid.y
        return (
            np.array([int(np.argmin(np.abs(lats - cy)))]),
            np.array([int(np.argmin(np.abs(lons - cx)))]),
        )
    li, oi = np.where(inside)
    return lat_in[li], lon_in[oi]


def site_metrics(ds: xr.Dataset, hs_var: str, polygon) -> tuple[float, float]:
    """Return (peak_hs, integrated_wave_action) for a polygon over the window.

    peak_hs: spatial mean over polygon cells, at the cell-wise temporal max.
    integrated_wave_action: time-integrated ∫ Hs² dt (units: m² · h),
    aggregated as the spatial mean of per-cell integrals.
    """
    lat_idx, lon_idx = _grid_cells_in_polygon(ds, polygon)
    hs = ds[hs_var].isel(latitude=lat_idx, longitude=lon_idx)
    peak_per_cell = hs.max(dim="time")
    peak_hs = float(peak_per_cell.mean().values)

    # Convert time to hours since window start for the integral.
    t = hs["time"].values.astype("datetime64[s]").astype("float64")
    dt_hours = (t - t[0]) / 3600.0
    hs_squared = hs ** 2
    integrated_per_cell = _trapezoid(hs_squared.values, x=dt_hours, axis=0)
    iwa = float(np.mean(integrated_per_cell))
    return peak_hs, iwa


# %% [markdown]
# ## Per-storm loop

# %%
per_site_rows: list[dict] = []
headline_rows: list[dict] = []

for storm_key in ACTIVE_STORMS:
    print(f"\n--- {storm_key} ---")
    aligned = xr.open_dataset(CLEAN_DIR / f"{storm_key}_aligned.nc")
    sites = gpd.read_parquet(CLEAN_DIR / f"{storm_key}_n2000_sites.parquet")

    site_col = next(c for c in sites.columns if c.upper() == "SITECODE")
    threshold_region = THRESHOLD_X_PER_REGION[storm_key]

    for _, site in sites.iterrows():
        wpeak, wiwa = site_metrics(aligned, "waverys_hs", site.geometry)
        rpeak, riwa = site_metrics(aligned, "regional_hs", site.geometry)
        delta_hs = rpeak - wpeak
        weight = float(
            np.log1p(site["n_annex1_habitats"] + site["n_annex2_species"])
        )
        per_site_rows.append(
            {
                "storm": storm_key,
                "site_code": site[site_col],
                "n_annex1_habitats": int(site["n_annex1_habitats"]),
                "n_annex2_species": int(site["n_annex2_species"]),
                "weight": weight,
                "peak_hs_waverys": wpeak,
                "peak_hs_regional": rpeak,
                "delta_hs": delta_hs,
                "abs_delta_hs": abs(delta_hs),
                "iwa_waverys": wiwa,
                "iwa_regional": riwa,
                "exceeds_X_headline": abs(delta_hs) > THRESHOLD_X_HEADLINE,
                "exceeds_X_regional": abs(delta_hs) > threshold_region,
            }
        )

    # Per-storm headline = weighted fraction.
    df = pd.DataFrame([r for r in per_site_rows if r["storm"] == storm_key])
    total_w = df["weight"].sum()
    if total_w == 0:
        weighted_frac_headline = float("nan")
        weighted_frac_region = float("nan")
    else:
        weighted_frac_headline = float(
            (df.loc[df["exceeds_X_headline"], "weight"].sum()) / total_w
        )
        weighted_frac_region = float(
            (df.loc[df["exceeds_X_regional"], "weight"].sum()) / total_w
        )
    headline_rows.append(
        {
            "storm": storm_key,
            "n_sites": len(df),
            "threshold_X_headline_m": THRESHOLD_X_HEADLINE,
            "weighted_frac_exceeds_X_headline": weighted_frac_headline,
            "threshold_X_region_m": threshold_region,
            "weighted_frac_exceeds_X_region": weighted_frac_region,
            "median_abs_delta_hs": float(df["abs_delta_hs"].median()),
            "max_abs_delta_hs": float(df["abs_delta_hs"].max()),
        }
    )
    print(
        f"  n_sites={len(df)}  weighted_frac(>{THRESHOLD_X_HEADLINE} m)="
        f"{weighted_frac_headline:.3f}  median|Δ|={df['abs_delta_hs'].median():.3f} m"
    )

# Aggregated row across all active storms — biodiversity-weighted across sites.
df_all = pd.DataFrame(per_site_rows)
if len(df_all):
    total_w = df_all["weight"].sum()
    headline_rows.append(
        {
            "storm": "aggregated",
            "n_sites": len(df_all),
            "threshold_X_headline_m": THRESHOLD_X_HEADLINE,
            "weighted_frac_exceeds_X_headline": float(
                df_all.loc[df_all["exceeds_X_headline"], "weight"].sum() / total_w
            ),
            "threshold_X_region_m": None,
            "weighted_frac_exceeds_X_region": float(
                df_all.loc[df_all["exceeds_X_regional"], "weight"].sum() / total_w
            ),
            "median_abs_delta_hs": float(df_all["abs_delta_hs"].median()),
            "max_abs_delta_hs": float(df_all["abs_delta_hs"].max()),
        }
    )

# %% [markdown]
# ## Persist results

# %%
pd.DataFrame(per_site_rows).to_csv(RESULTS_DIR / "per_site_delta.csv", index=False)
pd.DataFrame(headline_rows).to_csv(RESULTS_DIR / "headline_stats.csv", index=False)
# `summary.csv` keeps Snakefile + Jupyter Book TOC stable.
pd.DataFrame(headline_rows).to_csv(RESULTS_DIR / "summary.csv", index=False)

print("\n--- headline_stats.csv ---")
print(pd.DataFrame(headline_rows).to_string(index=False))
