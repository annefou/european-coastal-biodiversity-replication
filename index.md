# european-coastal-biodiversity-replication

> **Does the choice of CMEMS wave reanalysis product change biodiversity exposure attribution at European Natura 2000 marine sites during storm landfall?**

A question-rooted FORRT replication study comparing the global **WAVERYS** wave reanalysis against the matched **regional CMEMS** products (IBI, North-West Shelf, Mediterranean) over three storms — Xynthia (2010), Xaver (2013), Gloria (2020). It **qualifies** Loveland et al. 2024 ([10.1016/j.ocemod.2024.102387](https://doi.org/10.1016/j.ocemod.2024.102387)) by testing the analogous product-choice question in a different domain and three physically distinct regimes.

**Finding:** the product choice changes biodiversity exposure attribution at **73% of resolvable biodiversity-weighted sites** — present in all three regimes (Xaver 83%, Gloria 82%, Xynthia 60%), robust across the threshold sweep, decomposing as 27% agree / 44% magnitude-disagree / 29% categorically decisive (one product places the site in water, the other on land). About 16% of sites are too sub-grid for either basin-scale product (coverage caveat). Outcome: **Validated**; CiTO `qualifies` Loveland 2024.

This repository produces:

- A reproducible computational pipeline (Snakefile + notebooks).
- A FORRT-tagged nanopublication chain on the [Science Live platform](https://platform.sciencelive4all.org), documenting the question, the replication design, and the outcome with full provenance.
- Zenodo-archived data + software releases with citable DOIs.

## Quick start

```bash
git clone https://github.com/annefou/european-coastal-biodiversity-replication.git
cd european-coastal-biodiversity-replication
pixi install
pixi run snakemake --cores 1
```

Or with Docker:

```bash
docker run --rm ghcr.io/annefou/european-coastal-biodiversity-replication:latest
```

## Structure

- `notebooks/` — jupytext `.py` notebooks that drive the pipeline (01 download → 02 clean → 03 analysis → 04 figures).
- `data/` — downloaded by `notebooks/01_data_download.py` (or fetched from the Zenodo deposit), never committed.
- `nanopubs/` — drafts of the FORRT chain field-by-field, plus the published-URI registry.
- `docs/` — operating manuals (FORRT form fields, chain decision tree, claim-type vocabulary).
- `figures/` — figures used in this Jupyter Book.

## Nanopublication chain

The published chain is listed in [`nanopubs/PUBLISHED.md`](nanopubs/PUBLISHED.md). Each step links to its viewer URL on the Science Live platform.

## Citation

If you use this work, please cite:

- This software: [`CITATION.cff`](CITATION.cff) → concept DOI [10.5281/zenodo.20473380](https://doi.org/10.5281/zenodo.20473380).
- The data deposit: [10.5281/zenodo.20364376](https://doi.org/10.5281/zenodo.20364376).
- The prior work this study qualifies (Loveland et al. 2024): [10.1016/j.ocemod.2024.102387](https://doi.org/10.1016/j.ocemod.2024.102387).
