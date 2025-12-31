import os

async def post_to_channel(client, channel, course, website_base):
    try:
        # Construct caption with Bold Title, Description, and explicit spacing
        # User requested: Bold title, and 1 line gap after description end.
        caption = f"""
**{course['title']}**

Description:
{course.get('description', '')}


👉 Get Course:
{website_base}/course/{course['slug']}
""".strip()

        image_path = None
        if course.get("image"):
            # Image is in static folder
            image_path = os.path.join("../app/static/images", course["image"])

        # 🖼️ If image exists → send image + caption
        if image_path and os.path.exists(image_path):
            try:
                await client.send_file(
                    channel,
                    image_path,
                    caption=caption
                )
                print(f"✅ Posted IMAGE to target channel: {channel}")
            except Exception as e:
                 print(f"❌ Failed to post image: {e} - Falling back to text")
                 await client.send_message(channel, caption)
        else:
            # fallback → text only
            await client.send_message(channel, caption)
            print(f"✅ Posted TEXT to target channel: {channel}")

    except Exception as e:
        print(f"❌ Failed to post to channel: {e}")
