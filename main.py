from fastapi import FastAPI, HTTPException, status, Depends, Response, Request
from mongoengine import connect, DoesNotExist
from mongoDBModels import db_models
from pydanticModels import pydantic_models
from routers import users, goals, milestones, notes, reminders
from authentication import auth
from fastapi.middleware.cors import CORSMiddleware

# Connect to MongoDB
connect(db="GOAL_TRACKER", host="mongodb://localhost", port=27017)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with your frontend's URL
    allow_credentials=True,  # Allow cookies and authorization headers
    allow_methods=["*"],     # Allow all HTTP methods if needed
    allow_headers=["*"],     # Allow all headers if needed
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(goals.router, prefix="/goals", tags=["goals"])
app.include_router(milestones.router, prefix="/milestone", tags=["milestones"])
app.include_router(notes.router, prefix="/note", tags=["notes"])
app.include_router(reminders.router, prefix="/reminder", tags=["reminders"])


# FastAPI Endpoints       
@app.post("/login")
async def login(response: Response,user:pydantic_models.UserAuth):
    try:
        db_user = db_models.User.objects.get(username=user.username)
        if db_user is None or not db_user.check_password(user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = auth.create_access_token(data={"sub": db_user.username})
        id = str(db_user.id)
        response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
         
    )
        return {"username": db_user.username,"user_id":id,"status":"success"}
        
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        

if __name__ == "__main__":
   import uvicorn
   uvicorn.run(app, host="0.0.0.0", port=8000)
