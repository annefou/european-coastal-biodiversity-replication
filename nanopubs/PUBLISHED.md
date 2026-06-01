# Published FORRT nanopublication chain

This study's claim, its evidence, and its relationship to prior work are not just in this Jupyter Book — they are published as a chain of six atomic, cryptographically-signed nanopublications on the [Science Live platform](https://platform.sciencelive4all.org). Each step is independently citable and has its own URI; the chain is composable (downstream work can extend, qualify, or dispute individual steps without re-running the whole study).

## The chain at a glance

```
PICO question → AIDA → FORRT Claim → Replication Study → Replication Outcome → CiTO Citation
```

All six steps were published on **2026-06-01** and the chain has been verified internally consistent and externally resolving (Loveland 2024 DOI, software + data Zenodo concept DOIs) — see the `/verify-chain` report in the repository.

## Chain

| Step | Template | URI | Published |
|---|---|---|---|
| 01 | PICO question | <https://w3id.org/sciencelive/np/RAyX0cVVf8V-77Tz3AGRL08NiFgnBNGRlbRHedy-feUJQ> | 2026-06-01 |
| 02 | AIDA Sentence | <https://w3id.org/sciencelive/np/RARcOylTL-GAZq3UelKv_z3mAWBA1PWaHJQ2h41oE_sro> | 2026-06-01 |
| 03 | FORRT Claim | <https://w3id.org/sciencelive/np/RAhbrg-k2r9ExMkbhAJbtd1lXkO9Y36map0kIXvn6vyCk> | 2026-06-01 |
| 04 | FORRT Replication Study | <https://w3id.org/sciencelive/np/RAd29Za27oQerxSXwxoGtT1sCzaGXvv3D7bPkaEhaSoAw> | 2026-06-01 |
| 05 | FORRT Replication Outcome | <https://w3id.org/sciencelive/np/RAwrIP5nKIk8Qh7WeMs8z6HHVGssLVAkHDeI8nSB4LUK8> | 2026-06-01 |
| 06 | CiTO Citation | <https://w3id.org/sciencelive/np/RAEXzZcCXiwsNf19NbXvilwwxnFU5IvkplzWTNiNmT70A> | 2026-06-01 |

## What each step says

- **01 PICO question** — *Does the choice of CMEMS wave reanalysis product change biodiversity exposure attribution at European Natura 2000 marine sites during storm landfall?* Comparative (Causation): WAVERYS global vs the matched regional CMEMS products (IBI, North-West Shelf, Mediterranean) at coastal marine SAC/SPA polygons.
- **02 AIDA** — the atomic declarative version of the finding: *"Replacing a global ocean wave reanalysis with a matched higher-resolution regional wave reanalysis changes the storm-wave exposure attributed to European coastal Natura 2000 marine sites."* Grounded by the Zenodo data deposit + the four CMEMS product DOIs.
- **03 FORRT Claim** — types the AIDA as a `descriptive pattern` claim (observed cross-site distribution of inter-product disagreement). Linked back to Loveland et al. 2026 as source.
- **04 Replication Study** — Replication (different methodology / conditions): three-storm panel, native-grid per-product sampling, three-tier site classification, biodiversity-weighted fraction differs as headline. Deviations from Loveland 2024 (inter-product surrogate; European coastal biodiversity domain; native-grid; shared-ERA5 non-independence) recorded.
- **05 Replication Outcome** — verdict **Validated** (Moderate confidence). 73 % of biodiversity-weighted resolvable sites show attribution differing at X = 0.4 m, robust across the threshold sweep, present in all three regimes (Xaver 83 %, Gloria 82 %, Xynthia 60 %). Repository identifier is the software Zenodo concept DOI [10.5281/zenodo.20473380](https://doi.org/10.5281/zenodo.20473380); the data deposit DOI is [10.5281/zenodo.20364376](https://doi.org/10.5281/zenodo.20364376).
- **06 CiTO Citation** — `qualifies` Loveland et al. 2024 ([10.1016/j.ocemod.2024.102387](https://doi.org/10.1016/j.ocemod.2024.102387)): the adequacy of a coarser or simplified wave representation is application- and regime-dependent. Also `extends` the prior [coastal-rom replication chain](https://w3id.org/sciencelive/np/RAuvGPQk_nxEcBWzADcLnyfqgjJ9Hr2aSWxwof2sDAung).

## How to view and fetch

**Human-readable view** — open any URI in the Science Live viewer:

```
https://platform.sciencelive4all.org/np/?uri=<full-URI>
```

**Citing** — use the URI itself (the `https://w3id.org/sciencelive/np/RA…` form). It is a persistent identifier intended to survive the underlying server choice.

**Programmatic fetch of the raw signed TriG.** The nanopub specification says you should be able to content-negotiate against the persistent URI (`curl -H "Accept: application/trig" <URI>`); as of June 2026 the Science Live resolver returns the viewer HTML regardless of `Accept`, so that route does not yet work. Until it does, the Knowledge Pixels registry serves the TriG directly via:

```
GET https://registry.knowledgepixels.com/np/<RA-hash>.trig
```

(GET only — the same endpoint currently rejects HEAD. The KP registry is one specific nanopub server; if it is unavailable, the same nanopub can be fetched from any other server in the nanopub network that has replicated it.)

## Drafts and form structure

Per-step drafts (the field-by-field source used when publishing) are in [`nanopubs/drafts/`](drafts/); the platform form structure is documented in [`docs/forrt-form-fields.md`](../docs/forrt-form-fields.md).
