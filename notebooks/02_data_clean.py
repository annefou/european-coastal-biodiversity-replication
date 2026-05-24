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
# # 02 — Data clean
#
# Two data flows:
#
# 1. **Wave products.** For each active storm: open WAVERYS + regional CMEMS
#    NetCDFs from `01_data_download.py`, regrid regional → WAVERYS via bilinear
#    interpolation, drop the spin-up padding, write
#    `data/clean/<storm>_aligned.nc` (common-grid Hs pair) and
#    `data/clean/<storm>_regional_native.nc` (regional Hs on its native grid,
#    used by the spatial maps in `04_figures.py`).
# 2. **Natura 2000 sites.** Merge two EEA distributions: the spatial GeoPackage
#    (polygons, EPSG:3035) with the tabular CSVs (Standard Data Form — Annex I
#    habitats + Annex II species + marine flag). Reproject to WGS84, filter to
#    marine sites, clip per storm bbox, write
#    `data/clean/<storm>_n2000_sites.geojson` (small enough to ship beside the
#    aligned NetCDF, simple enough to read in 03 without spatial-DB tooling).
#
# **Why NetCDF and not `.npz`** — see `DOMAIN.md` § Data formats. Self-describing,
# CF-compliant, language-agnostic, the FORRT chain's audit trail expects it.

# %%
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

# %%
RAW_DIR = Path("../data/raw")
CLEAN_DIR = Path("../data/clean")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# Mirrors ACTIVE_STORMS in 01_data_download.py — keep these two in sync.
ACTIVE_STORMS = ["xynthia"]
# ACTIVE_STORMS = ["xynthia", "xaver", "gloria"]

# Drop the 24 h pre-storm spin-up padding before computing exposure metrics.
STORM_WINDOWS = {
    "xynthia": ("2010-02-26T00:00:00", "2010-03-01T23:59:59"),
    "xaver": ("2013-12-04T00:00:00", "2013-12-07T23:59:59"),
    "gloria": ("2020-01-19T00:00:00", "2020-01-23T23:59:59"),
}

# Two bbox families, decoupled on purpose:
#
# CORE_BBOXES — site SELECTION. The storm's landfall region; a Natura 2000 site
#   is "exposed to this storm" if it intersects the core box. Tight, so the
#   panel doesn't drag in sites the storm never reached (e.g. Iberian sites for
#   Xynthia).
# WAVE_BBOXES — wave-data COVERAGE + map frame (mirror 01_data_download.py).
#   Wider: the union bounds of the core-selected sites + margin, so every
#   selected site (including large offshore SACs) is fully covered by wave data.
#
# Invariant: WAVE_BBOXES ⊇ (union of geometries of sites selected by CORE_BBOXES).
# The coverage guard in the per-storm loop below verifies it at runtime.
CORE_BBOXES = {
    "xynthia": {"lon_min": -5.0, "lon_max": 0.0, "lat_min": 44.0, "lat_max": 48.5},
    "xaver":   {"lon_min":  2.0, "lon_max":  9.5, "lat_min": 51.0, "lat_max": 56.5},
    "gloria":  {"lon_min": -1.0, "lon_max":  5.0, "lat_min": 38.5, "lat_max": 43.5},
}
WAVE_BBOXES = {
    "xynthia": {"lon_min": -10.5, "lon_max": 0.0, "lat_min": 43.0, "lat_max": 49.5},
    "xaver":   {"lon_min":   1.5, "lon_max": 10.5, "lat_min": 50.5, "lat_max": 57.0},
    "gloria":  {"lon_min":  -2.75, "lon_max": 5.5, "lat_min": 37.0, "lat_max": 44.5},
}

# %% [markdown]
# ## Wave-product alignment
#
# WAVERYS (0.2°) is the common grid. The regional product (1/36° IBI for
# Xynthia, ~1.5 km NWS for Xaver, 1/24° MED for Gloria) is regridded onto
# WAVERYS via bilinear interpolation. Per `docs/phase1-plan.md` § 3, native
# regional resolution is preserved separately for the spatial maps in
# `04_figures.py`; the headline statistic uses the common-grid version.

