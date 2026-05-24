# 05 — FORRT Replication Outcome

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.
>
> **Numbers verified** against `results/headline_stats.csv`, `results/threshold_sensitivity.csv`, and `notebooks/03_analysis.py` on 2026-05-24 (additive biodiversity weight, commit `2cd131e`; three-storm panel). See `docs/verify-before-drafting.md`.

## Field-by-field draft

### Short URI suffix for outcome ID (text input, required)

Slug. Use kebab-case.

```
wave-product-exposure-regime-dependent
```

### Plain-text label for the outcome (text input, required)

Descriptive title.

```
Wave-product choice changes biodiversity exposure attribution at a quarter of European Natura 2000 marine sites — robustly in shallow shelf seas, marginally in the open ocean
```

### Search for a FORRT replication study (search/select, required)

URI of the Replication Study published in step 04. Pull from `nanopubs/PUBLISHED.md`.

```
<URI of step 04 — not yet published>
```

### Repository URL (text input, required)

> Per `docs/` + auto-memory, `hasOutcomeRepository` should be the **software Zenodo concept DOI**, which is minted at the Phase 4 GitHub release. Replace the GitHub URL below with that DOI at Phase 4. (The *data* deposit already has a concept DOI — `10.5281/zenodo.20364376` — but that is the data record, not the software archive.)

```
https://github.com/annefou/european-coastal-biodiversity-replication
```

### Completion date (date picker, required)

```
2026-05-24
```

### Validation status (dropdown, required)

- [ ] Validated
- [x] **PartiallySupported**
- [ ] Contradicted

Maps to the CiTO intention in step 06: PartiallySupported → `qualifies`. The PICO claim (that the wave-product choice changes exposure attribution) holds, but is strongly regime-dependent rather than uniform — hence partial, not full, support.

### Confidence level (dropdown, required)

> Verify the exact dropdown vocabulary against the live form before publishing. "Moderate" is used here (consistent with the prior coastal-rom chain), reflecting a real and threshold-robust signal in the North Sea but a shared-error caveat (see Limitations) that prevents high confidence.

```
Moderate
```

### Describe the overall conclusion about the original claim (textarea, required)

```
The choice between the global WAVERYS wave reanalysis and the matched regional CMEMS product (IBI, North-West Shelf, Mediterranean) materially changes biodiversity exposure attribution at coastal Natura 2000 marine sites, but the effect is strongly regime-dependent rather than uniform. Across the three-storm panel, the storm-window peak significant-wave-height difference between the two products exceeds the joint observational noise floor (approximately 0.4 metres) at 26.7 percent of biodiversity-weighted marine sites. That aggregate masks a wide spread: the difference is large and robust in the shallow North Sea (Storm Xaver — 38.5 percent of biodiversity-weighted sites at the 0.4 metre threshold, and still 34 percent at a much stricter 0.8 metre threshold), intermediate in the north-western Mediterranean (Storm Gloria — 29.4 percent), and marginal in the open Bay of Biscay (Storm Xynthia — 17.2 percent at 0.4 metres, collapsing to 3 percent at 0.8 metres). The PICO claim that the product choice changes exposure attribution is therefore partially supported: it holds robustly where nearshore wave transformation dominates and where the two products share least model lineage (the North-West Shelf product is WAVEWATCH III, versus WAVERYS's MFWAM), and only weakly in open-ocean settings where the two products largely converge. Relative to Loveland et al. 2024 (reduced-order source terms efficacious for a coupled wave-circulation model in the Gulf of Mexico), this qualifies rather than confirms or disputes: the adequacy of a coarser or simplified wave representation is application- and regime-dependent — for biodiversity-exposure attribution at shallow coastal Natura 2000 sites it is not negligible, even if it may be adequate in deeper, open settings.
```

### Describe the evidence that supports your conclusion (textarea, required)

```
Panel: three storms, 327 biodiversity-weighted Natura 2000 marine sites (Xynthia 111, Xaver 78, Gloria 138). Per-site exposure is the polygon-mean peak significant wave height (Hs) over the storm window; the inter-product delta is regional minus WAVERYS, both on the common 0.2-degree WAVERYS grid. Per-site biodiversity weight is log1p(Annex I habitats + Annex II species) from the EEA Standard Data Form (additive, so bird Special Protection Areas are not zero-weighted).

Headline — biodiversity-weighted fraction of sites with |delta Hs| > 0.4 metres: aggregate 26.7 percent (25.2 percent using the region-specific CMEMS QUID noise floors of 0.46 / 0.39 / 0.41 metres); per storm Xynthia 17.2, Xaver 38.5, Gloria 29.4 percent. Median |delta Hs|: Xynthia 0.24, Xaver 1.42, Gloria 0.59 metres; panel maximum 4.88 metres at a North Sea site.

Robustness — threshold-X sweep (results/threshold_sensitivity.csv, figures/threshold_sensitivity.png): Xaver stays between 0.34 and 0.41 across X = 0.2 to 0.8 metres (near-flat — a robust signal); Xynthia falls from 0.30 to 0.03 (steep — a marginal signal driven by near-threshold sites); Gloria falls from 0.36 to 0.15; the aggregate falls from 0.35 to 0.15. The diagnostic biodiversity-weight-versus-delta scatter (figures/biodiversity_vs_delta.png) shows no systematic correlation — biodiversity-rich sites are neither preferentially more nor less affected by the product choice.
```

### Describe what limits the conclusions of the study (textarea, optional)

```
1. Shared error / non-independence. WAVERYS and the three regional products are not independent: all are ERA5-forced (explicitly for the North-West Shelf and Mediterranean products) and two of the three regionals share MFWAM lineage with WAVERYS. The true inter-product disagreement is therefore tighter than the QUID validation RMSE values imply, because those were combined under an independence assumption. The 0.4 metre threshold is consequently conservative, and the reported fractions should be read as "sites where the two production products differ beyond the (independence-assumed) observational floor", not as a clean measure of independent model error.

2. Inter-product surrogate. This compares two operational wave reanalyses, not a coupled wave-circulation model run by us with full versus reduced-order source terms. It tests whether the production-product choice propagates to a downstream biodiversity-exposure metric — not the source-term physics of Loveland et al. directly. The inter-product path was chosen to keep compute tractable.

3. One storm per basin. The regime gradient (North Sea > Mediterranean > Biscay) is suggestive but confounds depth, grid resolution, and model physics; it is not a controlled separation of those factors.

4. Coarse exposure proxy. Peak Hs at the site polygon omits storm surge, wave period and direction, duration, and any ecological vulnerability of the habitats and species present.

5. Spatial generalisation. Site polygons are the EEA 1:100,000-generalised vector product (EPSG:3035); very small sites near the WAVERYS 0.2-degree (~22 km) grid scale fall back to nearest-cell sampling.

6. Simple biodiversity weight. log1p(Annex I habitats + Annex II species) is an unweighted count; it does not account for conservation status, species vulnerability, or site area.
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 05.
