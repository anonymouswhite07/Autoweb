# 🤖 Telegram Bot Setup Guide

## ✅ Quick Start - Run Bot Locally

Your Telegram bot is ready to run! It will:
- Listen to source Telegram channels for course posts
- Parse course information automatically
- Save courses to MongoDB via your API
- Post formatted courses to your target channel

## 🚀 How to Run

### **Option 1: Simple Command**

```bash
cd telegram-course-bot
python main.py
```

### **Option 2: With Virtual Environment** (Recommended)

```bash
cd telegram-course-bot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## ⚙️ Configuration Check

Your bot is configured in `telegram-course-bot\.env`:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
SOURCE_CHANNELS=channel1,channel2  # Channels to monitor
TARGET_CHANNEL=your_target_channel  # Where to post
WEBSITE_API=http://127.0.0.1:8000/api/courses
WEBSITE_BASE=http://127.0.0.1:8000
```

**Important:** Make sure your FastAPI server is running on port 8000!

## 🔄 How It Works

1. **Bot monitors** source channels for new course posts
2. **Parser extracts** course details (title, description, link, image)
3. **Saves to MongoDB** via API endpoint (`POST /api/courses`)
4. **Posts to channel** with formatted message and course link
5. **Downloads images** and saves to `app/static/images/`

## 📊 Data Flow

```
Telegram Source → Bot Parser → MongoDB (via API) → Your Website
                              ↓
                    Target Channel (formatted post)
```

## ✅ Prerequisites

- ✅ FastAPI server running (`uvicorn app.main:app --reload`)
- ✅ MongoDB Atlas connected
- ✅ Telegram API credentials configured
- ✅ Bot dependencies installed

## 🐛 Troubleshooting

### Bot won't start
- Check if `.env` file exists in `telegram-course-bot/`
- Verify API_ID and API_HASH are correct
- Make sure you have a valid session file

### Courses not saving
- Ensure FastAPI is running on port 8000
- Check `WEBSITE_API` URL is correct (no double slashes)
- Verify MongoDB connection is active

### Image download fails
- Check `app/static/images/` directory exists
- Verify bot has write permissions

## 📝 Logs

The bot will show:
- ✅ Course parsed successfully
- 🌍 Website API response
- 📸 Image download status
- ❌ Any errors encountered

## 🔧 Advanced Options

### Run in Background (Windows)

```powershell
Start-Process python -ArgumentList "main.py" -WorkingDirectory "telegram-course-bot" -WindowStyle Hidden
```

### Run with Logging

```bash
python main.py > bot.log 2>&1
```

## 🎯 What Happens When Bot Runs

1. Connects to Telegram with your session
2. Starts listening to SOURCE_CHANNELS
3. When new message arrives:
   - Parses course information
   - Downloads image (if available)
   - Saves to MongoDB via API
   - Posts to TARGET_CHANNEL
4. Continues running until stopped (Ctrl+C)

---

**Ready to start?** Run: `python telegram-course-bot/main.py`
