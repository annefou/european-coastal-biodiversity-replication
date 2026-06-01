# 02 — AIDA Sentence

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.

**Form heading:** *"AIDA Sentence — Make structured scientific claims following the AIDA model"*

## Field-by-field draft

### AIDA sentence (textarea, required)

Atomic, Independent, Declarative, Absolute. One empirical finding. Must end with a full stop.

> _One finding only: that the wave-product choice changes the exposure attribution. The magnitude, the regime-dependence, and the threshold robustness are evidence — they live in the Outcome (step 05), not here._

```
Replacing a global ocean wave reanalysis with a matched higher-resolution regional wave reanalysis changes the storm-wave exposure attributed to European coastal Natura 2000 marine sites.
```

### Select related topics/tags (dropdown, optional)

Predefined topic vocabulary — labels to pick from the dropdown (pick whichever the dropdown offers; these are the intended topics):

```
marine biodiversity; significant wave height; Natura 2000; Copernicus Marine Service; storm impacts
```

### Relates to this nanopublication (text input, required)

URI of the nanopub the AIDA derives from. Question-rooted chain → the **PICO** URI (step 01).

```
<PICO URI from nanopubs/PUBLISHED.md step 01 — publish 01 first, then paste here>
```

### Supported by datasets (repeatable group, optional)

DOIs/URLs of datasets that ground the AIDA claim.

- `https://doi.org/10.5281/zenodo.20364376`  — this study's pinned input + intermediate data deposit (concept DOI)
- `https://doi.org/10.48670/moi-00022`  — WAVERYS global wave reanalysis (CMEMS)
- `https://doi.org/10.48670/moi-00030`  — IBI regional wave reanalysis (CMEMS)
- `https://doi.org/10.48670/moi-00060`  — North-West Shelf wave reanalysis (CMEMS)
- `https://doi.org/10.48670/mds-00376`  — Mediterranean wave reanalysis (CMEMS)

### Supported by other publications (repeatable group, optional)

*(skip — optional)* The prior work this study qualifies (Loveland et al. 2024) is cited via the **CiTO Citation** in step 06, not here. Leaving this group empty also sidesteps the known platform bug below (datasets + other-publications populated together).

> **Known platform bug (2026-04-26):** if both *Supported by datasets* AND *Supported by other publications* are populated and publishing fails, fall back to publishing this AIDA via Nanodash. The URI namespace becomes `https://w3id.org/np/...` (still valid and citable). Here only *datasets* is populated, so this should not trigger.

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 02.
