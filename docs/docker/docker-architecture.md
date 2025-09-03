# 🏗️ Docker Architecture Overview

## System Architecture

The Anomaly Detection System uses a multi-service Docker architecture with the following components:

```
┌─────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                     │
│                        Port 80/443                         │
└─────────────────┬───────────────────┬───────────────────────┘
                  │                   │
      ┌───────────▼──────────┐   ┌────▼─────────────────────┐
      │   Frontend Service   │   │    Backend Services      │
      │   React App (3000)   │   │                          │
      └──────────────────────┘   │  ┌─────────────────────┐ │
                                 │  │   API Service       │ │
                                 │  │   Port 8000         │ │
                                 │  └─────────────────────┘ │
                                 │                          │
                                 │  ┌─────────────────────┐ │
                                 │  │ Dashboard Service   │ │
                                 │  │   Port 8001         │ │
                                 │  └─────────────────────┘ │
                                 └─────────────┬────────────┘
                                               │
                                 ┌─────────────▼────────────┐
                                 │    MongoDB Database      │
                                 │       Port 27017         │
                                 └──────────────────────────┘
```

## Service Details

### 🔧 Backend API Service
- **Container**: `anomaly-backend`
- **Port**: 8000
- **Purpose**: Main API for video processing, anomaly detection
- **Environment**: `SERVICE_TYPE=api`
- **Application**: `app.py`

### 📊 Dashboard Service  
- **Container**: `anomaly-dashboard`
- **Port**: 8001
- **Purpose**: Web dashboard for monitoring and management
- **Environment**: `SERVICE_TYPE=dashboard`
- **Application**: `dashboard_app.py`

### 🌐 Frontend Service
- **Container**: `anomaly-frontend`
- **Port**: 3000
- **Purpose**: React-based user interface
- **Technology**: Node.js, React

### 🗄️ MongoDB Database
- **Container**: `anomaly-mongo`
- **Port**: 27017
- **Purpose**: Data storage for anomaly records, user sessions
- **Persistent**: Data stored in `mongo_data` volume

### 🔀 Nginx Reverse Proxy
- **Container**: `anomaly-nginx`
- **Ports**: 80, 443
- **Purpose**: Load balancing, SSL termination, static file serving

## Shared Resources

### 📦 Model Cache Volume
- **Volume**: `model_cache`
- **Purpose**: Persistent storage for pre-loaded AI models
- **Shared**: Between backend and dashboard services
- **Models**: CLIP, BLIP, Whisper, MediaPipe

### 🔗 Network
- **Network**: `anomaly-network`
- **Type**: Bridge network for inter-service communication

## Build Strategy

### Single Dockerfile, Multiple Services
- **Efficiency**: One Dockerfile builds backend image
- **Flexibility**: `SERVICE_TYPE` environment variable controls startup
- **Model Pre-loading**: AI models cached during build time
- **Fast Startup**: No model download delays at runtime

### Environment-Based Service Selection
```dockerfile
if [ "$SERVICE_TYPE" = "dashboard" ]; then
    exec uvicorn dashboard_app:app --host 0.0.0.0 --port 8001
elif [ "$SERVICE_TYPE" = "api" ]; then
    exec uvicorn app:app --host 0.0.0.0 --port 8000
else
    exec uvicorn app:app --host 0.0.0.0 --port 8000
fi
```

## Data Flow

1. **User Request** → Nginx → Frontend/Backend
2. **Video Upload** → Backend API → Processing Pipeline
3. **Anomaly Detection** → AI Models (cached) → Results
4. **Dashboard Updates** → Dashboard Service → MongoDB
5. **Real-time Data** → WebSocket connections → Frontend

## Scalability

- **Horizontal**: Multiple backend/dashboard instances
- **Load Balancing**: Nginx distributes requests
- **Shared State**: MongoDB for persistence
- **Model Caching**: Shared volume reduces memory usage
