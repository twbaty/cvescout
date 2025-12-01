import argparse
from .db import get_session
from .models import Impact, Product, CVE, ImpactStatus


def daily():
    with next(get_session()) as session:
        new_impacts = (
            session.query(Impact)
            .filter(Impact.status == ImpactStatus.new)
            .all()
        )

        if not new_impacts:
            print("No new impacts.")
            return

        grouped = {}
        for imp in new_impacts:
            prod = imp.product
            cve = imp.cve
            grouped.setdefault(prod, []).append(cve)

        for prod, cves in grouped.items():
            print(f"\n{prod.name} ({prod.version})")
            for cve in cves:
                print(f"  {cve.cve_id} – CVSS {cve.cvss_v3_score}: {cve.summary}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["daily"], default="daily")
    args = parser.parse_args()

    if args.mode == "daily":
        daily()


if __name__ == "__main__":
    main()
