from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
import httpx
from bson import ObjectId
from bson.errors import InvalidId

from models import Task, TaskCreate, TaskUpdate, TaskStatus, TaskStats
from database import get_database
from config import settings

router = APIRouter()

async def notify_reminder_service(task: Task):
    """Notify the notification service about task with reminder"""
    if task.reminder_enabled and task.reminder_time:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.notification_service_url}/reminders",
                    json={
                        "task_id": task.id,
                        "title": f"Reminder: {task.title}",
                        "message": f"Task '{task.title}' is due soon",
                        "reminder_time": task.reminder_time.isoformat(),
                        "task_due_date": task.due_date.isoformat() if task.due_date else None
                    }
                )
        except Exception as e:
            # Log error but don't fail task creation
            print(f"Failed to notify reminder service: {e}")

@router.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate, db=Depends(get_database)):
    """Create a new task"""
    task_dict = task.model_dump()
    task_dict["created_at"] = datetime.utcnow()
    task_dict["updated_at"] = datetime.utcnow()
    task_dict["status"] = TaskStatus.PENDING
    
    result = await db.tasks.insert_one(task_dict)
    created_task = await db.tasks.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string
    created_task["_id"] = str(created_task["_id"])
    task_obj = Task(**created_task)
    
    # Notify reminder service if reminder is enabled
    await notify_reminder_service(task_obj)
    
    return task_obj

@router.get("/tasks", response_model=List[Task])
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db=Depends(get_database)
):
    """Get all tasks with optional filtering"""
    filter_dict = {}
    
    if status:
        filter_dict["status"] = status
    if priority:
        filter_dict["priority"] = priority
    if category:
        filter_dict["category"] = category
    if search:
        filter_dict["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    cursor = db.tasks.find(filter_dict).skip(skip).limit(limit).sort("created_at", -1)
    tasks = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for task in tasks:
        task["_id"] = str(task["_id"])
    
    return [Task(**task) for task in tasks]

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str, db=Depends(get_database)):
    """Get a specific task by ID"""
    try:
        object_id = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    
    task = await db.tasks.find_one({"_id": object_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task["_id"] = str(task["_id"])
    return Task(**task)

@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate, db=Depends(get_database)):
    """Update a task"""
    try:
        object_id = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    
    # Get existing task
    existing_task = await db.tasks.find_one({"_id": object_id})
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Prepare update data
    update_data = task_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # Update task
    await db.tasks.update_one({"_id": object_id}, {"$set": update_data})
    
    # Get updated task
    updated_task = await db.tasks.find_one({"_id": object_id})
    updated_task["_id"] = str(updated_task["_id"])
    task_obj = Task(**updated_task)
    
    # Notify reminder service if reminder settings changed
    if "reminder_enabled" in update_data or "reminder_time" in update_data:
        await notify_reminder_service(task_obj)
    
    return task_obj

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, db=Depends(get_database)):
    """Delete a task"""
    try:
        object_id = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    
    result = await db.tasks.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}

@router.patch("/tasks/{task_id}/complete", response_model=Task)
async def complete_task(task_id: str, db=Depends(get_database)):
    """Mark a task as completed"""
    try:
        object_id = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    
    update_data = {
        "status": TaskStatus.COMPLETED,
        "completed_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.tasks.update_one({"_id": object_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get updated task
    updated_task = await db.tasks.find_one({"_id": object_id})
    updated_task["_id"] = str(updated_task["_id"])
    
    return Task(**updated_task)

@router.get("/tasks/stats/overview", response_model=TaskStats)
async def get_task_stats(db=Depends(get_database)):
    """Get task statistics"""
    total_tasks = await db.tasks.count_documents({})
    pending_tasks = await db.tasks.count_documents({"status": TaskStatus.PENDING})
    in_progress_tasks = await db.tasks.count_documents({"status": TaskStatus.IN_PROGRESS})
    completed_tasks = await db.tasks.count_documents({"status": TaskStatus.COMPLETED})
    cancelled_tasks = await db.tasks.count_documents({"status": TaskStatus.CANCELLED})
    
    # Overdue tasks (due_date < now and status != completed)
    now = datetime.utcnow()
    overdue_tasks = await db.tasks.count_documents({
        "due_date": {"$lt": now},
        "status": {"$ne": TaskStatus.COMPLETED}
    })
    
    # Upcoming tasks (due in next 7 days)
    from datetime import timedelta
    upcoming_deadline = now + timedelta(days=7)
    upcoming_tasks = await db.tasks.count_documents({
        "due_date": {"$gte": now, "$lte": upcoming_deadline},
        "status": {"$ne": TaskStatus.COMPLETED}
    })
    
    return TaskStats(
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        in_progress_tasks=in_progress_tasks,
        completed_tasks=completed_tasks,
        cancelled_tasks=cancelled_tasks,
        overdue_tasks=overdue_tasks,
        upcoming_tasks=upcoming_tasks
    )