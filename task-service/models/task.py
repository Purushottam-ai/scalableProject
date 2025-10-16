from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: TaskPriority = TaskPriority.MEDIUM
    category: Optional[str] = Field(None, max_length=100)
    due_date: Optional[datetime] = None
    reminder_enabled: bool = False
    reminder_time: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[TaskPriority] = None
    category: Optional[str] = Field(None, max_length=100)
    due_date: Optional[datetime] = None
    reminder_enabled: Optional[bool] = None
    reminder_time: Optional[datetime] = None
    status: Optional[TaskStatus] = None

class Task(TaskBase):
    id: Optional[str] = Field(None, alias="_id")
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive documentation for the microservices project",
                "priority": "high",
                "category": "work",
                "due_date": "2024-12-31T23:59:59",
                "reminder_enabled": True,
                "reminder_time": "2024-12-30T09:00:00",
                "status": "pending"
            }
        }

class TaskStats(BaseModel):
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    cancelled_tasks: int
    overdue_tasks: int
    upcoming_tasks: int