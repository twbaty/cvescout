#app/tools/fetch_cpe.py
"""
Fetch the FULL CPE dictionary from MITRE (CPE 2.3 XML).
This avoids NVD API issues and provides a stable, complete dataset.

Source:
https://cpe.mitre.org/data/downloads/official-cpe-dictionary_v2.3.xml

Result:
Populates CPEDictionary table with vendor, product, version, cpe_uri.
"""

import os
import tempfile
import urllib.request
import xml.etree.ElementTree as ET

from app.db import SessionLocal
from app.models import CPEDictionary


CPE_XML_URL = "https://cpe.mitre.org/data/downloads/official-cpe-dictionary_v2.3.xml"


def download_xml():
    """Download the XML file to a temporary path and return path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
    print(f">>> Downloading XML from MITRE:\n    {CPE_XML_URL}")

    urllib.request.urlretrieve(CPE_XML_URL, tmp.name)
    return tmp.name


def parse_and_import(xml_path):
    """Parse the CPE XML and insert into database."""
    print(">>> Parsing XML… this may take a few seconds.")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Namespace used in the XML
    ns = {"cpe": "http://cpe.mitre.org/dictionary/2.0"}

    db = SessionLocal()

    # Wipe old entries
    db.query(CPEDictionary).delete()
    db.commit()

    total = 0

    for item in root.findall("cpe:item", ns):
        meta = item.find("cpe:cpe23-item", ns)
        if meta is None:
            continue

        uri = meta.get("name")  # cpe:2.3:a:microsoft:edge:109.0.1518.55

        # Split into fields
        parts = uri.split(":")
        if len(parts) < 6:
            continue

        vendor = parts[3]
        product = parts[4]
        version = parts[5]

        row = CPEDictionary(
            vendor=vendor,
            product=product,
            version=version,
            cpe_uri=uri,
        )

        db.add(row)
        total += 1

        # Batch commit every 2000 entries for speed
        if total % 2000 == 0:
            db.commit()

    db.commit()
    db.close()

    print(f">>> DONE. Imported {total:,} CPE entries.")


def fetch_and_import():
    print(">>> Starting MITRE CPE import (XML format).")
    xml_path = download_xml()
    parse_and_import(xml_path)


if __name__ == "__main__":
    fetch_and_import()
