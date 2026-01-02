"""
Test MongoDB Atlas Connection with SSL Support
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

load_dotenv()

mongodb_url = os.getenv("MONGODB_URL")
database_name = os.getenv("DATABASE_NAME", "sucourse_db")

print("=" * 60)
print("🔌 Testing MongoDB Atlas Connection")
print("=" * 60)
print()

if not mongodb_url:
    print("❌ MONGODB_URL not found in .env file")
    print("   Please add it to your .env file in the root directory")
    exit(1)

print(f"📡 Connecting to MongoDB Atlas...")
print(f"📊 Database: {database_name}")
print()

try:
    # Connect to MongoDB with SSL certificate
    client = MongoClient(
        mongodb_url,
        serverSelectionTimeoutMS=10000,
        tlsCAFile=certifi.where()  # Use certifi for SSL certificates
    )
    
    # Test connection
    client.server_info()
    print("✅ Successfully connected to MongoDB Atlas!")
    print()
    
    # Get database
    db = client[database_name]
    
    # List collections
    collections = db.list_collection_names()
    print(f"📚 Collections in '{database_name}':")
    if collections:
        for coll in collections:
            count = db[coll].count_documents({})
            print(f"   - {coll}: {count} documents")
    else:
        print("   (No collections yet - this is normal for a new database)")
    
    print()
    print("=" * 60)
    print("🎉 Connection test successful!")
    print("=" * 60)
    print()
    print("✅ Your MongoDB Atlas setup is working perfectly!")
    print()
    print("Next steps:")
    print("1. Run migration: python migrate_to_mongodb.py")
    print("2. Switch to MongoDB version:")
    print("   - Backup: move app\\main.py app\\main_sqlite.py")
    print("   - Switch: move app\\main_mongo.py app\\main.py")
    print("3. Start your app: uvicorn app.main:app --reload")
    
    client.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check your MongoDB Atlas cluster is running")
    print("2. Verify IP whitelist in Atlas:")
    print("   - Go to Network Access")
    print("   - Add IP: 0.0.0.0/0 (allow all)")
    print("3. Confirm username and password are correct")
    print("4. Try regenerating the connection string from Atlas")
    exit(1)
