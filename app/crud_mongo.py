from typing import List, Optional
from datetime import datetime
import re
from bson import ObjectId

from .database_mongo import (
    courses_collection,
    blog_posts_collection,
    pages_collection,
    sync_courses_collection,
    sync_blog_posts_collection,
    sync_pages_collection
)

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'\s+', '-', text).strip('-')

# ============ COURSE OPERATIONS ============

async def create_course_async(course_data: dict) -> dict:
    """Create a new course (async)"""
    slug = slugify(course_data.get("title", ""))
    
    # Check if course with this slug already exists
    existing = await courses_collection.find_one({"slug": slug})
    if existing:
        return existing
    
    course_doc = {
        "title": course_data.get("title"),
        "slug": slug,
        "description": course_data.get("description"),
        "rating": course_data.get("rating"),
        "instructor": course_data.get("instructor"),
        "coupon": course_data.get("coupon"),
        "image": course_data.get("image"),
        "udemy_link": course_data.get("udemy_link"),
        "created_at": datetime.utcnow()
    }
    
    result = await courses_collection.insert_one(course_doc)
    course_doc["_id"] = result.inserted_id
    return course_doc

def create_course_sync(course_data: dict) -> dict:
    """Create a new course (sync)"""
    slug = slugify(course_data.get("title", ""))
    
    # Check if course with this slug already exists
    existing = sync_courses_collection.find_one({"slug": slug})
    if existing:
        return existing
    
    course_doc = {
        "title": course_data.get("title"),
        "slug": slug,
        "description": course_data.get("description"),
        "rating": course_data.get("rating"),
        "instructor": course_data.get("instructor"),
        "coupon": course_data.get("coupon"),
        "image": course_data.get("image"),
        "udemy_link": course_data.get("udemy_link"),
        "created_at": datetime.utcnow()
    }
    
    result = sync_courses_collection.insert_one(course_doc)
    course_doc["_id"] = result.inserted_id
    return course_doc

async def get_courses_async(limit: Optional[int] = None) -> List[dict]:
    """Get all courses (async)"""
    cursor = courses_collection.find().sort("created_at", -1)
    if limit:
        cursor = cursor.limit(limit)
    courses = await cursor.to_list(length=None)
    return courses

def get_courses_sync(limit: Optional[int] = None) -> List[dict]:
    """Get all courses (sync)"""
    cursor = sync_courses_collection.find().sort("created_at", -1)
    if limit:
        cursor = cursor.limit(limit)
    return list(cursor)

async def get_course_async(slug: str) -> Optional[dict]:
    """Get a single course by slug (async)"""
    return await courses_collection.find_one({"slug": slug})

def get_course_sync(slug: str) -> Optional[dict]:
    """Get a single course by slug (sync)"""
    return sync_courses_collection.find_one({"slug": slug})

async def get_course_by_id_async(course_id: str) -> Optional[dict]:
    """Get a single course by ID (async)"""
    return await courses_collection.find_one({"_id": ObjectId(course_id)})

def get_course_by_id_sync(course_id: str) -> Optional[dict]:
    """Get a single course by ID (sync)"""
    return sync_courses_collection.find_one({"_id": ObjectId(course_id)})

async def update_course_async(course_id: str, update_data: dict) -> bool:
    """Update a course (async)"""
    update_data["updated_at"] = datetime.utcnow()
    result = await courses_collection.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

def update_course_sync(course_id: str, update_data: dict) -> bool:
    """Update a course (sync)"""
    update_data["updated_at"] = datetime.utcnow()
    result = sync_courses_collection.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

async def delete_course_async(course_id: str) -> bool:
    """Delete a course (async)"""
    result = await courses_collection.delete_one({"_id": ObjectId(course_id)})
    return result.deleted_count > 0

def delete_course_sync(course_id: str) -> bool:
    """Delete a course (sync)"""
    result = sync_courses_collection.delete_one({"_id": ObjectId(course_id)})
    return result.deleted_count > 0

async def search_courses_async(query: str) -> List[dict]:
    """Search courses by title (async)"""
    courses = await courses_collection.find(
        {"title": {"$regex": query, "$options": "i"}}
    ).to_list(length=None)
    return courses

def search_courses_sync(query: str) -> List[dict]:
    """Search courses by title (sync)"""
    return list(sync_courses_collection.find(
        {"title": {"$regex": query, "$options": "i"}}
    ))

# ============ BLOG POST OPERATIONS ============

async def get_posts_async() -> List[dict]:
    """Get all blog posts (async)"""
    posts = await blog_posts_collection.find().sort("created_at", -1).to_list(length=None)
    return posts

def get_posts_sync() -> List[dict]:
    """Get all blog posts (sync)"""
    return list(sync_blog_posts_collection.find().sort("created_at", -1))

async def get_post_async(slug: str) -> Optional[dict]:
    """Get a single blog post by slug (async)"""
    return await blog_posts_collection.find_one({"slug": slug})

def get_post_sync(slug: str) -> Optional[dict]:
    """Get a single blog post by slug (sync)"""
    return sync_blog_posts_collection.find_one({"slug": slug})

