import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://admin:password123@mongodb:27017")
    database_name: str = os.getenv("DATABASE_NAME", "task_db")
    notification_service_url: str = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8001")
    
settings = Settings()