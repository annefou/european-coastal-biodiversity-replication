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

The Outcome's validation status is **PartiallySupported** → `qualifies`.

```
qualifies
```

Rationale: the finding (the product choice changes exposure attribution robustly in shallow shelf seas but marginally in the open ocean) neither confirms nor disputes Loveland et al.'s source-term-efficacy argument — it qualifies it: the adequacy of a coarser or simplified wave representation is application- and regime-dependent.

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
