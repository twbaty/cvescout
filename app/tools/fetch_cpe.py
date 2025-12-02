import json
import time
import sys
import urllib.request
import urllib.parse
from app.db import SessionLocal
from app.models import CPEDictionary

API_URL = "https://services.nvd.nist.gov/rest/json/cpes/2.0"
API_KEY = ""   # ← PUT YOUR API KEY HERE


def fetch_page(keyword, start_index=0):
    """Fetch a single page of CPE results."""
    params = {
        "keywordSearch": keyword,
        "startIndex": start_index,
        "resultsPerPage": 2000
    }

    url = API_URL + "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "apiKey": API_KEY
        }
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_all(keyword):
    """Fetch all CPE entries for a given keyword."""
    print(f">>> Fetching CPEs for keyword: {keyword}")
    results = []

    start = 0
    while True:
        data = fetch_page(keyword, start)
        cpes = data.get("products", [])
        results.extend(cpes)

        total = data.get("totalResults", 0)
        print(f"    downloaded {len(results)}/{total}")

        if len(results) >= total:
            break

        start += 2000
        time.sleep(1.2)  # NVD rate limit

    return results


def import_cpes(keyword):
    db = SessionLocal()

    try:
        entries = fetch_all(keyword)
        print(f">>> Importing {len(entries)} CPE records...")

        for item in entries:
            cpe23 = item.get("cpe", {})
            if not cpe23:
                continue

            part = cpe23.get("part")
            vendor = cpe23.get("vendor")
            product = cpe23.get("product")
            version = cpe23.get("version")

            uri = f"cpe:2.3:{part}:{vendor}:{product}:{version}"

            db.add(
                CPEDictionary(
                    vendor=vendor or "",
                    product=product or "",
                    version=version or "",
                    cpe_uri=uri
                )
            )

        db.commit()
        print(">>> Import completed.")
    except Exception as e:
        db.rollback()
        print("ERROR:", e)
    finally:
        db.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.tools.fetch_cpe <keyword>")
        print("Example: python -m app.tools.fetch_cpe windows")
        sys.exit(1)

    keyword = sys.argv[1]
    import_cpes(keyword)


if __name__ == "__main__":
    main()
