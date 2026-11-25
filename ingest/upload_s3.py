"""Upload the raw CMS files from data/raw/ to the raw/ folder in our S3 bucket."""

import logging
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

BUCKET = "claims-pipeline-53875"
REGION = "us-east-2"
RAW_DIR = Path("data/raw")
S3_FOLDER = "raw/"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

s3 = boto3.client("s3", region_name=REGION)


def already_uploaded(path, key):
    """Return True if S3 already has this file with the same size."""
    try:
        info = s3.head_object(Bucket=BUCKET, Key=key)
    except ClientError as error:
        if error.response["Error"]["Code"] == "404":
            return False
        raise
    return info["ContentLength"] == path.stat().st_size

def upload(path):
    """Upload one file to raw/ in S3. Skip it if it is already there."""
    key = S3_FOLDER + path.name
    if already_uploaded(path, key):
        log.info("Already in S3: %s", key)
        return
    size_mb = path.stat().st_size / 1_000_000
    log.info("Uploading %s (%.1f MB) to s3://%s/%s", path.name, size_mb, BUCKET, key)
    s3.upload_file(str(path), BUCKET, key)
    log.info("Done: %s", key)


def main():
    files = sorted(RAW_DIR.glob("*.csv")) + [RAW_DIR / "icd9_descriptions.json"]
    for path in files:
        upload(path)
    log.info("All %d files are in s3://%s/%s", len(files), BUCKET, S3_FOLDER)


if __name__ == "__main__":
    main()