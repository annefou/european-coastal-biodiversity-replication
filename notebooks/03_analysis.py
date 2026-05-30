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
# **resolvable** Natura 2000 marine sites where the choice between WAVERYS and
# the regional product changes the attributed storm-wave exposure. Per
# `docs/phase1-plan.md` § 3-4.
#
# **Per-site exposure metric:** each product is sampled on its OWN native grid
# (WAVERYS 0.2°, regional fine) — peak Hs is the spatial mean of the wet cells
# inside the polygon at the storm-window temporal max. We do NOT regrid the
# regional down to WAVERYS: that would smooth away the nearshore difference and
# drop ~half the sites to coastal NaN. Three tiers result — both resolve
# (continuous delta), only one resolves (product choice decisive), neither
# resolves (out of scope, reported as coverage). See the sampling section.
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
# ## Per-site exposure extraction — native grid, three tiers
#
# Each product is sampled on its OWN native grid (WAVERYS 0.2°, regional fine):
# the per-site peak Hs is the spatial mean, over the storm window's temporal max,
# of the **wet** (non-NaN) cells whose centres fall inside the polygon. If no wet
# cell lies inside the polygon, we look one grid cell out (nearest wet cell) — so
# a site touching a wet cell is still sampled, but a site buried inside a single
# land-masked cell is NOT given a value pulled from far offshore.
#
# A site is **resolved** by a product if that product has a wet cell in/adjacent
# to the polygon. This yields three tiers:
#
# - **both** — both products resolve the site → continuous inter-product delta.
# - **regional_only** / **waverys_only** — only one product resolves it. This is
#   the product choice being *categorically decisive*: one product attributes a
#   wave field to the site, the other reports land / no estimate. (Almost always
#   `regional_only`: the fine regional resolves a coast the 0.2° WAVERYS sees as
#   land.) These count as "attribution differs".
# - **neither** — too small/sheltered for either basin-scale product → out of
#   scope; excluded from the denominator and reported as coverage.

# %%
def sample_native(peak: np.ndarray, lons: np.ndarray, lats: np.ndarray,
                  polygon) -> tuple[float, bool]:
    """Polygon-mean peak Hs over the product's own wet cells. Returns
    (hs, resolved).

    A product "resolves" a site only if the site's own location is wet in that
    product's grid — NO searching outward to nearest wet cells, which on the
    0.2° WAVERYS grid would pull open-ocean values from ~22 km offshore into
    sheltered coastal sites. Concretely:
      - if any grid-cell centre falls inside the polygon → mean of the wet ones;
      - else (sub-grid site) → the single cell that contains the polygon
        centroid, used only if it is wet.
    Returns resolved=False when the product places the site on land. That is the
    physically meaningful Tier-2 signal: the product cannot represent the site.
    """
    minx, miny, maxx, maxy = polygon.bounds
    li = np.where((lons >= minx) & (lons <= maxx))[0]
    la = np.where((lats >= miny) & (lats <= maxy))[0]
    if len(li) and len(la):
        sub = peak[np.ix_(la, li)]
        lo_grid, la_grid = np.meshgrid(lons[li], lats[la])
        inside = (
            gpd.GeoSeries(gpd.points_from_xy(lo_grid.ravel(), la_grid.ravel()))
            .within(polygon).values.reshape(sub.shape)
        )
        wet = sub[inside & np.isfinite(sub)]
        if wet.size:
            return float(wet.mean()), True
    # Sub-grid site: the single cell containing the centroid, used only if wet.
    cx, cy = polygon.centroid.x, polygon.centroid.y
    j = int(np.argmin(np.abs(lats - cy)))
    i = int(np.argmin(np.abs(lons - cx)))
    v = peak[j, i]
    return (float(v), True) if np.isfinite(v) else (float("nan"), False)


def peak_field(nc_path: Path, var: str):
    """Load a native product, return (peak_Hs_2d, lons, lats)."""
    ds = xr.open_dataset(nc_path)
    peak = ds[var].max(dim="time")
    return peak.values, ds["longitude"].values, ds["latitude"].values


# %% [markdown]
# ## Per-storm loop
#
# "Attribution differs" at a site means EITHER the products both resolve it and
# their peak-Hs delta exceeds threshold X, OR only one product resolves it (the
# product choice is categorically decisive). The headline is the
# biodiversity-weighted fraction of **resolvable** sites where attribution
# differs; sites neither product resolves are excluded and reported as coverage.

# %%
def _differs(tier: str, abs_delta: float, X: float) -> bool:
    if tier == "both":
        return abs_delta > X
    return tier in ("regional_only", "waverys_only")  # only one resolves → decisive


per_site_rows: list[dict] = []
headline_rows: list[dict] = []

