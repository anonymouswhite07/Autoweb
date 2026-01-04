"""
Updated main.py with Cloudinary image upload support
This replaces local file storage with cloud storage
"""

from telethon import TelegramClient, events
from config import *
from parser import parse_course
from poster import post_to_channel
from website import save_course
from utils import slugify
import cloudinary
import cloudinary.uploader
import os
from io import BytesIO

# Configure Cloudinary (add these to your .env)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

client = TelegramClient("user_session_clean", api_id, api_hash)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    try:
        text = event.message.text

        course = parse_course(event.message)
        
        if not course:
            return

        print(f"📝 Parsed course: {course['title']} | Status: {course.get('status')}")

        if not course.get("udemy_link"):
            print("⚠️ Course ignored or needs manual review (No Link)")
            return

        # ✅ CREATE SLUG FIRST (CRITICAL)
        course["slug"] = slugify(course["title"])

        # 🖼️ HANDLE IMAGE (Cloudinary Upload)
        if event.message.photo:
            print("🖼️ Downloading image from Telegram...")
            
            # Download to BytesIO (memory, not disk)
            image_bytes = BytesIO()
            await client.download_media(event.message.photo, file=image_bytes)
            image_bytes.seek(0)
            
            # Upload to Cloudinary
            print("☁️ Uploading to Cloudinary...")
            upload_result = cloudinary.uploader.upload(
                image_bytes,
                public_id=f"courses/{course['slug']}",
                folder="sucourse",
                overwrite=True,
                resource_type="image"
            )
            
            # Get the secure URL
            course["image"] = upload_result.get("secure_url")
            print(f"✅ Image uploaded to cloud: {course['image']}")
            
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
