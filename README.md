# european-coastal-biodiversity-replication

[![CI](https://github.com/annefou/european-coastal-biodiversity-replication/actions/workflows/ci.yml/badge.svg)](https://github.com/annefou/european-coastal-biodiversity-replication/actions/workflows/ci.yml)
[![Jupyter Book](https://github.com/annefou/european-coastal-biodiversity-replication/actions/workflows/jupyter-book.yml/badge.svg)](https://annefou.github.io/european-coastal-biodiversity-replication/)
[![Docker](https://github.com/annefou/european-coastal-biodiversity-replication/actions/workflows/docker.yml/badge.svg)](https://github.com/annefou/european-coastal-biodiversity-replication/pkgs/container/european-coastal-biodiversity-replication)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/{{ZENODO_DOI}}.svg)]({{ZENODO_DOI}})
[![FAIR4RS](https://img.shields.io/badge/FAIR4RS-conformant-brightgreen)](docs/fair4rs-checklist.md)
[![FORRT](https://img.shields.io/badge/FORRT-replication-blue)](https://forrt.org/)
[![Science Live](https://img.shields.io/badge/Science%20Live-nanopub%20chain-purple)](nanopubs/PUBLISHED.md)
[![RO-Crate](https://img.shields.io/badge/RO--Crate-1.2-orange)](ro-crate-metadata.json)

> **Does the choice of CMEMS wave reanalysis product change biodiversity exposure attribution at European Natura 2000 marine sites during storm landfall?**

A question-rooted FORRT replication study. It compares the global **WAVERYS** wave reanalysis against the matched **regional CMEMS** products (IBI, North-West Shelf, Mediterranean) over three storms — Xynthia (2010, French Atlantic), Xaver (2013, North Sea), Gloria (2020, NW Mediterranean) — and asks whether the product choice changes which coastal Natura 2000 sites are flagged as wave-exposed. It **qualifies** the source-term-efficacy argument of Loveland et al. 2024 ([10.1016/j.ocemod.2024.102387](https://doi.org/10.1016/j.ocemod.2024.102387)) by testing the analogous product-choice question in a different domain (biodiversity exposure) and three physically distinct regimes.

It produces a reproducible computational pipeline, a Zenodo-archived data deposit + software release with citable DOIs, and a FORRT-tagged nanopublication chain on the [Science Live platform](https://platform.sciencelive4all.org).

### What this study found

The product choice **materially changes exposure attribution, but strongly regime-dependently**. Across 327 biodiversity-weighted Natura 2000 marine sites, the storm-window peak wave-height difference exceeds the joint observational noise floor (~0.4 m) at **26.7%** of sites — but this splits sharply by regime: **robust in the shallow North Sea** (Xaver, 38.5% and still 34% at a stricter 0.8 m threshold), intermediate in the Mediterranean (Gloria, 29.4%), and **marginal in the open Bay of Biscay** (Xynthia, 17.2%, collapsing to 3% at 0.8 m). The effect is strongest where nearshore wave transformation dominates and the two products share least model lineage. Outcome: **PartiallySupported**.

---

## Quick start

**Full reproduction from source** (needs free Copernicus Marine credentials — see [`data/README.md`](data/README.md) — and downloads several GB incl. the EEA Natura 2000 archive):

```bash
git clone https://github.com/annefou/european-coastal-biodiversity-replication.git
cd european-coastal-biodiversity-replication
pixi install
pixi run snakemake --cores 1
```

**Fast path** (no credentials, ~74 MB) — fetch the pinned intermediates from the Zenodo data deposit ([10.5281/zenodo.20364376](https://doi.org/10.5281/zenodo.20364376)) and run only the analysis + figures:

```bash
pixi run python scripts/fetch_intermediates.py
pixi run python notebooks/03_analysis.py
pixi run python notebooks/04_figures.py
```

(Pixi resolves `pixi.toml` against the per-platform `pixi.lock`, installs the env under `.pixi/`, and provides `pixi run` for any task without needing an `activate` step.)

Or with Docker (runs the fast path out of the box):

```bash
docker run --rm ghcr.io/annefou/european-coastal-biodiversity-replication:latest
```

The Jupyter Book version is at <https://annefou.github.io/european-coastal-biodiversity-replication/>.

## Built from a template

This repository was created from [`sciencelivehub/forrt-replication-template`](https://github.com/sciencelivehub/forrt-replication-template). The template ships an operating manual for AI assistants ([`CLAUDE.md`](CLAUDE.md), [`AGENTS.md`](AGENTS.md)), domain conventions ([`DOMAIN.md`](DOMAIN.md)), and reference docs (`docs/`) so that an AI working only inside this repository can guide a researcher from "paper PDF + GitHub repo" to "published FORRT chain + Zenodo DOI" with no other context.

If you are reading this in a fresh fork, run [`/init-template`](.claude/skills/init-template/SKILL.md) inside Claude Code to substitute the placeholder tokens with your details. (For other AI tools, see [`docs/ai-portability.md`](docs/ai-portability.md).)

After `/init-template`, do these one-time setup steps to enable the full CI/CD path:

- **Enable GitHub Pages** at *Settings → Pages → Source: GitHub Actions*. Until enabled, the Jupyter Book build runs but the deploy step is skipped (CI stays green).
- The CI workflows ship with **scaffold-detection guards** — they run end-to-end only after you implement Phase 2 (the `notebooks/*.py` files). Until then they exit early with an informative `::notice::` and the badges stay green.

## Repository structure

```
.
├── CLAUDE.md / AGENTS.md       # operating manual for AI assistants
├── DOMAIN.md                   # domain flavour (current: biodiversity + earth observation)
├── USER_PREFERENCES.md         # per-user style (edit on first clone)
├── README.md                   # this file
├── LICENSE                     # MIT
├── CITATION.cff                # how to cite
├── codemeta.json               # software metadata (CodeMeta-2.0)
├── ro-crate-metadata.json      # research object packaging (RO-Crate 1.2)
├── pixi.toml + pixi.lock       # pinned dependencies (single source of truth; lockfile is per-platform)
├── Dockerfile                  # container build
├── Snakefile                   # pipeline orchestration
├── myst.yml + index.md         # Jupyter Book scaffold
├── paper/                      # the source paper PDF
├── data/                       # downloaded artefacts (gitignored)
├── notebooks/                  # jupytext .py pipeline (01–04)
├── nanopubs/                   # FORRT chain drafts + published-URI registry
├── docs/                       # reference material
├── figures/                    # curated figures used in the Jupyter Book
├── .github/workflows/          # CI, Jupyter Book, Docker
└── .claude/                    # Claude Code agents, skills, sandbox config
```

## What you get

This template bakes in conventions that took multiple replications to discover. By using it, you inherit:

- **FAIR4RS conformance** — see [`docs/fair4rs-checklist.md`](docs/fair4rs-checklist.md) for the principle-by-principle mapping.
- **Self-contained data downloads** — the first notebook fetches everything; no manual data prep.
- **`pixi.toml` + `pixi.lock` as single source of truth** — local dev, Docker, and CI all install the same per-platform-pinned env.
- **`prefix-dev/setup-pixi`-based CI** — caches the env, runs the pipeline with `pixi run`, executes notebooks via a glob, fails fast on a stale lockfile.
- **Jupyter Book deployment** — auto-deploys to GitHub Pages with `BASE_URL` set correctly. (Don't put `base_url` in `myst.yml` — MyST silently ignores it.)
- **Docker + GHCR + Zenodo image archival** — `release` trigger pushes to GHCR and (optionally) archives to Zenodo for long-term preservation.
- **RO-Crate packaging** — the entire repo is a navigable Research Object via `ro-crate-metadata.json` (Process Run Crate + Workflow RO-Crate profiles).
- **Six-step FORRT chain workspace** — `nanopubs/drafts/` has a field-by-field skeleton for each step. `nanopubs/PUBLISHED.md` is the URI registry.
- **Layered AI guidance** — `CLAUDE.md` (universal) + `DOMAIN.md` (swappable per field) + `USER_PREFERENCES.md` (per-user). See [`docs/ai-portability.md`](docs/ai-portability.md) for non-Claude AI tools.
- **Sandbox by default** — `.claude/settings.json` denies file ops outside the repo, so a fresh AI session can't accidentally read `~/.ssh/` or write to `/etc/`.

## The six FORRT chain steps

A complete FORRT chain has six steps published on [platform.sciencelive4all.org](https://platform.sciencelive4all.org):

```
Quote-with-comment  →  AIDA  →  FORRT Claim  →  Replication Study  →  Replication Outcome  →  CiTO Citation
```

(For question-rooted chains with no upstream paper, replace step 1 with PICO or PCC. See [`docs/chain-decision-tree.md`](docs/chain-decision-tree.md).)

Drafts live in [`nanopubs/drafts/`](nanopubs/drafts/) field-by-field. Published URIs go into [`nanopubs/PUBLISHED.md`](nanopubs/PUBLISHED.md).

Optional further layers:

- **Research Software nanopub** — for reusable upstream tools (not demo repos). See [`docs/forrt-form-fields.md`](docs/forrt-form-fields.md) § Research Software.
- **Research Synthesis nanopub** — when this chain is part of a multi-chain story. See [`docs/forrt-form-fields.md`](docs/forrt-form-fields.md) § Research Synthesis.

## After publishing

When the chain is live and the FAIR4RS checklist is green, drafting an announcement post is the next step. See [`docs/announcement-template.md`](docs/announcement-template.md) for the structural template (vision-piece-first; the worked replication is the payoff, not the lead).

For lower-level nanopub work — retraction, superseding, batch publishing — see [`docs/programmatic-nanopubs.md`](docs/programmatic-nanopubs.md).

## Citation

If you use this work, please cite:

- This software: [`CITATION.cff`](CITATION.cff) → concept DOI [{{ZENODO_DOI}}]({{ZENODO_DOI}})
- The data deposit: [10.5281/zenodo.20364376](https://doi.org/10.5281/zenodo.20364376)
- The prior work this study qualifies (Loveland et al. 2024): [10.1016/j.ocemod.2024.102387](https://doi.org/10.1016/j.ocemod.2024.102387)

Wave data generated using E.U. Copernicus Marine Service Information; biodiversity data © European Environment Agency (Natura 2000). See [`data/README.md`](data/README.md).

## Acknowledgements

This repository was built from [`sciencelivehub/forrt-replication-template`](https://github.com/sciencelivehub/forrt-replication-template), part of the [Science Live platform](https://platform.sciencelive4all.org). The template is licensed MIT and contributions (especially new domain flavours under [`docs/domain-flavours/`](docs/domain-flavours/)) are welcome.
