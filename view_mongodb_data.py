"""
MongoDB Data Viewer - See all your data in a nice format
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
from datetime import datetime

load_dotenv()

mongodb_url = os.getenv("MONGODB_URL")
database_name = os.getenv("DATABASE_NAME", "sucourse_db")

def print_separator(char="=", length=70):
    print(char * length)

def view_collection(collection, name):
    """Display all documents in a collection"""
    print(f"\n📚 {name.upper()}")
    print_separator()
    
    docs = list(collection.find().sort("_id", -1))
    print(f"Total: {len(docs)} documents\n")
    
    for i, doc in enumerate(docs, 1):
        print(f"{i}. {doc.get('title', 'N/A')}")
        print(f"   ID: {doc.get('_id')}")
        print(f"   Slug: {doc.get('slug', 'N/A')}")
        
        if 'description' in doc:
            desc = doc.get('description', '')
            print(f"   Description: {desc[:80]}..." if len(desc) > 80 else f"   Description: {desc}")
        
        if 'udemy_link' in doc:
            print(f"   Udemy Link: {doc.get('udemy_link')}")
        
        if 'content' in doc:
            content = doc.get('content', '')
            print(f"   Content: {content[:80]}..." if len(content) > 80 else f"   Content: {content}")
        
        if 'created_at' in doc:
            created = doc.get('created_at')
            if isinstance(created, datetime):
                print(f"   Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print()

try:
    print_separator()
    print("🔍 MONGODB ATLAS DATA VIEWER")
    print_separator()
    print(f"\n📊 Database: {database_name}")
    print(f"🌐 Cluster: MongoDB Atlas")
    print()
    
    # Connect
    client = MongoClient(mongodb_url, tlsCAFile=certifi.where())
    db = client[database_name]
    
    # View all collections
    view_collection(db["courses"], "COURSES")
    view_collection(db["blog_posts"], "BLOG POSTS")
    view_collection(db["pages"], "PAGES")
    
    print_separator()
    print("✅ All data displayed successfully!")
    print_separator()
    print("\n💡 To view in browser:")
    print("   1. Go to: https://cloud.mongodb.com")
    print("   2. Click 'Browse Collections'")
    print("   3. Select 'sucourse_db' database")
    print()
    
    client.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