# %%
def _try_xesmf_bilinear(src: xr.Dataset, target: xr.Dataset) -> xr.Dataset:
    """Bilinear regrid src→target via xesmf if installed, else xarray.interp.

    xesmf depends on the ESMF C library and may fail to import on some
    platforms; xarray.interp is the documented fallback (DOMAIN.md § pixi
    fallback). Bilinear-only, no conservative — adequate for inter-product
    comparison at site polygons.
    """
    try:
        import xesmf as xe
    except ImportError:
        return src.interp(
            longitude=target["longitude"], latitude=target["latitude"]
        )
    regridder = xe.Regridder(src, target, "bilinear", periodic=False)
    return regridder(src, keep_attrs=True)


def _trim_window(ds: xr.Dataset, t0: str, t1: str) -> xr.Dataset:
    """Slice on the dataset's time coordinate (CMEMS uses 'time')."""
    time_name = "time" if "time" in ds.coords else next(
        c for c in ds.coords if "time" in c.lower()
    )
    return ds.sel({time_name: slice(t0, t1)})


def _hs_var(ds: xr.Dataset) -> str:
    """CMEMS Hs is VHM0; defend against per-product capitalisation drift."""
    for cand in ("VHM0", "vhm0", "Hs", "hs"):
        if cand in ds.data_vars:
            return cand
    raise KeyError(
        f"No Hs-like variable found in dataset. Variables: {list(ds.data_vars)}"
    )


def align_storm(storm_key: str) -> Path:
    """WAVERYS + regional → common (WAVERYS) grid, trimmed to storm window."""
    waverys = xr.open_dataset(RAW_DIR / f"waverys_{storm_key}.nc")
    regional = xr.open_dataset(RAW_DIR / f"regional_{storm_key}.nc")

    t0, t1 = STORM_WINDOWS[storm_key]
    waverys = _trim_window(waverys, t0, t1)
    regional = _trim_window(regional, t0, t1)

    regional_on_waverys = _try_xesmf_bilinear(regional, waverys)

    waverys_hs_name = _hs_var(waverys)
    regional_hs_name = _hs_var(regional_on_waverys)
    aligned = xr.Dataset(
        {
            "waverys_hs": waverys[waverys_hs_name],
            "regional_hs": regional_on_waverys[regional_hs_name],
        },
        attrs={
            "title": f"Aligned WAVERYS + regional wave heights — {storm_key}",
            "storm": storm_key,
            "storm_window": f"{t0}/{t1}",
            "regridding": "regional → WAVERYS, bilinear",
        },
    )

    out = CLEAN_DIR / f"{storm_key}_aligned.nc"
    aligned.to_netcdf(out)
    # Preserve the native-resolution regional Hs separately — spatial maps use it.
    regional[[regional_hs_name]].rename(
        {regional_hs_name: "regional_hs_native"}
    ).to_netcdf(CLEAN_DIR / f"{storm_key}_regional_native.nc")
    print(f"  → {out.name}  ({out.stat().st_size / 1e6:.1f} MB)")
    return out


# %%
for storm_key in ACTIVE_STORMS:
    print(f"Aligning {storm_key}...")
    align_storm(storm_key)

# %% [markdown]
# ## Natura 2000 — extract two archives
#
# The tabular archive (`Natura2000_end2024.zip`) extracts to a directory whose
# `Natura2000_end2024_rev1_csv.zip` contains the actual CSVs we need
# (HABITATS, SPECIES, NATURA2000SITES). Extract both into `data/raw/`.
#
# The spatial archive (`Natura2000_end2024_spatial.zip`) holds the GeoPackage.
# It's pan-European and ~2.3 GB extracted — we read it with `bbox=` to keep
# memory usage modest.

# %%
def _extract_once(zip_path: Path, target_dir: Path, sentinel_glob: str) -> Path:
    """Extract `zip_path` into `target_dir` unless a sentinel file already exists.

    Repeated runs (notebook re-execution, Snakemake retries) shouldn't pay the
    extraction cost twice.
    """
    if target_dir.exists() and any(target_dir.rglob(sentinel_glob)):
        return target_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(target_dir)
    return target_dir


