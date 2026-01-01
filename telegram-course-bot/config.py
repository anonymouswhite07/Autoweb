import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Handle Multiple Source Channels
SOURCE_CHANNELS = []
raw_sources = os.getenv("SOURCE_CHANNELS", os.getenv("SOURCE_CHANNEL", ""))
for src in raw_sources.split(","):
    src = src.strip()
    if not src: continue
    try:
        # Try as ID
        SOURCE_CHANNELS.append(int(src))
    except ValueError:
        # Keep as username
        SOURCE_CHANNELS.append(src)

TARGET_CHANNEL = int(os.getenv("TARGET_CHANNEL"))

WEBSITE_API = os.getenv("WEBSITE_API")
WEBSITE_BASE = os.getenv("WEBSITE_BASE")

print("🌐 WEBSITE_API =", WEBSITE_API)
print("📁 ENV PATH USED =", ENV_PATH)
