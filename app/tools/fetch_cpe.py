# app/tools/fetch_cpe.py

import gzip
import json
import urllib.request

from app.db import SessionLocal
from app.models import CPEDictionary

CPE_URL = "https://nvd.nist.gov/feeds/json/cpe/dictionary/official-cpe-dictionary_v2.3.json.gz"

def fetch_and_import():
    print(">>> Downloading CPE dictionary...")
    response = urllib.request.urlopen(CPE_URL)
    data = gzip.decompress(response.read())

    print(">>> Parsing JSON...")
    doc = json.loads(data)

    items = doc.get("matchString", [])
    print(f">>> Found {len(items)} CPE entries")

    db = SessionLocal()

    try:
        inserted = 0

        for entry in items:
            cpe = entry.get("criteria")
            if not cpe:
                continue

            # split URI
            parts = cpe.split(":")
            vendor  = parts[3] if len(parts) > 3 else ""
            product = parts[4] if len(parts) > 4 else ""
            version = parts[5] if len(parts) > 5 else ""

            row = CPEDictionary(
                vendor=vendor,
                product=product,
                version=version,
                cpe_uri=cpe
            )
            db.add(row)
            inserted += 1

        db.commit()
        print(f">>> Imported {inserted} CPE rows")

    except Exception as e:
        db.rollback()
        print("!!! ERROR:", e)

    finally:
        db.close()


if __name__ == "__main__":
    fetch_and_import()
