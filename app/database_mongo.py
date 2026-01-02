from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sucourse_db")

# Async MongoDB client (for async operations)
async_client = AsyncIOMotorClient(MONGODB_URL, tlsCAFile=certifi.where())
async_db = async_client[DATABASE_NAME]

# Sync MongoDB client (for sync operations)
sync_client = MongoClient(MONGODB_URL, tlsCAFile=certifi.where())
sync_db = sync_client[DATABASE_NAME]

# Collections
courses_collection = async_db["courses"]
blog_posts_collection = async_db["blog_posts"]
pages_collection = async_db["pages"]

# Sync collections (for non-async operations)
sync_courses_collection = sync_db["courses"]
sync_blog_posts_collection = sync_db["blog_posts"]
sync_pages_collection = sync_db["pages"]

async def init_db():
    """Initialize database indexes"""
    # Create indexes for better query performance
    await courses_collection.create_index("slug", unique=True)
    await courses_collection.create_index("title")
    await courses_collection.create_index("created_at")
    
    await blog_posts_collection.create_index("slug", unique=True)
    await blog_posts_collection.create_index("created_at")
    
    await pages_collection.create_index("slug", unique=True)
    
    print("✅ MongoDB indexes created successfully")

async def close_db():
    """Close database connections"""
    async_client.close()
    sync_client.close()
