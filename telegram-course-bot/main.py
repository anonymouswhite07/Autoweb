from telethon import TelegramClient, events
from config import *
from parser import parse_course
from poster import post_to_channel
from website import save_course
from utils import slugify

client = TelegramClient("bot_session", api_id, api_hash)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    try:
        text = event.message.text
        print(f"\n📩 New message received from {event.chat_id}")

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
                
                # Save to absolute path inside app/static/images
                import shutil
                import os
                
                # Resolving absolute path to app/static/images relative to this script
                base_dir = os.path.dirname(os.path.abspath(__file__))
                website_images_dir = os.path.join(base_dir, "..", "app", "static", "images")
                os.makedirs(website_images_dir, exist_ok=True)
                
                dest_path = os.path.join(website_images_dir, filename)
                shutil.move(path, dest_path)
                
                print(f"✅ Image moved to {dest_path}")
                # Store full relative URL for website to use as per professional standard
                course["image"] = f"/static/images/{filename}"

                
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
    print(f"🤖 Connected to Telegram! Listening on {SOURCE_CHANNELS}...")
    print("------------------------------------------------")
    await client.run_until_disconnected()

def start_bot():
    import asyncio
    asyncio.run(main())

if __name__ == '__main__':
    start_bot()
