# `data/` — downloaded artefacts, never committed

This directory holds the raw and cleaned datasets used by the replication pipeline. **Files in this directory are never committed to git** (`.gitignore` excludes everything except this README).

## Why download-on-first-run

Every replication must be self-contained: a user clones the repo and runs `snakemake --cores 1` (or executes notebook 01 directly), and the code fetches its own input data. No "ask the author for the dataset" steps; no folder-of-CSVs that drift out of sync with the analysis.

## Sources for this study

| Dataset | Provider | Access pattern | Local layout |
|---|---|---|---|
| WAVERYS (`cmems_mod_glo_wav_my_0.2deg_PT3H-i`) | CMEMS Marine Data Store, DOI [10.48670/moi-00022](https://doi.org/10.48670/moi-00022) | `copernicusmarine.subset(...)` per storm window + bbox | `data/raw/waverys_<storm>.nc` |
| IBI MY wave (`cmems_mod_ibi_wav_my_0.027deg_PT1H-i`) | CMEMS Marine Data Store | `copernicusmarine.subset(...)` for Xynthia | `data/raw/regional_xynthia.nc` |
| NWS reanalysis wave (`cmems_mod_nws_wav_my_0.027deg-0.014deg_PT1H-i`) | CMEMS Marine Data Store | `copernicusmarine.subset(...)` for Xaver | `data/raw/regional_xaver.nc` |
| MED MY wave (`cmems_mod_med_wav_my_4.2km-2D_PT1H-i`) | CMEMS Marine Data Store | `copernicusmarine.subset(...)` for Gloria | `data/raw/regional_gloria.nc` |
| Natura 2000 End-2024 (revision 01) — polygons + Standard Data Form | EEA SDI ([d713bff7-...](https://sdi.eea.europa.eu/data/d713bff7-0cdf-4f0d-acd1-dc3c63af237e)) | `requests.get(...)` against bulk archive | `data/raw/Natura2000_end2024.zip` (extracted to `data/raw/Natura2000_end2024/`) |

A `data/raw/sources.json` registry is regenerated each time `01_data_download.py` runs; it records the dataset IDs, DOIs, licences, and the date each was accessed.

## Required credentials

**CMEMS Marine Data Store** is the only credentialled API in this study.

- Get an account: <https://marine.copernicus.eu/>
- Local path: `~/.copernicusmarine/.copernicusmarine-credentials` (INI file)
  ```
  [credentials]
  username=<your-username>
  password=<your-password>
  ```
- **CI:** populated from the `COPERNICUS_CREDENTIALS_BASE64` GitHub Actions secret (base64-encoded INI content). `copernicusmarine login` is interactive and cannot run in CI. See `DOMAIN.md` § Copernicus credentials in CI.

The Natura 2000 archive at EEA is open download — no credentials.

## File layout produced by the pipeline

```
data/
├── raw/                              # gitignored, fetched by 01
│   ├── waverys_<storm>.nc            # one per active storm
│   ├── regional_<storm>.nc           # one per active storm
│   ├── Natura2000_end2024.zip
│   ├── Natura2000_end2024/           # extracted by 02 on first run
│   └── sources.json                  # registry written by 01
└── clean/                            # gitignored, written by 02
    ├── <storm>_aligned.nc            # WAVERYS + regional on common grid
    ├── <storm>_regional_native.nc    # regional Hs on native grid (for maps)
    └── <storm>_n2000_sites.parquet  # marine sites + Annex I/II counts
```

## CI cache

Large downloads (>100 MB) should be cached in GitHub Actions via `actions/cache@v4`. See `.github/workflows/ci.yml` for the pattern. The Natura 2000 archive is the heaviest item (~ several hundred MB extracted); WAVERYS + regional subsets are small per-storm (single-window slices, typically <50 MB each).
