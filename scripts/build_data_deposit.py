#!/usr/bin/env python3
"""Assemble the Zenodo *data* deposit for this replication.

Bundles the small, exact data slices and derived intermediates that pin the
study — NOT the large authoritative source archives (the 2.3 GB EEA Natura 2000
spatial archive and the full CMEMS products are cited by DOI instead, see
DATA_PROVENANCE.md). Run:

    pixi run python scripts/build_data_deposit.py

Outputs (gitignored):
    data_deposit/                  staging tree (raw/ clean/ results/ + docs)
    data_deposit/DATA_PROVENANCE.md  full source table, DOIs, versions, attribution
    data_deposit/MANIFEST.sha256   checksums of every bundled file
    data_deposit.zip               the archive to drag-and-drop into Zenodo

The Zenodo upload + publish is a manual step (needs your Zenodo login). After
publishing, copy the concept DOI into scripts/fetch_intermediates.py and
CITATION.cff (data reference).
"""
from __future__ import annotations

import hashlib
import shutil
import zipfile
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEPOSIT = REPO / "data_deposit"

STORMS = ["xynthia", "xaver", "gloria"]

# Files that go in the deposit, relative to the repo root. The raw wave subsets
# pin the exact CMEMS slices; the clean intermediates let 03/04 (analysis +
# figures) run without re-downloading anything.
BUNDLE_FILES = (
    [f"data/raw/waverys_{s}.nc" for s in STORMS]
    + [f"data/raw/regional_{s}.nc" for s in STORMS]
    + [f"data/clean/{s}_aligned.nc" for s in STORMS]
    + [f"data/clean/{s}_regional_native.nc" for s in STORMS]
    + [f"data/clean/{s}_n2000_sites.parquet" for s in STORMS]
    + ["results/headline_stats.csv", "results/per_site_delta.csv", "results/summary.csv"]
)

# --- provenance metadata (verified against the CMEMS / EEA catalogs 2026-05-24) ---

WAVE_PRODUCTS = {
    "WAVERYS (global)": {
        "product": "GLOBAL_MULTIYEAR_WAV_001_032",
        "dataset": "cmems_mod_glo_wav_my_0.2deg_PT3H-i",
        "doi": "10.48670/moi-00022",
        "version": "202411",
        "model": "MFWAM, 0.2°, 3-hourly",
        "used_for": "all three storms (the global product under comparison)",
    },
    "IBI (Atlantic–Iberian–Biscay)": {
        "product": "IBI_MULTIYEAR_WAV_005_006",
        "dataset": "cmems_mod_ibi_wav_my_0.027deg_PT1H-i",
        "doi": "10.48670/moi-00030",
        "version": "202511",
        "model": "MFWAM, 1/36° (~3 km), hourly",
        "used_for": "Xynthia (French Atlantic, Feb 2010)",
    },
    "NWS (North-West Shelf)": {
        "product": "NWSHELF_REANALYSIS_WAV_004_015",
        "dataset": "MetO-NWS-WAV-RAN",
        "doi": "10.48670/moi-00060",
        "version": "202007",
        "model": "WAVEWATCH III, ~1.5 km, hourly, ERA5-forced",
        "used_for": "Xaver (North Sea, Dec 2013)",
    },
    "MED (Mediterranean)": {
        "product": "MEDSEA_MULTIYEAR_WAV_006_012",
        "dataset": "cmems_mod_med_wav_my_4.2km_PT1H-i",
        "doi": "10.48670/mds-00376",
        "version": "202511",
        "model": "Med-WAV (MFWAM-derived), 1/24° (~4 km), hourly",
        "used_for": "Gloria (NW Mediterranean, Jan 2020)",
    },
}

NATURA2000 = {
    "tabular (Standard Data Form)": {
        "dataset": "eea_t_natura2000_p_2024_v01_r01",
        "url": "https://sdi.eea.europa.eu/data/d713bff7-0cdf-4f0d-acd1-dc3c63af237e",
    },
    "spatial (polygons, EPSG:3035)": {
        "dataset": "eea_v_3035_100_k_natura2000_p_2024_v01_r00",
        "url": "https://sdi.eea.europa.eu/data/91357f39-7866-41ce-b447-43905c364ec8",
    },
}

STORM_WINDOWS = {
    "xynthia": "2010-02-26 → 2010-03-01 (French Atlantic)",
    "xaver": "2013-12-04 → 2013-12-07 (North Sea)",
    "gloria": "2020-01-19 → 2020-01-23 (NW Mediterranean)",
}


