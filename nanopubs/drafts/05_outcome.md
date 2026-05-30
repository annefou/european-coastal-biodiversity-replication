# 05 — FORRT Replication Outcome

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.
>
> **Numbers verified** against `results/headline_stats.csv`, `results/per_site_delta.csv`, `results/threshold_sensitivity.csv` and `notebooks/03_analysis.py` after the native-grid + three-tier rework (2026-05-30). See `docs/verify-before-drafting.md`.

## Field-by-field draft

### Short URI suffix for outcome ID (text input, required)

Slug. Use kebab-case.

```
wave-product-changes-exposure-native-three-tier
```

### Plain-text label for the outcome (text input, required)

Descriptive title.

```
Wave-product choice changes biodiversity exposure attribution at most resolvable European Natura 2000 marine sites — robustly and across three regimes — primarily as a resolution effect
```

### Search for a FORRT replication study (search/select, required)

URI of the Replication Study published in step 04. Pull from `nanopubs/PUBLISHED.md`.

```
<URI of step 04 — not yet published>
```

### Repository URL (text input, required)

> Per `docs/` + auto-memory, `hasOutcomeRepository` should be the **software Zenodo concept DOI**, which is minted at the Phase 4 GitHub release. Replace the GitHub URL below with that DOI at Phase 4. (The *data* deposit has its own concept DOI — `10.5281/zenodo.20364376` — but that is the data record, not the software archive.)

```
https://github.com/annefou/european-coastal-biodiversity-replication
```

### Completion date (date picker, required)

```
2026-05-30
```

### Validation status (dropdown, required)

- [x] **Validated**
- [ ] PartiallySupported
- [ ] Contradicted

The PICO claim — that the choice between the global WAVERYS and the matched regional CMEMS wave reanalysis changes the biodiversity exposure attributed to coastal Natura 2000 marine sites — is well supported across all three storm regimes, robustly across reasonable thresholds, and via two complementary mechanisms (continuous magnitude differences where both products resolve, and categorically decisive cases where one product resolves the site and the other places it on land). See the CiTO Citation note in step 06 — the CiTO relation to Loveland et al. 2024 is **`qualifies`** (intentionally decoupled from the mechanical Validated → `confirms` mapping), because the chain qualifies prior work in a new domain rather than confirming a numerically-comparable result.

### Confidence level (dropdown, required)

> Verify the exact dropdown vocabulary against the live form before publishing.

```
Moderate
```

Moderate — not high — because (a) ~16% of biodiversity-weighted marine sites are out of scope for both basin-scale products (Tier 3), (b) WAVERYS and the regionals share ERA5 forcing and partial physics, so the inter-product delta is conservative and primarily a *resolution* effect rather than two independent models disagreeing, and (c) the three-storm panel samples three regimes but is not a controlled separation of depth, grid resolution, and model physics.

### Describe the overall conclusion about the original claim (textarea, required)

```
The choice between the global WAVERYS wave reanalysis and the matched regional CMEMS product (IBI, North-West Shelf, Mediterranean) changes the biodiversity exposure attributed to coastal Natura 2000 marine sites at 73 percent of biodiversity-weighted resolvable sites across the three-storm panel. The effect is present and majoritarian in all three regimes — Xaver (North Sea) 83 percent, Gloria (NW Mediterranean) 82 percent, Xynthia (French Atlantic / open Bay of Biscay) 60 percent — and robust across the threshold sweep (0.84 down to 0.58 over X = 0.2 to 0.8 metres). The 73 percent decomposes cleanly into 44 percentage points of magnitude disagreement at sites both products resolve (peak-Hs delta exceeds the joint observational noise floor) and 29 percentage points of categorically decisive sites where one product places the site in open water and the other on land or sub-wave-field. Because WAVERYS and the regional products share ERA5 forcing and partial model lineage, the inter-product delta is conservative (positively correlated errors) and is dominated by RESOLUTION rather than by two independent models disagreeing on physics — for a user picking one product to compute coastal exposure, the resolution-and-physics bundle is what they pick, and that bundle changes the answer at most sites. Relative to Loveland et al. 2024 (reduced-order source terms efficacious for a coupled wave-circulation model in the Gulf of Mexico), this qualifies rather than confirms or disputes: the adequacy of a coarser or simplified wave representation is application- and regime-dependent — for biodiversity exposure attribution at coastal Natura 2000 sites in shallow shelf seas and complex coastal Mediterranean it is not negligible, and it is non-trivial even in the open Bay of Biscay.
```

### Describe the evidence that supports your conclusion (textarea, required)

