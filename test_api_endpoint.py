"""
Test API Endpoint - Verify courses can be saved via API
"""
import requests
import json

API_URL = "http://127.0.0.1:8000/api/courses"

# Test course data
test_course = {
    "title": "API Test Course - MongoDB Integration",
    "description": "This is a test course to verify the API endpoint works with MongoDB",
    "udemy_link": "https://www.udemy.com/test-api-course",
    "rating": "4.5",
    "instructor": "Test Instructor",
    "image": "/static/images/test.jpg"
}

print("=" * 60)
print("🧪 Testing API Endpoint")
print("=" * 60)
print()
print(f"📡 Endpoint: {API_URL}")
print(f"📦 Payload:")
print(json.dumps(test_course, indent=2))
print()

try:
    response = requests.post(API_URL, json=test_course, timeout=10)
    
    print(f"📊 Response Status: {response.status_code}")
    print()
    
    if response.status_code in (200, 201):
        print("✅ SUCCESS! Course saved to MongoDB")
        print()
        print("Response Data:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ FAILED! Status Code: {response.status_code}")
        print()
        print("Error Response:")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Connection Error: Is the FastAPI server running on port 8000?")
    print("   Run: uvicorn app.main:app --reload --port 8000")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 60)
