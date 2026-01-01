import sqlite3

db_path = "courses.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Correcting 'None' strings in database...")

# 1. Fix 'None' strings to NULL
cursor.execute("UPDATE courses SET image = NULL WHERE image = 'None'")
cursor.execute("UPDATE courses SET image = NULL WHERE image = ''")

print(f"Rows updated: {cursor.rowcount}")

conn.commit()
conn.close()
print("Database corrected.")
