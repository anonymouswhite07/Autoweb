from telethon import TelegramClient, events
from config import *
from parser import parse_course
from poster import post_to_channel
from website import save_course
from utils import slugify


# Global client removed to avoid event loop conflicts in threads
# client = TelegramClient("user_session_clean", api_id, api_hash)
# Handlers are now registered inside main()

async def course_handler(event):
    """
    Event handler for new messages. 
    Registered dynamically in main() to ensure robust loop handling.
    """
    # Access client from the event itself to avoid global scope issues
    client = event.client
    
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
    """
    Main entry point. Initializes client on the current running loop.
    """
    print("👤 Authenticating with User Session...")
    
    # Initialize client HERE, inside the async function (uses current loop)
    # Using 'with' block acts as start() and disconnect() automatically
    async with TelegramClient("user_session_clean", api_id, api_hash) as client:
        
        # Register event handler dynamically
        client.add_event_handler(course_handler, events.NewMessage(chats=SOURCE_CHANNELS))
        
        print(f"🤖 Connected to Telegram! Listening on {SOURCE_CHANNELS}...")
        print("------------------------------------------------")
        
        # Keep running
        await client.run_until_disconnected()

def start_bot():
    """
    Entry point for external scripts (like web_bot.py).
    Creates a new loop and runs the main async function.
    """
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        # Re-raise to let the runner handle restarts if needed
        raise e

if __name__ == '__main__':
    start_bot()
