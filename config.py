import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DB_PATH = os.environ.get(
    "CVESCOUT_DB",
    str(BASE_DIR / "cve_scout.db")
)

NVD_API_KEY = os.environ.get("NVD_API_KEY", "")
NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
