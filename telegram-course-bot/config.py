import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

try:
    SOURCE_CHANNEL = int(os.getenv("SOURCE_CHANNEL"))
except (ValueError, TypeError):
    SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL")

TARGET_CHANNEL = int(os.getenv("TARGET_CHANNEL"))

WEBSITE_API = os.getenv("WEBSITE_API")
WEBSITE_BASE = os.getenv("WEBSITE_BASE")

print("🌐 WEBSITE_API =", WEBSITE_API)
print("📁 ENV PATH USED =", ENV_PATH)
