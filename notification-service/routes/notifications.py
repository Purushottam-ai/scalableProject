from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from bson.errors import InvalidId

from models import (
    Reminder, ReminderCreate, ReminderUpdate, 
    Notification, NotificationCreate, 
    NotificationStatus, NotificationType
)
from database import get_database

router = APIRouter()

async def send_notification_logic(notification: Notification):
    """Background task to simulate sending notification"""
    # In a real implementation, this would integrate with email/SMS/push notification services
    print(f"Sending notification: {notification.title} - {notification.message}")
    
    # Simulate notification sending delay
    import asyncio
    await asyncio.sleep(1)
    
    # For demo purposes, we'll just log the notification
    return True

@router.post("/reminders", response_model=Reminder)
async def create_reminder(reminder: ReminderCreate, db=Depends(get_database)):
    """Create a new reminder"""
    reminder_dict = reminder.model_dump()
    reminder_dict["created_at"] = datetime.utcnow()
    reminder_dict["updated_at"] = datetime.utcnow()
    reminder_dict["status"] = NotificationStatus.PENDING
    
    result = await db.reminders.insert_one(reminder_dict)
    created_reminder = await db.reminders.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string
    created_reminder["_id"] = str(created_reminder["_id"])
    
    return Reminder(**created_reminder)

@router.get("/reminders", response_model=List[Reminder])
async def get_reminders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[NotificationStatus] = None,
    task_id: Optional[str] = None,
    db=Depends(get_database)
):
    """Get all reminders with optional filtering"""
    filter_dict = {}
    
    if status:
        filter_dict["status"] = status
    if task_id:
        filter_dict["task_id"] = task_id
    
    cursor = db.reminders.find(filter_dict).skip(skip).limit(limit).sort("reminder_time", 1)
    reminders = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for reminder in reminders:
        reminder["_id"] = str(reminder["_id"])
    
    return [Reminder(**reminder) for reminder in reminders]

@router.get("/reminders/{reminder_id}", response_model=Reminder)
async def get_reminder(reminder_id: str, db=Depends(get_database)):
    """Get a specific reminder by ID"""
    try:
        object_id = ObjectId(reminder_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid reminder ID format")
    
    reminder = await db.reminders.find_one({"_id": object_id})
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    reminder["_id"] = str(reminder["_id"])
    return Reminder(**reminder)

@router.put("/reminders/{reminder_id}", response_model=Reminder)
async def update_reminder(reminder_id: str, reminder_update: ReminderUpdate, db=Depends(get_database)):
    """Update a reminder"""
    try:
        object_id = ObjectId(reminder_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid reminder ID format")
    
    # Get existing reminder
    existing_reminder = await db.reminders.find_one({"_id": object_id})
    if not existing_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Prepare update data
    update_data = reminder_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # Update reminder
    await db.reminders.update_one({"_id": object_id}, {"$set": update_data})
    
    # Get updated reminder
    updated_reminder = await db.reminders.find_one({"_id": object_id})
    updated_reminder["_id"] = str(updated_reminder["_id"])
    
    return Reminder(**updated_reminder)

@router.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: str, db=Depends(get_database)):
    """Delete a reminder"""
    try:
        object_id = ObjectId(reminder_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid reminder ID format")
    
    result = await db.reminders.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    return {"message": "Reminder deleted successfully"}

@router.post("/notifications/send", response_model=Notification)
async def send_notification(
    notification: NotificationCreate, 
    background_tasks: BackgroundTasks,
    db=Depends(get_database)
):
    """Send a notification immediately"""
    notification_dict = notification.model_dump()
    notification_dict["created_at"] = datetime.utcnow()
    notification_dict["status"] = NotificationStatus.PENDING
    
    result = await db.notifications.insert_one(notification_dict)
    created_notification = await db.notifications.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string
    created_notification["_id"] = str(created_notification["_id"])
    notification_obj = Notification(**created_notification)
    
    # Send notification in background
    background_tasks.add_task(send_notification_logic, notification_obj)
    
    # Update status to sent
    await db.notifications.update_one(
        {"_id": result.inserted_id},
        {"$set": {"status": NotificationStatus.SENT, "sent_at": datetime.utcnow()}}
    )
    
    return notification_obj

@router.get("/notifications/history", response_model=List[Notification])
async def get_notification_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[NotificationStatus] = None,
    notification_type: Optional[NotificationType] = None,
    task_id: Optional[str] = None,
    db=Depends(get_database)
):
    """Get notification history with optional filtering"""
    filter_dict = {}
    
    if status:
        filter_dict["status"] = status
    if notification_type:
        filter_dict["notification_type"] = notification_type
    if task_id:
        filter_dict["task_id"] = task_id
    
    cursor = db.notifications.find(filter_dict).skip(skip).limit(limit).sort("created_at", -1)
    notifications = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for notification in notifications:
        notification["_id"] = str(notification["_id"])
    
    return [Notification(**notification) for notification in notifications]

@router.get("/reminders/due/check")
async def check_due_reminders(db=Depends(get_database)):
    """Check for due reminders and send notifications"""
    now = datetime.utcnow()
    
    # Find reminders that are due (reminder_time <= now and status = pending)
    due_reminders = await db.reminders.find({
        "reminder_time": {"$lte": now},
        "status": NotificationStatus.PENDING
    }).to_list(length=None)
    
    notifications_sent = 0
    
    for reminder_doc in due_reminders:
        # Create notification
        notification = NotificationCreate(
            task_id=reminder_doc["task_id"],
            title=reminder_doc["title"],
            message=reminder_doc["message"],
            notification_type=NotificationType.REMINDER
        )
        
        # Send notification
        notification_dict = notification.model_dump()
        notification_dict["created_at"] = now
        notification_dict["status"] = NotificationStatus.SENT
        notification_dict["sent_at"] = now
        
        await db.notifications.insert_one(notification_dict)
        
        # Update reminder status
        await db.reminders.update_one(
            {"_id": reminder_doc["_id"]},
            {"$set": {"status": NotificationStatus.SENT, "sent_at": now, "updated_at": now}}
        )
        
        notifications_sent += 1
    
    return {"message": f"Processed {notifications_sent} due reminders"}

@router.get("/stats/overview")
async def get_notification_stats(db=Depends(get_database)):
    """Get notification statistics"""
    total_reminders = await db.reminders.count_documents({})
    pending_reminders = await db.reminders.count_documents({"status": NotificationStatus.PENDING})
    sent_reminders = await db.reminders.count_documents({"status": NotificationStatus.SENT})
    
    total_notifications = await db.notifications.count_documents({})
    sent_notifications = await db.notifications.count_documents({"status": NotificationStatus.SENT})
    failed_notifications = await db.notifications.count_documents({"status": NotificationStatus.FAILED})
    
    # Due reminders in next hour
    next_hour = datetime.utcnow() + timedelta(hours=1)
    due_soon = await db.reminders.count_documents({
        "reminder_time": {"$lte": next_hour},
        "status": NotificationStatus.PENDING
    })
    
    return {
        "total_reminders": total_reminders,
        "pending_reminders": pending_reminders,
        "sent_reminders": sent_reminders,
        "total_notifications": total_notifications,
        "sent_notifications": sent_notifications,
        "failed_notifications": failed_notifications,
        "due_soon": due_soon
    }