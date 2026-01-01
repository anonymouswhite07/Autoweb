from telethon import TelegramClient, events
from config import *
from parser import parse_course
from poster import post_to_channel
from website import save_course
from utils import slugify

client = TelegramClient("bot_session", api_id, api_hash)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    try:
        text = event.message.text
        print("\n📩 New message received")

        course = parse_course(event.message)
        
        if not course:
            print("⚠️ Message ignored (parser returned None)")
            return

        print(f"📝 Parsed course: {course['title']} | Status: {course.get('status')}")

        if not course.get("udemy_link"):
            print("⚠️ Course ignored or needs manual review (No Link)")
            return

        # ✅ CREATE SLUG FIRST (CRITICAL)
        course["slug"] = slugify(course["title"])

        # 🖼️ HANDLE IMAGE
        if event.message.media:
            print("🖼️ Found media, downloading...")
            path = None
            try:
                # Use slug as filename
                filename = f"{course['slug']}.jpg"
                path = await client.download_media(event.message, file=filename)
                
                # Move to website static folder (Assuming local relative path for Phase 2 local test)
                import shutil
                import os
                
                website_images_dir = "../app/static/images"
                os.makedirs(website_images_dir, exist_ok=True)
                
                dest_path = os.path.join(website_images_dir, filename)
                shutil.move(path, dest_path)
                
                print(f"✅ Image moved to {dest_path}")
                course["image"] = filename
                
            except Exception as e:
                print(f"⚠️ Image processing failed: {e}")
                # clean up if move failed but download succeeded
                if path and os.path.exists(path):
                    os.remove(path)
        else:
             course["image"] = None

        save_course(course, WEBSITE_API)
        await post_to_channel(client, TARGET_CHANNEL, course, WEBSITE_BASE)

        print("✅ Course posted successfully")

    except Exception as e:
        print("❌ ERROR in handler:", e)

async def main():
    await client.start()
    print(f"🤖 Connected to Telegram! Listening on {SOURCE_CHANNEL}...")
    print("------------------------------------------------")
    await client.run_until_disconnected()

def start_bot():
    import asyncio
    asyncio.run(main())

if __name__ == '__main__':
    start_bot()
