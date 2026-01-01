from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_
from starlette.requests import Request
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Depends, HTTPException, Form

from .database import SessionLocal, engine
from .models import Base, Course, BlogPost, Page
from .schemas import CourseCreate
from .crud import create_course, get_courses, get_course, get_posts, get_post, get_page, get_pages

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Ensure image directory exists
os.makedirs("app/static/images", exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API
@app.post("/api/courses")
def add_course(course: CourseCreate, db: Session = Depends(get_db)):
    return create_course(db, course)

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
def sitemap_xml(request: Request, db: Session = Depends(get_db)):
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
    courses = get_courses(db)
    for c in courses:
        if c.slug:
            xml += f"""
    <url>
        <loc>{base_url}/course/{c.slug}</loc>
        <lastmod>{c.created_at.strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>"""

    # Blog Posts
    posts = get_posts(db)
    for p in posts:
        if p.slug:
             xml += f"""
    <url>
        <loc>{base_url}/blog/{p.slug}</loc>
        <lastmod>{p.created_at.strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.7</priority>
    </url>"""

    xml += "\n</urlset>"
    return Response(content=xml, media_type="application/xml")

# Pages
@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    courses = get_courses(db)
    page = get_page(db, "home")
    
    # Popular Courses Logic
    keywords = ["%java%", "%python%", "%ai%", "%web%"]
    filters = [Course.title.ilike(k) for k in keywords]
    popular_courses = db.query(Course).filter(or_(*filters)).limit(8).all()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "courses": courses,
        "popular_courses": popular_courses,
        "page": page
    })

@app.get("/course/{slug}", response_class=HTMLResponse)
def course_page(slug: str, request: Request, db: Session = Depends(get_db)):
    course = get_course(db, slug)
    if not course:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("course.html", {
        "request": request,
        "course": course
    })

@app.get("/go/{slug}")
def redirect_to_udemy(slug: str, db: Session = Depends(get_db)):
    course = get_course(db, slug)
    print("DEBUG COURSE:", course)
    
    if not course:
        return {"detail": "Course not found"}
        
    print("DEBUG SOURCE LINK:", course.udemy_link)

    if not course.udemy_link:
        return {"detail": "Course link not found"}

    return RedirectResponse(course.udemy_link)

@app.get("/courses", response_class=HTMLResponse)
def all_courses(request: Request, db: Session = Depends(get_db)):
    # All courses for the catalog page
    courses = get_courses(db)
    return templates.TemplateResponse("courses.html", {
        "request": request,
        "courses": courses,
        "title": "All Courses - SU Course"
    })

from .models import Course
@app.get("/search", response_class=HTMLResponse)
def search(request: Request, q: str = "", db: Session = Depends(get_db)):
    courses = []
    if q:
        courses = (
            db.query(Course)
            .filter(Course.title.ilike(f"%{q}%"))
            .all()
        )
    return templates.TemplateResponse(
        "search.html",
        {"request": request, "courses": courses, "query": q, "title": f"Search: {q}"}
    )

@app.get("/about", response_class=HTMLResponse)
def about(request: Request, db: Session = Depends(get_db)):
    page = get_page(db, "about")
    return templates.TemplateResponse("about.html", {"request": request, "page": page, "title": "About - SU Course"})

@app.get("/blog", response_class=HTMLResponse)
def blog(request: Request, db: Session = Depends(get_db)):
    posts = get_posts(db)
    return templates.TemplateResponse("blog.html", {"request": request, "posts": posts, "title": "Blog - SU Course"})

@app.get("/blog/{slug}", response_class=HTMLResponse)
def blog_post(slug: str, request: Request, db: Session = Depends(get_db)):
    post = get_post(db, slug)
    if not post: raise HTTPException(404)
    return templates.TemplateResponse("blog_post.html", {"request": request, "post": post, "title": f"{post.title} - SU Course"})

@app.get("/contact", response_class=HTMLResponse)
def contact(request: Request, db: Session = Depends(get_db)):
    page = get_page(db, "contact")
    return templates.TemplateResponse("contact.html", {"request": request, "page": page, "title": "Contact Us - SU Course"})

