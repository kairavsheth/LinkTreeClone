from fastapi import HTTPException, APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder

from app import pwd_context, db
from app.auth import create_jwt_token, get_current_user
from app.models import UserCredentials, UserProfile, User

router = APIRouter()


@router.post("/signup", tags=['Authentication'])
async def signup(user: UserCredentials = Body(...)):
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = pwd_context.hash(user.password)
    new_user = {
        "username": user.username,
        "password": hashed_password,
    }
    result = await db.users.insert_one(new_user)
    token = create_jwt_token(str(result.inserted_id))
    return {"token": token}


@router.post("/login", tags=['Authentication'], responses={})
async def login(user: UserCredentials = Body(...)):
    _user = await db.users.find_one({"username": user.username})
    if not _user or not pwd_context.verify(user.password, _user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials.")
    token = create_jwt_token(str(_user["_id"]))
    return {"token": token}


@router.get("/user/profile", tags=["Current User Profile"], responses={})
async def view_profile(user: User = Depends(get_current_user)):
    return jsonable_encoder(UserProfile(**user.__dict__))


@router.put("/user/profile", tags=["Current User Profile"], responses={})
async def update_profile(profile: UserProfile = Body(...), user: User = Depends(get_current_user)):
    await db.users.update_one({'_id': user.id}, {'$set': jsonable_encoder(profile)})
    return {"detail": "Updated successfully."}

