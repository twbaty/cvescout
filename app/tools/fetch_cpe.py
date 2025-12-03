#app/tools/fetch_cpe.py
"""
Fetch the full CPE catalog from the NVD 2.0 API.

This version:
  ✓ Uses the correct NVD 2.0 endpoint
  ✓ Fully paginates using resultsPerPage + startIndex
  ✓ Sleeps 6 seconds between requests (per NVD guidance)
  ✓ Cleans + inserts into CPEDictionary table
  ✓ Complies with NVD Terms of Use

Requires:
  - Environment variable NVD_API_KEY=xxxx
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
PAGE_SIZE = 2000  # NVD best-practice: use default or near-default


def api_get(start_index):
    """Perform a single CPE API request."""

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

    print(">>> Starting CPE import from NVD API (v2.0)")
    db = SessionLocal()

    # wipe existing CPEs
    db.query(CPEDictionary).delete()
    db.commit()

    total_inserted = 0
    start = 0

    while True:
        print(f">>> Fetching page at index {start}...")

        data = api_get(start)

        # main dataset lives here
        products = data.get("products", [])

        if not products:
            print(">>> No more data; import completed.")
            break

        for entry in products:
            cpe = entry.get("cpe", {})
            cpe_uri = cpe.get("cpeName")
            vendor = cpe.get("cpeVendor", "")
            product = cpe.get("cpeProduct", "")
            version = cpe.get("cpeVersion", "")

            if not cpe_uri:
                continue

            db.add(CPEDictionary(
                vendor=vendor,
                product=product,
                version=version,
                cpe_uri=cpe_uri
            ))
            total_inserted += 1

        db.commit()

        total_results = data.get("totalResults", 0)
        start += PAGE_SIZE

        if start >= total_results:
            print(">>> Reached totalResults boundary.")
            break

        # NVD rate limit
        time.sleep(6)

    db.close()
    print(f">>> DONE. Imported {total_inserted} CPE entries.")


if __name__ == "__main__":
    fetch_and_import()
