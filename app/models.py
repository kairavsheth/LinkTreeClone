from typing import List, Optional, Literal

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


class LinkCreate(BaseModel):
    url: HttpUrl
    platform: Literal['DRIBBLE', 'GITHUB', 'INSTAGRAM', 'LINKEDIN', 'TELEGRAM', 'TWITTER', 'WEBSITE', 'YOUTUBE']
    text: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {}


class Link(LinkCreate):
    id: ObjectId = Field(default_factory=ObjectId)

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

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {}


class UserDisplay(UserProfile, UserLinks):
    pass


class User(UserDisplay, UserCredentials):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {}
