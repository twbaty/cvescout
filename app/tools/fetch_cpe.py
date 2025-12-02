#app/tools/fetch_cpe.py
import gzip
import json
import urllib.request
from app.db import SessionLocal
from app.models import CPEDictionary

CPE_URL = (
    "https://nvd.nist.gov/feeds/json/cpe/2.3/nvdcpes-1.0.json.gz"
)

def fetch_and_import_cpe():
    print("Downloading CPE dictionary…")
    resp = urllib.request.urlopen(CPE_URL)
    raw = gzip.decompress(resp.read())

    data = json.loads(raw)
    items = data.get("matches", [])

    print(f"Received {len(items)} CPE entries.")

    db = SessionLocal()

    # wipe the dictionary first (optional)
    db.query(CPEDictionary).delete()

    count = 0
    for entry in items:
        cpe_uri = entry.get("cpe23Uri")
        parts = entry.get("cpe_name", [{}])[0].get("cpe_name", "")

        # vendor/product/version parsing
        # cpe:/a:microsoft:office:16  → split on ':'
        vendor, product, version = "", "", ""
        try:
            fields = cpe_uri.split(":")
            vendor = fields[3]
            product = fields[4]
            version = fields[5]
        except Exception:
            pass

        db.add(CPEDictionary(
            vendor=vendor,
            product=product,
            version=version,
            cpe_uri=cpe_uri
        ))
        count += 1

    db.commit()
    db.close()

    print(f"Imported {count} CPE records.")
