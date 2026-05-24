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
# # 01 — Data download
#
# Fetches all input data for the European coastal biodiversity replication.
# Three storms × two wave products (WAVERYS global + matching regional CMEMS),
# plus the Natura 2000 N2K dataset (polygons + Standard Data Form).
#
# **Phase 2 status (2026-05-23):** Xynthia (Feb 2010, IBI) implemented and
# tested first as the smallest window. Xaver (Dec 2013, NWS) and Gloria
# (Jan 2020, MED) are configured below and will be enabled once Xynthia
# round-trips end-to-end through `02_data_clean.py` and `03_analysis.py`.
#
# **Credentials.** `copernicusmarine` reads
# `~/.copernicusmarine/.copernicusmarine-credentials`
# (INI file: `[credentials]\nusername=...\npassword=...`). In CI, the file is
# created from the `COPERNICUS_CREDENTIALS_BASE64` secret. See `DOMAIN.md`
# § Copernicus credentials in CI.

# %%
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import copernicusmarine
import requests

# %%
RAW_DIR = Path("../data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

CMEMS_CREDS = Path.home() / ".copernicusmarine" / ".copernicusmarine-credentials"
if not CMEMS_CREDS.exists():
    raise FileNotFoundError(
        f"CMEMS credentials not found at {CMEMS_CREDS}. "
        "See DOMAIN.md § Copernicus credentials. "
        "Locally: create the file as INI with [credentials]/username/password. "
        "In CI: the COPERNICUS_CREDENTIALS_BASE64 secret writes it."
    )

# %% [markdown]
# ## Storm panel configuration
#
# Each storm is (a) a time window padded 24 h pre-storm for spin-up consistency,
# (b) a bounding box that fully contains the affected Natura 2000 sites with
# coastal buffer, (c) the WAVERYS dataset ID + the matching regional product.
# Product IDs and coverage are verified in `docs/phase1-plan.md` § A1.

# %%
STORMS = {
    "xynthia": {
        "label": "Storm Xynthia (French Atlantic, 26 Feb – 1 Mar 2010)",
        # 24 h pre-storm padding for wave-model spin-up:
        "time_start": "2010-02-25T00:00:00",
        "time_end": "2010-03-01T23:59:59",
        # Wave bbox = union bounds of marine Natura 2000 sites in the French
        # Atlantic landfall region + margin. Widened west to -10.5°W so the
        # wave data fully covers the large offshore cetacean/seabird SACs
        # (which reach -10°W); otherwise their per-site Hs is under-sampled.
        "bbox": {"lon_min": -10.5, "lon_max": 0.0, "lat_min": 43.0, "lat_max": 49.5},
        "waverys_dataset": "cmems_mod_glo_wav_my_0.2deg_PT3H-i",
        "regional_dataset": "cmems_mod_ibi_wav_my_0.027deg_PT1H-i",
        "regional_label": "IBI MY (Atlantic-Iberian-Biscay) 1/36° hourly",
    },
    "xaver": {
        "label": "Storm Xaver (North Sea, 4 – 7 Dec 2013)",
        "time_start": "2013-12-03T00:00:00",
        "time_end": "2013-12-07T23:59:59",
        # Wave bbox = union bounds of marine Natura 2000 sites in the southern
        # + central North Sea + margin — Wadden Sea (DE/NL/DK trinational),
        # German Bight, Doggerbank southern margin. Sites reach 10°E / 56.8°N.
        "bbox": {"lon_min": 1.5, "lon_max": 10.5, "lat_min": 50.5, "lat_max": 57.0},
        "waverys_dataset": "cmems_mod_glo_wav_my_0.2deg_PT3H-i",
        "regional_dataset": "cmems_mod_nws_wav_my_0.027deg-0.014deg_PT1H-i",
        "regional_label": "NWS reanalysis WAV 004_015 ~1.5 km hourly",
    },
    "gloria": {
        "label": "Storm Gloria (NW Mediterranean, 19 – 23 Jan 2020)",
        "time_start": "2020-01-18T00:00:00",
        "time_end": "2020-01-23T23:59:59",
        # Wave bbox = union bounds of marine Natura 2000 sites in the NW
        # Mediterranean landfall region + margin — Ebro Delta SAC, Balearic
        # margin, Gulf of Lion fringe. Sites span -2.38°W (Alboran approach)
        # to 5.29°E and 37.6°N to 44.3°N. Gloria's wave field reached >8 m Hs
        # offshore Catalonia.
        "bbox": {"lon_min": -2.75, "lon_max": 5.5, "lat_min": 37.0, "lat_max": 44.5},
        "waverys_dataset": "cmems_mod_glo_wav_my_0.2deg_PT3H-i",
        "regional_dataset": "cmems_mod_med_wav_my_4.2km-2D_PT1H-i",
        "regional_label": "MED MY 1/24° hourly",
    },
}

# Wave variables we pull from every product. VHM0 is the headline statistic
# (significant wave height, Hs). VTPK + VMDR are auxiliary — kept for the
# spectral-context figures in 04_figures.py.
WAVE_VARIABLES = ["VHM0", "VTPK", "VMDR"]

# Which storms to actually fetch this run. Start with Xynthia only; uncomment
# the other two once the Xynthia round-trip is validated.
ACTIVE_STORMS = ["xynthia"]
# ACTIVE_STORMS = ["xynthia", "xaver", "gloria"]

# %% [markdown]
# ## Download helper

# %%
def _covers_bbox(nc_path: Path, bbox: dict, tol: float = 0.5) -> bool:
    """True if the cached NetCDF's lon/lat extent covers the requested bbox.

    `tol` (degrees) allows for the product grid being slightly coarser than the
    requested bbox edge — CMEMS snaps to grid cells, so the cached extent can be
    marginally inside the request without being "wrong".
    """
    try:
        import xarray as _xr
        with _xr.open_dataset(nc_path) as ds:
            lon = ds["longitude"]
            lat = ds["latitude"]
            return (
                float(lon.min()) <= bbox["lon_min"] + tol
                and float(lon.max()) >= bbox["lon_max"] - tol
                and float(lat.min()) <= bbox["lat_min"] + tol
                and float(lat.max()) >= bbox["lat_max"] - tol
            )
    except (OSError, KeyError, ValueError):
        return False  # unreadable / unexpected schema → re-download


def download_wave_product(
    dataset_id: str, storm_cfg: dict, out_path: Path, variables: list[str]
) -> Path:
    """Subset + download a CMEMS wave product to NetCDF.

    The CMEMS Marine Data Store handles spatial / temporal subsetting server-side
    via `copernicusmarine.subset`. Output is a NetCDF file in `data/raw/`.

    Fails loudly if the response is empty (most likely failure: regional
    product's temporal coverage doesn't reach the storm window — see
    docs/phase1-plan.md § A1, Storm Daniel was rejected partly to keep the
    panel inside well-validated coverage).
    """
    bbox = storm_cfg["bbox"]
    # Cache is keyed by filename only, so a cached file from a previous run with
    # a different bbox would silently persist. Validate that the cached extent
    # covers the requested bbox; re-download if it doesn't.
    if out_path.exists() and _covers_bbox(out_path, bbox):
        print(f"  cached: {out_path} ({out_path.stat().st_size / 1e6:.1f} MB)")
        return out_path

    copernicusmarine.subset(
        dataset_id=dataset_id,
        variables=variables,
        minimum_longitude=bbox["lon_min"],
        maximum_longitude=bbox["lon_max"],
        minimum_latitude=bbox["lat_min"],
        maximum_latitude=bbox["lat_max"],
        start_datetime=storm_cfg["time_start"],
        end_datetime=storm_cfg["time_end"],
        output_filename=out_path.name,
        output_directory=str(out_path.parent),
        overwrite=True,
    )
    if not out_path.exists() or out_path.stat().st_size < 1024:
        raise RuntimeError(
            f"Empty / missing download for {dataset_id} (storm {storm_cfg['label']}). "
            "Most likely cause: dataset temporal coverage does not reach the "
            "storm window. Check the CMEMS catalog for the product's date range."
        )
    return out_path


# %% [markdown]
# ## Fetch wave products per storm

# %%
sources: list[dict] = []

for storm_key in ACTIVE_STORMS:
    storm = STORMS[storm_key]
    print(f"\n{storm['label']}")
    print(f"  window: {storm['time_start']} → {storm['time_end']}")
    print(f"  bbox:   {storm['bbox']}")

    waverys_path = RAW_DIR / f"waverys_{storm_key}.nc"
    print(f"  WAVERYS → {waverys_path.name}")
    download_wave_product(
        storm["waverys_dataset"], storm, waverys_path, WAVE_VARIABLES
    )

    regional_path = RAW_DIR / f"regional_{storm_key}.nc"
    print(f"  {storm['regional_label']} → {regional_path.name}")
    download_wave_product(
        storm["regional_dataset"], storm, regional_path, WAVE_VARIABLES
    )

    sources.extend(
        [
            {
                "name": f"WAVERYS ({storm_key})",
                "dataset_id": storm["waverys_dataset"],
                "doi": "https://doi.org/10.48670/moi-00022",
                "license": "CMEMS Service Commitments (open, attribution required)",
                "accessed_on": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "local_path": str(waverys_path.relative_to(RAW_DIR.parent)),
            },
            {
                "name": f"{storm['regional_label']} ({storm_key})",
                "dataset_id": storm["regional_dataset"],
                "doi": None,  # filled per-product in CITATION.cff
                "license": "CMEMS Service Commitments (open, attribution required)",
                "accessed_on": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "local_path": str(regional_path.relative_to(RAW_DIR.parent)),
            },
        ]
    )

# %% [markdown]
# ## Natura 2000 N2K dataset (one-time, shared across storms)
#
# Two separate EEA distributions, both End-2024 (revision 01, published 2026):
#
# 1. **Tabular** — Standard Data Form (`.mdb` Access database + CSV zip).
#    Contains Annex I habitats and Annex II species per site code. ~500 MB.
# 2. **Vector (spatial)** — pan-European polygons in EPSG:3035 LAEA, 1:100k
#    generalisation (`.gpkg` inside a zip). ~2.3 GB.
#
# Both are needed: spatial gives the `geometry`; tabular gives the biodiversity
# counts. They join on `SITECODE`. The downloads are large but one-time and
# shared across all three storms (the bbox subsetting happens in
# `02_data_clean.py`).

# %%
N2K_DOWNLOADS = {
    "tabular": {
        "url": "https://sdi.eea.europa.eu/datashare/s/P6rmxbD6eyjCPmk/download",
        "local": RAW_DIR / "Natura2000_end2024.zip",
        "size_mb_estimate": 507,
        "metadata_page": "https://sdi.eea.europa.eu/data/d713bff7-0cdf-4f0d-acd1-dc3c63af237e",
        "dataset_id": "eea_t_natura2000_p_2024_v01_r01",
    },
    "spatial": {
        "url": "https://sdi.eea.europa.eu/datashare/s/mwzs9eNsJ9Sn4Q4/download",
        "local": RAW_DIR / "Natura2000_end2024_spatial.zip",
        "size_mb_estimate": 2300,
        "metadata_page": "https://sdi.eea.europa.eu/data/91357f39-7866-41ce-b447-43905c364ec8",
        "dataset_id": "eea_v_3035_100_k_natura2000_p_2024_v01_r00",
    },
}


def download_n2k(label: str, url: str, out_path: Path) -> Path:
    """Stream a Natura 2000 archive with periodic progress reporting."""
    if out_path.exists() and out_path.stat().st_size > 1024:
        print(f"  cached {label}: {out_path.name} ({out_path.stat().st_size / 1e6:.1f} MB)")
        return out_path

    bytes_seen = 0
    last_report = 0
    with requests.get(url, stream=True, timeout=1800) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
                bytes_seen += len(chunk)
                # Report every 100 MB so a 2.3 GB download isn't silent.
                if bytes_seen - last_report > 100 * (1 << 20):
                    print(f"  {label}: {bytes_seen / 1e6:.0f} MB", flush=True)
                    last_report = bytes_seen
    print(f"  {label} done: {bytes_seen / 1e6:.0f} MB → {out_path.name}")
    return out_path


print("\nNatura 2000 N2K end-2024")
for label, cfg in N2K_DOWNLOADS.items():
    download_n2k(label, cfg["url"], cfg["local"])
    sources.append(
        {
            "name": f"Natura 2000 (End-2024, {label})",
            "dataset_id": cfg["dataset_id"],
            "url": cfg["url"],
            "metadata_page": cfg["metadata_page"],
            "license": "EEA standard reuse policy (free reuse with attribution)",
            "accessed_on": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "local_path": str(cfg["local"].relative_to(RAW_DIR.parent)),
        }
    )

# %% [markdown]
# ## Source log
#
# Persist the source registry so `02_data_clean.py` (and the FORRT Replication
# Study draft) can audit which datasets fed the pipeline.

# %%
sources_log = RAW_DIR / "sources.json"
with open(sources_log, "w") as f:
    json.dump({"sources": sources}, f, indent=2)
print(f"\nLogged {len(sources)} source(s) to {sources_log}")
