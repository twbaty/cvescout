# app/config.py
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "cvescout.db")

load_dotenv()

# Always an absolute sqlite path
DB_PATH = os.environ.get("DB_PATH", DEFAULT_DB_PATH)

# API Key: must come only from environment
NVD_API_KEY = os.getenv("NVD_API_KEY", "")
