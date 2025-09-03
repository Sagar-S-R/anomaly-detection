# 🔧 Docker Services Configuration

## Service Overview

The Anomaly Detection System consists of 5 main services that work together to provide a complete video anomaly detection solution.

## Backend Services

### 🔧 API Service (`backend`)
```yaml
backend:
  build:
    context: ./backend
    dockerfile: Dockerfile
  container_name: anomaly-backend
  ports:
    - "8000:8000"
  environment:
    - SERVICE_TYPE=api
    - GROQ_API_KEY=${GROQ_API_KEY}
    - MONGODB_URL=mongodb://mongo:27017
    - DATABASE_NAME=anomaly_detection
```

**Purpose**: Main API service for video processing and anomaly detection
**Application**: `app.py` (FastAPI application)
**Key Features**:
- Video upload and processing
- AI-powered anomaly detection
- RESTful API endpoints
- Real-time processing pipeline

### 📊 Dashboard Service (`dashboard`)  
```yaml
dashboard:
  build:
    context: ./backend
    dockerfile: Dockerfile
  container_name: anomaly-dashboard
  ports:
    - "8001:8001"
  environment:
    - SERVICE_TYPE=dashboard
    - GROQ_API_KEY=${GROQ_API_KEY}
    - MONGODB_URL=mongodb://mongo:27017
```

**Purpose**: Web dashboard for monitoring and management
**Application**: `dashboard_app.py` (FastAPI application)
**Key Features**:
- System monitoring interface
- Anomaly detection results visualization
- Configuration management
- Real-time status updates

## Frontend Service

### 🌐 Frontend (`frontend`)
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  container_name: anomaly-frontend
  ports:
    - "3000:3000"
  environment:
    - REACT_APP_API_URL=http://localhost:8000
    - REACT_APP_DASHBOARD_URL=http://localhost:8001
```

**Purpose**: User interface for the application
**Technology**: React.js with Node.js
**Key Features**:
- File upload interface
- Real-time result display
- Responsive design
- API integration

## Database Service

### 🗄️ MongoDB (`mongo`)
```yaml
mongo:
  image: mongo:7.0
  container_name: anomaly-mongo
  ports:
    - "27017:27017"
  environment:
    - MONGO_INITDB_ROOT_USERNAME=${MONGO_ROOT_USERNAME:-admin}
    - MONGO_INITDB_ROOT_PASSWORD=${MONGO_ROOT_PASSWORD:-password123}
    - MONGO_INITDB_DATABASE=${DATABASE_NAME:-anomaly_detection}
  volumes:
    - mongo_data:/data/db
```

**Purpose**: Data persistence for anomaly records and user sessions
**Database**: MongoDB 7.0
**Key Features**:
- Document storage for detection results
- User session management
- Persistent data storage
- Automatic initialization

## Proxy Service

### 🔀 Nginx (`nginx`)
```yaml
nginx:
  image: nginx:alpine
  container_name: anomaly-nginx
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    - ./nginx/ssl:/etc/nginx/ssl
  depends_on:
    - backend
    - dashboard
    - frontend
```

**Purpose**: Reverse proxy and load balancer
**Key Features**:
- SSL termination
- Static file serving
- Load balancing
- Request routing

## Service Dependencies

### Dependency Graph
```
nginx
├── frontend
├── backend
│   └── mongo
└── dashboard
    └── mongo
```

### Startup Order
1. **mongo** - Database starts first
2. **backend** - API service connects to database
3. **dashboard** - Dashboard service connects to database
4. **frontend** - UI connects to backend services
5. **nginx** - Proxy routes to all services

## Shared Resources

### 📦 Volumes
```yaml
volumes:
  mongo_data:
    driver: local
  model_cache:
    driver: local
```

- **mongo_data**: Persistent MongoDB storage
- **model_cache**: Shared AI model cache between backend/dashboard

### 🔗 Network
```yaml
networks:
  anomaly-network:
    driver: bridge
```

- All services communicate through `anomaly-network`
- Internal DNS resolution (e.g., `backend`, `mongo`)

## Environment Variables

### Required Variables
```bash
# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Database
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=password123
DATABASE_NAME=anomaly_detection

# URLs (for frontend)
REACT_APP_API_URL=http://localhost:8000
REACT_APP_DASHBOARD_URL=http://localhost:8001
```

### Optional Variables
```bash
# MongoDB connection
MONGODB_URL=mongodb://mongo:27017

# Model cache paths
TRANSFORMERS_CACHE=/app/model_cache
TORCH_HOME=/app/model_cache
HF_HOME=/app/model_cache
```

## Health Checks

### Backend/Dashboard Health Check
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

### Frontend Health Check
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Service Communication

### Internal URLs
- **Backend API**: `http://backend:8000`
- **Dashboard**: `http://dashboard:8001`
- **MongoDB**: `mongodb://mongo:27017`
- **Frontend**: `http://frontend:3000`

### External URLs (through Nginx)
- **Frontend**: `http://localhost:80`
- **API**: `http://localhost:80/api`
- **Dashboard**: `http://localhost:80/dashboard`

## Resource Requirements

### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 20GB (including model cache)

### Recommended
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Disk**: 50GB+ SSD
- **GPU**: Optional (for faster AI processing)

## Development vs Production

### Development Configuration
- Live reload enabled
- Debug logging
- Hot module replacement
- Volume mounting for code changes

### Production Configuration
- Optimized builds
- Health checks enabled
- Restart policies
- SSL certificates
- Resource limits