def _provenance_md() -> str:
    wave_rows = "\n".join(
        f"| {name} | `{p['dataset']}` | [{p['doi']}](https://doi.org/{p['doi']}) "
        f"| {p['version']} | {p['model']} | {p['used_for']} |"
        for name, p in WAVE_PRODUCTS.items()
    )
    n2k_rows = "\n".join(
        f"| Natura 2000 End-2024 rev01 — {k} | `{v['dataset']}` | [{v['url']}]({v['url']}) |"
        for k, v in NATURA2000.items()
    )
    window_rows = "\n".join(f"- **{s}**: {w}" for s, w in STORM_WINDOWS.items())
    return f"""# Data provenance — European coastal biodiversity replication

**Compiled:** {date.today().isoformat()}

This archive contains the *exact data slices and derived intermediates* used by
the replication study at
<https://github.com/annefou/european-coastal-biodiversity-replication>.
It exists so the analysis can be reproduced without re-downloading the large
authoritative source archives, and to pin the precise data versions used (CMEMS
reanalyses are periodically reprocessed).

It is **not** the primary reproduction path: `notebooks/01_data_download.py` in
the repository downloads everything from source on first run. This deposit is a
preservation + fast-path layer.

## Contents

```
raw/      per-storm WAVERYS + regional CMEMS wave subsets (NetCDF, the exact
          spatial/temporal slices the study used)
clean/    analysis-ready intermediates:
            <storm>_aligned.nc          WAVERYS + regional Hs on a common grid
            <storm>_regional_native.nc  regional Hs on its native grid (maps)
            <storm>_n2000_sites.parquet marine Natura 2000 sites + Annex I/II counts
results/   headline_stats.csv, per_site_delta.csv, summary.csv
```

Storm windows (24 h pre-storm spin-up dropped):
{window_rows}

## Wave data — Copernicus Marine Service (CMEMS)

| Product | Dataset ID | DOI | Version | Model / resolution | Used for |
|---|---|---|---|---|---|
{wave_rows}

> **Attribution (required):** *"Generated using E.U. Copernicus Marine Service
> Information"*, plus the product DOIs above. The NetCDF files in `raw/` are
> spatial + temporal **subsets** of these products, not the full products.
> License: Copernicus Marine free-and-open, attribution required.

## Biodiversity data — European Environment Agency (EEA)

| Dataset | Dataset ID | Source |
|---|---|---|
{n2k_rows}

> The `clean/<storm>_n2000_sites.parquet` files are **derived** from the EEA
> Natura 2000 End-2024 (revision 01) spatial polygons joined with the Standard
> Data Form (Annex I habitat + Annex II species counts), filtered to marine
> sites in each storm region. License: EEA standard reuse policy (free reuse
> with attribution to the European Environment Agency). The full 2.3 GB spatial
> archive and the tabular SDF are **not** redistributed here — cite the EEA
> sources above.

## How to use this deposit

Place the `raw/`, `clean/`, and `results/` directories under the repository's
`data/` and `results/` paths, then run the analysis + figure notebooks
(`03_analysis.py`, `04_figures.py`) directly — they read from `data/clean/`.
A fast-path fetch helper (planned for the repo, to be wired once this deposit's
concept DOI exists) will automate the download + placement.
"""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if DEPOSIT.exists():
        shutil.rmtree(DEPOSIT)
    DEPOSIT.mkdir(parents=True)

    missing = [f for f in BUNDLE_FILES if not (REPO / f).exists()]
    if missing:
        raise SystemExit(
            "Missing files (run the pipeline for all three storms first):\n  "
            + "\n  ".join(missing)
        )

    manifest_lines = []
    total = 0
    for rel in BUNDLE_FILES:
        src = REPO / rel
        # Flatten data/ prefix: data/raw/x -> raw/x, data/clean/x -> clean/x.
        dest_rel = rel[len("data/"):] if rel.startswith("data/") else rel
        dest = DEPOSIT / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        digest = _sha256(dest)
        size = dest.stat().st_size
        total += size
        manifest_lines.append(f"{digest}  {dest_rel}  ({size/1e6:.2f} MB)")
        print(f"  + {dest_rel}  ({size/1e6:.1f} MB)")

    (DEPOSIT / "DATA_PROVENANCE.md").write_text(_provenance_md())
    (DEPOSIT / "MANIFEST.sha256").write_text("\n".join(manifest_lines) + "\n")

    # Zip the staging tree for one-shot upload.
    zip_path = REPO / "data_deposit.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(DEPOSIT.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(DEPOSIT))

    print(
        f"\nBundled {len(BUNDLE_FILES)} files, {total/1e6:.0f} MB → {DEPOSIT}/"
        f"\nArchive: {zip_path} ({zip_path.stat().st_size/1e6:.0f} MB)"
        f"\nProvenance: {DEPOSIT/'DATA_PROVENANCE.md'}"
        "\n\nNext: upload data_deposit.zip (or the data_deposit/ tree) to Zenodo,"
        " publish, then copy the concept DOI into scripts/fetch_intermediates.py"
        " and CITATION.cff."
    )


if __name__ == "__main__":
    main()
