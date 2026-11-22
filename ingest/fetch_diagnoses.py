"""Look up the meaning of the most common ICD-9 diagnosis codes with the NLM REST API."""

import csv
import json
import logging
import time
from collections import Counter
from pathlib import Path

import requests

RAW_DIR = Path("data/raw")
CLAIM_FILES = [
    RAW_DIR / "DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.csv",
    RAW_DIR / "DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.csv",
]
OUTPUT_FILE = RAW_DIR / "icd9_descriptions.json"
API_URL = "https://clinicaltables.nlm.nih.gov/api/icd9cm_dx/v3/search"
TOP_N = 500

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def top_codes(n):
    """Count the primary diagnosis code on every claim and return the n most common."""
    counts = Counter()
    for path in CLAIM_FILES:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                code = row["ICD9_DGNS_CD_1"]
                if code:
                    counts[code] += 1
    log.info("Found %d different codes on %d claims", len(counts), sum(counts.values()))
    return [code for code, count in counts.most_common(n)]

def lookup(code, retries=3):
    """Ask the API what one code means. Try again if the call fails."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(API_URL, params={"terms": code}, timeout=10)
            response.raise_for_status()
            total, codes, extra, details = response.json()
            for found_code, detail in zip(codes, details):
                if found_code == code:
                    return detail[1].strip()
            return None
        except requests.RequestException as error:
            log.warning("Try %d of %d failed for %s: %s", attempt, retries, code, error)
            time.sleep(2 ** attempt)
    log.error("Giving up on %s", code)
    return None


def main():
    descriptions = {}
    if OUTPUT_FILE.exists():
        descriptions = json.loads(OUTPUT_FILE.read_text())
        log.info("Loaded %d saved descriptions", len(descriptions))

    for i, code in enumerate(top_codes(TOP_N), start=1):
        if descriptions.get(code):
            continue
        descriptions[code] = lookup(code)
        if i % 50 == 0:
            log.info("Looked up %d of %d codes", i, TOP_N)
            OUTPUT_FILE.write_text(json.dumps(descriptions, indent=2))
        time.sleep(0.1)

    OUTPUT_FILE.write_text(json.dumps(descriptions, indent=2))
    found = sum(1 for d in descriptions.values() if d)
    log.info("Saved %d codes (%d with a description) to %s", len(descriptions), found, OUTPUT_FILE)


if __name__ == "__main__":
    main()