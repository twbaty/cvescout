import gzip
import json
import urllib.request

from app.db import SessionLocal
from app.models import CPEDictionary

CPE_URL = (
    "https://csrc.nist.gov/csrc/media/Projects/national-vulnerability-database/"
    "data-feeds/json/cpe/official-cpe-dictionary_v2.3.json.gz"
)

def fetch_and_import():
    print(">>> Downloading CPE dictionary...")

    # ---- Download .gz ----
    response = urllib.request.urlopen(CPE_URL)
    gz_data = response.read()

    print(f">>> Downloaded {len(gz_data):,} bytes (compressed)")

    # ---- Decompress ----
    json_data = gzip.decompress(gz_data).decode("utf-8")
    data = json.loads(json_data)

    items = data.get("matches", [])
    print(f">>> Parsed {len(items):,} CPE entries")

    db = SessionLocal()
    inserted = 0

    try:
        # Optional: wipe old entries
        db.query(CPEDictionary).delete()

        for item in items:
            cpe23 = item.get("cpe23Uri", "")
            parts = cpe23.split(":")

            vendor = parts[3] if len(parts) > 3 else ""
            product = parts[4] if len(parts) > 4 else ""
            version = parts[5] if len(parts) > 5 else ""

            db.add(CPEDictionary(
                vendor=vendor,
                product=product,
                version=version,
                cpe_uri=cpe23
            ))
            inserted += 1

        db.commit()
        print(f">>> Inserted {inserted:,} CPE records into DB.")

    except Exception as e:
        db.rollback()
        print("!!! ERROR importing CPEs:", e)

    finally:
        db.close()


if __name__ == "__main__":
    fetch_and_import()
