# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.environ.get("DB_PATH", "sqlite:///cvescout.db")

# NVD API key comes ONLY from environment
NVD_API_KEY = os.environ.get("NVD_API_KEY", "")
