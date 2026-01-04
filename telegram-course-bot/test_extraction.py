"""
Test script to verify Coursevania link extraction works end-to-end
"""
import sys
sys.path.insert(0, 'c:\\Users\\jonat\\OneDrive\\Desktop\\autoweb\\telegram-course-bot')

from parser import resolve_coursevania_link
from website import save_course
import os
from dotenv import load_dotenv

load_dotenv()

# Test URL
coursevania_url = "https://coursevania.com/courses/ai-for-beginners-learn-chatgpt-gemini-perplexity-and-grok/"

print("=" * 60)
print("TESTING COURSEVANIA LINK EXTRACTION")
print("=" * 60)

# Step 1: Extract Udemy link
print(f"\n1. Resolving Coursevania link...")
print(f"   Input: {coursevania_url}")

udemy_link = resolve_coursevania_link(coursevania_url)

print(f"\n2. Result:")
print(f"   Extracted Link: {udemy_link}")

if "udemy.com" in udemy_link and "couponCode" in udemy_link:
    print("   ✅ SUCCESS: Got Udemy link with coupon code!")
else:
    print("   ❌ FAILED: Did not get proper Udemy link")
    sys.exit(1)

# Step 2: Save to website
print(f"\n3. Saving to website database...")

course_data = {
    "title": "TEST: AI for Beginners (Coursevania Extraction Test)",
    "description": "This is a test course to verify Coursevania link extraction is working.",
    "udemy_link": udemy_link,
    "image": None,
    "rating": None,
    "instructor": "Test Instructor"
}

WEBSITE_API = os.getenv("WEBSITE_API", "http://127.0.0.1:8000/api/courses")
print(f"   API Endpoint: {WEBSITE_API}")

try:
    save_course(course_data, WEBSITE_API)
    print("\n4. ✅ COMPLETE: Course saved successfully!")
    print(f"\n   Visit: http://127.0.0.1:8000/courses")
    print(f"   Look for: {course_data['title']}")
    print(f"   The GET COURSE button should link to: {udemy_link}")
except Exception as e:
    print(f"\n4. ❌ FAILED to save: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
