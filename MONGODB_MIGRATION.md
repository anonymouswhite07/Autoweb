# MongoDB Migration Guide

This guide will help you migrate your application from SQLite to MongoDB.

## 📋 Prerequisites

1. **Install MongoDB** (choose one option):
   
   ### Option A: Local MongoDB Installation
   - Download and install MongoDB Community Server from [mongodb.com/download-center/community](https://www.mongodb.com/try/download/community)
   - Start MongoDB service:
     ```bash
     # Windows
     net start MongoDB
     
     # macOS (with Homebrew)
     brew services start mongodb-community
     
     # Linux
     sudo systemctl start mongod
     ```

   ### Option B: MongoDB Atlas (Cloud)
   - Create a free account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
   - Create a new cluster (free tier available)
   - Get your connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Migration Steps

### Step 1: Configure MongoDB Connection

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your MongoDB configuration:
   ```env
   # For local MongoDB
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=sucourse_db
   
   # OR for MongoDB Atlas
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
   DATABASE_NAME=sucourse_db
   ```

### Step 2: Run the Migration Script

This script will transfer all your existing data from SQLite to MongoDB:

```bash
python migrate_to_mongodb.py
```

The script will:
- ✅ Migrate all courses
- ✅ Migrate all blog posts
- ✅ Migrate all pages
- ✅ Skip duplicates if you run it multiple times
- ✅ Show detailed progress

### Step 3: Switch to MongoDB Version

**Option A: Rename files (recommended)**
```bash
# Backup current main.py
mv app/main.py app/main_sqlite.py

# Use MongoDB version
mv app/main_mongo.py app/main.py
```

**Option B: Manual update**
Update your imports in `app/main.py` to use the MongoDB modules:
- Replace `from .database import ...` with `from .database_mongo import ...`
- Replace `from .crud import ...` with `from .crud_mongo import ...`
- Replace `from .models import ...` with `from .models_mongo import ...`

### Step 4: Test Your Application

```bash
uvicorn app.main:app --reload
```

Visit:
- Homepage: http://localhost:8000
- Admin: http://localhost:8000/admin
- API Health: http://localhost:8000/health

### Step 5: Verify Data Migration

1. Check that all courses appear on the homepage
2. Verify course detail pages work
3. Test the admin panel
4. Check blog posts and pages

## 🔄 Rollback (if needed)

If you encounter issues, you can easily rollback:

```bash
# Restore SQLite version
mv app/main_sqlite.py app/main.py
```

Your SQLite database (`courses.db`) remains untouched during migration.

## 📊 MongoDB vs SQLite Comparison

| Feature | SQLite | MongoDB |
|---------|--------|---------|
| **Scalability** | Limited | Excellent |
| **Concurrent Writes** | Limited | Excellent |
| **Cloud Hosting** | Difficult | Easy (Atlas) |
| **Query Performance** | Good for small data | Better for large data |
| **Schema Flexibility** | Rigid | Flexible |
| **Backup** | Single file | Cloud backups available |

## 🛠️ MongoDB Features You Can Now Use

### 1. Advanced Queries
```python
# Text search
await courses_collection.find({"$text": {"$search": "python"}})

# Complex filters
await courses_collection.find({
    "rating": {"$gte": 4.5},
    "created_at": {"$gte": datetime(2024, 1, 1)}
})
```

### 2. Aggregation Pipeline
```python
# Get course statistics
pipeline = [
    {"$group": {
        "_id": "$instructor",
        "course_count": {"$sum": 1},
        "avg_rating": {"$avg": "$rating"}
    }}
]
results = await courses_collection.aggregate(pipeline).to_list(None)
```

### 3. Indexes for Performance
```python
# Already created in init_db(), but you can add more:
await courses_collection.create_index([("title", "text")])
await courses_collection.create_index([("rating", -1)])
```

## 🔧 Troubleshooting

### Connection Issues

**Error: `ServerSelectionTimeoutError`**
- Check if MongoDB is running: `mongosh` (should connect)
- Verify MONGODB_URL in `.env`
- For Atlas: Check IP whitelist and credentials

**Error: `Authentication failed`**
- Verify username and password in connection string
- For Atlas: Check database user permissions

### Migration Issues

**Error: `Duplicate key error`**
- This is normal if you run migration multiple times
- The script skips duplicates automatically

**Error: `Module not found`**
- Run: `pip install -r requirements.txt`
- Ensure you're in the correct virtual environment

## 📝 Environment Variables

```env
# Required for MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=sucourse_db

# Optional (existing)
SMTP_USER=your_email@example.com
SMTP_PASS=your_password
ADMIN_PASSWORD=adminpass123
```

## 🎯 Next Steps

After successful migration:

1. **Monitor Performance**: MongoDB provides better analytics
2. **Set up Backups**: 
   - Local: `mongodump --db sucourse_db`
   - Atlas: Automatic backups available
3. **Optimize Indexes**: Add indexes based on your query patterns
4. **Consider Sharding**: For very large datasets (future)

## 📚 Additional Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [Motor (Async Driver) Docs](https://motor.readthedocs.io/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB University](https://university.mongodb.com/) - Free courses

## ⚠️ Important Notes

1. **Keep SQLite Backup**: Don't delete `courses.db` until you're 100% sure MongoDB works
2. **Environment Variables**: Make sure `.env` is in `.gitignore`
3. **Connection Pooling**: Motor handles this automatically
4. **Async Operations**: The new code uses both sync and async operations for compatibility

## 🆘 Need Help?

If you encounter issues:
1. Check MongoDB logs: `tail -f /var/log/mongodb/mongod.log` (Linux/Mac)
2. Test connection: `mongosh "your_connection_string"`
3. Verify data: `mongosh` → `use sucourse_db` → `db.courses.find()`

---

**Status**: ✅ Migration files created and ready to use!
