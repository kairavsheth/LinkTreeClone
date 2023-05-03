from bson import ObjectId
from fastapi import HTTPException, APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder

from app import pwd_context, db
from app.auth import create_jwt_token, get_current_user
from app.models import UserCredentials, UserProfile, User, Link, UserLinks, LinkCreate, UserDisplay, response_401, \
    response_404, Message, Token, response_500, LinkResponse

router = APIRouter()


@router.post("/signup", tags=['Authentication'], response_description="Authorisation token",
             responses={
                 "400": {
                     "description": "Duplicate signup",
                     "model": Message
                 }})
async def signup(user: UserCredentials = Body(...)) -> Token:
    """
    Registers new user using credentials and responds with authorisation token
    """
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


@router.post("/login", tags=['Authentication'], response_description="Authorisation token",
             responses={
                 "400": {
                     "description": "Incorrect username or password",
                     "model": Message
                 }})
async def login(user: UserCredentials = Body(...)) -> Token:
    """
    Login existing user using credentials and responds with authorisation token
    """
    _user = await db.users.find_one({"username": user.username})
    if not _user or not pwd_context.verify(user.password, _user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials.")
    token = create_jwt_token(str(_user["_id"]))
    return {"token": token}


@router.get("/user/profile", tags=["Current User Profile"], response_description="Profile of the logged in user",
            responses=response_401)
async def view_profile(user: User = Depends(get_current_user)) -> UserProfile:
    """
    Get profile of current authorised user
    """
    return jsonable_encoder(UserProfile(**user.__dict__))


@router.put("/user/profile", tags=["Current User Profile"], response_description="Success message",
            responses={**response_401, **response_500})
async def update_profile(profile: UserProfile = Body(...), user: User = Depends(get_current_user)) -> Message:
    """
    Update profile of current authorised user
    """
    _profile = profile.__dict__
    response = await db.users.update_one({'_id': user.id}, {'$set': _profile})
    if response.acknowledged:
        return {"detail": "Updated successfully."}
    raise HTTPException(500, detail="Database client failed to update resource.")


@router.get("/links", tags=["User Links"], response_description="Array of link objects belonging to authorized user",
            responses=response_401)
async def view_all_links(user: User = Depends(get_current_user)) -> UserLinks:
    """
    View all links of current authorised user
    """
    return jsonable_encoder(UserLinks(**user.__dict__))


@router.post("/links", tags=["User Links"], response_description="Message and Link object",
             responses=response_401)
async def create_link(link: LinkCreate = Body(...), user: User = Depends(get_current_user)) -> LinkResponse:
    """
    Create new link for current authorised user
    """
    _link = Link(**link.__dict__)
    await db.users.update_one({'_id': user.id}, {'$push': {'links': _link.__dict__}})
    return {"detail": "Inserted successfully.", "link_item": jsonable_encoder(_link)}


@router.get("/links/{link_id}", tags=["User Links"], response_description="Link object",
            responses={**response_404, **response_401})
async def view_link(link_id: str, user: User = Depends(get_current_user)) -> Link:
    """
    View link of current authorised user using id
    """
    link_id = ObjectId(link_id)
    for link in user.links:
        if link.id == link_id:
            return jsonable_encoder(link)

    raise HTTPException(404, detail="Link not found.")


@router.put("/links/{link_id}", tags=["User Links"], response_description="Message and Link object",
            responses={**response_404, **response_401, **response_500})
async def update_link(link_id: str, link: LinkCreate = Body(...),
                      user: User = Depends(get_current_user)) -> LinkResponse:
    """
    Update a link of current authorised user using id
    """
    result = await db.users.update_one({
        "_id": user.id,
        "links.id": ObjectId(link_id)
    }, {"$set": {f"links.$.{field}": value for field, value in link.__dict__.items()}})

    if not result.acknowledged:
        raise HTTPException(500, detail="Database client failed to update resource.")

    if result.matched_count == 0:
        raise HTTPException(404, detail="Link not found.")

    if result.modified_count > 0:
        return {"detail": "Updated successfully.", "updated_link": jsonable_encoder(link)}


@router.delete("/links/{link_id}", tags=["User Links"], response_description="Message",
               responses={**response_404, **response_401, **response_500})
async def delete_link(link_id: str, user: User = Depends(get_current_user)) -> Message:
    """
    Delete a link of current authorised user using id
    """
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


@router.get("/{username}", tags=["Public View"], response_description="User's profile with all links",
            responses=response_404)
async def link_tree(username: str) -> UserDisplay:
    """
    Get the linktree of a user through url slug a.k.a. username
    """

    document = await db.users.find_one({'username': username})
    if document:
        return jsonable_encoder(UserDisplay(**document))
    raise HTTPException(404, detail="Page not found")
