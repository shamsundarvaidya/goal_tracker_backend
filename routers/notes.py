from fastapi import  HTTPException, status, Depends, Response, Request, APIRouter
from datetime import datetime, timezone
from mongoDBModels import db_models
from pydanticModels import pydantic_models
from authentication import auth
from pymongo.errors import DuplicateKeyError
from typing import List


router = APIRouter()

@router.post("/add/{goal_id}/", response_model=pydantic_models.Note)
async def create_note(goal_id: str, note: pydantic_models.Note,current_user: db_models.User = Depends(auth.get_current_user)):

    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    
    db_note = db_models.Note(**note.model_dump())
    goal.notes.append(db_note)
    goal.save()
    return note

@router.get("/get/{goal_id}/", response_model=List[pydantic_models.Note])
async def list_notes(goal_id: str,current_user: db_models.User = Depends(auth.get_current_user)):
    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")

    return goal.notes

@router.put("/update/{goal_id}", response_model=pydantic_models.Note)
async def update_note(goal_id: str, note_update: pydantic_models.Note,current_user: db_models.User = Depends(auth.get_current_user)):
    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()

    if not goal  :
        raise HTTPException(status_code=404, detail="Goal or milestone not found.")

    
    # Find the specific milestone in the goal's milestones list by ID
    note = next((r for r in goal.notes if str(r.id) == note_update.id), None)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
     # Update only fields that are provided in the request, ignoring 'id'
    update_data = note_update.model_dump(exclude_unset=True, exclude={"id"})

    for field, value in update_data.items():
        setattr(note, field, value)

    goal.save()
    return note


@router.delete("/delete/{goal_id}/note/{note_id}")
async def delete_milestone(goal_id: str, note_id: str,current_user: db_models.User = Depends(auth.get_current_user)):
    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not ( goal and note_id ):
        raise HTTPException(status_code=404, detail="Goal or milestone not found.")
    goal.milestones = [r for r in goal.notes if str(r.id) != note_id]
    goal.save()
    return {"detail": "Note deleted successfully."}


