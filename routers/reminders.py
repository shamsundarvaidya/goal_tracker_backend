from fastapi import  HTTPException, status, Depends, Response, Request, APIRouter
from datetime import datetime, timezone
from mongoDBModels import db_models
from pydanticModels import pydantic_models
from authentication import auth
from pymongo.errors import DuplicateKeyError
from typing import List


router = APIRouter()

@router.post("/add/{goal_id}/", response_model=pydantic_models.Reminder)
async def create_reminder(goal_id: str, reminder: pydantic_models.Reminder,current_user: db_models.User = Depends(auth.get_current_user)):

    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    
    db_reminder = db_models.Reminder(**reminder.model_dump())
    goal.reminders.append(db_reminder)
    goal.save()
    return reminder

@router.get("/get/{goal_id}/", response_model=List[pydantic_models.Reminder])
async def list_reminders(goal_id: str,current_user: db_models.User = Depends(auth.get_current_user)):
    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")

    return goal.reminders

@router.put("/update/{goal_id}", response_model=pydantic_models.Reminder)
async def update_reminder(goal_id: str, reminder_update: pydantic_models.Reminder,current_user: db_models.User = Depends(auth.get_current_user)):
    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()

    if not goal  :
        raise HTTPException(status_code=404, detail="Goal or milestone not found.")

    
    # Find the specific milestone in the goal's milestones list by ID
    reminder = next((r for r in goal.reminders if str(r.id) == reminder_update.id), None)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
     # Update only fields that are provided in the request, ignoring 'id'
    update_data = reminder_update.model_dump(exclude_unset=True, exclude={"id"})

    for field, value in update_data.items():
        setattr(reminder, field, value)

    goal.save()
    return reminder


@router.delete("/delete/{goal_id}/reminder/{reminder_id}")
async def delete_milestone(goal_id: str, reminder_id: str,current_user: db_models.User = Depends(auth.get_current_user)):
    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not ( goal and reminder_id ):
        raise HTTPException(status_code=404, detail="Goal or milestone not found.")
    goal.milestones = [r for r in goal.reminders if str(r.id) != reminder_id]
    goal.save()
    return {"detail": "Reminder deleted successfully."}


