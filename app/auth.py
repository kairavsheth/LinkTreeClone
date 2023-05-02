from datetime import datetime, timedelta

import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app import security, db
from app.models import User
from config import settings


def create_jwt_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=settings.JWT_EXP_DELTA_SECONDS),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload["user_id"]
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(**user)
        else:
            raise HTTPException(status_code=401, detail=f"Invalid user credentials.")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
