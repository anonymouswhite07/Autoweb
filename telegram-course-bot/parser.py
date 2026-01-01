import re
import requests
from utils import udemy_slug_from_title, build_udemy_url

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
        return {
            "title": title,
            "description": description,
            "udemy_link": udemy_match.group(1),
            "status": "AUTO"
        }
    
    # Check for other links if no udemy link
    link_match = re.search(r"(https?://[^\s]+)", text)
    if link_match:
        return {
            "title": title,
            "description": description,
            "udemy_link": link_match.group(1),
            "status": "AUTO_OTHER_LINK"
        }

    # 2️⃣ Button link (Enroll Now)
    button_link = extract_button_link(message)
    if button_link:
        return {
            "title": title,
            "description": description,
            "udemy_link": button_link,
            "status": "AUTO_BUTTON"
        }

    # 3️⃣ Guess Udemy URL from title (fallback)
    slug = udemy_slug_from_title(title)
    guessed_url = f"https://www.udemy.com/course/{slug}/"

    if udemy_url_exists(guessed_url):
        return {
            "title": title,
            "description": description,
            "udemy_link": guessed_url,
            "status": "AUTO_GUESSED"
        }

    # Final fallback
    return {
        "title": title,
        "description": description,
        "udemy_link": None,
        "status": "NEEDS_LINK"
    }
