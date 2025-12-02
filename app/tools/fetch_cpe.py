#app/tools/fetch_cpe.py
"""
Fetches the full CPE dictionary from the official NVD bulk data feed.
No paging. No API calls. Fully compliant with NVD Terms.

Source:
https://nvd.nist.gov/products/cpe
"""

import os
import gzip
import json
import urllib.request

from app.db import SessionLocal
from app.models import CPEDictionary

CPE_URL = "https://nvd.nist.gov/feeds/json/cpe/official-cpe-dictionary_v2.3.json.gz"

def download_cpe():
    print(">>> Downloading CPE dictionary...")
    tmp_path = "official-cpe-dictionary.json.gz"
    urllib.request.urlretrieve(CPE_URL, tmp_path)
    return tmp_path

def load_cpe(path):
    print(">>> Decompressing and loading JSON...")
    with gzip.open(path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("matches", [])

def fetch_and_import():
    print(">>> Starting CPE dictionary import...")

    gz_path = download_cpe()
    entries = load_cpe(gz_path)

    db = SessionLocal()
    db.query(CPEDictionary).delete()
    db.commit()

    count = 0
    for item in entries:
        cpe23 = item.get("cpe23Uri")
        if not cpe23:
            continue

        parts = cpe23.split(":")
        vendor = parts[3] if len(parts) > 3 else ""
        product = parts[4] if len(parts) > 4 else ""
        version = parts[5] if len(parts) > 5 else ""

        row = CPEDictionary(
            vendor=vendor,
            product=product,
            version=version,
            cpe_uri=cpe23
        )
        db.add(row)
        count += 1

    db.commit()
    db.close()

    print(f">>> DONE. Imported {count} CPE entries.")

if __name__ == "__main__":
    fetch_and_import()
