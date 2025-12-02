# app/tools/fetch_cpe.py

import gzip
import xml.etree.ElementTree as ET
from urllib.request import urlopen

from app.db import SessionLocal
from app.models import CPEDictionary

CPE_URL = "https://nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.3.xml.gz"


def fetch_and_import():
    print(">>> Downloading CPE dictionary...")

    response = urlopen(CPE_URL)
    data = gzip.decompress(response.read())

    print(">>> Parsing XML...")
    root = ET.fromstring(data)

    ns = {"cpe": "http://cpe.mitre.org/dictionary/2.0"}

    rows = []
    for item in root.findall(".//cpe:generator/cpe:item", ns):
        name = item.get("name")  # cpe:/a:vendor:product:version etc.

        if not name:
            continue

        parts = name.split(":")

        # cpe:/<part>:<vendor>:<product>:<version>:...
        vendor = parts[3] if len(parts) > 3 else ""
        product = parts[4] if len(parts) > 4 else ""
        version = parts[5] if len(parts) > 5 else ""

        rows.append((vendor, product, version, name))

    print(f">>> Parsed {len(rows)} entries. Importing to DB...")

    db = SessionLocal()
    try:
        db.query(CPEDictionary).delete()

        for vendor, product, version, uri in rows:
            db.add(CPEDictionary(
                vendor=vendor,
                product=product,
                version=version,
                cpe_uri=uri
            ))

        db.commit()
        print(">>> DONE. Imported CPE dictionary.")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    fetch_and_import()