@app.post("/contact", response_class=HTMLResponse)
async def contact_post(
    request: Request, 
    name: str = Form(...), 
    email: str = Form(...), 
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    print(f"📧 EMAIL REQUEST FROM: {name} <{email}>\nMessage: {message}")
    
    # Simple simulation logic (or actual send if creds configured)
    success_msg = "Message sent successfully! We will get back to you soon."
    
    # Placeholder for actual SMTP if user adds env vars later
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
            
            # Assuming Zoho SMTP (ssl/tls)
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
       # Log it clearly so user can see it in terminal
       print(f"--- START MESSAGE ---\nFrom: {name} <{email}>\n{message}\n--- END MESSAGE ---")

    page = get_page(db, "contact")
    return templates.TemplateResponse("contact.html", {
        "request": request, 
        "page": page, 
        "title": "Contact Us - SU Course",
        "success": success_msg
    })

@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request, db: Session = Depends(get_db)):
    page = get_page(db, "privacy")
    return templates.TemplateResponse("privacy.html", {"request": request, "page": page, "title": "Privacy Policy - SU Course"})

# --- ADMIN PANEL ---
from fastapi import Form
from .crud import slugify
from dotenv import load_dotenv

load_dotenv()

# Centralized Password Logic
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

@app.get("/admin", response_class=HTMLResponse, dependencies=[Depends(admin_auth)])
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    courses = db.query(Course).order_by(Course.id.desc()).all()
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "courses": courses}
    )

@app.get("/admin/new", response_class=HTMLResponse, dependencies=[Depends(admin_auth)])
def admin_new_course(request: Request):
    return templates.TemplateResponse("admin/form.html", {"request": request, "course": None})

from fastapi import Form, File, UploadFile
import shutil

# ... imports ...

