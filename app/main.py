from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import shutil
from bson import ObjectId

from .database_mongo import init_db, close_db
from .crud_mongo import (
    slugify,
    # Course operations
    create_course_sync, get_courses_sync, get_course_sync, 
    get_course_by_id_sync, update_course_sync, delete_course_sync,
    delete_courses_by_days_sync,
    search_courses_sync,
    # Blog operations
    get_posts_sync, get_post_sync, get_post_by_id_sync,
    create_post_sync, update_post_sync, delete_post_sync,
    # Page operations
    get_pages_sync, get_page_sync, get_page_by_id_sync,
    create_page_sync, update_page_sync
)
from .schemas import CourseCreate
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Ensure image directory exists
os.makedirs("app/static/images", exist_ok=True)

# Initialize MongoDB on startup
@app.on_event("startup")
async def startup_event():
    await init_db()
    print("✅ MongoDB connected and initialized")

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()
    print("👋 MongoDB connection closed")

# Helper function to convert MongoDB ObjectId to string
def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    
    # Create a copy to avoid modifying the original
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == "_id":
                result["id"] = str(value)
            else:
                result[key] = value
        return result
    
    return doc

# API
@app.post("/api/courses")
def add_course(course: CourseCreate):
    try:
        course_data = {
            "title": course.title,
            "description": course.description,
            "rating": course.rating,
            "instructor": course.instructor,
            "image": course.image,
            "udemy_link": course.udemy_link
        }
        result = create_course_sync(course_data)
        return serialize_doc(result)
    except Exception as e:
        print(f"❌ API ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
@app.head("/health")
def health():
    return {"status": "healthy"}

@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return f"""User-agent: *
Disallow: /admin
Allow: /

Sitemap: {base_url}/sitemap.xml
"""

@app.get("/sitemap.xml")
def sitemap_xml(request: Request):
    base_url = str(request.base_url).rstrip("/")
    
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    # Static pages
    for path in ["", "/about", "/contact", "/privacy", "/blog", "/courses"]:
        xml += f"""
    <url>
        <loc>{base_url}{path}</loc>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>"""

    # Courses
    courses = get_courses_sync()
    for c in courses:
        if c.get("slug"):
            created_at = c.get("created_at")
            lastmod = created_at.strftime('%Y-%m-%d') if created_at else ""
            xml += f"""
    <url>
        <loc>{base_url}/course/{c['slug']}</loc>
        <lastmod>{lastmod}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>"""

    # Blog Posts
    posts = get_posts_sync()
    for p in posts:
        if p.get("slug"):
            created_at = p.get("created_at")
            lastmod = created_at.strftime('%Y-%m-%d') if created_at else ""
            xml += f"""
    <url>
        <loc>{base_url}/blog/{p['slug']}</loc>
        <lastmod>{lastmod}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.7</priority>
    </url>"""

    xml += "\n</urlset>"
    return Response(content=xml, media_type="application/xml")

# Pages
@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse)
def home(request: Request):
    courses = get_courses_sync()
    page = get_page_sync("home")
    
    # Popular Courses Logic - search for courses with specific keywords
    keywords = ["java", "python", "ai", "web"]
    popular_courses = []
    for course in courses:
        title_lower = course.get("title", "").lower()
        if any(keyword in title_lower for keyword in keywords):
            popular_courses.append(course)
            if len(popular_courses) >= 8:
                break
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "courses": serialize_doc(courses),
        "popular_courses": serialize_doc(popular_courses),
        "page": serialize_doc(page)
    })

@app.get("/course/{slug}", response_class=HTMLResponse)
def course_page(slug: str, request: Request):
    course = get_course_sync(slug)
    if not course:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("course.html", {
        "request": request,
        "course": serialize_doc(course)
    })

@app.get("/go/{slug}")
def redirect_to_udemy(slug: str):
    course = get_course_sync(slug)
    print("DEBUG COURSE:", course)
    
    if not course:
        return {"detail": "Course not found"}
        
    udemy_link = course.get("udemy_link")
    print("DEBUG SOURCE LINK:", udemy_link)

    if not udemy_link:
        return {"detail": "Course link not found"}

    return RedirectResponse(udemy_link)

@app.get("/courses", response_class=HTMLResponse)
def all_courses(request: Request):
    courses = get_courses_sync()
    return templates.TemplateResponse("courses.html", {
        "request": request,
        "courses": serialize_doc(courses),
        "title": "All Courses - SU Course"
    })

@app.get("/search", response_class=HTMLResponse)
def search(request: Request, q: str = ""):
    courses = []
    if q:
        courses = search_courses_sync(q)
    return templates.TemplateResponse(
        "search.html",
        {"request": request, "courses": serialize_doc(courses), "query": q, "title": f"Search: {q}"}
    )

@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    page = get_page_sync("about")
    return templates.TemplateResponse("about.html", {
        "request": request, 
        "page": serialize_doc(page), 
        "title": "About - SU Course"
    })

