import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Pydantic Model for Request Body
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str




class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None




class UserAuth(BaseModel):
    username: str
    password: str


#Document models for goal

class Milestone(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))  # Unique identifier
    title: str
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[str] = Field(default="Pending")
    completed_date: Optional[datetime] = None


class Reminder(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))  # Unique identifier
    reminder_date: datetime
    message: str


class Note(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))  # Unique identifier
    note_date: datetime
    content: str


# Main document model
class Goal(BaseModel):
    goal_id: Optional[str] = Field(alias="_id", default=None)
    user_id: Optional[str] = Field(default=None)
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = Field(default="In Progress")
    progress: int = Field(default=0)
    milestones: List[Milestone] = Field(default_factory=list)
    reminders: List[Reminder] = Field(default_factory=list)
    notes: List[Note] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UpdateGoal(BaseModel):
    goal_id: str = Field(alias="_id", default=None)
    title: Optional[str] = ""
    description: Optional[str] = ""
    category: Optional[str] = ""
    start_date: Optional[datetime] = ""
    end_date: Optional[datetime] = ""
    status: Optional[str] = ""
    progress: Optional[int] = Field(default=0)
    milestones: Optional[List[Milestone]] = Field(default_factory=list)
    reminders: Optional[List[Reminder]] = Field(default_factory=list)
    notes: Optional[List[Note]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)


    model_config = ConfigDict(from_attributes=True)