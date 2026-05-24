#!/usr/bin/env python3
"""Fast path: fetch the pinned data intermediates from Zenodo.

Resolves the data deposit's *concept* DOI to its latest version, downloads
`data_deposit.zip`, verifies its checksum, and unpacks the `raw/`, `clean/`, and
`results/` trees into the repository so the analysis + figure notebooks can run
without re-downloading anything from CMEMS / EEA.

    pixi run python scripts/fetch_intermediates.py

This is the counterpart to scripts/build_data_deposit.py (which produced the
deposit) and to notebooks/01_data_download.py (the full from-source path). It is
used by the `ECB_DATA_MODE=zenodo` fast path and by CI / the Jupyter Book, which
have no CMEMS credentials.

Deposit: https://doi.org/10.5281/zenodo.20364376 (concept DOI, all versions)
"""
from __future__ import annotations

import hashlib
import tempfile
import time
import zipfile
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent

# Concept DOI / record — stable across versions; always resolves to the latest.
ZENODO_CONCEPT_RECID = "20364376"
ZENODO_CONCEPT_DOI = "10.5281/zenodo.20364376"

# Top-level dirs inside data_deposit.zip → where they land in the repo.
PLACEMENT = {"raw": "data/raw", "clean": "data/clean", "results": "results"}


def _latest_record() -> dict:
    """Resolve the concept record to its latest published version (InvenioRDM)."""
    base = f"https://zenodo.org/api/records/{ZENODO_CONCEPT_RECID}"
    # Preferred: the versions/latest endpoint. Fall back to links.latest.
    r = requests.get(f"{base}/versions/latest", timeout=60)
    if r.status_code == 200:
        return r.json()
    r = requests.get(base, timeout=60)
    r.raise_for_status()
    latest_url = r.json().get("links", {}).get("latest")
    if not latest_url:
        return r.json()
    r = requests.get(latest_url, timeout=60)
    r.raise_for_status()
    return r.json()


def _download_to(url: str, dest: Path, checksum: str | None, retries: int = 3) -> None:
    """Stream `url` to `dest`, verifying md5 if advertised; retry on timeout.

    Streaming to disk (not into memory) + a per-read timeout makes the 74 MB
    download robust against Zenodo stalls that broke a single non-streamed GET.
    """
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            md5 = hashlib.md5()
            with requests.get(url, stream=True, timeout=(30, 120)) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        f.write(chunk)
                        md5.update(chunk)
            if checksum and checksum.startswith("md5:"):
                want = checksum.split(":", 1)[1]
                if md5.hexdigest() != want:
                    raise RuntimeError(
                        f"Checksum mismatch: got md5:{md5.hexdigest()}, expected {checksum}"
                    )
            return
        except (requests.RequestException, RuntimeError) as e:
            last_err = e
            print(f"  attempt {attempt}/{retries} failed ({e}); retrying…")
            time.sleep(3 * attempt)
    raise SystemExit(f"Download failed after {retries} attempts: {last_err}")


def main() -> None:
    print(f"Resolving Zenodo concept DOI {ZENODO_CONCEPT_DOI} …")
    rec = _latest_record()
    print(f"  latest version: {rec.get('doi')}  (record {rec.get('id')})")

    files = {f["key"]: f for f in rec.get("files", [])}
    if "data_deposit.zip" not in files:
        raise SystemExit(
            f"Expected data_deposit.zip in the record; found {list(files)}"
        )
    fobj = files["data_deposit.zip"]
    url = fobj["links"].get("content") or fobj["links"]["self"]
    size_mb = fobj.get("size", 0) / 1e6
    print(f"  downloading data_deposit.zip ({size_mb:.0f} MB) …")

    extracted = 0
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "data_deposit.zip"
        _download_to(url, zip_path, fobj.get("checksum"))
        print("  checksum OK" if fobj.get("checksum") else "  (no checksum advertised)")
        with zipfile.ZipFile(zip_path) as zf:
            for member in zf.namelist():
                if member.endswith("/"):
                    continue
                top = member.split("/", 1)[0]
                dest_root = PLACEMENT.get(top)
                if dest_root is None:
                    continue  # DATA_PROVENANCE.md, MANIFEST.sha256 — skip placement
                dest = REPO / dest_root / member.split("/", 1)[1]
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zf.read(member))
                extracted += 1

    print(f"\nPlaced {extracted} files into data/raw, data/clean, results/.")
    print("Analysis is ready: run notebooks 03_analysis.py and 04_figures.py "
          "(01/02 are not needed on this fast path).")


if __name__ == "__main__":
    main()
