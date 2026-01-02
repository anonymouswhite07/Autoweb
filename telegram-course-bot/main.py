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

        # 🖼️ HANDLE IMAGE (Base64 for MongoDB Storage)
        # Check if message has a photo to upload
        if event.message.photo:
            print("🖼️ Downloading image from Telegram...")
            
            # Download image to memory (BytesIO)
            from io import BytesIO
            import base64
            
            image_bytes = BytesIO()
            await client.download_media(event.message.photo, file=image_bytes)
            image_bytes.seek(0)
            
            # Convert to Base64
            image_base64 = base64.b64encode(image_bytes.read()).decode('utf-8')
            
            # Create data URI for HTML img tag
            course["image"] = f"data:image/jpeg;base64,{image_base64}"
            print(f"✅ Image converted to Base64 (size: {len(image_base64)} chars)")
            
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
