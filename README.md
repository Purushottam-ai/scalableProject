# Personal Task & Reminder App

This is a microservices-based Personal Task & Reminder application built with Python, FastAPI, Streamlit, MongoDB, Docker, and Kubernetes.

## Project Structure

```
scalableProject/
├── ARCHITECTURE.md                 # Detailed architecture documentation
├── README.md                       # This file
├── Task.txt                       # Original requirements
├── docker-compose.yml             # Local development setup
├── frontend-service/              # Streamlit frontend microservice
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── config.py
├── task-service/                  # Task management REST API
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── database.py
│   └── config.py
├── notification-service/          # Notification management REST API
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── database.py
│   └── config.py
├── k8s-manifests/                # Kubernetes deployment files
│   ├── namespace.yaml
│   ├── mongodb/
│   ├── task-service/
│   ├── notification-service/
│   ├── frontend-service/
│   └── hpa/
└── scripts/                      # Deployment and utility scripts
    ├── deploy.ps1
    ├── cleanup.ps1
    └── test-endpoints.ps1
```

## Services Overview

### 1. Frontend Service (Port 8501)
- **Technology**: Streamlit
- **Purpose**: User interface for task and reminder management
- **Features**: Dashboard, task creation/editing, notifications view

### 2. Task Service (Port 8000)
- **Technology**: FastAPI + MongoDB
- **Purpose**: Task CRUD operations and management
- **Features**: Create, read, update, delete tasks; search and filtering

### 3. Notification Service (Port 8001)
- **Technology**: FastAPI + MongoDB
- **Purpose**: Reminder and notification management
- **Features**: Schedule reminders, send notifications, manage preferences

## Quick Start

### Prerequisites
- Docker and Docker Compose
- minikube
- kubectl
- Python 3.9+

### Local Development
```bash
# Clone and navigate to project
cd scalableProject

# Start all services with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:8501
# Task API: http://localhost:8000/docs
# Notification API: http://localhost:8001/docs
```

### Kubernetes Deployment
```bash
# Start minikube
minikube start

# Deploy to Kubernetes
.\scripts\deploy.ps1

# Access the frontend service
minikube service frontend-service -n task-app

# View Kubernetes dashboard
minikube dashboard
```

## API Endpoints

### Task Service (http://localhost:8000)
- `GET /tasks` - Get all tasks
- `POST /tasks` - Create new task
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `PATCH /tasks/{id}/complete` - Mark task complete

### Notification Service (http://localhost:8001)
- `GET /reminders` - Get all reminders
- `POST /reminders` - Create reminder
- `GET /reminders/{id}` - Get specific reminder
- `PUT /reminders/{id}` - Update reminder
- `DELETE /reminders/{id}` - Delete reminder
- `GET /notifications/history` - Get notification history

## Scaling Features

The application implements Horizontal Pod Autoscaler (HPA) for automatic scaling based on CPU utilization:
- **Min replicas**: 1
- **Max replicas**: 10
- **Target CPU**: 70%

## Technology Stack

- **Frontend**: Streamlit
- **Backend APIs**: FastAPI
- **Database**: MongoDB
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Scaling**: HPA
- **Language**: Python 3.9+

## Development

Each microservice is maintained as a separate component with its own:
- Dependencies (requirements.txt)
- Dockerfile
- Configuration
- Database models
- API routes

This ensures independent development, testing, and deployment of each service.