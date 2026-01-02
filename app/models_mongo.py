from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class CourseModel(BaseModel):
    """MongoDB Course Model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    slug: str
    description: Optional[str] = None
    rating: Optional[str] = None
    instructor: Optional[str] = None
    coupon: Optional[str] = None
    image: Optional[str] = None
    udemy_link: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class BlogPostModel(BaseModel):
    """MongoDB BlogPost Model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    slug: str
    content: Optional[str] = None
    excerpt: Optional[str] = None
    image: Optional[str] = None
    is_published: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PageModel(BaseModel):
    """MongoDB Page Model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    slug: str
    title: str
    content: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Helper class to convert MongoDB documents to dict
class MongoDocument:
    """Helper to convert MongoDB documents"""
    @staticmethod
    def to_dict(doc):
        if doc is None:
            return None
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
        return doc
