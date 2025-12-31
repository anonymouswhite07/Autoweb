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
        # coupon removed per recent revert, but crud might still have it if schema has it. 
        # Reverting to simple structure if needed, but schema shows coupon.
        # Let's align with the fact we reverted coupon logic in parser/website but DB might still expect it or allow None.
        # Safest is to keep it if field exists, but pass None if not provided.
        # But wait, the user said "description is not available in web".
        # This means `course.description` might be missing or not saving.
        # Let's verify `website.py` sending it.
        # website.py sends: "description": course.get("description"),
        # schemas.py has: description: str | None = None
        # models.py has: description = Column(String)
        # So it SHOULD work.
        # Let's just ensure this block is correct.
        image=course.image,
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
