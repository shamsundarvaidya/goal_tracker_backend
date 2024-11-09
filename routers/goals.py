from fastapi import  HTTPException, status, Depends, Response, Request, APIRouter
from datetime import datetime, timezone
from mongoDBModels import db_models
from pydanticModels import pydantic_models
from authentication import auth
from pymongo.errors import DuplicateKeyError
from typing import List


router = APIRouter()


    
@router.post("/add-goal/", response_model=pydantic_models.Goal)
async def create_goal(goal: pydantic_models.Goal,current_user: db_models.User = Depends(auth.get_current_user)):
    try:
        # if goal.user_id != str(current_user.id):  # Assuming current_user has an id attribute
        #     raise HTTPException(status_code=403, detail="User ID does not match the authenticated user.")
        # Convert Pydantic model to MongoEngine model
        goal_doc = db_models.Goal(
            user_id=str(current_user.id),
            title=goal.title,
            description=goal.description,
            category=goal.category,
            start_date=goal.start_date,
            end_date=goal.end_date,
            status=goal.status,
            progress=goal.progress,
            milestones=[db_models.Milestone(**m.model_dump()) for m in goal.milestones],
            reminders=[db_models.Reminder(**r.model_dump()) for r in goal.reminders],
            notes=[db_models.Note(**n.model_dump()) for n in goal.notes],
            tags=goal.tags,
            created_at=goal.created_at or datetime.now(timezone.utc),
            updated_at=goal.updated_at or datetime.now(timezone.utc)
        )
        goal_doc.save()
        print(goal_doc.id)
        goal.goal_id = str(goal_doc.id)
        goal.user_id = goal_doc.user_id
        return goal
    except DuplicateKeyError:
        # Return custom error if title is not unique
        raise HTTPException(status_code=400, detail="A goal with this title already exists.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/read-goals/", response_model=List[pydantic_models.Goal])
async def list_user_goals(current_user: db_models.User = Depends(auth.get_current_user)):

    try:
        # Fetch goals for the specified user
        goals = db_models.Goal.objects(user_id=str(current_user.id))

        # Check if user has any goals
        if not goals:
            raise HTTPException(status_code=404, detail="No goals found for this user.")

        # Convert MongoEngine documents to Pydantic models
        goal_list:List[pydantic_models.Goal] = []

        for goal in goals:
            # Convert the MongoEngine document to a dictionary
            doc = goal.to_mongo().to_dict()
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string for Pydantic

            # Create the GoalModel instance using model_validate
            goal_model = pydantic_models.Goal.model_validate(doc)
            goal_list.append(goal_model)

        return goal_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-goal/{goal_id}", response_model=dict)
async def delete_goal(goal_id: str, current_user: db_models.User = Depends(auth.get_current_user)):
    try:
        # Fetch the goal by ID
        goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()

        # Check if the goal exists
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found.")

        # Delete the goal
        goal.delete()

        return {"detail": "Goal deleted successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-milestone/{goal_id}/", response_model=pydantic_models.Milestone)
async def create_milestone(goal_id: str, milestone: pydantic_models.Milestone,current_user: db_models.User = Depends(auth.get_current_user)):

    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    
    db_milestone = db_models.Milestone(**milestone.model_dump())
    goal.milestones.append(db_milestone)
    goal.save()
    return milestone

@router.get("/get-milestones/{goal_id}/", response_model=List[pydantic_models.Milestone])
async def list_milestones(goal_id: str,current_user: db_models.User = Depends(auth.get_current_user)):
    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")

    # if str(goal.user_id) != str(current_user.id):  # Assuming `current_user` has an `id` attribute
    #     raise HTTPException(status_code=403, detail="No permission to access milestone to this goal.")

    return goal.milestones

@router.put("/update-milestone/{goal_id}/milestone/{milestone_id}", response_model=pydantic_models.Milestone)
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


@router.delete("/delete-milestone/{goal_id}/milestone/{milestone_id}")
async def delete_milestone(goal_id: str, milestone_id: str,current_user: db_models.User = Depends(auth.get_current_user)):
    goal = db_models.Goal.objects(id=goal_id,user_id=str(current_user.id)).first()
    if not ( goal and milestone_id ):
        raise HTTPException(status_code=404, detail="Goal or milestone not found.")
    goal.milestones = [m for m in goal.milestones if str(m.id) != milestone_id]
    goal.save()
    return {"detail": "Milestone deleted successfully."}


