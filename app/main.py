from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.requests import Request
import os

from .database import SessionLocal, engine
from .models import Base
from .schemas import CourseCreate
from .crud import create_course, get_courses, get_course

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

# Pages
@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    courses = get_courses(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "courses": courses
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
    if not course:
        raise HTTPException(status_code=404)
    return RedirectResponse(course.udemy_link)

@app.get("/courses", response_class=HTMLResponse)
def all_courses(request: Request, db: Session = Depends(get_db)):
    # reusing index template for now which lists all courses
    courses = get_courses(db)
    return templates.TemplateResponse("index.html", {
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

@app.post("/admin/new", dependencies=[Depends(admin_auth)])
def admin_create_course(
    title: str = Form(...),
    description: str = Form(...),
    udemy_link: str = Form(...),
    db: Session = Depends(get_db)
):
    course = Course(
        title=title,
        slug=slugify(title),
        description=description,
        udemy_link=udemy_link
    )
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
def admin_update_course(
    id: int,
    title: str = Form(...),
    description: str = Form(...),
    udemy_link: str = Form(...),
    db: Session = Depends(get_db)
):
    course = db.query(Course).get(id)
    course.title = title
    # Only update slug if title changed significantly, but for now simple overwrite is fine
    # course.slug = slugify(title) 
    course.description = description
    course.udemy_link = udemy_link
    db.commit()
    return RedirectResponse("/admin", status_code=302)

@app.get("/admin/delete/{id}", dependencies=[Depends(admin_auth)])
def admin_delete_course(id: int, db: Session = Depends(get_db)):
    course = db.query(Course).get(id)
    db.delete(course)
    db.commit()
    return RedirectResponse("/admin", status_code=302)