N2K_TAB_ZIP = RAW_DIR / "Natura2000_end2024.zip"
N2K_TAB_DIR = RAW_DIR / "Natura2000_end2024"
N2K_SPATIAL_ZIP = RAW_DIR / "Natura2000_end2024_spatial.zip"
N2K_SPATIAL_DIR = RAW_DIR / "Natura2000_end2024_spatial"

_extract_once(N2K_TAB_ZIP, N2K_TAB_DIR, "*_csv.zip")
_extract_once(N2K_SPATIAL_ZIP, N2K_SPATIAL_DIR, "*.gpkg")

# Tabular CSVs live in a nested zip — extract once into `csv/`.
inner_csv_zip = next(N2K_TAB_DIR.rglob("*_csv.zip"))
csv_dir = N2K_TAB_DIR / "csv"
if not csv_dir.exists() or not any(csv_dir.glob("*.csv")):
    csv_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(inner_csv_zip) as zf:
        zf.extractall(csv_dir)

# %% [markdown]
# ## Load EEA tabular tables
#
# Three tables join on `SITECODE`:
#
# - `NATURA2000SITES` — site-level attributes (SITETYPE, MARINE_AREA_PERCENTAGE,
#   AREAHA, COUNTRY_CODE, …).
# - `HABITATS` — one row per Annex I habitat per site. Count of rows where
#   `NON_PRESENCE_IN_SITE` is false ⇒ Annex I habitat count.
# - `SPECIES` — one row per Annex II species per site. Count of rows where
#   `NONPRESENCEINSITE` is false ⇒ Annex II species count.
#
# CSVs are UTF-8-BOM (`utf-8-sig`).

# %%
def _read_csv(name: str) -> pd.DataFrame:
    path = next(csv_dir.glob(f"*_{name}.csv"))
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)


sites_tab = _read_csv("NATURA2000SITES")
habitats = _read_csv("HABITATS")
species = _read_csv("SPECIES")

# Strip BOM from any column name that still has it (defensive).
for df in (sites_tab, habitats, species):
    df.columns = [c.lstrip("﻿") for c in df.columns]

# Counts per site — drop "documented as absent" rows where the column exists.
if "NON_PRESENCE_IN_SITE" in habitats.columns:
    h_present = habitats[habitats["NON_PRESENCE_IN_SITE"].fillna(False).astype(str).str.upper() != "TRUE"]
else:
    h_present = habitats
habitat_counts = h_present.groupby("SITECODE").size().rename("n_annex1_habitats")

if "NONPRESENCEINSITE" in species.columns:
    s_present = species[species["NONPRESENCEINSITE"].fillna(False).astype(str).str.upper() != "TRUE"]
else:
    s_present = species
species_counts = s_present.groupby("SITECODE").size().rename("n_annex2_species")

# Marine flag — End-2024 schema uses MARINE_AREA_PERCENTAGE.
marine_pct_col = next(
    (c for c in sites_tab.columns if c.upper() == "MARINE_AREA_PERCENTAGE"),
    None,
)
if marine_pct_col is None:
    raise KeyError(
        "Expected MARINE_AREA_PERCENTAGE column in NATURA2000SITES.csv; "
        f"got columns: {list(sites_tab.columns)[:25]}…"
    )

marine_sites = (
    sites_tab[sites_tab[marine_pct_col].fillna(0) > 0]
    [["SITECODE", "SITETYPE", marine_pct_col, "COUNTRY_CODE"]]
    .merge(habitat_counts, on="SITECODE", how="left")
    .merge(species_counts, on="SITECODE", how="left")
    .fillna({"n_annex1_habitats": 0, "n_annex2_species": 0})
    .assign(
        n_annex1_habitats=lambda d: d["n_annex1_habitats"].astype(int),
        n_annex2_species=lambda d: d["n_annex2_species"].astype(int),
    )
)
print(
    f"Marine sites (EU-wide): {len(marine_sites):,} of {len(sites_tab):,} total. "
    f"median habitats={int(marine_sites['n_annex1_habitats'].median())}, "
    f"median species={int(marine_sites['n_annex2_species'].median())}"
)

