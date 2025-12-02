# app/tools/fetch_cpe.py
"""
Fetches the full CPE dictionary from NVD (JSON.gz file)
and loads it into the CPEDictionary table.

This method avoids the deprecated CPE REST API.
"""

import os
import json
import gzip
import urllib.request
import tempfile

from app.db import SessionLocal
from app.models import CPEDictionary

CPE_URL = "https://nvd.nist.gov/feeds/json/cpe/dictionary/official-cpe-dictionary_v2.3.json.gz"


def download_cpe():
    """Download the gzipped CPE dictionary."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json.gz")
    tmp.close()

    print(f">>> Downloading: {CPE_URL}")
    urllib.request.urlretrieve(CPE_URL, tmp.name)
    return tmp.name


def load_json_gz(path):
    """Load and decompress the gzipped JSON."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def fetch_and_import():
    print(">>> Starting CPE dictionary import...")

    gz_path = download_cpe()
    print(">>> Decompressing JSON...")
    data = load_json_gz(gz_path)

    items = data.get("matches", [])
    print(f">>> Total entries in dictionary: {len(items)}")

    db = SessionLocal()
    db.query(CPEDictionary).delete()
    db.commit()

    count = 0

    for entry in items:
        cpe = entry.get("cpe23Uri")
        if not cpe:
            continue

        vendor = entry.get("vendor", "")
        product = entry.get("product", "")
        version = entry.get("version", "")

        row = CPEDictionary(
            vendor=vendor,
            product=product,
            version=version,
            cpe_uri=cpe,
        )
        db.add(row)
        count += 1

        if count % 2000 == 0:
            db.commit()

    db.commit()
    db.close()

    print(f">>> DONE. Imported {count} CPE entries.")


if __name__ == "__main__":
    fetch_and_import()
