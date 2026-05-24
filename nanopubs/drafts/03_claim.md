# 03 — FORRT Claim

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.

**Form heading:** *"FORRT Claim — Declare an original claim according to FORRT, linking it to an AIDA sentence with a specific FORRT type."*

## Field-by-field draft

### Short URI suffix as claim ID (text input, required)

Slug becomes part of the nanopub URI. Use kebab-case.

```
wave-product-changes-exposure-attribution
```

### Label of the claim (text input, required)

A descriptive title (not a sentence). Used for searches/discovery.

```
Wave-product choice changes storm-wave exposure attribution at European Natura 2000 marine sites
```

### Search for an AIDA sentence (search/select, required)

URI of the AIDA published in step 02. Pull from `nanopubs/PUBLISHED.md`.

```
<AIDA URI from nanopubs/PUBLISHED.md step 02 — publish 02 first, then paste here>
```

### Type of FORRT claim (dropdown, required)

Pick one. See `docs/claim-type-vocabulary.md`.

- [ ] computational performance
- [ ] scalability
- [ ] data quality
- [ ] data governance
- [x] **descriptive pattern**
- [ ] model performance
- [ ] statistical significance

Rationale: the claim asserts an **observed empirical relationship** across a population of sites — that the inter-product wave-height difference, biodiversity-weighted, exceeds the observational noise floor at a measurable fraction of Natura 2000 marine sites. That is a `descriptive pattern` (an observed distribution/relationship), not a model-accuracy metric and not a significance-test result. *(Alternative if you prefer the data-pipeline framing: `data quality` — "does the input-product choice preserve the downstream exposure attribution"; `descriptive pattern` is the better fit because the headline is an observed cross-site distribution, not a preprocessing-fidelity claim.)*

### Source URI (text input, optional)

Full URL form: `https://doi.org/...` (NOT bare DOI). The prior work this claim relates to:

```
https://doi.org/10.1016/j.ocemod.2024.102387
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 03.
