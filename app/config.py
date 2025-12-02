# app/config.py
import os
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")

load_dotenv()

DB_PATH = os.environ.get("DB_PATH", "sqlite:///cvescout.db")

# NVD API key comes ONLY from environment
NVD_API_KEY = os.environ.get("NVD_API_KEY", "")
