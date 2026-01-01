import sqlite3
conn = sqlite3.connect("courses.db")
cursor = conn.cursor()
cursor.execute("SELECT title, image, udemy_link FROM courses ORDER BY id DESC LIMIT 3")
rows = cursor.fetchall()
for row in rows:
    print(f"Title: {row[0]}")
    print(f"Image: {row[1]}")
    print(f"Link: {row[2]}")
    print("-" * 20)
conn.close()
