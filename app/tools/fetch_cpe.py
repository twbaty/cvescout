# app/tools/fetch_cpe.py
"""
Fetches the full CPE catalog from the NVD API v2 and stores it
into the CPEDictionary table.

Requires environment variable: NVD_API_KEY
"""

import os
import time
import json
import urllib.request
import urllib.parse

from app.db import SessionLocal
from app.models import CPEDictionary


API_KEY = os.getenv("NVD_API_KEY")
BASE_URL = "https://services.nvd.nist.gov/rest/json/cpes/2.0"
PAGE_SIZE = 2000   # NVD allows up to 2000 per page


def api_get(start_index):
    """Call NVD API with paging."""
    params = {
        "resultsPerPage": PAGE_SIZE,
        "startIndex": start_index,
        "apiKey": API_KEY,
    }

    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "cvescout/1.0"})

    with urllib.request.urlopen(req) as resp:
        data = resp.read().decode("utf-8")
        return json.loads(data)


def fetch_and_import():
    if not API_KEY:
        print("ERROR: Missing NVD_API_KEY environment variable.")
        return

    print(">>> Fetching CPE records from NVD API...")

    db = SessionLocal()
    db.query(CPEDictionary).delete()   # wipe old entries
    db.commit()

    total_collected = 0
    start_index = 0

    while True:
        print(f">>> Fetching page starting at {start_index}...")
        data = api_get(start_index)

        cpe_data = data.get("products", [])
        if not cpe_data:
            break

        for entry in cpe_data:
            cpe = entry.get("cpe", {})
            uri = cpe.get("cpeName")
            vendor = cpe.get("cpeVendor", "")
            product = cpe.get("cpeProduct", "")
            version = cpe.get("cpeVersion", "")

            if not uri:
                continue

            row = CPEDictionary(
                vendor=vendor,
                product=product,
                version=version,
                cpe_uri=uri,
            )
            db.add(row)
            total_collected += 1

        db.commit()

        # Paging logic
        total_results = data.get("totalResults", 0)
        start_index += PAGE_SIZE

        if start_index >= total_results:
            break

        # Respect NVD rate limits
        time.sleep(1.2)

    db.close()
    print(f">>> DONE. Imported {total_collected} CPE entries.")


if __name__ == "__main__":
    fetch_and_import()
