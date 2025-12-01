"""
Match new CVEs to products.
"""

from .db import get_session
from .models import Product, CVE, CVECPE, Impact, ImpactStatus
from datetime import datetime


def versions_match(prod_version, start, start_incl, end, end_incl):
    # v1-based dumb compare for now ― implement real semver/cpe range later.
    if not prod_version:
        return False
    if start and (prod_version < start if not start_incl else prod_version < start):
        return False
    if end and (prod_version > end if not end_incl else prod_version > end):
        return False
    return True


def run_match():
    with next(get_session()) as session:
        products = session.query(Product).filter_by(active=True).all()
        cves = session.query(CVE).all()

        for cve in cves:
            for cpe in cve.cpe_entries:

                # Extract Product fields from CPE (later: proper parser)
                cpe_uri = cpe.cpe_uri.lower()

                for prod in products:
                    if prod.cpe_uri and prod.cpe_uri.lower() in cpe_uri:
                        hit = True
                    else:
                        hit = (
                            prod.vendor.lower() in cpe_uri and
                            prod.name.lower() in cpe_uri and
                            versions_match(
                                prod.version,
                                cpe.version_start,
                                cpe.version_start_incl,
                                cpe.version_end,
                                cpe.version_end_incl
                            )
                        )

                    if hit:
                        existing = (
                            session.query(Impact)
                            .filter_by(product_id=prod.id, cve_id=cve.cve_id)
                            .first()
                        )

                        if not existing:
                            impact = Impact(
                                product_id=prod.id,
                                cve_id=cve.cve_id,
                                status=ImpactStatus.new,
                                first_seen=datetime.utcnow(),
                                last_seen=datetime.utcnow(),
                            )
                            session.add(impact)
                        else:
                            existing.last_seen = datetime.utcnow()

        session.commit()


if __name__ == "__main__":
    run_match()
