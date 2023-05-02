from enum import Enum
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, HttpUrl, Field


class UserCredentials(BaseModel):
    username: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "$Abc123#"
            }
        }


class Platform(Enum):
    DRIBBLE = 'DRIBBLE'
    GITHUB = 'GITHUB'
    INSTAGRAM = 'INSTAGRAM'
    LINKEDIN = 'LINKEDIN'
    TELEGRAM = 'TELEGRAM'
    TWITTER = 'TWITTER'
    WEBSITE = 'WEBSITE'
    YOUTUBE = 'YOUTUBE'
    OTHER = 'OTHER'


class Link(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    url: HttpUrl
    platform: Platform
    text: str
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {}


class UserProfile(BaseModel):
    username: str
    title: Optional[str]
    profile_picture: Optional[HttpUrl]


class UserLinks(BaseModel):
    links: List[Link] = Field(default=[])


class User(UserProfile, UserCredentials, UserLinks):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {}