@app.get("/blog", response_class=HTMLResponse)
def blog(request: Request):
    posts = get_posts_sync()
    return templates.TemplateResponse("blog.html", {
        "request": request, 
        "posts": serialize_doc(posts), 
        "title": "Blog - SU Course"
    })

@app.get("/blog/{slug}", response_class=HTMLResponse)
def blog_post(slug: str, request: Request):
    post = get_post_sync(slug)
    if not post: 
        raise HTTPException(404)
    return templates.TemplateResponse("blog_post.html", {
        "request": request, 
        "post": serialize_doc(post), 
        "title": f"{post.get('title')} - SU Course"
    })

@app.get("/contact", response_class=HTMLResponse)
def contact(request: Request):
    page = get_page_sync("contact")
    return templates.TemplateResponse("contact.html", {
        "request": request, 
        "page": serialize_doc(page), 
        "title": "Contact Us - SU Course"
    })

@app.post("/contact", response_class=HTMLResponse)
async def contact_post(
    request: Request, 
    name: str = Form(...), 
    email: str = Form(...), 
    message: str = Form(...)
):
    print(f"📧 EMAIL REQUEST FROM: {name} <{email}>\nMessage: {message}")
    
    success_msg = "Message sent successfully! We will get back to you soon."
    
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    
    if smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = "sucourse@zohomail.in"
            msg['Subject'] = f"New Contact from {name}"
            
            body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP("smtp.zoho.in", 587)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            text = msg.as_string()
            server.sendmail(smtp_user, "sucourse@zohomail.in", text)
            server.quit()
            
            success_msg += " (Email Sent)"
            print("✅ Email sent successfully via Zoho SMTP")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            success_msg += " (Failed to send email, logged on server)"
    else:
       print(f"--- START MESSAGE ---\nFrom: {name} <{email}>\n{message}\n--- END MESSAGE ---")

    page = get_page_sync("contact")
    return templates.TemplateResponse("contact.html", {
        "request": request, 
        "page": serialize_doc(page), 
        "title": "Contact Us - SU Course",
        "success": success_msg
    })

@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    page = get_page_sync("privacy")
    return templates.TemplateResponse("privacy.html", {
        "request": request, 
        "page": serialize_doc(page), 
        "title": "Privacy Policy - SU Course"
    })

# --- ADMIN PANEL ---
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpass123")
print(f"🔑 ADMIN PASSWORD ACTIVE: {ADMIN_PASSWORD}")

def admin_auth(request: Request):
    password = request.cookies.get("admin_pass")
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@app.post("/admin/login")
def admin_login_post(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        response = RedirectResponse("/admin", status_code=302)
        response.set_cookie("admin_pass", password, httponly=True)
        return response
    return HTMLResponse("Invalid password", status_code=401)

from fastapi import Depends

@app.get("/admin", response_class=HTMLResponse, dependencies=[Depends(admin_auth)])
def admin_dashboard(request: Request):
    courses = get_courses_sync()
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "courses": serialize_doc(courses)}
    )

@app.get("/admin/new", response_class=HTMLResponse, dependencies=[Depends(admin_auth)])
def admin_new_course(request: Request):
    return templates.TemplateResponse("admin/form.html", {"request": request, "course": None})

@app.post("/admin/new", dependencies=[Depends(admin_auth)])
async def admin_create_course(
    title: str = Form(...),
    description: str = Form(...),
    udemy_link: str = Form(...),
    image_file: UploadFile = File(None)
):
    slug = slugify(title)
    course_data = {
        "title": title,
        "slug": slug,
        "description": description,
        "udemy_link": udemy_link
    }
    
    # Handle Image Upload
    if image_file and image_file.filename:
        extension = os.path.splitext(image_file.filename)[1] or ".jpg"
        file_name = f"{slug}{extension}"
        file_path = f"app/static/images/{file_name}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
            
        course_data["image"] = f"/static/images/{file_name}"

    create_course_sync(course_data)
    return RedirectResponse("/admin", status_code=302)

@app.get("/admin/edit/{id}", response_class=HTMLResponse, dependencies=[Depends(admin_auth)])
def admin_edit_course(id: str, request: Request):
    course = get_course_by_id_sync(id)
    return templates.TemplateResponse(
        "admin/form.html",
        {"request": request, "course": serialize_doc(course)}
    )

@app.post("/admin/edit/{id}", dependencies=[Depends(admin_auth)])
async def admin_update_course(
    id: str,
    title: str = Form(...),
    description: str = Form(...),
    udemy_link: str = Form(...),
    image_file: UploadFile = File(None),
    delete_image: bool = Form(False)
):
    course = get_course_by_id_sync(id)
    update_data = {
        "title": title,
        "description": description,
        "udemy_link": udemy_link
    }
    
    # Handle Image Deletion
    if delete_image:
        update_data["image"] = None
        
    # Handle Image Replacement
    if image_file and image_file.filename:
        slug = course.get("slug") or slugify(title)
        extension = os.path.splitext(image_file.filename)[1] or ".jpg"
        file_name = f"{slug}{extension}"
        file_path = f"app/static/images/{file_name}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
            
        update_data["image"] = f"/static/images/{file_name}"

    update_course_sync(id, update_data)
    return RedirectResponse("/admin", status_code=302)

