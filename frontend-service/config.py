import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL", "http://task-service:8000/api/v1")
    NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8001/api/v1")
    
    # For local development
    if os.getenv("ENVIRONMENT") == "development":
        TASK_SERVICE_URL = "http://localhost:8000/api/v1"
        NOTIFICATION_SERVICE_URL = "http://localhost:8001/api/v1"

config = Config()