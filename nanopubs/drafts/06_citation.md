# 06 — CiTO Citation

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.

**Description:** *"Declare citations between papers or other works, using Citation Typing Ontology"*

## Field-by-field draft

### Identifier for the citing creative work (text input, required)

URI of the Outcome published in step 05. Pull from `nanopubs/PUBLISHED.md`.

```
<Outcome URI from nanopubs/PUBLISHED.md step 05 — publish 05 first, then paste here>
```

### List citations (repeatable group, required ≥1)

#### Citation 1 — qualifies the prior paper

##### Citation Type (dropdown)

`qualifies`. **Deliberately decoupled from the mechanical verdict→CiTO mapping.** The Outcome's validation status is `Validated` (the PICO claim is well supported, in all three regimes, robustly), which would mechanically map to `confirms` — but the chain does not confirm Loveland: it qualifies them in a different domain and regime. We tested the analogous product-/resolution-choice question for biodiversity exposure at European coastal Natura 2000 sites and found the choice matters at 73 percent of resolvable biodiversity-weighted sites; Loveland argued reduced-order source terms are efficacious for a coupled wave-circulation model in the Gulf of Mexico. Same broad question (does a simplified wave representation suffice?), different application, different answer. `qualifies` captures that honestly; `confirms` would be wrong.

```
qualifies
```

##### DOI or other URL of the cited work (text input)

```
https://doi.org/10.1016/j.ocemod.2024.102387
```

#### Citation 2 — extends the prior FORRT chain (optional but recommended)

This new chain builds on the prior Coastal-ROM replication of Loveland et al. 2024 (the chain registered in `CITATION.cff` `references:`). Linking it makes the constellation navigable.

##### Citation Type (dropdown)

```
extends
```

##### DOI or other URL of the cited work (text input)

```
https://w3id.org/sciencelive/np/RAuvGPQk_nxEcBWzADcLnyfqgjJ9Hr2aSWxwof2sDAung
```

> If the platform's CiTO dropdown rejects a nanopub URI for the cited work (some deployments expect a DOI/paper URL), drop Citation 2 and keep only Citation 1 (the Loveland `qualifies`). The prior-chain link is then preserved via `CITATION.cff` `references:` and the `/import-from-nanopub` provenance.

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 06.

This completes the six-step FORRT chain. Optional next layers:

- **Research Software** (`drafts/07_research_software.md`) — if the repo *produces* a reusable software artefact. This repo is a one-off replication study, not a reusable tool, so step 07 is **not applicable** (the reusable upstream artefacts — `copernicusmarine`, `geopandas`, `xesmf` — are not ours to describe).
- **Research Synthesis** (`drafts/08_synthesis.md`) — only if this chain is bound with others under a shared property.
