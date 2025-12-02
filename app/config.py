# app/config.py
import os
from dotenv import load_dotenv

# Load .env first
load_dotenv()

# -------------------------------------------------------------
# DATABASE LOCATION (single source of truth)
# -------------------------------------------------------------
# If DB_PATH is set in .env, we use it.
# Otherwise we store SQLite DB in the project root, which is correct.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB = f"sqlite:///{os.path.join(ROOT_DIR, 'cvescout.db')}"

DB_PATH = os.environ.get("DB_PATH", DEFAULT_DB)

# -------------------------------------------------------------
# NVD API KEY (must be in environment, never in code)
# -------------------------------------------------------------
NVD_API_KEY = os.environ.get("NVD_API_KEY", "")
