"""Download CMS DE-SynPUF sample files and unzip them into data/raw/."""

import logging
import zipfile
from pathlib import Path

import requests

BASE_URL = (
    "https://www.cms.gov/Research-Statistics-Data-and-Systems/"
    "Downloadable-Public-Use-Files/SynPUFs/Downloads/"
)

FILES = [
    "DE1_0_2008_Beneficiary_Summary_File_Sample_1.zip",
    "DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.zip",
    "DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.zip",
]

RAW_DIR = Path("data/raw")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def download_file(file_name):
    """Download one zip file. Skip it if we already have it."""
    zip_path = RAW_DIR / file_name
    if zip_path.exists():
        log.info("Already downloaded: %s", file_name)
        return zip_path

    url = BASE_URL + file_name
    log.info("Downloading %s", url)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    zip_path.write_bytes(response.content)
    log.info("Saved %s (%.1f MB)", zip_path, zip_path.stat().st_size / 1_000_000)
    return zip_path

def unzip_file(zip_path):
    """Unzip one file into data/raw/ and return the CSV names inside."""
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        zf.extractall(RAW_DIR)
    log.info("Unzipped %s -> %s", zip_path.name, names)
    return names


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for file_name in FILES:
        zip_path = download_file(file_name)
        unzip_file(zip_path)
    log.info("All %d files are ready in %s", len(FILES), RAW_DIR)


if __name__ == "__main__":
    main()