from bson import ObjectId
from fastapi import HTTPException, APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder

from app import pwd_context, db
from app.auth import create_jwt_token, get_current_user
from app.models import UserCredentials, UserProfile, User, Link, UserLinks, LinkCreate, UserDisplay

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
    _profile = profile.__dict__
    response = await db.users.update_one({'_id': user.id}, {'$set': _profile})
    if response.acknowledged:
        return {"detail": "Updated successfully.", "updated_profile": _profile}
    raise HTTPException(500, detail="Database client failed to update resource.")


@router.get("/links", tags=["User Links"], responses={})
async def view_all_links(user: User = Depends(get_current_user)):
    return jsonable_encoder(UserLinks(**user.__dict__))


@router.post("/links", tags=["User Links"], responses={})
async def create_link(link: LinkCreate = Body(...), user: User = Depends(get_current_user)):
    _link = Link(**link.__dict__)
    await db.users.update_one({'_id': user.id}, {'$push': {'links': _link.__dict__}})
    return {"detail": "Inserted successfully.", "inserted_link": jsonable_encoder(_link)}


@router.get("/links/{link_id}", tags=["User Links"], responses={})
async def view_link(link_id: str, user: User = Depends(get_current_user)):
    link_id = ObjectId(link_id)
    for link in user.links:
        if link.id == link_id:
            return jsonable_encoder(link)

    raise HTTPException(404, detail="Link not found.")


@router.put("/links/{link_id}", tags=["User Links"], responses={})
async def update_link(link_id: str, link: LinkCreate = Body(...), user: User = Depends(get_current_user)):
    result = await db.users.update_one({
        "_id": user.id,
        "links.id": ObjectId(link_id)
    }, {"$set": {f"links.$.{field}": value for field, value in link.__dict__.items()}})

    if not result.acknowledged:
        raise HTTPException(500, detail="Database client failed to update resource.")

    if result.matched_count == 0:
        raise HTTPException(404, detail="Link not found.")

    if result.modified_count > 0:
        return {"detail": "Updated successfully.", "updated_profile": jsonable_encoder(link)}


@router.delete("/links/{link_id}", tags=["User Links"], responses={})
async def delete_link(link_id: str, user: User = Depends(get_current_user)):
    result = await db.users.update_one({
        "_id": user.id,
        "links.id": ObjectId(link_id)
    }, {"$pull": {
        "links": {"id": ObjectId(link_id)}
    }})

    if not result.acknowledged:
        raise HTTPException(500, detail="Database client failed to delete resource.")

    if result.matched_count == 0:
        raise HTTPException(404, detail="Link not found.")

    if result.modified_count > 0:
        return {"detail": "Deleted successfully."}


@router.get("/{username}", tags=[], responses={})
async def delete_link(username: str):
    document = await db.users.find_one({'username': username})
    return jsonable_encoder(UserDisplay(**document))
