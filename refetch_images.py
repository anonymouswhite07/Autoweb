import sqlite3
import requests
from bs4 import BeautifulSoup
import time

def fetch_og_image(url: str) -> str:
    try:
        if not url: return None
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                return og_image["content"]
    except Exception as e:
        print(f"⚠️ Failed to fetch OG image for {url}: {e}")
    return None

db_path = "courses.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Fetching missing images from source...")

# Get courses with no image
cursor.execute("SELECT id, title, udemy_link FROM courses WHERE image IS NULL OR image = ''")
rows = cursor.fetchall()

print(f"Found {len(rows)} courses needing images.")

for row in rows:
    course_id, title, link = row
    print(f"Processing: {title[:30]}... | Link: {link}")
    
    if "udemy.com" not in link:
        print(" -> Not a Udemy link, skipping.")
        continue

    new_image = fetch_og_image(link)
    
    if new_image:
        print(f" -> Found Image: {new_image}")
        cursor.execute("UPDATE courses SET image = ? WHERE id = ?", (new_image, course_id))
        conn.commit()
    else:
        print(" -> No image found.")
    
    time.sleep(1) # Polite delay

conn.close()
print("Refetch complete.")
