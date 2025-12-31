import requests

def udemy_url_exists(url: str) -> bool:
    try:
        # Use a HEAD request to check if the URL exists without downloading body
        # User-Agent is important as some sites block empty agents
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.head(url, allow_redirects=True, timeout=8, headers=headers)
        return r.status_code == 200
    except Exception as e:
        print(f"⚠️ URL verification failed: {e}")
        return False
