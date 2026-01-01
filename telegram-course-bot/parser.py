import re
import requests
from utils import udemy_slug_from_title, build_udemy_url

def fetch_og_image(url: str) -> str:
    try:
        if not url: return None
        # Fake header to avoid being blocked
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            # Simple regex search for og:image to avoid bs4 dependency if desired, or use it if installed.
            # Assuming bs4 is installed since googlesearch-python uses it.
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, 'html.parser')
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                return og_image["content"]
    except Exception as e:
        print(f"⚠️ Failed to fetch OG image: {e}")
    return None

def udemy_url_exists(url: str) -> bool:
    try:
        r = requests.head(url, allow_redirects=True, timeout=8)
        return r.status_code == 200
    except:
        return False

def extract_button_link(message):
    '''Extracts URL from message buttons if available.'''
    if not hasattr(message, 'buttons') or not message.buttons:
        return None

    try:
        # message.buttons is often a list of lists (rows)
        # We iterate safely
        rows = message.buttons if isinstance(message.buttons, list) else []
        for row in rows:
            # Each row might be a list of buttons or a single button object
            buttons = row if isinstance(row, list) else [row]
            for button in buttons:
                if hasattr(button, "url") and button.url:
                    return button.url
    except Exception as e:
        print(f"⚠️ Button extraction error: {e}")
        
    return None

def parse_course(message):
    text = message.text or ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    if not lines:
        return None

    # Remove markdown bolding from title
def is_promo_line(line: str) -> bool:
    promo_keywords = [
        "free for",
        "free enroll",
        "limited",
        "100%",
        "enroll now",
        "limited time"
    ]
    l = line.lower()
    return any(k in l for k in promo_keywords)


def extract_description(lines):
    desc_lines = []

    for line in lines[1:]:  # skip title
        if line.startswith("http") or "udemy.com" in line:
            break

        # BLACKLIST CLEANING
        blacklist = [
            "Description:", 
            "👉 Get Course:", 
            "Coupon Code:-",
            "Rating:",
            "Students:",
            "Duration:"
        ]
        
        should_skip = False
        for bad_word in blacklist:
            if bad_word in line:
                line = line.replace(bad_word, "")
                # If line becomes empty or just symbols, skip it
                if not line.strip() or line.strip() in [":", "-"]:
                    should_skip = True
        
        if should_skip: continue
        
        # skip promo lines
        if is_promo_line(line):
            continue

        desc_lines.append(line)

    description = " ".join(desc_lines).strip()
    return description

def parse_course(message):
    text = message.text or ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    if not lines:
        return None

    title = lines[0].replace("**", "").strip()
    description = extract_description(lines)

    # 1️⃣ Plain text link found in message body
    # Prioritize Udemy links
    udemy_match = re.search(r"(https?://www\.udemy\.com/course/[^\s]+)", text)
    if udemy_match:
        link = udemy_match.group(1)
        return {
            "title": title,
            "description": description,
            "udemy_link": link,
            "status": "AUTO",
            "image_url": fetch_og_image(link)
        }
    
    # Check for other links if no udemy link
    link_match = re.search(r"(https?://[^\s]+)", text)
    if link_match:
        link = link_match.group(1)
        return {
            "title": title,
            "description": description,
            "udemy_link": link,
            "status": "AUTO_OTHER_LINK",
             "image_url": fetch_og_image(link)
        }

    # 2️⃣ Button link (Enroll Now)
    button_link = extract_button_link(message)
    if button_link:
        return {
            "title": title,
            "description": description,
            "udemy_link": button_link,
            "status": "AUTO_BUTTON",
            "image_url": fetch_og_image(button_link)
        }

    # 3️⃣ Guess Udemy URL from title (fallback)
    slug = udemy_slug_from_title(title)
    guessed_url = f"https://www.udemy.com/course/{slug}/"

    if udemy_url_exists(guessed_url):
        return {
            "title": title,
            "description": description,
            "udemy_link": guessed_url,
            "status": "AUTO_GUESSED",
            "image_url": fetch_og_image(guessed_url)
        }

    # Final fallback
    return {
        "title": title,
        "description": description,
        "udemy_link": None,
        "status": "NEEDS_LINK",
        "image_url": None
    }
