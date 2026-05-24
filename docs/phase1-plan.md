# Phase 1 plan — European coastal biodiversity follow-up

**Status:** planning doc, written 2026-05-23, no repo yet
**Predecessor chain:** [Coastal-ROM replication of Loveland et al. 2024](https://w3id.org/sciencelive/np/RAuvGPQk_nxEcBWzADcLnyfqgjJ9Hr2aSWxwof2sDAung) (CiTO Citation URI)
**Author:** Anne Fouilloux (ORCID 0000-0002-1784-2920, Lifewatch-ERIC)

This is the "sketch Phase 1 on paper" output (option B from 2026-05-23). It maps the locked PICO into concrete data, tooling, and notebook stubs **before** creating the new repo, so the design problems surface before file proliferation.

Once approved, the next step is option A: spin up a fresh repo from `forrt-replication-template`, run `/init-template`, and seed `nanopubs/drafts/00_question_summary.md` + `nanopubs/drafts/01_question.md` from sections 1–2 of this doc.

---

## 1. Locked scope (recap)

**Chain shape:** Question-rooted PICO chain. CiTO at step 06 cites Loveland 2024 (`10.1016/j.ocemod.2024.102387`) with relation `extends` or `qualifies` depending on outcome. The chain does **not** root on a paper Quote — it roots on the PICO question.

**PICO:**

- **P** Coastal Natura 2000 marine sites (SAC + SPA, marine area > 0) in European storm landfall paths
- **I** Coupled wave hindcast using **WAVERYS** (CMEMS global, MFWAM physics)
- **C** Coupled wave hindcast using **regional CMEMS wave products** (IBI / NWS / MED — region-specific physics, finer grids)
- **O** Difference in biodiversity exposure attribution at Natura 2000 sites

**Storm panel (three storms, three CMEMS regional models, all wave-surge-driven):**

| Storm | Date window | Region | CMEMS regional model | Headline N2000 site |
|---|---|---|---|---|
| Xynthia | 26 Feb – 1 Mar 2010 | French Atlantic | IBI (1/36°, ~3 km) | Pertuis Charentais SAC (FR5200659) |
| Xaver | 4 – 7 Dec 2013 | North Sea | NWS (~1.5 km on shelf) | Wadden Sea (DE/NL/DK trinational) |
| Gloria | 19 – 23 Jan 2020 | NW Mediterranean | MED (~4 km) | Ebro Delta SAC (ES0000020) |

**Biodiversity layer:** marine SAC/SPA polygons from Natura 2000 N2K dataset. Per-site weight = function of Annex I habitat count × Annex II species count drawn from the EEA Standard Data Form.

**Headline statistic:** fraction of biodiversity-weighted Natura 2000 marine sites where the WAVERYS-vs-regional Hs delta during the storm window exceeds threshold X, reported per-storm and aggregated.

---

## 2. PICO → data + tooling mapping

### P — Natura 2000 marine sites

- **Source:** EEA Natura 2000 N2K dataset, https://www.eea.europa.eu/data-and-maps/data/natura-15 (or latest version). Two artefacts:
  - `Natura2000_end<year>.gpkg` — polygons (SAC/SPA boundaries)
  - `Natura2000_end<year>.sqlite` — Standard Data Forms (habitats + species per site)
- **Tooling:** `geopandas` (polygons), `sqlite3` / `pandas` (SDF queries)
- **Filter:** marine sites only (SDF field `MARINE_AREA_HA > 0` or designation type ∈ {marine SAC, marine SPA, coastal SAC}). Spatial filter: within each storm's bounding box.

### I — WAVERYS (global, MFWAM)

- **Product:** `cmems_mod_glo_wav_my_0.2_PT3H-i` (multi-year WAVERYS hourly) — **verify exact dataset ID against current CMEMS catalog before download**, the catalog was reorganised in 2022 and product IDs have shifted.
- **Resolution:** 0.2° × 0.2°, 3-hourly (some products hourly)
- **Variables:** `VHM0` (Hs), `VTPK` (peak period), `VMDR` (mean wave direction)
- **Tooling:** `copernicusmarine` Python package (per DOMAIN.md). Credentials at `~/.copernicusmarine/.copernicusmarine-credentials`; CI handles via `COPERNICUS_CREDENTIALS_BASE64` secret.
- **Time slices:** the three storm windows above, plus 24 h pre-storm padding for spin-up consistency.

### C — Regional CMEMS wave products

| Region | Likely product ID (verify) | Resolution | Time coverage check |
|---|---|---|---|
| Atlantic (Xynthia) | `IBI_MULTIYEAR_WAV_005_006` or successor | 1/36° (~3 km) | Confirm covers Feb 2010 |
| North Sea (Xaver) | `cmems_mod_nws_wav_my_*` family | ~1.5 km shelf | **Confirm Dec 2013 is in temporal coverage** — this is the most fragile of the three |
| Mediterranean (Gloria) | `MEDSEA_MULTIYEAR_WAV_006_012` or successor | ~4 km | Confirm covers Jan 2020 |

- **Tooling:** same `copernicusmarine` package, same variables (VHM0/VTPK/VMDR) for apples-to-apples comparison.

### O — Difference in biodiversity exposure attribution

Defined operationally in section 3 (analysis notebook).

### Auxiliary data (sanity checks, not load-bearing)

- **In-situ buoys** for noise-floor estimation (see section 4 on threshold X): selected buoys in each region from EMODnet Physics / Copernicus Marine in-situ TAC.
- **GBIF + OBIS occurrence overlays** for one or two figures showing where biodiversity actually sits within the affected polygons — `pygbif` per DOMAIN.md, always mint download DOIs.
- **ERA5 winds** for context maps (storm track + wind field) — `cdsapi`.

---

## 3. Notebook structure

The repo uses the standard four-notebook pipeline from CLAUDE.md § Phase 2. As jupytext `.py` files synced to `.ipynb` per `docs/cicd-conventions.md`.

### `01_data_download.py`

Self-contained per DOMAIN.md § Self-contained data downloads.

1. Authenticate `copernicusmarine` from the credentials file (fail clearly if missing).
2. For each storm, download WAVERYS over (bbox, storm_window + 24h pre-padding). Save as NetCDF per storm: `data/raw/waverys_<storm>.nc`.
3. Download the matching regional CMEMS wave product over the same (bbox, window). Save as NetCDF: `data/raw/regional_<storm>.nc`.
4. Download (or cache) Natura 2000 N2K geopackage + SDF SQLite from EEA. One-time download for all three storms.
5. Optional: download a few in-situ buoy time series (CMEMS InSitu) for noise-floor estimation.
6. Optional: download GBIF/OBIS occurrence subsets for the headline sites — mint download DOIs and record in `data/raw/citations.txt`.

**Failure mode to guard against:** if a regional product's temporal coverage doesn't reach the storm date (most likely for NWS / Xaver 2013), the notebook should fail loudly with a clear message rather than silently downloading nothing. The whole storm panel hinges on three valid regional fields.

### `02_data_clean.py`

1. Open WAVERYS + regional product as `xarray.Dataset`s.
2. Spatially subset both to the storm region of interest.
3. Temporally subset to the storm window (drop padding).
4. **Regrid the regional product onto the WAVERYS grid** (rationale: apples-to-apples comparison across all three storms requires a common grid; the headline statistic uses this; spatial maps in `04_figures.py` use the native regional grid). Tooling: `xesmf` (bilinear) or `xarray.interp` for simple cases.
5. Load Natura 2000 polygons, filter to marine sites in each storm's bbox, compute per-site Annex I + Annex II counts from the SDF.
6. Output per storm: tidy NetCDF `data/intermediate/<storm>_aligned.nc` containing `waverys_hs`, `regional_hs`, `sites_polygons` (as a separate GeoJSON or stored as JSON in a sidecar — NetCDF doesn't carry polygons natively).

Per DOMAIN.md: **no `.npz`**, NetCDF for the gridded fields, GeoJSON / GeoPackage for the polygons.

### `03_analysis.py`

For each (storm, site):

1. **Compute the storm-window exposure metric.** Recommended primary metric: peak Hs at the site during the storm window, computed as the spatial mean of grid cells within the polygon at the temporal max. Secondary: integrated wave action `∫ Hs² dt` over the storm window.
2. **Compute the inter-product delta:** `delta_hs = regional_hs - waverys_hs` (signed) and `|delta_hs|` (absolute).
3. **Apply the per-site biodiversity weight:** `w_site = log1p(n_annex1_habitats + n_annex2_species)`. The `log1p` avoids over-weighting one or two mega-biodiverse sites (Wadden Sea has 100+ habitats/species recorded, a Greek islet has 2–3). *(Revised 2026-05-24 in Phase 3 from the originally-planned multiplicative `log1p(habitats × species)`: the product zeroed 91% of bird SPAs — Annex II species, no Annex I habitat listing — so the additive form is used instead. Commit `2cd131e`.)*
4. **Compute the headline statistic:** weighted fraction of sites where `|delta_hs| > X`, where X is set per section 4.

Save:
- `results/per_site_delta.csv` — one row per (storm, site_code) with columns `n_habitats`, `n_species`, `weight`, `peak_hs_waverys`, `peak_hs_regional`, `delta_hs`, `exceeds_X`.
- `results/headline_stats.csv` — one row per storm + one row "aggregated", with the weighted fraction.

### `04_figures.py`

- **`figures/main_result.png`** — three-panel regional map. Each panel: WAVERYS peak-Hs background (light grey contours), regional peak-Hs colored, Natura 2000 polygons overlaid with fill color = `delta_hs` (diverging colormap), polygon edge weight = biodiversity weight `w_site`. Cartopy projection per region.
- **`figures/headline_stats_bars.png`** — bar chart, x-axis = (Xynthia, Xaver, Gloria, aggregated), y-axis = weighted fraction of sites exceeding threshold X. Threshold X printed in the title for unambiguous interpretation.
- **`figures/biodiversity_vs_delta.png`** — scatter, x = `w_site`, y = `|delta_hs|`, points colored by storm. Tests whether the biodiversity-rich sites are systematically more or less affected by the inter-product choice. Mostly diagnostic — null result here is fine.
- Optional **`figures/sanity_storm_tracks.png`** — three-panel storm track + ERA5 max wind speed, just to anchor the reader.

---

## 4. Threshold-X design (the load-bearing decision)

The risk we flagged on 2026-05-23: WAVERYS and the regional CMEMS products are both production-grade and validated. The Hs delta between them at any given site might be small enough that "fraction of sites where delta > X" is uninformative unless X is well-chosen.

Three approaches, ordered by rigour:

### A. Fixed physical threshold (X = 0.5 m Hs)

Defensible because 0.5 m is the rough scale of inter-product mean bias in published WAVERYS / IBI validation papers. Cells exceeding 0.5 m delta signal "production-choice-matters" above the validation noise.

- **Pro:** clean, easy to defend, comparable across studies.
- **Con:** 0.5 m may be too aggressive in calmer regimes (Med) and too lenient in extreme regimes (Xaver peak Hs ~10 m in the German Bight).

### B. Relative threshold (X = fraction of storm-peak Hs)

E.g., X = 10% of the storm-window peak Hs at the site. Adapts to storm magnitude.

- **Pro:** storm-aware, region-aware.
- **Con:** "10%" is arbitrary; harder to compare across studies than a fixed value.

### C. Data-driven threshold from independent buoy validation **← recommended**

Use the published WAVERYS / IBI / NWS / MED validation RMSE against in-situ buoys for the relevant region/season as the observational noise floor. Then:

```
X = sqrt(RMSE_WAVERYS² + RMSE_regional²)
```

…the joint observational noise floor. Sites where `|delta_hs| > X` differ between the two products by more than they each differ from observations — a defensible operational definition of "the production choice matters here."

- **Pro:** most rigorous; threshold is empirically grounded; defensible in the Outcome and CiTO `qualifies` framing.
- **Con:** validation RMSE statistics are scattered across CMEMS product documentation; gathering them is one extra notebook section. Likely needs three different X values (one per region) because RMSE differs by basin.

**Recommendation:** use **C** as the headline, with **A** (X = 0.5 m) as a sensitivity check in a supplementary figure / table. A and C agreeing would be reassuring; disagreement is interpretable.

---

## 5. Open decisions for the user

These need to be settled before repo creation, or at least labelled in the planning doc so the new repo's `00_question_summary.md` can be authoritative:

1. **Threshold X approach** — recommendation C above. Confirm, or pick A / B.
2. **Regridding direction** — onto WAVERYS (coarser, common grid) vs onto the regional product (finer, per-region). Recommendation: WAVERYS for the headline statistic, native regional for the spatial maps. Confirm, or change.
3. **Biodiversity weighting function** — `log1p(n_habitats × n_species)` recommended. Alternatives: raw product, IUCN-weighted, EBV-based composite. Confirm.
4. **Single repo vs three repos for the storm panel** — strongly recommend single repo, single chain. Three storms become the multi-storm dimension of the headline statistic, not three separate chains. Confirm.
5. **CiTO relation pre-commitment** — leave as "to be decided at Phase 3" or pre-commit to `extends` / `qualifies` based on expected effect direction. Recommendation: leave open, decide after the Outcome.
6. **Whether to also publish a Research Software nanopub** at the end — depends on whether the repo produces a reusable tool (a pip-installable package for "compute WAVERYS-vs-regional exposure delta at any polygon set") or just a worked-example. Recommendation: defer to Phase 4; if the analysis ends up modular enough, factor out and publish; otherwise the FORRT chain is sufficient.

---

## 6. Repo skeleton (preview for option A)

When you spin up the repo from `forrt-replication-template`:

```
european-coastal-biodiversity-replication/
├── CLAUDE.md             # universal operating manual (don't edit)
├── DOMAIN.md             # biodiversity + EO flavour (already correct)
├── USER_PREFERENCES.md   # Anne's identity (re-run /init-template)
├── README.md
├── LICENSE               # MIT
├── pixi.toml             # see below
├── pixi.lock             # regenerate
├── Dockerfile
├── Snakefile             # 4-stage DAG: download → clean → analyse → figures
├── CITATION.cff          # cite Loveland in references:
├── codemeta.json
├── myst.yml
├── index.md
├── .github/workflows/
│   ├── ci.yml
│   ├── docker.yml
│   └── jupyter-book.yml
├── paper/                # leave empty (no upstream paper, question-rooted chain)
├── notebooks/
│   ├── 01_data_download.py
│   ├── 02_data_clean.py
│   ├── 03_analysis.py
│   └── 04_figures.py
├── nanopubs/
│   ├── drafts/
│   │   ├── 00_question_summary.md   # written from sections 1–2 of THIS doc
│   │   ├── 01_question.md           # PICO question nanopub fields
│   │   ├── 02_aida.md
│   │   ├── 03_claim.md
│   │   ├── 04_study.md
│   │   ├── 05_outcome.md
│   │   └── 06_citation.md           # CiTO → Loveland 2024
│   └── PUBLISHED.md
├── data/
│   ├── raw/                         # gitignored, ≥100 MB behind actions/cache
│   ├── intermediate/                # gitignored
│   └── README.md                    # data sources + DOIs
├── figures/
└── results/
```

### `pixi.toml` additions on top of the template default

- `copernicusmarine` (waves data)
- `cdsapi` (ERA5 winds for context)
- `geopandas` + `pyogrio` (Natura 2000 polygons)
- `xesmf` (regridding)
- `pygbif` (occurrence DOIs)
- `cartopy` (regional maps)
- `xarray` + `netcdf4` + `dask` (already in template)
- Optionally: `healpix-geo` if the spatial Hs sensitivity figure benefits from a DGGS view (lower priority; native cartopy is fine for the headline).

### CI secrets needed

- `COPERNICUS_CREDENTIALS_BASE64` — required for CMEMS downloads in CI.
- Optionally `CDSAPI_KEY` if ERA5 context maps are in CI.

---

## 7. Phase 2–5 outlook (so you know what you're committing to)

| Phase | Effort | Key risk |
|---|---|---|
| 2 — Code + data port | ~3–5 days of focused work | NWS wave product temporal coverage; regridding artefacts |
| 3 — Local results + figures | ~2 days | Threshold X choice + null-result framing if deltas are small |
| 4 — Release + Zenodo | ~1 day | Standard release ritual |
| 5 — FORRT chain | ~1 day with skill help | Question-rooted Quote-equivalent (PICO question template) — slightly less familiar than Quote-with-comment |

**Total realistic estimate:** 1.5–2.5 weeks of focused work, not counting waiting on CMEMS authentication or KP outages.

---

## 8. What to do next

1. **Read this doc**, push back on anything that feels off.
2. **Settle the open decisions in section 5** (especially threshold X and single-repo-vs-three).
3. **Then:** option A — clone `forrt-replication-template`, run `/init-template`, and use sections 1–2 of this doc as the source material for `00_question_summary.md`.

I can help with any of those steps when you're ready.

---

## Addendum (2026-05-23) — pre-flight derisk findings

Three derisks were run before committing to repo creation. Outcome: **all three resolved; the plan stands as written. One subtle risk surfaced** (see § A4 below) that the user should be aware of going into Phase 2.

### A1. CMEMS product IDs and coverage — ✅ verified

All four products exist, are reachable in the current catalog, and cover all three storm dates. The highest-risk item (NWS coverage of Dec 2013) is confirmed.

| Product | Product ID | Coverage | Resolution | Wave model |
|---|---|---|---|---|
| WAVERYS (I) | `GLOBAL_MULTIYEAR_WAV_001_032` | 1 Jan 1980 – 31 Mar 2026 | 0.2° | MFWAM |
| IBI (Xynthia) | `IBI_MULTIYEAR_WAV_005_006` | 1 Jan 1980 – present (M-4) | 1/36° (~3 km) | MFWAM |
| NWS (Xaver) | `NWSHELF_REANALYSIS_WAV_004_015` | **1 Jan 1980 – 31 Dec 2025 — Dec 2013 confirmed in coverage** | ~1.5 km (0.0135°×0.0303°) | WAVEWATCH III, ERA5-forced |
| MED (Gloria) | `MEDSEA_MULTIYEAR_WAV_006_012` | Reanalysis 1993-2018, Interim Jun 2020 onwards (covers Jan 2020 boundary — verify locally) | 1/24° (~4 km) | MFWAM-derived (Med-WAV) |

**Note on MED coverage of Jan 2020:** the QUID describes the reanalysis as 1993-2018 and an INTERIM extension Jun 2020 – Jun 2021. Storm Gloria (19-23 Jan 2020) falls between these — needs to be confirmed at first download whether Jan 2020 sits in the reanalysis tail, the interim, or a gap. If it's a gap, swap Gloria → an early-2021 NW Med storm or the late-2019 Med storms.

### A2. Natura 2000 SDF schema — ✅ workable, schema discoverable at Phase 2

- **Current release:** Natura 2000 end-of-2024 (revision 01), published 5 March 2026 by EEA.
- **Formats distributed:** vector polygons as Shapefile + GeoPackage; tabular data as `.csv` / `.txt` / `.sql` / `.mdb` / `.accdb`. No native SQLite, but `.sql` (SQL DDL + inserts) loads cleanly into SQLite; `.mdb` opens with `mdb-tools` (Homebrew `mdb-tools`).
- **Bulk download:** `https://sdi.eea.europa.eu/data/d713bff7-0cdf-4f0d-acd1-dc3c63af237e`
- **Schema documentation:** ER diagram + Excel schema available on the Reportnet 3 public page for Natura 2000 — referenced from the EIONET CDR help page. Tables for Annex I habitats and Annex II species are present but exact table names need confirmation at Phase 2 first inspection (no blocker, just an extra 30 min).
- **Per-site SDF viewer:** `https://natura2000.eea.europa.eu/Natura2000/SDF.aspx?site=<SITE_CODE>` is a SPA — useful for human verification of headline sites, but use the bulk download for programmatic access.

### A3. Validation RMSE for threshold X — ✅ harvested, threshold C is empirically grounded

Source: CMEMS QUID documents fetched and text-extracted on 2026-05-23.

**SWH validation RMSD against in-situ buoys (coastal subset where reported):**

| Product | SWH RMSD vs buoys | Bias | Buoy network | Validation period |
|---|---|---|---|---|
| WAVERYS — open ocean | 0.22 m | +4 cm | CMEMS INSITU_GLO_WAVE_REP_OBSERVATIONS_013_045 | 1993-2019 |
| WAVERYS — **coastal** | **0.34 m** | -5 cm | (same) | (same) |
| IBI — **coastal mooring** | **0.31 m** | -9 cm | 157 buoys | 1993-2022 |
| IBI — deep water | 0.39 m | -19 cm | (same) | (same) |
| NWS — Southern North Sea (Xaver-relevant) | **0.196 m** | +2 cm | UK ChannelCoast / WaveNet + open-water platforms | (date-range published in QUID) |
| NWS — North Sea Approaches | 0.361 m | +2 cm | (same) | (same) |
| MED — full Mediterranean (in-situ) | **0.227 ± 0.012 m** | -5.6 cm | 53 wave buoys + ISPRA Italian buoys | 1993-2018 |
| MED — atl sub-region (Iberian) | 0.210 m | +2.4 cm | satellite altimetry | (same) |

**Threshold X (joint observational noise floor) per region:**

```
X_Xynthia  = sqrt(0.34² + 0.31²) ≈ 0.46 m  (WAVERYS coastal + IBI coastal)
X_Xaver    = sqrt(0.34² + 0.196²) ≈ 0.39 m  (WAVERYS coastal + NWS S North Sea)
X_Gloria   = sqrt(0.34² + 0.227²) ≈ 0.41 m  (WAVERYS coastal + MED full Med)
```

**Implications:**

- Threshold approach C in the plan is now empirically defensible — the three regional X values converge in a narrow band (0.39–0.46 m).
- They converge to **roughly the 0.5 m fixed-threshold heuristic (option A in section 4)**, which is reassuring: A and C give comparable answers, and we can report both in the Outcome with a "robustness" framing.
- The narrowness of the three X values means a single rounded threshold (X = 0.4 m) can be used as the headline if simplicity matters, with the three region-specific values as a supplementary sensitivity check.

### A4. Subtle risk surfaced — shared-error correlation

WAVERYS and the regional products do NOT have fully independent errors:

- Both NWS and MED are forced by **ERA5 atmosphere** (NWS QUID: explicit; MED QUID: ERA5 winds).
- WAVERYS itself was *evaluated against* ERA5 in the QUID and discussed extensively as a reference baseline.
- All three regional products use MFWAM-derived physics for IBI and MED (and WAVEWATCH III for NWS) — different from WAVERYS's MFWAM but related Météo-France lineage for two of three.

Consequence: the **inter-product delta is likely smaller than `sqrt(RMSE_a² + RMSE_b²)` would predict** under the independence assumption. The joint noise floor formula overestimates the threshold; the true noise floor (under correlated errors) is lower. Operationally this means:

- Threshold X = 0.4 m is **conservative** — sites that exceed it are "production-choice-matters" sites with high confidence, but a null result (few sites exceed) doesn't mean the products fully agree.
- For the supplementary analysis, consider also reporting a relative threshold (X' = 10% of storm-peak Hs at the site) as in option B — this isolates "the products disagree relative to storm signal" from "the products disagree in absolute terms."
- This subtlety belongs in the Replication Study's Methodology / Scope field (Phase 5) and the Outcome's Limitations field. It does not block Phase 2.

### A5. Verdict

**The plan holds.** Proceed to option A (spin up the new repo) when ready. The three derisks have:

1. Confirmed all CMEMS products + storm coverage (one minor MED Jan-2020 gap-check needed at first download).
2. Confirmed N2K data formats and a bulk-download URL (schema inspection deferred to Phase 2, ~30 min cost).
3. Grounded threshold X empirically: **X ≈ 0.4 m** is the recommended headline, with regional values 0.39 / 0.46 / 0.41 m as a sensitivity check.

One new caveat to carry forward into Phase 5: shared-error correlation between WAVERYS and the regionals (both leaning on ERA5 atmosphere) means the inter-product delta will be tighter than the QUID noise floors imply. Frame the headline statistic accordingly.
