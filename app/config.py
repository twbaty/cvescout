# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))

DB_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(BASE_DIR, "cvescout.db")
)

NVD_API_KEY = os.environ.get("NVD_API_KEY", "")
