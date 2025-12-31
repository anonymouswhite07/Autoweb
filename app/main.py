from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.requests import Request

from .database import SessionLocal, engine
from .models import Base
from .schemas import CourseCreate
from .crud import create_course, get_courses, get_course

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

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

# Pages
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    courses = get_courses(db)
    return templates.TemplateResponse("home.html", {
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
