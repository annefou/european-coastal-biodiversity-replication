# 01 — PICO Research Question (question-rooted, comparative)

> This chain is question-rooted (PICO). The chain shape: PICO question → AIDA → FORRT Claim → Replication Study → Replication Outcome → CiTO. See `docs/chain-decision-tree.md`.
>
> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before publishing.
>
> After this draft is published, `01_quote.md` and `01_pcc.md` will have been deleted (they are unused — chain is PICO not Quote-rooted, not PCC-rooted).

**Form heading:** *"PICO Research Question — Define a research question using the PICO framework (Population, Intervention, Comparator, Outcome)"*

## Field-by-field draft

### Short ID (text input, required)

Slug becomes part of the nanopub URI. Use kebab-case.

```
wave-product-biodiversity-exposure-europe
```

### Research Question Title (text input, required)

10-200 characters. Length-bounded.

```
Does the choice of CMEMS wave reanalysis product change biodiversity exposure attribution at European Natura 2000 marine sites during storm landfall?
```

(149 characters.)

### Complete Research Question (textarea, required)

One coherent sentence/paragraph that names P, I, C, O inline.

```
At coastal Natura 2000 marine sites in the landfall path of three European storms (Xynthia 2010, Xaver 2013, Gloria 2020), does coupled wave hindcasting using the WAVERYS global ocean wave reanalysis (Copernicus Marine, MFWAM, 0.2 degrees) produce a different biodiversity exposure attribution — measured as the fraction of biodiversity-weighted sites where the storm-window peak significant-wave-height delta exceeds the joint observational noise floor of approximately 0.4 metres — than coupled wave hindcasting using the matched regional CMEMS wave reanalysis (Iberia-Biscay-Ireland at 3 km, North-West Shelf at 1.5 km, Mediterranean at 4 km)?
```

### Question Type (radio button, required)

- [x] **Causation**
- [ ] Descriptive
- [ ] Effectiveness
- [ ] Experience
- [ ] Prediction

Rationale: the question asks whether the choice of wave product (I vs C) causally produces a different attribution outcome (O) at the population of interest (P). This is a causal question about methodological choice, not an effectiveness question (we are not asking whether one product is "better"), not descriptive (we are not characterising a prevalence), not prediction.

### Population (P) (textarea, required)

Who/what is being studied. Discipline-level concept — not implementation. See `docs/pico-study-outcome-levels.md`.

```
Coastal Natura 2000 marine sites — Special Areas of Conservation (SAC) and Special Protection Areas (SPA) with marine area greater than zero — designated under the EU Habitats Directive (92/43/EEC) and the Birds Directive (2009/147/EC). The population spans three European basins reached by the three storms in the panel: the French Atlantic coast (Bay of Biscay, Pertuis Charentais), the southern North Sea and German Bight (Wadden Sea trinational SAC), and the north-western Mediterranean (Catalan coast, Ebro Delta). Each site carries an EEA-published Standard Data Form (SDF) listing the Annex I habitat types and Annex II species present, which is used to compute a per-site biodiversity weight.
```

### Intervention (I) (textarea, required)

The intervention or exposure being examined. Discipline-level concept.

```
Coupled wave hindcasting at the storm landfall using the WAVERYS global ocean wave reanalysis from the Copernicus Marine Service (product ID GLOBAL_MULTIYEAR_WAV_001_032). WAVERYS uses MFWAM (a third-generation spectral wave model derived from WAM by Meteo-France), forced by ERA5 winds, assimilating altimeter significant wave height and Sentinel-1 SAR directional spectra, on a 0.2-degree (~22 km) global grid at 3-hourly resolution. The intervention is methodological: WAVERYS represents the choice to compute the wave field globally with a uniformly-parameterised production model and downsample to the site polygon.
```

### Comparison (C) (textarea, required)

The comparison or control condition. Discipline-level concept.

```
Coupled wave hindcasting at the storm landfall using the regional CMEMS wave reanalysis matched to each storm's basin: IBI_MULTIYEAR_WAV_005_006 (Iberia-Biscay-Ireland, 1/36 degree about 3 km, MFWAM) for Xynthia; NWSHELF_REANALYSIS_WAV_004_015 (North-West European Shelf, 1.5 km on the shelf, WAVEWATCH III) for Xaver; MEDSEA_MULTIYEAR_WAV_006_012 (Mediterranean, 1/24 degree about 4 km, Med-WAV derived from MFWAM) for Gloria. The comparison condition represents the choice to compute the wave field with a basin-specific, higher-resolution production model. Both conditions are operationally validated against in-situ buoys via published CMEMS QUID documents.
```

### Outcome (O) (textarea, required)

What outcomes are being measured. The kind of measurement, not the value.

```
Difference in biodiversity exposure attribution between the two wave products. Operationalised as the biodiversity-weighted fraction of Natura 2000 marine sites where the inter-product significant-wave-height delta during the storm window exceeds threshold X — the joint observational noise floor X equals the square root of the sum of the squared CMEMS QUID validation RMSE values of WAVERYS and the matched regional product, approximately 0.4 metres across all three regions. Per-site biodiversity weight is log1p of (number of Annex I habitats plus number of Annex II species) from the EEA Standard Data Form (additive, so bird Special Protection Areas with Annex II species but no Annex I habitat listing are not zero-weighted). The outcome is reported per-storm and aggregated across the panel; supplementary sensitivity analyses report a fixed-threshold variant (X equals 0.5 metres) and a relative-threshold variant (X equals 10 percent of storm-peak Hs at the site).
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 01.
