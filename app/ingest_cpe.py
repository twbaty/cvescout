#/app/ingest_cpe.py
import gzip
import json
import requests
from sqlalchemy import select
from app.db import SessionLocal
from app.models import CPEDictionary

CPE_URL = "https://services.nvd.nist.gov/rest/json/cpes/2.0?resultsPerPage=2000&startIndex={}"

def save_cpe(entry, db):
    cpe = entry.get("cpeName")
    if not cpe:
        return

    uri = cpe.get("cpeName")

    # Check if exists
    existing = db.execute(
        select(CPEDictionary).where(CPEDictionary.cpe_uri == uri)
    ).scalar_one_or_none()

    fields = {
        "cpe_uri": uri,
        "part": cpe.get("part"),
        "vendor": cpe.get("vendor"),
        "product": cpe.get("product"),
        "version": cpe.get("version"),
        "update": cpe.get("update"),
        "edition": cpe.get("edition"),
        "language": cpe.get("language"),
        "sw_edition": cpe.get("swEdition"),
        "target_sw": cpe.get("targetSw"),
        "target_hw": cpe.get("targetHw"),
        "other": cpe.get("other"),
        "titles": json.dumps(entry.get("titles", [])),
        "deprecated": entry.get("deprecated", False),
    }

    if existing:
        for k, v in fields.items():
            setattr(existing, k, v)
    else:
        db.add(CPEDictionary(**fields))


def fetch_all_cpe():
    db = SessionLocal()
    index = 0
    total = 1

    print(">>> Syncing CPE dictionary from NVD…")

    while index < total:
        url = CPE_URL.format(index)
        r = requests.get(url, timeout=30)
        data = r.json()

        total = data["totalResults"]
        entries = data.get("products", [])

        print(f"   → Batch {index} / {total}, items={len(entries)}")

        for item in entries:
            save_cpe(item, db)

        db.commit()
        index += 2000

    db.close()
    print(">>> Done.")
