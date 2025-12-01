#/app/ingest_nvd.py
"""
Daily NVD sync job.
"""

import requests
from datetime import datetime, timedelta
from dateutil import parser
from .db import get_session
from .models import CVE, CVECPE
from .config import NVD_BASE_URL, NVD_API_KEY


def fetch_nvd_modified(days_back=1):
    params = {
        "lastModStartDate": (datetime.utcnow() - timedelta(days=days_back)).isoformat(),
        "resultsPerPage": 2000,
    }

    headers = {}
    if NVD_API_KEY:
        headers["apiKey"] = NVD_API_KEY

    resp = requests.get(NVD_BASE_URL, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def ingest():
    data = fetch_nvd_modified()

    with next(get_session()) as session:
        for item in data.get("vulnerabilities", []):
            cve_data = item["cve"]
            cve_id = cve_data["id"]

            # Upsert CVE
            db_cve = session.query(CVE).filter_by(cve_id=cve_id).first()
            if not db_cve:
                db_cve = CVE(cve_id=cve_id)
                session.add(db_cve)

            db_cve.summary = cve_data.get("descriptions", [{}])[0].get("value")
            metrics = cve_data.get("metrics", {}).get("cvssMetricV31", [])
            if metrics:
                base = metrics[0]["cvssData"]
                db_cve.cvss_v3_score = base.get("baseScore")
                db_cve.cvss_v3_vector = base.get("vectorString")

            db_cve.published_date = parser.parse(cve_data.get("published"))
            db_cve.last_modified_date = parser.parse(cve_data.get("lastModified"))
            db_cve.raw_json = item

            # Clear old CPE entries
            session.query(CVECPE).filter_by(cve_id=cve_id).delete()

            # Insert new CPE entries
            for config in cve_data.get("configurations", []):
                for node in config.get("nodes", []):
                    for match in node.get("cpeMatch", []):
                        entry = CVECPE(
                            cve_id=cve_id,
                            cpe_uri=match["criteria"],
                            vulnerable=match.get("vulnerable", True),
                            version_start=match.get("versionStartExcluding")
                                or match.get("versionStartIncluding"),
                            version_start_incl=bool(match.get("versionStartIncluding")),
                            version_end=match.get("versionEndExcluding")
                                or match.get("versionEndIncluding"),
                            version_end_incl=bool(match.get("versionEndIncluding")),
                        )
                        session.add(entry)

        session.commit()


if __name__ == "__main__":
    ingest()