@app.post("/admin/new", dependencies=[Depends(admin_auth)])
async def admin_create_course(
    title: str = Form(...),
    description: str = Form(...),
    udemy_link: str = Form(...),
    image_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    slug = slugify(title)
    course = Course(
        title=title,
        slug=slug,
        description=description,
        udemy_link=udemy_link
    )
    
    # Handle Image Upload
    if image_file and image_file.filename:
        # Save to static/images
        extension = os.path.splitext(image_file.filename)[1] or ".jpg"
        file_name = f"{slug}{extension}"
        file_path = f"app/static/images/{file_name}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
            
        course.image = f"/static/images/{file_name}"

    db.add(course)
    db.commit()
    return RedirectResponse("/admin", status_code=302)

@app.get("/admin/edit/{id}", response_class=HTMLResponse, dependencies=[Depends(admin_auth)])
def admin_edit_course(id: int, request: Request, db: Session = Depends(get_db)):
    course = db.query(Course).get(id)
    return templates.TemplateResponse(
        "admin/form.html",
        {"request": request, "course": course}
    )

@app.post("/admin/edit/{id}", dependencies=[Depends(admin_auth)])
async def admin_update_course(
    id: int,
    title: str = Form(...),
    description: str = Form(...),
    udemy_link: str = Form(...),
    image_file: UploadFile = File(None),
    delete_image: bool = Form(False),
    db: Session = Depends(get_db)
):
    course = db.query(Course).get(id)
    course.title = title
    course.description = description
    course.udemy_link = udemy_link
    
    # Handle Image Deletion
    if delete_image:
        course.image = None
        # Could delete file here too, but keeping it simple for now is safer
        
    # Handle Image Replacement
    if image_file and image_file.filename:
        slug = course.slug or slugify(title)
        extension = os.path.splitext(image_file.filename)[1] or ".jpg"
        file_name = f"{slug}{extension}"
        file_path = f"app/static/images/{file_name}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
            
        course.image = f"/static/images/{file_name}"

    db.commit()
    return RedirectResponse("/admin", status_code=302)

@app.get("/admin/delete/{id}", dependencies=[Depends(admin_auth)])
def admin_delete_course(id: int, db: Session = Depends(get_db)):
    course = db.query(Course).get(id)
    db.delete(course)
    db.commit()
    return RedirectResponse("/admin", status_code=302)
# --- Admin Blog ---
@app.get("/admin/blog", dependencies=[Depends(admin_auth)])
async def admin_blog_list(request: Request, db: Session = Depends(get_db)):
    posts = db.query(BlogPost).order_by(BlogPost.created_at.desc()).all()
    return templates.TemplateResponse("admin/blog_list.html", {"request": request, "posts": posts})

@app.get("/admin/blog/new", dependencies=[Depends(admin_auth)])
async def admin_blog_new(request: Request):
    return templates.TemplateResponse("admin/blog_form.html", {"request": request})

@app.post("/admin/blog/new", dependencies=[Depends(admin_auth)])
async def admin_blog_create(
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str = Form(None),
    image_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    slug = slugify(title)
    post = BlogPost(title=title, slug=slug, content=content, excerpt=excerpt)
    
    if image_file and image_file.filename:
        extension = os.path.splitext(image_file.filename)[1] or ".jpg"
        file_name = f"blog-{slug}{extension}"
        file_path = f"app/static/images/{file_name}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        post.image = f"/static/images/{file_name}"

    db.add(post)
    db.commit()
    return RedirectResponse("/admin/blog", status_code=302)

@app.get("/admin/blog/edit/{id}", dependencies=[Depends(admin_auth)])
async def admin_blog_edit(request: Request, id: int, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.id == id).first()
    if not post: raise HTTPException(404)
    return templates.TemplateResponse("admin/blog_form.html", {"request": request, "post": post})

@app.post("/admin/blog/edit/{id}", dependencies=[Depends(admin_auth)])
async def admin_blog_update(
    id: int,
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str = Form(None),
    image_file: UploadFile = File(None),
    delete_image: bool = Form(False),
    db: Session = Depends(get_db)
):
    post = db.query(BlogPost).filter(BlogPost.id == id).first()
    if not post: raise HTTPException(404)
    
    post.title = title
    post.content = content
    post.excerpt = excerpt
    # simple re-slugify if title changed? or keep slug? Let's keep slug stable usually, or update it.
    # post.slug = slugify(title) # optional

    if delete_image:
         post.image = None

    if image_file and image_file.filename:
        extension = os.path.splitext(image_file.filename)[1] or ".jpg"
        file_name = f"blog-{slugify(title)}{extension}"
        file_path = f"app/static/images/{file_name}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        post.image = f"/static/images/{file_name}"
    
    db.commit()
    return RedirectResponse("/admin/blog", status_code=302)

@app.get("/admin/blog/delete/{id}", dependencies=[Depends(admin_auth)])
async def admin_blog_delete(id: int, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.id == id).first()
    if post:
        db.delete(post)
        db.commit()
    return RedirectResponse("/admin/blog", status_code=302)


# --- Admin Pages ---
@app.get("/admin/pages", dependencies=[Depends(admin_auth)])
async def admin_page_list(request: Request, db: Session = Depends(get_db)):
    pages = db.query(Page).all()
    # Ensure default pages exist
    required = ["home", "about", "privacy", "contact"]
    existing_slugs = [p.slug for p in pages]
    for slug in required:
        if slug not in existing_slugs:
            db.add(Page(title=slug.capitalize(), slug=slug, content=""))
            db.commit()
    pages = db.query(Page).all()
    return templates.TemplateResponse("admin/page_list.html", {"request": request, "pages": pages})

@app.get("/admin/pages/edit/{id}", dependencies=[Depends(admin_auth)])
async def admin_page_edit(request: Request, id: int, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.id == id).first()
    if not page: raise HTTPException(404)
    return templates.TemplateResponse("admin/page_form.html", {"request": request, "page": page})

@app.post("/admin/pages/edit/{id}", dependencies=[Depends(admin_auth)])
async def admin_page_update(
    id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    page = db.query(Page).filter(Page.id == id).first()
    if not page: raise HTTPException(404)
    page.title = title
    page.content = content
    db.commit()
    return RedirectResponse("/admin/pages", status_code=302)
