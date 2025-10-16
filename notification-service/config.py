import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
    database_name: str = os.getenv("DATABASE_NAME", "notification_db")
    task_service_url: str = os.getenv("TASK_SERVICE_URL", "http://task-service:8000")
    
settings = Settings()