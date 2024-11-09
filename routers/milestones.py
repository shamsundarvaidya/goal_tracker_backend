from fastapi import  HTTPException, status, Depends, Response, Request, APIRouter
from datetime import datetime, timezone
from mongoDBModels import db_models
from pydanticModels import pydantic_models
from authentication import auth
from pymongo.errors import DuplicateKeyError
from typing import List


router = APIRouter()

@router.post("/add/{goal_id}/", response_model=pydantic_models.Milestone)
async def create_milestone(goal_id: str, milestone: pydantic_models.Milestone,current_user: db_models.User = Depends(auth.get_current_user)):

    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    
    db_milestone = db_models.Milestone(**milestone.model_dump())
    goal.milestones.append(db_milestone)
    goal.save()
    return milestone

@router.get("/get/{goal_id}/", response_model=List[pydantic_models.Milestone])
async def list_milestones(goal_id: str,current_user: db_models.User = Depends(auth.get_current_user)):
    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")

    # if str(goal.user_id) != str(current_user.id):  # Assuming `current_user` has an `id` attribute
    #     raise HTTPException(status_code=403, detail="No permission to access milestone to this goal.")

    return goal.milestones

@router.put("/update/{goal_id}/milestone/{milestone_id}", response_model=pydantic_models.Milestone)
async def update_milestone(goal_id: str, milestone_id: str, milestone_update: pydantic_models.Milestone,current_user: db_models.User = Depends(auth.get_current_user)):
    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()

    if not (goal and milestone_id) :
        raise HTTPException(status_code=404, detail="Goal or milestone not found.")

    
    # Find the specific milestone in the goal's milestones list by ID
    milestone = next((m for m in goal.milestones if str(m.id) == milestone_id), None)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
     # Update only fields that are provided in the request, ignoring 'id'
    update_data = milestone_update.model_dump(exclude_unset=True, exclude={"id"})

    for field, value in update_data.items():
        setattr(milestone, field, value)

    goal.save()
    return milestone


@router.delete("/delete/{goal_id}/milestone/{milestone_id}")
async def delete_milestone(goal_id: str, milestone_id: str,current_user: db_models.User = Depends(auth.get_current_user)):
    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not ( goal and milestone_id ):
        raise HTTPException(status_code=404, detail="Goal or milestone not found.")
    goal.milestones = [m for m in goal.milestones if str(m.id) != milestone_id]
    goal.save()
    return {"detail": "Milestone deleted successfully."}


