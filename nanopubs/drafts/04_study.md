# 04 — FORRT Replication Study

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.
>
> Method below verified against `notebooks/02_data_clean.py` and `notebooks/03_analysis.py` (2026-05-24). No result numbers — those live in the Outcome (step 05).

## Field-by-field draft

### Short URI suffix for study ID (text input, required)

Slug. Use kebab-case.

```
wave-product-exposure-three-storm-study
```

### Label/name of replication study (text input, required)

Human-readable title.

```
Inter-product wave-exposure comparison at Natura 2000 marine sites across three European storms
```

### Study type (dropdown, required)

- [ ] Reproduction Study — direct reproduction: same methodology, same tools.
- [x] **Replication Study** — replication with different methodology or conditions.
- [ ] Reproduction/Replication Study — both.

Rationale: this is not a re-run of Loveland et al.'s coupled-model experiment; it tests the analogous product-/model-choice-sensitivity question with different data, a different domain, and a different downstream metric. That is a Replication Study (different methodology and conditions).

### Search for a FORRT claim (search/select, required)

URI of the Claim published in step 03. Pull from `nanopubs/PUBLISHED.md`.

```
<FORRT Claim URI from nanopubs/PUBLISHED.md step 03 — publish 03 first, then paste here>
```

### Describe what part of the claim is reproduced/replicated (textarea, required)

The **scope** — which aspect of the claim is tested, what is in and out of scope. NOT method, NOT results.

```
Tested: whether substituting the global WAVERYS wave reanalysis with the matched higher-resolution regional CMEMS reanalysis changes the storm-wave exposure attributed to coastal marine Natura 2000 sites. Scope is three named European storms spanning three physically distinct regimes — Xynthia (2010, French Atlantic / Bay of Biscay), Xaver (2013, southern North Sea), Gloria (2020, north-western Mediterranean) — and the marine Special Areas of Conservation and Special Protection Areas in each storm's landfall region. Exposure is operationalised at the level of the storm-window peak significant wave height attributed to each site polygon, and the claim is tested at the level of the biodiversity-weighted prevalence of inter-product disagreement across sites. Out of scope: storm surge, wave period and direction, duration, any ecological-impact or population modelling, and running a coupled wave-circulation model directly.
```

### Describe how the claim is reproduced/replicated (textarea, required)

The **method** in plain prose. NOT exact numerical results.

```
For each storm, the WAVERYS global product and the basin-matched regional CMEMS product (IBI for Xynthia, North-West Shelf for Xaver, Mediterranean for Gloria) are downloaded over the storm window (with 24 hours of pre-storm padding) and a bounding box that fully contains the marine Natura 2000 sites of that region. The regional product is regridded onto the WAVERYS 0.2-degree grid by bilinear interpolation, and both are trimmed to the storm window. EEA Natura 2000 (End-2024, revision 01) polygons are joined with the Standard Data Form; marine sites intersecting each storm's core region are selected and their Annex I habitat and Annex II species counts attached. For every site, the per-product exposure is the spatial mean over the grid cells inside the polygon of the temporal-maximum significant wave height, and the signed inter-product delta is the regional value minus the WAVERYS value. Each site is weighted by log1p(number of Annex I habitats + number of Annex II species). The headline statistic is the biodiversity-weighted fraction of sites whose absolute inter-product delta exceeds a threshold X equal to the joint observational noise floor (the root-sum-square of the two products' published CMEMS QUID validation RMSE values, approximately 0.4 metres), reported per storm and aggregated. A sweep of X is run to assess robustness, and a per-site biodiversity-versus-delta diagnostic is produced. The pipeline is a four-notebook Snakemake workflow in a pixi-pinned environment.
```

### Describe any deviations from original methodology (textarea, optional)

What's different from the original method. Verified against the code, not guessed.

```
Loveland et al. 2024 ran a coupled wave-circulation model with full versus reduced-order source terms in the Gulf of Mexico and evaluated the internal wave and water-level fields. This study deviates in four ways. (1) Inter-product surrogate: rather than running a coupled model with full versus reduced-order source terms, it compares two operational production wave reanalyses, testing whether the product choice propagates to a downstream metric rather than the source-term physics directly. (2) Domain: European coasts and three extratropical/Mediterranean storms, not Gulf of Mexico hurricanes. (3) Downstream metric: biodiversity-exposure attribution at Natura 2000 marine sites, not the model's internal fields. (4) Non-independence: the two products share ERA5 atmospheric forcing (explicitly for the North-West Shelf and Mediterranean products) and partial model lineage (MFWAM for WAVERYS, IBI, and Mediterranean; WAVEWATCH III for the North-West Shelf), so the comparison is conservative — the noise-floor threshold computed under an independence assumption over-estimates the true disagreement floor.
```

### Search keywords (Wikidata) (multi-select, optional)

Provide labels (not QIDs) — the Wikidata search picks up labels.

- significant wave height
- Natura 2000
- wind wave model
- Copernicus Marine Environment Monitoring Service
- marine protected area

### Search discipline (Wikidata) (search, optional)

Provide labels.

- physical oceanography
- conservation biology

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 04.
