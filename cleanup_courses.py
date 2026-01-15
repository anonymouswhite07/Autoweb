from datetime import datetime, timedelta
import sys
import os

# Add current directory to path to allow imports
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from app.database_mongo import sync_courses_collection as courses_collection

def cleanup_recent_courses():
    # 10 days ago
    cutoff_date = datetime.utcnow() - timedelta(days=10)
    
    print(f"🔍 Checking for courses created on or after: {cutoff_date} (UTC)")

    try:
        # Count first
        count = courses_collection.count_documents({
            "created_at": {"$gte": cutoff_date}
        })
        print(f"📊 Found {count} courses created in the last 10 days.")

        if count > 0:
            # Delete
            result = courses_collection.delete_many({
                "created_at": {"$gte": cutoff_date}
            })
            print(f"✅ Successfully deleted {result.deleted_count} courses.")
        else:
            print("ℹ️ No courses found to delete in this range.")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_recent_courses()
