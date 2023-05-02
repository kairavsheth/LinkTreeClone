from fastapi.security import HTTPBearer
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

from config import settings

mongo_client = AsyncIOMotorClient(settings.MONGO_DETAILS)
db = mongo_client.linktree

security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
