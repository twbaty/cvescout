# app/tools/fetch_cpe.py
"""
Fetch the official CPE 2.3 dictionary from NVD's static feed.
No paging. No API key. No deprecated endpoints.
"""

import gzip
import json
import tempfile
import urllib.request

from app.db import SessionLocal
from app.models import CPEDictionary

CPE_URL = "https://nvd.nist.gov/feeds/json/cpe/2.3/nvd_cpe_dictionary_2.3.json.gz"


def fetch_and_import():
    print(">>> Starting CPE dictionary import...")
    print(f">>> Downloading: {CPE_URL}")

    # Download feed
    tmp = tempfile.NamedTemporaryFile(delete=False)
    urllib.request.urlretrieve(CPE_URL, tmp.name)

    print(">>> Decompressing JSON...")
    with gzip.open(tmp.name, "rt", encoding="utf-8") as f:
        payload = json.load(f)

    items = payload.get("matches", [])

    print(f">>> Loaded {len(items)} CPE entries from feed.")

    # Import into DB
    db = SessionLocal()
    db.query(CPEDictionary).delete()
    db.commit()

    count = 0
    for item in items:
        cpe23 = item.get("cpe23Uri")
        if not cpe23:
            continue

        vendor = item.get("vendor", "")
        product = item.get("product", "")
        version = item.get("version", "")

        row = CPEDictionary(
            vendor=vendor,
            product=product,
            version=version,
            cpe_uri=cpe23,
        )
        db.add(row)
        count += 1

    db.commit()
    db.close()
    print(f">>> DONE. Imported {count} CPE entries.")


if __name__ == "__main__":
    fetch_and_import()