async def get_post_by_id_async(post_id: str) -> Optional[dict]:
    """Get a single blog post by ID (async)"""
    return await blog_posts_collection.find_one({"_id": ObjectId(post_id)})

def get_post_by_id_sync(post_id: str) -> Optional[dict]:
    """Get a single blog post by ID (sync)"""
    return sync_blog_posts_collection.find_one({"_id": ObjectId(post_id)})

async def create_post_async(post_data: dict) -> dict:
    """Create a new blog post (async)"""
    slug = slugify(post_data.get("title", ""))
    post_doc = {
        "title": post_data.get("title"),
        "slug": slug,
        "content": post_data.get("content"),
        "excerpt": post_data.get("excerpt"),
        "image": post_data.get("image"),
        "is_published": post_data.get("is_published", True),
        "created_at": datetime.utcnow()
    }
    result = await blog_posts_collection.insert_one(post_doc)
    post_doc["_id"] = result.inserted_id
    return post_doc

def create_post_sync(post_data: dict) -> dict:
    """Create a new blog post (sync)"""
    slug = slugify(post_data.get("title", ""))
    post_doc = {
        "title": post_data.get("title"),
        "slug": slug,
        "content": post_data.get("content"),
        "excerpt": post_data.get("excerpt"),
        "image": post_data.get("image"),
        "is_published": post_data.get("is_published", True),
        "created_at": datetime.utcnow()
    }
    result = sync_blog_posts_collection.insert_one(post_doc)
    post_doc["_id"] = result.inserted_id
    return post_doc

async def update_post_async(post_id: str, update_data: dict) -> bool:
    """Update a blog post (async)"""
    update_data["updated_at"] = datetime.utcnow()
    result = await blog_posts_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

def update_post_sync(post_id: str, update_data: dict) -> bool:
    """Update a blog post (sync)"""
    update_data["updated_at"] = datetime.utcnow()
    result = sync_blog_posts_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

async def delete_post_async(post_id: str) -> bool:
    """Delete a blog post (async)"""
    result = await blog_posts_collection.delete_one({"_id": ObjectId(post_id)})
    return result.deleted_count > 0

def delete_post_sync(post_id: str) -> bool:
    """Delete a blog post (sync)"""
    result = sync_blog_posts_collection.delete_one({"_id": ObjectId(post_id)})
    return result.deleted_count > 0

# ============ PAGE OPERATIONS ============

async def get_pages_async() -> List[dict]:
    """Get all pages (async)"""
    pages = await pages_collection.find().to_list(length=None)
    return pages

def get_pages_sync() -> List[dict]:
    """Get all pages (sync)"""
    return list(sync_pages_collection.find())

async def get_page_async(slug: str) -> Optional[dict]:
    """Get a single page by slug (async)"""
    return await pages_collection.find_one({"slug": slug})

def get_page_sync(slug: str) -> Optional[dict]:
    """Get a single page by slug (sync)"""
    return sync_pages_collection.find_one({"slug": slug})

async def get_page_by_id_async(page_id: str) -> Optional[dict]:
    """Get a single page by ID (async)"""
    return await pages_collection.find_one({"_id": ObjectId(page_id)})

def get_page_by_id_sync(page_id: str) -> Optional[dict]:
    """Get a single page by ID (sync)"""
    return sync_pages_collection.find_one({"_id": ObjectId(page_id)})

async def create_page_async(page_data: dict) -> dict:
    """Create a new page (async)"""
    page_doc = {
        "slug": page_data.get("slug"),
        "title": page_data.get("title"),
        "content": page_data.get("content", ""),
        "updated_at": datetime.utcnow()
    }
    result = await pages_collection.insert_one(page_doc)
    page_doc["_id"] = result.inserted_id
    return page_doc

def create_page_sync(page_data: dict) -> dict:
    """Create a new page (sync)"""
    page_doc = {
        "slug": page_data.get("slug"),
        "title": page_data.get("title"),
        "content": page_data.get("content", ""),
        "updated_at": datetime.utcnow()
    }
    result = sync_pages_collection.insert_one(page_doc)
    page_doc["_id"] = result.inserted_id
    return page_doc

async def update_page_async(page_id: str, update_data: dict) -> bool:
    """Update a page (async)"""
    update_data["updated_at"] = datetime.utcnow()
    result = await pages_collection.update_one(
        {"_id": ObjectId(page_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

def update_page_sync(page_id: str, update_data: dict) -> bool:
    """Update a page (sync)"""
    update_data["updated_at"] = datetime.utcnow()
    result = sync_pages_collection.update_one(
        {"_id": ObjectId(page_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

async def delete_page_async(page_id: str) -> bool:
    """Delete a page (async)"""
    result = await pages_collection.delete_one({"_id": ObjectId(page_id)})
    return result.deleted_count > 0

def delete_page_sync(page_id: str) -> bool:
    """Delete a page (sync)"""
    result = sync_pages_collection.delete_one({"_id": ObjectId(page_id)})
    return result.deleted_count > 0
