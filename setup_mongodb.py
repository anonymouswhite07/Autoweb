"""
Quick Setup Script for MongoDB Migration
Run this to check your setup and get started quickly
"""

import sys
import os

def check_mongodb_installed():
    """Check if MongoDB packages are installed"""
    try:
        import pymongo
        import motor
        import dnspython
        print("✅ MongoDB packages installed")
        print(f"   - pymongo: {pymongo.__version__}")
        print(f"   - motor: {motor.version}")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has MongoDB config"""
    if not os.path.exists(".env"):
        print("⚠️  .env file not found")
        print("   Run: cp env.example .env")
        print("   Then edit .env with your MongoDB connection details")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
        if "MONGODB_URL" in content:
            print("✅ .env file exists with MongoDB configuration")
            return True
        else:
            print("⚠️  .env file exists but missing MONGODB_URL")
            print("   Add: MONGODB_URL=mongodb://localhost:27017")
            return False

def check_mongodb_connection():
    """Try to connect to MongoDB"""
    try:
        from dotenv import load_dotenv
        import pymongo
        
        load_dotenv()
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        
        client = pymongo.MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        client.server_info()  # Will raise exception if cannot connect
        print(f"✅ Successfully connected to MongoDB at {mongodb_url}")
        client.close()
        return True
    except Exception as e:
        print(f"❌ Cannot connect to MongoDB: {e}")
        print("\n   Options:")
        print("   1. Install MongoDB locally: https://www.mongodb.com/try/download/community")
        print("   2. Use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas")
        print("   3. Update MONGODB_URL in .env file")
        return False

def main():
    print("=" * 60)
    print("🚀 MongoDB Migration Setup Check")
    print("=" * 60)
    print()
    
    checks = []
    
    # Check 1: Packages
    print("1️⃣  Checking MongoDB packages...")
    checks.append(check_mongodb_installed())
    print()
    
    # Check 2: Environment file
    print("2️⃣  Checking environment configuration...")
    checks.append(check_env_file())
    print()
    
    # Check 3: MongoDB connection
    print("3️⃣  Testing MongoDB connection...")
    checks.append(check_mongodb_connection())
    print()
    
    # Summary
    print("=" * 60)
    if all(checks):
        print("✅ ALL CHECKS PASSED!")
        print("=" * 60)
        print()
        print("🎉 You're ready to migrate! Next steps:")
        print()
        print("1. Run migration script:")
        print("   python migrate_to_mongodb.py")
        print()
        print("2. Switch to MongoDB version:")
        print("   # Backup current main.py")
        print("   mv app/main.py app/main_sqlite.py")
        print("   # Use MongoDB version")
        print("   mv app/main_mongo.py app/main.py")
        print()
        print("3. Start your application:")
        print("   uvicorn app.main:app --reload")
        print()
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("=" * 60)
        print()
        print("Please fix the issues above before proceeding.")
        print("See MONGODB_MIGRATION.md for detailed instructions.")
        print()
    
    return 0 if all(checks) else 1

if __name__ == "__main__":
    exit(main())
