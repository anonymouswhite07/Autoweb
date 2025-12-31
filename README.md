# SU Course - Curated Course Platform

A professional, editorial-style course curation platform built to bridge Telegram updates with a clean web interface.

## ✨ Features
- **Editorial Design**: Clean, minimal, trust-focused UI (Shadcn-style).
- **Admin Panel**: Secure management interface (`/admin`) for manual curation.
- **Search**: Fast, server-side search functionality.
- **Automation Ready**: API-first design for easy integration with Telegram bots.
- **SEO Optimized**: Server-side rendered HTML (FastAPI + Jinja2).

## 🚀 Setup & Run

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Create a `.env` file in the root directory:
   ```env
   ADMIN_PASSWORD=your_secure_password
   ```

3. **Run Server**
   ```bash
   uvicorn app.main:app --reload
   ```
   Visit `http://127.0.0.1:8000`

## 🔐 Admin Panel
- **Login**: `/admin/login`
- **Dashboard**: `/admin`
- Manage courses, edit details, and clean up listings manually.

## 🛠 Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite (Simple & Fast)
- **Frontend**: Jinja2 + Plain CSS (No complex build steps)
- **Design**: "21st.dev" Editorial Style

## 📦 Deployment (Render)
1. Fork/Clone this repo.
2. Connect to Render.com as a **Web Service**.
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5. Add `ADMIN_PASSWORD` to Render Environment Variables.
