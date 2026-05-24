FROM ghcr.io/prefix-dev/pixi:0.68.1

LABEL org.opencontainers.image.source="https://github.com/annefou/european-coastal-biodiversity-replication"
LABEL org.opencontainers.image.description="Replication study container for european-coastal-biodiversity-replication"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Install the pinned environment first (separate from source copy so the lock
# layer is cached across source-only edits).
COPY pixi.toml pixi.lock /app/
RUN pixi install --locked

COPY . /app

# Default: the credential-free fast path — fetch the pinned intermediates from
# the Zenodo data deposit, then run analysis + figures. This makes
# `docker run --rm <image>` produce results out of the box (no CMEMS account).
#
# For the full from-source reproduction (downloads from CMEMS + EEA), mount
# credentials and override the command, e.g.:
#   docker run -v ~/.copernicusmarine:/root/.copernicusmarine <image> \
#     pixi run snakemake --cores 1
# See data/README.md for per-dataset credential setup.
CMD ["sh", "-c", "pixi run python scripts/fetch_intermediates.py && pixi run python notebooks/03_analysis.py && pixi run python notebooks/04_figures.py"]
