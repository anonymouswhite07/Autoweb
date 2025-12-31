import requests

def save_course(course, api_url):
    payload = {
        "title": course["title"],
        "description": course.get("description"),
        "udemy_link": course["udemy_link"],
        "image": course.get("image"),
        "rating": course.get("rating"),
        "instructor": course.get("instructor")
    }
    # Note: Coupon is technically part of the link now in your logic, 
    # but if we want to store it explicitly we need to add it to schema.
    # For now, let's just make sure 'description' is passed correctly.

    r = requests.post(api_url, json=payload, timeout=10)
    print(f"🌍 Website API Response: {r.status_code}")
    if r.status_code not in (200, 201):
        print("❌ Failed to save course:", r.text)
    else:
        print("✅ Course saved to website!")