for storm_key in ACTIVE_STORMS:
    print(f"\n--- {storm_key} ---")
    w_peak, w_lons, w_lats = peak_field(CLEAN_DIR / f"{storm_key}_waverys.nc", "waverys_hs")
    r_peak, r_lons, r_lats = peak_field(CLEAN_DIR / f"{storm_key}_regional.nc", "regional_hs")
    sites = gpd.read_parquet(CLEAN_DIR / f"{storm_key}_n2000_sites.parquet")
    site_col = next(c for c in sites.columns if c.upper() == "SITECODE")

    for _, site in sites.iterrows():
        whs, wres = sample_native(w_peak, w_lons, w_lats, site.geometry)
        rhs, rres = sample_native(r_peak, r_lons, r_lats, site.geometry)
        if wres and rres:
            tier, delta = "both", rhs - whs
        elif rres:
            tier, delta = "regional_only", float("nan")
        elif wres:
            tier, delta = "waverys_only", float("nan")
        else:
            tier, delta = "neither", float("nan")
        abs_delta = abs(delta)
        weight = float(np.log1p(site["n_annex1_habitats"] + site["n_annex2_species"]))
        per_site_rows.append(
            {
                "storm": storm_key,
                "site_code": site[site_col],
                "n_annex1_habitats": int(site["n_annex1_habitats"]),
                "n_annex2_species": int(site["n_annex2_species"]),
                "weight": weight,
                "tier": tier,
                "resolvable": tier != "neither",
                "peak_hs_waverys": whs,
                "peak_hs_regional": rhs,
                "delta_hs": delta,
                "abs_delta_hs": abs_delta,
                "differs_headline": _differs(tier, abs_delta, THRESHOLD_X_HEADLINE),
                "differs_region": _differs(tier, abs_delta, THRESHOLD_X_PER_REGION[storm_key]),
            }
        )


def _headline_row(df: pd.DataFrame, storm: str, threshold_region) -> dict:
    res = df[df["resolvable"]]
    w_res = res["weight"].sum()
    both = df[df["tier"] == "both"]
    tier_counts = df["tier"].value_counts().to_dict()
    return {
        "storm": storm,
        "n_sites": len(df),
        "n_resolvable": len(res),
        "n_tier_both": tier_counts.get("both", 0),
        "n_tier_regional_only": tier_counts.get("regional_only", 0),
        "n_tier_waverys_only": tier_counts.get("waverys_only", 0),
        "n_tier_neither": tier_counts.get("neither", 0),
        "threshold_X_headline_m": THRESHOLD_X_HEADLINE,
        "weighted_frac_differs_headline": (
            float(res.loc[res["differs_headline"], "weight"].sum() / w_res)
            if w_res else float("nan")
        ),
        "threshold_X_region_m": threshold_region,
        "weighted_frac_differs_region": (
            float(res.loc[res["differs_region"], "weight"].sum() / w_res)
            if w_res else float("nan")
        ),
        # Coverage: biodiversity-weighted fraction of sites that are resolvable.
        "weighted_coverage": (
            float(w_res / df["weight"].sum()) if df["weight"].sum() else float("nan")
        ),
        # Magnitude stats over Tier-1 (both-resolved) sites, where delta is defined.
        "median_abs_delta_hs_both": float(both["abs_delta_hs"].median()) if len(both) else float("nan"),
        "max_abs_delta_hs_both": float(both["abs_delta_hs"].max()) if len(both) else float("nan"),
    }


for storm_key in ACTIVE_STORMS:
    df = pd.DataFrame([r for r in per_site_rows if r["storm"] == storm_key])
    row = _headline_row(df, storm_key, THRESHOLD_X_PER_REGION[storm_key])
    headline_rows.append(row)
    print(
        f"  resolvable={row['n_resolvable']}/{row['n_sites']} "
        f"(both={row['n_tier_both']}, regional_only={row['n_tier_regional_only']}, "
        f"neither={row['n_tier_neither']})  "
        f"weighted_frac_differs(>{THRESHOLD_X_HEADLINE} m)="
        f"{row['weighted_frac_differs_headline']:.3f}"
    )

df_all = pd.DataFrame(per_site_rows)
if len(df_all):
    headline_rows.append(_headline_row(df_all, "aggregated", None))

# %% [markdown]
# ## Threshold-X sensitivity
#
# Over **resolvable** sites, how does the biodiversity-weighted "attribution
# differs" fraction vary with X? Only the both-resolved (Tier-1) contribution
# responds to X; the only-one-resolves (Tier-2) sites are decisive regardless of
# threshold, so they form a floor. A near-flat curve = a robust finding.

# %%
THRESHOLD_SWEEP = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
sensitivity_rows: list[dict] = []


def _frac_differs_at(df: pd.DataFrame, X: float) -> float:
    res = df[df["resolvable"]]
    w = res["weight"].sum()
    if not w:
        return float("nan")
    differs = res["tier"].isin(["regional_only", "waverys_only"]) | (
        (res["tier"] == "both") & (res["abs_delta_hs"] > X)
    )
    return float(res.loc[differs, "weight"].sum() / w)


for X in THRESHOLD_SWEEP:
    row = {"threshold_X_m": X}
    for storm_key in ACTIVE_STORMS:
        row[storm_key] = _frac_differs_at(df_all[df_all["storm"] == storm_key], X)
    row["aggregated"] = _frac_differs_at(df_all, X)
    sensitivity_rows.append(row)

# %% [markdown]
# ## Persist results

# %%
pd.DataFrame(per_site_rows).to_csv(RESULTS_DIR / "per_site_delta.csv", index=False)
pd.DataFrame(headline_rows).to_csv(RESULTS_DIR / "headline_stats.csv", index=False)
pd.DataFrame(sensitivity_rows).to_csv(RESULTS_DIR / "threshold_sensitivity.csv", index=False)
# `summary.csv` keeps Snakefile + Jupyter Book TOC stable.
pd.DataFrame(headline_rows).to_csv(RESULTS_DIR / "summary.csv", index=False)

print("\n--- headline_stats.csv ---")
print(pd.DataFrame(headline_rows).to_string(index=False))
print("\n--- threshold_sensitivity.csv ---")
print(pd.DataFrame(sensitivity_rows).to_string(index=False))
print("\n--- threshold_sensitivity.csv ---")
print(pd.DataFrame(sensitivity_rows).to_string(index=False))
