import sqlite3
import os

db_path = "courses.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Checking for bad rows...")
    cursor.execute("SELECT count(*) FROM courses WHERE slug IS NULL OR slug = ''")
    bad_slugs = cursor.fetchone()[0]
    
    cursor.execute("SELECT count(*) FROM courses WHERE image IS NULL OR image = ''")
    bad_images = cursor.fetchone()[0]
    
    print(f"Found {bad_slugs} rows with bad slugs.")
    print(f"Found {bad_images} rows with bad images.")
    
    if bad_slugs > 0 or bad_images > 0:
        print("Cleaning up...")
        # Delete rows with no slug (critical for routing)
        cursor.execute("DELETE FROM courses WHERE slug IS NULL OR slug = ''")
        # Optional: Delete rows with no image if we want strictly clean homepage
        # cursor.execute("DELETE FROM courses WHERE image IS NULL OR image = ''") 
        conn.commit()
        print("Clean up complete.")
    else:
        print("Database is clean.")
        
    conn.close()
else:
    print("courses.db not found.")
