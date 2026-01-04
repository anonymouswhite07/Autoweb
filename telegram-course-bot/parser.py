import re
import requests
from utils import udemy_slug_from_title, build_udemy_url
from bs4 import BeautifulSoup

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

def resolve_coursevania_link(url: str) -> str:
    """
    Follows a Coursevania link and extracts the actual Udemy URL.
    Uses requests with retries as Playwright has network timeout issues.
    """
    try:
        if "coursevania.com" not in url:
            return url

        print(f"🔄 Resolving Coursevania link: {url}")
        
        # Try with requests first (simpler and faster)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Try multiple times with increasing timeout
        for attempt in range(3):
            try:
                timeout = 10 + (attempt * 5)  # 10s, 15s, 20s
                print(f"  Attempt {attempt + 1}/3 (timeout: {timeout}s)...")
                
                r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
                
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    
                    # Method 1: Look for "Get on Udemy" link
                    anchor = soup.find('a', string=re.compile(r"Get on Udemy", re.IGNORECASE))
                    if anchor and anchor.get('href'):
                        print(f"✅ Found 'Get on Udemy' link: {anchor['href']}")
                        return anchor['href']
                    
                    # Method 2: Look for any udemy.com/course link
                    udemy_anchor = soup.find('a', href=re.compile(r"udemy\.com/course", re.IGNORECASE))
                    if udemy_anchor and udemy_anchor.get('href'):
                        print(f"✅ Found Udemy course link: {udemy_anchor['href']}")
                        return udemy_anchor['href']
                    
                    print("⚠️ Page loaded but no Udemy link found")
                    break  # Don't retry if page loaded successfully
                    
            except requests.Timeout:
                print(f"  ⏱️ Timeout on attempt {attempt + 1}")
                if attempt == 2:  # Last attempt
                    print("❌ All attempts timed out")
            except requests.ConnectionError as e:
                print(f"  ❌ Connection error: {e}")
                break  # Don't retry on connection errors
            except Exception as e:
                print(f"  ⚠️ Error on attempt {attempt + 1}: {e}")
                if attempt == 2:
                    break
        
        print("⚠️ Returning original URL (resolution failed)")
        return url
        
    except Exception as e:
        print(f"❌ Failed to resolve Coursevania link: {e}")
        return url

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

def extract_coupon_code(text: str):
    """
    Extracts coupon code from:
    Coupon Code:- HNY2026_2
    """
    # Regex to handle "Coupon Code:- CODE" or "Coupon Code: CODE" variants
    match = re.search(r"Coupon Code\s*:?-?\s*([A-Z0-9_\-]+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def build_udemy_link(title: str, coupon: str):
    slug = udemy_slug_from_title(title)
    return f"https://www.udemy.com/course/{slug}/?couponCode={coupon}"

def parse_course(message):
    text = message.text or ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    if not lines:
        return None

    title = lines[0].replace("**", "").strip()
    description = extract_description(lines)

    # 0️⃣ PRIORITY: Check for Coursevania links FIRST
    # This ensures we get the actual Udemy link with coupon from Coursevania
    link_match = re.search(r"(https?://[^\s]+)", text)
    if link_match:
        link = link_match.group(1)
        
        # 🆕 Attempt to resolve if it's a Coursevania link
        if "coursevania.com" in link:
            print(f"📍 Found Coursevania link, extracting Udemy URL...")
            resolved_link = resolve_coursevania_link(link)
            if "udemy.com" in resolved_link:
                print(f"✅ Coursevania extraction successful!")
                return {
                    "title": title,
                    "description": description,
                    "udemy_link": resolved_link,
                    "status": "AUTO_RESOLVED",
                    "image_url": fetch_og_image(resolved_link)
                }
        
        # Check if it's a direct Udemy link
        if "udemy.com/course" in link:
            print(f"📍 Found direct Udemy link")
            return {
                "title": title,
                "description": description,
                "udemy_link": link,
                "status": "AUTO",
                "image_url": fetch_og_image(link)
            }

    # 1️⃣ FALLBACK: Extract Coupon & Build Link (only if no links found)
    coupon = extract_coupon_code(text)
    if coupon:
        print(f"📍 No links found, building Udemy link from coupon code: {coupon}")
        direct_link = build_udemy_link(title, coupon)
        return {
            "title": title,
            "description": description,
            "udemy_link": direct_link,
            "status": "DIRECT_UDEMY",
            "image_url": fetch_og_image(direct_link)
        }

    # 2️⃣ If we found a link but it's not Coursevania or Udemy
    if link_match:
        link = link_match.group(1)
        print(f"📍 Found other link: {link}")
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

    # Final fallback
    return {
        "title": title,
        "description": description,
        "udemy_link": None,
        "status": "NEEDS_LINK",
        "image_url": None
    }
