from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NotificationType(str, Enum):
    REMINDER = "reminder"
    DUE_DATE = "due_date"
    OVERDUE = "overdue"
    COMPLETION = "completion"

class ReminderBase(BaseModel):
    task_id: str = Field(..., description="ID of the associated task")
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=500)
    reminder_time: datetime = Field(..., description="When to send the reminder")
    task_due_date: Optional[datetime] = None

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    message: Optional[str] = Field(None, min_length=1, max_length=500)
    reminder_time: Optional[datetime] = None
    task_due_date: Optional[datetime] = None
    status: Optional[NotificationStatus] = None

class Reminder(ReminderBase):
    id: Optional[str] = Field(None, alias="_id")
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "task_id": "60f7b0c5d5f8a7b3c8e9f1a2",
                "title": "Reminder: Complete project documentation",
                "message": "Your task 'Complete project documentation' is due soon",
                "reminder_time": "2024-12-30T09:00:00",
                "task_due_date": "2024-12-31T23:59:59",
                "status": "pending"
            }
        }

class NotificationBase(BaseModel):
    task_id: str = Field(..., description="ID of the associated task")
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=500)
    notification_type: NotificationType = NotificationType.REMINDER

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: Optional[str] = Field(None, alias="_id")
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        populate_by_name = True

class UserPreferences(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str = Field(..., description="User identifier")
    email_notifications: bool = True
    push_notifications: bool = True
    reminder_advance_time: int = Field(30, description="Minutes before due date to send reminder")
    quiet_hours_start: Optional[str] = Field(None, description="Start of quiet hours (HH:MM format)")
    quiet_hours_end: Optional[str] = Field(None, description="End of quiet hours (HH:MM format)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "email_notifications": True,
                "push_notifications": True,
                "reminder_advance_time": 30,
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "08:00"
            }
        }