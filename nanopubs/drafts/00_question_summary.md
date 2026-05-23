# Question summary (question-rooted chain)

> This is a working scratchpad for the question-framing phase. The output of this file feeds the PICO / AIDA / Claim drafts. It is not itself a nanopub.
>
> This chain is **question-rooted**, not paper-rooted — there is no upstream paper whose headline sentence we're testing verbatim. Instead, the chain is anchored on a PICO research question (`01_pico.md`). The CiTO step at the end of the chain (`06_citation.md`) cites the prior FORRT chain at https://w3id.org/sciencelive/np/RAuvGPQk_nxEcBWzADcLnyfqgjJ9Hr2aSWxwof2sDAung (coastal-ROM replication of Loveland et al. 2024) as prior art motivating this question.

## Research question (PICO)

**Title:** Does the choice of CMEMS wave reanalysis product change biodiversity exposure attribution at European Natura 2000 marine sites?

- **P** Coastal Natura 2000 marine sites (SAC + SPA, marine area > 0) in European storm landfall paths.
- **I** Coupled wave hindcast using **WAVERYS** (CMEMS global ocean wave reanalysis, `GLOBAL_MULTIYEAR_WAV_001_032`, MFWAM physics, 0.2°).
- **C** Coupled wave hindcast using **regional CMEMS wave reanalyses** matched to each storm's basin: `IBI_MULTIYEAR_WAV_005_006` (Atlantic, ~3 km, MFWAM), `NWSHELF_REANALYSIS_WAV_004_015` (North Sea, ~1.5 km, WAVEWATCH III), `MEDSEA_MULTIYEAR_WAV_006_012` (Mediterranean, ~4 km, Med-WAV).
- **O** Fraction of biodiversity-weighted Natura 2000 marine sites where the inter-product significant-wave-height delta during the storm window exceeds the joint observational noise floor X ≈ 0.4 m.

**Question type:** Causation — testing whether the choice of wave product causally changes the attribution outcome.

## Why this question

The prior chain (`coastal-rom-replication`) validated Loveland et al. (2024)'s conditional claim that, for water-surface-elevation hindcasting, reduced-order wave source terms (Gen1, Gen2) save computation versus the third-generation ST6 package without meaningfully compromising WSE accuracy at NOAA gauges. Loveland's own §6 Conclusions also flagged that wave statistics (peak period, mean direction, significant wave height near hurricane tracks) ARE sensitive to source-term choice — particularly in storm-track corridors.

This chain extends that finding by asking the cross-domain question: **when the choice of wave model machinery changes the wave field in storm corridors, does it change biodiversity-exposure attribution at protected coastal habitats?** The inter-product comparison (WAVERYS vs regional CMEMS) is an analogue of Loveland's Gen1/Gen2/Gen3 axis at production-grade granularity: both products are validated, both serve operational users, the choice between them is a real one for anyone running European coastal vulnerability assessments.

The biodiversity layer is Natura 2000 — EU's network of designated protected areas — because (a) the spatial unit is uniform across the three storm basins, (b) the Habitats Directive's Annex I (habitats) and Annex II (species) data are openly available via the EEA, (c) it ties the methodological question to a tangible policy framework, and (d) it fits the institutional mission of Lifewatch-ERIC.

## Methodology summary

- **Storm panel (3 storms, 3 CMEMS regional models, all wave-surge-driven):**
  - Xynthia — 26 Feb – 1 Mar 2010, French Atlantic, IBI regional, headline site Pertuis Charentais SAC (FR5200659).
  - Xaver — 4 – 7 Dec 2013, North Sea, NWS regional, headline site Wadden Sea (DE/NL/DK trinational).
  - Gloria — 19 – 23 Jan 2020, NW Mediterranean, MED regional, headline site Ebro Delta SAC (ES0000020).
- **Inter-product comparison:** for each storm window, download both WAVERYS and the matched regional product, regrid to a common reference, compute per-cell delta_Hs and integrated wave-action delta over the storm window.
- **Regridding:** *both grids, split by figure.* The headline bar chart uses the WAVERYS grid (0.2°, common across all three storms) so the multi-storm aggregation is apples-to-apples. Spatial maps in `04_figures.py` use the native regional grid to preserve high-resolution structure.
- **Biodiversity weighting:** per Natura 2000 marine site, weight w_site = `log1p(n_AnnexI_habitats × n_AnnexII_species)` drawn from the site's Standard Data Form (EEA bulk download). log1p compresses dynamic range so biodiversity-rich sites (Wadden Sea, 100+ recorded habitats/species) don't swamp smaller sites.
- **Exposure metric:** peak Hs at each site during the storm window (spatial mean within polygon, temporal max). Secondary metric: integrated wave action ∫ Hs² dt.
- **Threshold X:** the joint observational noise floor X = √(RMSE_WAVERYS² + RMSE_regional²) derived from CMEMS QUID validation against in-situ buoys. **Headline X ≈ 0.4 m**, with region-specific values 0.46 / 0.39 / 0.41 m for Xynthia / Xaver / Gloria respectively (see `docs/phase1-plan.md` § Addendum A3 for the derivation).
- **Headline statistic:** weighted fraction of Natura 2000 marine sites where |delta_Hs| > X. Reported per-storm and aggregated.
- **Anti-pattern guardrail:** WAVERYS and the regional products do NOT have fully independent errors — NWS and MED both use ERA5 atmospheric forcing, and WAVERYS was evaluated against ERA5 in its QUID. The inter-product delta is therefore expected to be smaller than the joint noise floor predicts under independence. The X ≈ 0.4 m threshold is therefore *conservative* (sites exceeding it are high-confidence "product-choice-matters" sites), and a near-null headline does not mean the products fully agree — only that they agree above noise. This caveat goes in `04_study.md` (Methodology / Scope) and `05_outcome.md` (Limitations).