@app.get("/admin/delete/{id}", dependencies=[Depends(admin_auth)])
def admin_delete_course(id: str):
    delete_course_sync(id)
    return RedirectResponse("/admin", status_code=302)

@app.delete("/admin/delete-days/{days}", dependencies=[Depends(admin_auth)])
def delete_courses_by_days(days: int):
    if days not in [5, 10, 20]:
        return {"error": "Invalid range"}

    deleted_count = delete_courses_by_days_sync(days)

    return {
        "status": "success",
        "days": days,
        "deleted": deleted_count
    }

# --- Admin Blog ---
@app.get("/admin/blog", dependencies=[Depends(admin_auth)])
async def admin_blog_list(request: Request):
    posts = get_posts_sync()
    return templates.TemplateResponse("admin/blog_list.html", {
        "request": request, 
        "posts": serialize_doc(posts)
    })

@app.get("/admin/blog/new", dependencies=[Depends(admin_auth)])
async def admin_blog_new(request: Request):
    return templates.TemplateResponse("admin/blog_form.html", {"request": request})

@app.post("/admin/blog/new", dependencies=[Depends(admin_auth)])
async def admin_blog_create(
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str = Form(None),
    image_file: UploadFile = File(None)
):
    slug = slugify(title)
    post_data = {
        "title": title,
        "slug": slug,
        "content": content,
        "excerpt": excerpt
    }
    
    if image_file and image_file.filename:
        extension = os.path.splitext(image_file.filename)[1] or ".jpg"
        file_name = f"blog-{slug}{extension}"
        file_path = f"app/static/images/{file_name}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        post_data["image"] = f"/static/images/{file_name}"

    create_post_sync(post_data)
    return RedirectResponse("/admin/blog", status_code=302)

@app.get("/admin/blog/edit/{id}", dependencies=[Depends(admin_auth)])
async def admin_blog_edit(request: Request, id: str):
    post = get_post_by_id_sync(id)
    if not post: 
        raise HTTPException(404)
    return templates.TemplateResponse("admin/blog_form.html", {
        "request": request, 
        "post": serialize_doc(post)
    })

@app.post("/admin/blog/edit/{id}", dependencies=[Depends(admin_auth)])
async def admin_blog_update(
    id: str,
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str = Form(None),
    image_file: UploadFile = File(None),
    delete_image: bool = Form(False)
):
    post = get_post_by_id_sync(id)
    if not post: 
        raise HTTPException(404)
    
    update_data = {
        "title": title,
        "content": content,
        "excerpt": excerpt
    }

    if delete_image:
        update_data["image"] = None

    if image_file and image_file.filename:
        extension = os.path.splitext(image_file.filename)[1] or ".jpg"
        file_name = f"blog-{slugify(title)}{extension}"
        file_path = f"app/static/images/{file_name}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        update_data["image"] = f"/static/images/{file_name}"
    
    update_post_sync(id, update_data)
    return RedirectResponse("/admin/blog", status_code=302)

@app.get("/admin/blog/delete/{id}", dependencies=[Depends(admin_auth)])
async def admin_blog_delete(id: str):
    delete_post_sync(id)
    return RedirectResponse("/admin/blog", status_code=302)

# --- Admin Pages ---
@app.get("/admin/pages", dependencies=[Depends(admin_auth)])
async def admin_page_list(request: Request):
    pages = get_pages_sync()
    # Ensure default pages exist
    required = ["home", "about", "privacy", "contact"]
    existing_slugs = [p.get("slug") for p in pages]
    for slug in required:
        if slug not in existing_slugs:
            create_page_sync({
                "title": slug.capitalize(),
                "slug": slug,
                "content": ""
            })
    pages = get_pages_sync()
    return templates.TemplateResponse("admin/page_list.html", {
        "request": request, 
        "pages": serialize_doc(pages)
    })

@app.get("/admin/pages/edit/{id}", dependencies=[Depends(admin_auth)])
async def admin_page_edit(request: Request, id: str):
    page = get_page_by_id_sync(id)
    if not page: 
        raise HTTPException(404)
    return templates.TemplateResponse("admin/page_form.html", {
        "request": request, 
        "page": serialize_doc(page)
    })

@app.post("/admin/pages/edit/{id}", dependencies=[Depends(admin_auth)])
async def admin_page_update(
    id: str,
    title: str = Form(...),
    content: str = Form(...)
):
    page = get_page_by_id_sync(id)
    if not page: 
        raise HTTPException(404)
    
    update_data = {
        "title": title,
        "content": content
    }
    update_page_sync(id, update_data)
    return RedirectResponse("/admin/pages", status_code=302)
