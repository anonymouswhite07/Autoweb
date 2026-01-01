from googlesearch import search
import time

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'\s+', '-', text).strip('-')

def search_udemy_url(title):
    query = f"site:udemy.com {title}"
    try:
        # Search and return the first result that is a valid course link
        for result in search(query, num_results=5, lang="en"):
            if "udemy.com/course/" in result:
                return result
    except Exception as e:
        print(f"⚠️ Search error: {e}")
def udemy_slug_from_title(title: str) -> str:
    text = title.lower()
    text = text.replace("&", "and")
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text.strip('-')

def build_udemy_url(title: str) -> str:
    slug = udemy_slug_from_title(title)
    return f"https://www.udemy.com/course/{slug}/"
