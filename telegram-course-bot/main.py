from telethon import TelegramClient, events
from config import *
from parser import parse_course
from poster import post_to_channel
from website import save_course
from utils import slugify


client = TelegramClient("user_session_clean", api_id, api_hash)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    try:
        text = event.message.text
        # print(f"\n📩 New message received from {event.chat_id}")

        course = parse_course(event.message)
        
        if not course:
            # print("⚠️ Message ignored (parser returned None)")
            return

        print(f"📝 Parsed course: {course['title']} | Status: {course.get('status')}")

        if not course.get("udemy_link"):
            print("⚠️ Course ignored or needs manual review (No Link)")
            return

        # ✅ CREATE SLUG FIRST (CRITICAL)
        course["slug"] = slugify(course["title"])

        # 🖼️ HANDLE IMAGE (Local Storage)
        # Check if message has a photo to upload
        if event.message.photo:
            print("🖼️ Downloading image from Telegram...")
            # Define path
            file_name = f"{course['slug']}.jpg"
            save_path = os.path.join("..", "app", "static", "images", file_name)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Download
            await client.download_media(event.message.photo, file=save_path)
            
            # Save relative path to DB (compatible with our templates)
            course["image"] = f"/static/images/{file_name}"
            print(f"✅ Saved local image: {course['image']}")
            
        else:
             # Fallback to OG if no photo
             course["image"] = course.get("image_url")

        print("SENDING TO WEBSITE:", course)

        save_course(course, WEBSITE_API)
        
        # Pass the actual media object to the poster to send to Telegram
        await post_to_channel(client, TARGET_CHANNEL, course, WEBSITE_BASE, media=event.message.media)

        print("✅ Course posted successfully (Stateless)")

    except Exception as e:
        print("❌ ERROR in handler:", e)

async def main():
    print("👤 Authenticating with User Session...")
    await client.start()
    
    print(f"🤖 Connected to Telegram! Listening on {SOURCE_CHANNELS}...")
    print("------------------------------------------------")
    await client.run_until_disconnected()

def start_bot():
    import asyncio
    asyncio.run(main())

if __name__ == '__main__':
    start_bot()
