# app/tools/fetch_cpe.py

import gzip
import json
import urllib.request
from app.db import SessionLocal
from app.models import CPEDictionary

CPE_URL = "https://nvd.nist.gov/feeds/json/cpe/1.0/nvdcpelist.json.gz"


def fetch_and_import():
    print(">>> Downloading CPE dictionary...")

    # Download compressed JSON
    response = urllib.request.urlopen(CPE_URL)
    compressed_data = response.read()

    print(">>> Decompressing...")
    data = gzip.decompress(compressed_data)

    print(">>> Parsing JSON...")
    parsed = json.loads(data)

    items = parsed.get("cpeItems", [])
    print(f">>> Found {len(items)} CPE entries")

    db = SessionLocal()

    try:
        print(">>> Clearing existing CPE dictionary...")
        db.query(CPEDictionary).delete()

        count = 0
        for item in items:
            meta = item.get("cpe23Uri", "")

            # CPE format: cpe:2.3:a:microsoft:office:365:::
            parts = meta.split(":")
            if len(parts) < 5:
                continue

            _, _, part, vendor, product, version, *rest = parts + [None] * 7

            cpe_entry = CPEDictionary(
                vendor=vendor or "",
                product=product or "",
                version=version or "",
                cpe_uri=meta
            )

            db.add(cpe_entry)
            count += 1

        db.commit()
        print(f">>> Imported {count} CPE records.")

    except Exception as e:
        db.rollback()
        print("!!! ERROR:", e)
    finally:
        db.close()


if __name__ == "__main__":
    fetch_and_import()
