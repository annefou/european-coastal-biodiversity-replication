# Snakefile — European coastal biodiversity replication pipeline.
#
# Each rule wraps a jupytext notebook executed in place so the notebooks
# remain the source of truth and `snakemake --cores 1` end-to-end works.
#
# Usage:
#   snakemake --cores 1            # run everything
#   snakemake --cores 1 -n         # dry run
#   snakemake --cores 1 figures    # just the final figures step

# Storms that the four notebooks actually process. To enable Xaver / Gloria,
# update ACTIVE_STORMS here AND in each notebook (they read their own list).
ACTIVE_STORMS = ["xynthia", "xaver", "gloria"]

NOTEBOOKS = "notebooks"
DATA = "data"
RESULTS = "results"
FIGURES = "figures"


rule all:
    input:
        f"{FIGURES}/main_result.png",
        f"{FIGURES}/headline_stats_bars.png",
        f"{FIGURES}/biodiversity_vs_delta.png",
        f"{FIGURES}/threshold_sensitivity.png",
        f"{RESULTS}/headline_stats.csv",
        f"{RESULTS}/per_site_delta.csv",
        f"{RESULTS}/threshold_sensitivity.csv",


# ---------- 01: Data download ----------
# Per CLAUDE.md § Self-contained data downloads — every input is fetched
# from a citable source (CMEMS, EEA). CMEMS reads
# ~/.copernicusmarine/.copernicusmarine-credentials (created from
# COPERNICUS_CREDENTIALS_BASE64 in CI).
rule data_download:
    output:
        expand(f"{DATA}/raw/waverys_{{storm}}.nc", storm=ACTIVE_STORMS),
        expand(f"{DATA}/raw/regional_{{storm}}.nc", storm=ACTIVE_STORMS),
        f"{DATA}/raw/Natura2000_end2024.zip",
        f"{DATA}/raw/sources.json",
    log:
        f"{RESULTS}/logs/01_data_download.log",
    shell:
        "cd {NOTEBOOKS} && jupytext --to notebook --execute 01_data_download.py 2>&1 | tee ../{log}"


# ---------- 02: Data clean ----------
rule data_clean:
    input:
        expand(f"{DATA}/raw/waverys_{{storm}}.nc", storm=ACTIVE_STORMS),
        expand(f"{DATA}/raw/regional_{{storm}}.nc", storm=ACTIVE_STORMS),
        f"{DATA}/raw/Natura2000_end2024.zip",
    output:
        expand(f"{DATA}/clean/{{storm}}_aligned.nc", storm=ACTIVE_STORMS),
        expand(f"{DATA}/clean/{{storm}}_regional_native.nc", storm=ACTIVE_STORMS),
        expand(f"{DATA}/clean/{{storm}}_n2000_sites.parquet", storm=ACTIVE_STORMS),
    log:
        f"{RESULTS}/logs/02_data_clean.log",
    shell:
        "cd {NOTEBOOKS} && jupytext --to notebook --execute 02_data_clean.py 2>&1 | tee ../{log}"


# ---------- 03: Analysis ----------
rule analysis:
    input:
        expand(f"{DATA}/clean/{{storm}}_aligned.nc", storm=ACTIVE_STORMS),
        expand(f"{DATA}/clean/{{storm}}_n2000_sites.parquet", storm=ACTIVE_STORMS),
    output:
        f"{RESULTS}/per_site_delta.csv",
        f"{RESULTS}/headline_stats.csv",
        f"{RESULTS}/threshold_sensitivity.csv",
        f"{RESULTS}/summary.csv",
    log:
        f"{RESULTS}/logs/03_analysis.log",
    shell:
        "cd {NOTEBOOKS} && jupytext --to notebook --execute 03_analysis.py 2>&1 | tee ../{log}"


# ---------- 04: Figures ----------
rule figures:
    input:
        f"{RESULTS}/per_site_delta.csv",
        f"{RESULTS}/headline_stats.csv",
        f"{RESULTS}/threshold_sensitivity.csv",
        expand(f"{DATA}/clean/{{storm}}_aligned.nc", storm=ACTIVE_STORMS),
        expand(f"{DATA}/clean/{{storm}}_regional_native.nc", storm=ACTIVE_STORMS),
        expand(f"{DATA}/clean/{{storm}}_n2000_sites.parquet", storm=ACTIVE_STORMS),
    output:
        f"{FIGURES}/main_result.png",
        f"{FIGURES}/headline_stats_bars.png",
        f"{FIGURES}/biodiversity_vs_delta.png",
        f"{FIGURES}/threshold_sensitivity.png",
    log:
        f"{RESULTS}/logs/04_figures.log",
    shell:
        "cd {NOTEBOOKS} && jupytext --to notebook --execute 04_figures.py 2>&1 | tee ../{log}"