## Study design choice

Which of the three FORRT Study Types fits this question-rooted chain?

- [ ] **Reproduction Study** — direct reproduction: same methodology, same tools.
- [x] **Replication Study** — replication with different methodology and conditions. Different data (European storms, not Gulf hurricanes), different biodiversity domain (Natura 2000 marine sites, not NOAA gauges/buoys), different inter-product axis (production-grade WAVERYS vs regional, not Gen1/Gen2/Gen3 source-term choice). The question Loveland's claim raised — "does wave-model machinery choice matter for downstream attribution?" — is being asked in a new domain.
- [ ] **Reproduction/Replication Study** — both.

### Justification

A pure Reproduction is impossible here: we are not re-running ADCIRC+SWAN with Loveland's source-term configurations. We are testing whether the choice of operational wave model changes attribution at coastal protected sites — a different empirical question that *extends* Loveland's source-term-sensitivity finding into a new domain (biodiversity exposure) and a new physical regime (European extratropical and Med storms). The CiTO relation in step 06 will be `extends` or `qualifies` depending on Outcome direction.

## Phase 1 derisk findings (summary)

Per `docs/phase1-plan.md` § Addendum (2026-05-23), three derisks were run before this repo was created:

1. **CMEMS product IDs / coverage** — all four products verified in current catalog, all three storm dates in coverage. NWS Dec 2013 (the biggest risk) is confirmed in `1980-12-31 2025` range. Small flag: MED reanalysis runs 1993-2018 and INTERIM extension Jun 2020 onwards; Storm Gloria (19-23 Jan 2020) sits between — 5-min confirmation needed at first download whether Jan 2020 is reachable; if not, swap to early-2021 NW Med storm.
2. **Natura 2000 SDF schema** — workable. EEA distributes Natura 2000 end-of-2024 (revision 01, published 5 March 2026) in CSV / SQL / MDB / ACCDB formats plus polygons as Shapefile + GeoPackage. Bulk download at `https://sdi.eea.europa.eu/data/d713bff7-0cdf-4f0d-acd1-dc3c63af237e`. Exact table names for Annex I × Annex II queries to be confirmed at Phase 2 first inspection (~30 min, no blocker).
3. **Threshold X** — empirically grounded from CMEMS QUID validation RMSE against in-situ buoys. X ≈ 0.4 m is defensible; region-specific values within 0.39-0.46 m converge in a narrow band that's reassuringly close to the 0.5 m fixed-threshold heuristic.

## Decisions baked in (2026-05-23)

These were settled before this draft was written; do not re-open without strong reason:

- **Regridding direction:** both grids, split by figure (WAVERYS for headline, native regional for spatial maps).
- **Biodiversity weighting function:** `log1p(habitats × species)` from Standard Data Form.
- **Repo scope:** single repo, single chain; multi-storm aggregation is a dimension of the headline statistic, not three separate chains.
- **Research Software nanopub (step 07):** deferred to Phase 4. Decide whether to publish once the analysis modular structure is known.

## Notes for downstream drafts

- The PICO question is the rooting nanopub (`01_pico.md`). The AIDA sentence in `02_aida.md` should anchor on a single empirical finding from this question — likely "the fraction of biodiversity-weighted Natura 2000 marine sites where inter-product Hs delta exceeds X varies by storm basin" or similar (decide after Phase 3 results are in).
- The Claim type in `03_claim.md` is most likely "comparative-effects" or "causal" — the question is asking whether the choice of wave product has a causal effect on attribution. See `docs/claim-type-vocabulary.md`.
- The CiTO relation in `06_citation.md` is `extends` if our headline statistic confirms that product choice changes attribution at storm-track-affected sites; `qualifies` if it confirms only weakly or only in one basin; `confirms` is unlikely (Loveland's claim is about source-term choice, not product choice, so a direct `confirms` would be a category match error).
- This chain does not produce a reusable software artefact at this stage. If `notebooks/` factors out cleanly into a pip-installable tool in Phase 4, publish a Research Software nanopub (step 07) citing the FORRT Claim.
- Storm Daniel (September 2023) was considered and rejected: dominant damage mechanism was inland river flooding (Thessaly) and dam failure (Derna), not marine waves; Libya is outside Natura 2000. Storm Gloria (January 2020, Catalan coast) was selected as the Mediterranean representative because the dominant damage was wave-driven and overlaps a major Natura 2000 site (Ebro Delta).
