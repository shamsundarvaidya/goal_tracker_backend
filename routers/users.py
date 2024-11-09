from fastapi import  HTTPException, status, APIRouter
from mongoengine import DoesNotExist
from mongoDBModels import db_models
from pydanticModels import pydantic_models

router = APIRouter()

@router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def signup(user: pydantic_models.UserCreate):
    try:
        new_user = db_models.User(username=user.username, email=user.email)
        new_user.set_password(user.password)
        new_user.save()
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/user/{email}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(email: str):
    try:
        user = db_models.User.objects.get(email=email)
        user.delete()
        
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    

@router.put("/user/{email}/", status_code=status.HTTP_200_OK)
async def update_user(email: str, user_update: pydantic_models.UserUpdate):
    try:
        user = db_models.User.objects.get(email=email)
        if user_update.username:
            user.username = user_update.username
        #if user_update.email:
        #    user.email = user_update.email
        if user_update.password:
            user.set_password(user_update.password)
        user.save()
        return {"message": "User updated successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@router.get("/users/", status_code=status.HTTP_200_OK)
async def get_all_users():
    users = db_models.User.objects().all()
    return {"users": [{"username": user.username, "email": user.email} for user in users]}

@router.get("/user/{email}/", status_code=status.HTTP_200_OK)
async def get_user_by_email(email: str):
    try:
        user = db_models.User.objects.get(email=email)
        return {"username": user.username, "email": user.email}
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")