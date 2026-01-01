import threading
import time
from fastapi import FastAPI
from main import start_bot  # Exposing the bot starter

app = FastAPI()

@app.get("/")
@app.head("/")
def root():
    return {"status": "bot running"}

@app.get("/health")
@app.head("/health")
def health():
    return {"status": "bot healthy"}

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