# %% [markdown]
# ## Load + reproject spatial GeoPackage
#
# EU-wide polygons in EPSG:3035 (LAEA Europe), layer `NaturaSite_polygon`. The
# GPKG driver ignores pyogrio's `bbox_crs`, so we reproject each storm's WGS84
# bbox to EPSG:3035 ourselves and pass the bbox in native units — this keeps
# memory modest (only the storm-region polygons are read, not all 27k). We
# read only SITECODE + geometry from the polygon layer; every other attribute
# (SITETYPE, marine flag, biodiversity counts) comes from the tabular merge,
# which avoids column collisions.

# %%
from shapely.geometry import box  # noqa: E402

N2K_POLYGON_LAYER = "NaturaSite_polygon"
N2K_NATIVE_CRS = "EPSG:3035"

n2k_gpkg = next(
    (p for p in N2K_SPATIAL_DIR.rglob("*.gpkg")), None
)
if n2k_gpkg is None:
    raise FileNotFoundError(
        f"No .gpkg under {N2K_SPATIAL_DIR}. Inspect the extracted directory tree."
    )
print(f"Using polygons: {n2k_gpkg.relative_to(RAW_DIR)} (layer {N2K_POLYGON_LAYER})")


def _bbox_in_native(bb: dict) -> tuple[float, float, float, float]:
    """Reproject a WGS84 lon/lat bbox to the GPKG's native CRS bounds."""
    wgs = gpd.GeoSeries(
        [box(bb["lon_min"], bb["lat_min"], bb["lon_max"], bb["lat_max"])],
        crs="EPSG:4326",
    )
    return tuple(wgs.to_crs(N2K_NATIVE_CRS).total_bounds)


def _per_storm_sites(storm_key: str) -> gpd.GeoDataFrame:
    """Marine sites intersecting the storm CORE region, with SDF counts."""
    native_bbox = _bbox_in_native(CORE_BBOXES[storm_key])
    polys = gpd.read_file(
        n2k_gpkg,
        layer=N2K_POLYGON_LAYER,
        bbox=native_bbox,
        columns=["SITECODE"],  # geometry comes implicitly; drop colliding attrs
    )
    site_col = next(c for c in polys.columns if c.upper() == "SITECODE")
    polys = polys.rename(columns={site_col: "SITECODE"})[["SITECODE", "geometry"]]
    polys = polys.to_crs("EPSG:4326")
    # Inner join keeps only marine sites (marine_sites is the marine subset).
    return polys.merge(marine_sites, on="SITECODE", how="inner")


for storm_key in ACTIVE_STORMS:
    storm_sites = _per_storm_sites(storm_key)
    # Coverage guard: every core-selected site must fall inside the WAVE bbox,
    # else its per-site Hs would be computed from a clipped polygon
    # (under-sampled). If this fires, widen WAVE_BBOXES (here + in 01).
    bb = WAVE_BBOXES[storm_key]
    bbox_poly = box(bb["lon_min"], bb["lat_min"], bb["lon_max"], bb["lat_max"])
    outside = ~storm_sites.geometry.within(bbox_poly)
    if outside.any():
        codes = storm_sites.loc[outside, "SITECODE"].tolist()
        print(
            f"  WARNING {storm_key}: {outside.sum()} site(s) extend beyond the "
            f"wave bbox and will be under-sampled: {codes[:8]}"
            f"{'…' if len(codes) > 8 else ''}. Widen WAVE_BBOXES in 01+02."
        )
    out = CLEAN_DIR / f"{storm_key}_n2000_sites.geojson"
    storm_sites[
        ["SITECODE", "SITETYPE", "COUNTRY_CODE",
         "n_annex1_habitats", "n_annex2_species", "geometry"]
    ].to_file(out, driver="GeoJSON")
    print(
        f"  {storm_key}: {len(storm_sites):,} marine sites in bbox "
        f"(median habitats={int(np.median(storm_sites['n_annex1_habitats']))}, "
        f"median species={int(np.median(storm_sites['n_annex2_species']))}) → {out.name}"
    )

print("\n02_data_clean done.")
