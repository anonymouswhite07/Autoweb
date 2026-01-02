"""
Verify MongoDB Storage - Check if new course was added
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

load_dotenv()

mongodb_url = os.getenv("MONGODB_URL")
database_name = os.getenv("DATABASE_NAME", "sucourse_db")

print("=" * 60)
print("🔍 Checking MongoDB for New Course")
print("=" * 60)
print()

try:
    # Connect to MongoDB
    client = MongoClient(mongodb_url, tlsCAFile=certifi.where())
    db = client[database_name]
    courses_collection = db["courses"]
    
    # Get all courses
    courses = list(courses_collection.find().sort("_id", -1))
    
    print(f"📊 Total courses in MongoDB: {len(courses)}")
    print()
    
    print("📚 All Courses in Database:")
    print("-" * 60)
    for i, course in enumerate(courses, 1):
        print(f"\n{i}. {course.get('title')}")
        print(f"   Slug: {course.get('slug')}")
        print(f"   MongoDB ID: {course.get('_id')}")
        print(f"   Description: {course.get('description', 'N/A')[:80]}...")
        print(f"   Udemy Link: {course.get('udemy_link', 'N/A')}")
    
    print()
    print("=" * 60)
    
    # Check for the test course
    test_course = courses_collection.find_one({"slug": "test-mongodb-course"})
    if test_course:
        print("✅ TEST COURSE FOUND IN MONGODB!")
        print("=" * 60)
        print(f"Title: {test_course.get('title')}")
        print(f"Description: {test_course.get('description')}")
        print(f"MongoDB ID: {test_course.get('_id')}")
        print()
        print("🎉 Confirmation: New courses ARE being stored in MongoDB Atlas!")
    else:
        print("⚠️  Test course not found yet (may need to refresh)")
    
    client.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
