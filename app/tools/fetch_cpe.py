#app/tools/fetch_cpe.py
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
PAGE_SIZE = 2000   # Max allowed


def api_get(start_index):
    params = {
        "resultsPerPage": PAGE_SIZE,
        "startIndex": start_index,
        "apiKey": API_KEY
    }

    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "cvescout/1.0"})

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_and_import():
    if not API_KEY:
        print("ERROR: Missing NVD_API_KEY environment variable.")
        return

    print(">>> Fetching CPE records from NVD API...")

    db = SessionLocal()
    db.query(CPEDictionary).delete()
    db.commit()

    start = 0
    total = 0

    while True:
        print(f">>> Fetching page at index {start}...")
        data = api_get(start)

        items = data.get("products", [])
        if not items:
            break

        for entry in items:
            c = entry.get("cpe", {})
            uri = c.get("cpeName")
            if not uri:
                continue

            row = CPEDictionary(
                vendor=c.get("cpeVendor", ""),
                product=c.get("cpeProduct", ""),
                version=c.get("cpeVersion", ""),
                cpe_uri=uri,
            )
            db.add(row)
            total += 1

        db.commit()

        total_results = data.get("totalResults", 0)
        start += PAGE_SIZE

        if start >= total_results:
            break

        time.sleep(1.2)

    db.close()
    print(f">>> DONE. Imported {total} CPE entries.")


if __name__ == "__main__":
    fetch_and_import()
