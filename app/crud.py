from sqlalchemy.orm import Session
from .models import Course
import re

def slugify(text: str):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'\s+', '-', text).strip('-')

def create_course(db: Session, course):
    slug = slugify(course.title)

    existing = db.query(Course).filter(Course.slug == slug).first()
    if existing:
        return existing

    db_course = Course(
        title=course.title,
        slug=slug,
        description=course.description,
        rating=course.rating,
        instructor=course.instructor,
        udemy_link=course.udemy_link,
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_courses(db: Session):
    return db.query(Course).order_by(Course.created_at.desc()).all()

def get_course(db: Session, slug: str):
    return db.query(Course).filter(Course.slug == slug).first()
