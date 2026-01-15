from telethon import TelegramClient
from config import api_id, api_hash
import asyncio

async def main():
    async with TelegramClient("user_session_clean", api_id, api_hash) as client:
        print("Fetching dialogs...")
        async for dialog in client.iter_dialogs():
            print(f"Name: {dialog.name}, ID: {dialog.id}")

if __name__ == '__main__':
    try:
        import platform
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
