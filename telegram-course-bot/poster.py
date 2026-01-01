import os

async def post_to_channel(client, channel, course, website_base, media=None):
    try:
        # Construct caption with Bold Title, Description, and explicit spacing
        caption = f"""
**{course['title']}**

Description:
{course.get('description', '')}


👉 Get Course:
{website_base}/course/{course['slug']}
""".strip()

        # 🖼️ If media object provided (Stateless) → send media + caption
        if media:
            try:
                await client.send_file(
                    channel,
                    media,
                    caption=caption
                )
                print(f"✅ Posted MEDIA to target channel: {channel}")
            except Exception as e:
                 print(f"❌ Failed to post media: {e} - Falling back to text")
                 await client.send_message(channel, caption)
        else:
            # fallback → text only
            await client.send_message(channel, caption)
            print(f"✅ Posted TEXT to target channel: {channel}")

    except Exception as e:
        print(f"❌ Failed to post to channel: {e}")
