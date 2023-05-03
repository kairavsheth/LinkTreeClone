from typing import List, Optional, Literal

from bson import ObjectId
from pydantic import BaseModel, HttpUrl, Field


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise ValueError("Not a valid ObjectId")
        return str(v)


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


class Link(LinkCreate):
    id: ObjectIdStr = Field(default_factory=ObjectId)


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


class UserDisplay(UserProfile):
    links: List[LinkCreate] = Field(default=[])


class User(UserProfile, UserLinks, UserCredentials):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Message(BaseModel):
    detail: str


class Token(BaseModel):
    token: str


class LinkResponse(Message):
    link_item: Link


response_404 = {
    "404": {
        "description": "Not found",
        "model": Message
    }}

response_401 = {
    "401": {
        "description": "Unauthorized access",
        "model": Message
    }}

response_500 = {
    "500": {
        "description": "Server Error",
        "model": Message
    }}
