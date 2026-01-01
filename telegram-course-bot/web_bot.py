import threading
import time
from fastapi import FastAPI
from main import start_bot  # Exposing the bot starter

app = FastAPI()

@app.get("/")
def health():
    return {"status": "bot running"}

def bot_runner():
    while True:
        try:
            print("🤖 Starting Telegram Bot inside Web Service...")
            start_bot()
        except Exception as e:
            print("❌ Bot crashed, restarting in 5s:", e)
            time.sleep(5)

# Run bot in a separate thread so Uvicorn can handle HTTP requests
threading.Thread(target=bot_runner, daemon=True).start()
