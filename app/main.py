from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
import os

from pathlib import Path

# Safe DB Init
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Error creating database tables: {e}")

app = FastAPI(title="Simply Course")

# Get absolute path to current directory
BASE_DIR = Path(__file__).resolve().parent

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/ping")
def ping():
    return {"status": "ok"}

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints
@app.post("/api/courses", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    return crud.create_course(db=db, course=course)

@app.get("/api/courses", response_model=list[schemas.Course])
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courses = crud.get_courses(db, skip=skip, limit=limit)
    return courses

@app.get("/api/course/{slug}", response_model=schemas.Course)
def read_course(slug: str, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, slug=slug)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course

# Web Pages
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    courses = crud.get_courses(db, limit=20)
    return templates.TemplateResponse("index.html", {"request": request, "courses": courses})

@app.get("/course/{slug}", response_class=HTMLResponse)
async def course_detail(request: Request, slug: str, db: Session = Depends(get_db)):
    course = crud.get_course(db, slug=slug)
    if not course:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("detail.html", {"request": request, "course": course})
