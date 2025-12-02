import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

# ---- DATABASE ----
DB_NAME = os.environ.get("DB_NAME", "cve_scout.db")
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), DB_NAME)

SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"

# ---- NVD API KEY ----
NVD_API_KEY = os.environ.get("NVD_API_KEY", "")
