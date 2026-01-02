"""
Migration script to transfer data from SQLite to MongoDB
Run this script to migrate your existing data.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Course, BlogPost, Page
from datetime import datetime
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection with SSL support
mongodb_url = os.getenv("MONGODB_URL")
database_name = os.getenv("DATABASE_NAME", "sucourse_db")

sync_client = MongoClient(mongodb_url, tlsCAFile=certifi.where())
sync_db = sync_client[database_name]

sync_courses_collection = sync_db["courses"]
sync_blog_posts_collection = sync_db["blog_posts"]
sync_pages_collection = sync_db["pages"]

def migrate_courses():
    """Migrate courses from SQLite to MongoDB"""
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        print(f"📦 Found {len(courses)} courses to migrate...")
        
        migrated = 0
        for course in courses:
            course_doc = {
                "title": course.title,
                "slug": course.slug,
                "description": course.description,
                "rating": course.rating,
                "instructor": course.instructor,
                "coupon": course.coupon,
                "image": course.image,
                "udemy_link": course.udemy_link,
                "created_at": course.created_at or datetime.utcnow()
            }
            
            # Check if already exists
            existing = sync_courses_collection.find_one({"slug": course.slug})
            if existing:
                print(f"⏭️  Skipping existing course: {course.title}")
                continue
            
            sync_courses_collection.insert_one(course_doc)
            migrated += 1
            print(f"✅ Migrated course: {course.title}")
        
        print(f"✨ Successfully migrated {migrated} courses!")
        return migrated
    finally:
        db.close()

def migrate_blog_posts():
    """Migrate blog posts from SQLite to MongoDB"""
    db = SessionLocal()
    try:
        posts = db.query(BlogPost).all()
        print(f"📦 Found {len(posts)} blog posts to migrate...")
        
        migrated = 0
        for post in posts:
            post_doc = {
                "title": post.title,
                "slug": post.slug,
                "content": post.content,
                "excerpt": post.excerpt,
                "image": post.image,
                "is_published": post.is_published,
                "created_at": post.created_at or datetime.utcnow()
            }
            
            # Check if already exists
            existing = sync_blog_posts_collection.find_one({"slug": post.slug})
            if existing:
                print(f"⏭️  Skipping existing post: {post.title}")
                continue
            
            sync_blog_posts_collection.insert_one(post_doc)
            migrated += 1
            print(f"✅ Migrated blog post: {post.title}")
        
        print(f"✨ Successfully migrated {migrated} blog posts!")
        return migrated
    finally:
        db.close()

def migrate_pages():
    """Migrate pages from SQLite to MongoDB"""
    db = SessionLocal()
    try:
        pages = db.query(Page).all()
        print(f"📦 Found {len(pages)} pages to migrate...")
        
        migrated = 0
        for page in pages:
            page_doc = {
                "slug": page.slug,
                "title": page.title,
                "content": page.content,
                "updated_at": page.updated_at or datetime.utcnow()
            }
            
            # Check if already exists
            existing = sync_pages_collection.find_one({"slug": page.slug})
            if existing:
                print(f"⏭️  Skipping existing page: {page.title}")
                continue
            
            sync_pages_collection.insert_one(page_doc)
            migrated += 1
            print(f"✅ Migrated page: {page.title}")
        
        print(f"✨ Successfully migrated {migrated} pages!")
        return migrated
    finally:
        db.close()

def main():
    """Run all migrations"""
    print("=" * 60)
    print("🚀 Starting SQLite to MongoDB Migration")
    print("=" * 60)
    print()
    
    try:
        # Migrate courses
        print("📚 MIGRATING COURSES")
        print("-" * 60)
        courses_count = migrate_courses()
        print()
        
        # Migrate blog posts
        print("📝 MIGRATING BLOG POSTS")
        print("-" * 60)
        posts_count = migrate_blog_posts()
        print()
        
        # Migrate pages
        print("📄 MIGRATING PAGES")
        print("-" * 60)
        pages_count = migrate_pages()
        print()
        
        # Summary
        print("=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        print(f"Total migrated:")
        print(f"  - Courses: {courses_count}")
        print(f"  - Blog Posts: {posts_count}")
        print(f"  - Pages: {pages_count}")
        print()
        print("🎉 Your data has been successfully migrated to MongoDB!")
        print()
        print("Next steps:")
        print("1. Update your .env file with MONGODB_URL")
        print("2. Test the application with MongoDB")
        print("3. Once verified, you can backup and remove courses.db")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