```
Three storms, 327 biodiversity-weighted coastal Natura 2000 marine sites (Xynthia 111, Xaver 78, Gloria 138). Each product is sampled on its OWN native grid per site polygon — WAVERYS at 0.2 degrees and the matched regional at its native fine grid (1/36 degree IBI, ~1.5 km NWS, 1/24 degree Mediterranean) — without regridding the regional onto the WAVERYS grid (which would have smoothed away the nearshore difference being measured and dropped about half the sites to coastal land-mask NaN). For each site and each product, peak Hs over the storm window is the mean of the wet cells whose centres fall inside the polygon, with a single-cell containing-centroid fallback for sub-grid sites; if neither yields a wet value, the product does not resolve the site (no nearest-wet-cell buffer outward — a 1-cell buffer on the 0.2-degree WAVERYS grid would pull open-ocean values ~22 km onto sheltered coastal sites).

Three tiers result per site: both products resolve (Tier 1, continuous delta defined), only one product resolves (Tier 2, product choice categorically decisive), neither resolves (Tier 3, out of scope). 276 of 327 sites are resolvable (Tier 1 plus Tier 2), giving 84 percent biodiversity-weighted coverage; the remaining 16 percent are reported as a coverage limitation. Per-site biodiversity weight is log1p(Annex I habitats + Annex II species) from the EEA Standard Data Form (additive, so bird Special Protection Areas with species but no Annex I habitat listing are not zero-weighted).

Headline — biodiversity-weighted decomposition of resolvable sites at the threshold X = 0.4 metres (joint observational noise floor from CMEMS QUID validation RMSE, region-specific 0.46 / 0.39 / 0.41 metres):

- Aggregate (276 sites): 27 percent agree (Tier 1, |delta| <= 0.4 m), 44 percent magnitude-disagree (Tier 1, |delta| > 0.4 m), 29 percent decisive (Tier 2). "Attribution differs" = magnitude + decisive = 73 percent.
- Xynthia (99 resolvable / 111): 40 / 31 / 29 percent → 60 percent differ. Median |delta| at Tier-1 sites = 0.40 m; max = 2.97 m.
- Xaver (67 / 78): 17 / 46 / 37 percent → 83 percent differ. Median |delta| = 1.80 m; max = 7.26 m.
- Gloria (110 / 138): 18 / 58 / 25 percent → 82 percent differ. Median |delta| = 0.59 m; max = 2.49 m.

Tier-2 (decisive) split, aggregate: 38 sites where the fine regional resolves a site WAVERYS calls land (regional adds nearshore exposure the coarse product misses); 41 sites where WAVERYS reports a value the fine regional masks as sub-wave-field (the coarse product over-attributes open-ocean Hs to a sheltered site). Both directions are legitimate product-choice-decisive cases for the claim.

Robustness — threshold-X sweep over resolvable sites (results/threshold_sensitivity.csv, figures/threshold_sensitivity.png): aggregate 0.84 → 0.58 across X = 0.2 to 0.8 metres; Xaver 0.90 → 0.79 (nearly flat — Tier-2 floor); Gloria 0.92 → 0.57; Xynthia 0.74 → 0.47. The Tier-2 contribution is threshold-independent and forms a substantial floor everywhere, which is the structural reason the result is robust.

Diagnostic — the biodiversity-weight versus delta scatter (figures/biodiversity_vs_delta.png) shows no systematic correlation between site biodiversity richness and |delta| — biodiversity-rich sites are neither preferentially more nor less affected by the product choice. This rules out the weighting choice as the driver of the headline.
```

### Describe what limits the conclusions of the study (textarea, optional)

```
1. Coverage limit. About 16 percent of biodiversity-weighted marine sites are too sub-grid for both basin-scale wave products (Tier 3, neither resolves); the headline describes the resolvable subset. Studies of those very sheltered or intertidal sites need a nested coastal-wave model, not a basin reanalysis. This bounds the claim to "marine sites the basin-scale products can place in water."

2. Shared error / non-independence. WAVERYS and the three regional products are not independent: all are ERA5-forced (explicitly for NWS and the Mediterranean product) and two of three regionals share MFWAM lineage with WAVERYS. Their errors are positively correlated, so the inter-product delta is *conservative* and the X = 0.4 metres threshold (computed assuming independence as the root-sum-square of QUID RMSE values) *overestimates* the true noise floor. The 44 percentage points of magnitude disagreement is, if anything, an underestimate of where the products differ beyond observational uncertainty. The honest framing is that the difference is dominated by RESOLUTION — the fine regional resolves nearshore structure WAVERYS cannot — rather than by two independent models disagreeing on physics.

3. Tier-2 is real but asymmetric. The 29 percentage points of categorically decisive sites split into 38 "regional resolves, WAVERYS sees land" (the fine product adds real nearshore exposure) and 41 "WAVERYS resolves, regional sees land/sheltered" (the coarse product over-attributes open-ocean Hs to a sheltered site the fine product correctly masks). Both directions are legitimate "product choice changes attribution," but they have opposite scientific direction — readers who only care about cases where the regional adds information should focus on the regional-only sub-tier.

4. Inter-product surrogate. This compares two operational wave reanalyses, not a coupled wave-circulation model run by us with full versus reduced-order source terms. It tests whether the production-product choice propagates to a downstream biodiversity exposure metric — not the source-term physics of Loveland et al. directly. The inter-product path was chosen to keep compute tractable.

5. One storm per basin. The regime gradient (North Sea ≈ NW Mediterranean > open Bay of Biscay, set by coastal complexity and depth) is suggestive but confounds depth, grid resolution, and model physics; it is not a controlled separation of those factors.

6. Coarse exposure proxy. Peak Hs at the site polygon omits storm surge, wave period and direction, duration, and any ecological vulnerability of the habitats and species present. The site polygons are the EEA 1:100,000-generalised vector product (EPSG:3035).

7. Simple biodiversity weight. log1p(Annex I habitats + Annex II species) is an unweighted count; it does not account for conservation status, species vulnerability, or site area. The diagnostic scatter shows no biodiversity-versus-delta correlation, so the weighting choice does not drive the headline.
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 05.
