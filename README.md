# Personal Task & Reminder App

This is a microservices-based Personal Task & Reminder application built with Python, FastAPI, Streamlit, MongoDB, Docker, and Kubernetes.

## Project Structure

```
scalableProject/
├── README.md                       # This file
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
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py
│   └── routes/
│       ├── __init__.py
│       └── tasks.py
├── notification-service/          # Notification management REST API
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── notification.py
│   └── routes/
│       ├── __init__.py
│       └── notifications.py
└── k8s-manifests/                # Kubernetes deployment files
    ├── namespace.yaml
    ├── mongodb/
    │   ├── mongodb-deployment.yaml
    │   ├── mongodb-pvc.yaml
    │   ├── mongodb-secret.yaml
    │   └── mongodb-service.yaml
    ├── task-service/
    │   ├── task-service-configmap.yaml
    │   ├── task-service-deployment.yaml
    │   └── task-service-service.yaml
    ├── notification-service/
    │   ├── notification-service-configmap.yaml
    │   ├── notification-service-deployment.yaml
    │   └── notification-service-service.yaml
    ├── frontend-service/
    │   ├── frontend-service-configmap.yaml
    │   ├── frontend-service-deployment.yaml
    │   └── frontend-service-service.yaml
    └── hpa/
        ├── frontend-service-hpa.yaml
        ├── notification-service-hpa.yaml
        └── task-service-hpa.yaml
```

## Services Overview

### 1. Frontend Service (Port 8002)
- **Technology**: Streamlit
- **Purpose**: User interface for task and reminder management
- **Features**: Dashboard, task creation/editing, notifications view
- **Dependencies**: streamlit, requests, pandas, plotly

### 2. Task Service (Port 8000)
- **Technology**: FastAPI + MongoDB (with Motor async driver)
- **Purpose**: Task CRUD operations and management
- **Features**: Create, read, update, delete tasks; search and filtering
- **API Prefix**: `/api/v1`
- **Dependencies**: FastAPI, uvicorn, pymongo, motor, pydantic, httpx

### 3. Notification Service (Port 8001)
- **Technology**: FastAPI + MongoDB (with Motor async driver)
- **Purpose**: Reminder and notification management
- **Features**: Schedule reminders, send notifications, manage preferences
- **API Prefix**: `/api/v1`
- **Dependencies**: FastAPI, uvicorn, pymongo, motor, pydantic, schedule, httpx

## Quick Start

### Prerequisites
- Docker and Docker Compose
- minikube
- kubectl
- Python 3.9+

### Local Development with Docker Compose
```powershell
# Clone and navigate to project
cd scalableProject

# Create Docker network
docker network create task_network

# Start all services with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:8002
# Task API: http://localhost:8000/docs
# Notification API: http://localhost:8001/docs
# MongoDB: mongodb://admin:password123@localhost:27017
```

### Kubernetes Deployment
```powershell
# Start minikube
minikube start

# Create namespace
kubectl apply -f k8s-manifests/namespace.yaml

# Deploy MongoDB
kubectl apply -f k8s-manifests/mongodb/

# Deploy services
kubectl apply -f k8s-manifests/task-service/
kubectl apply -f k8s-manifests/notification-service/
kubectl apply -f k8s-manifests/frontend-service/

# Deploy HPA (Horizontal Pod Autoscaler)
kubectl apply -f k8s-manifests/hpa/

# Check deployments
kubectl get pods -n task-app
kubectl get services -n task-app
kubectl get hpa -n task-app

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