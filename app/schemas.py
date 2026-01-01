from pydantic import BaseModel

class CourseCreate(BaseModel):
    title: str
    description: str | None = None
    rating: str | None = None
    instructor: str | None = None
    image: str | None = None
    udemy_link: str

class CourseOut(BaseModel):
    id: int
    title: str
    slug: str
    description: str | None = None
    image: str | None = None
    udemy_link: str | None = None
    rating: str | None = None
    instructor: str | None = None

    class Config:
        orm_mode = True
