# 🔧 Backend Services Documentation

## Overview

The backend consists of two main services running on different ports, each serving specific purposes in the anomaly detection system.

## 🚀 API Service (Port 8000)

### **Primary Purpose**
Main backend service handling video processing, user authentication, and data management.

### **Access URL**
- **Local**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Health Check**: `http://localhost:8000/health`

### **Core Responsibilities**

#### 📤 **File Upload & Processing**
```python
POST /upload/video
- Accepts video files for analysis
- Supports formats: MP4, AVI, MOV, MKV
- Max file size: 500MB
- Returns: Upload confirmation and processing status
```

#### 📹 **CCTV Feed Integration**
```python
POST /stream/connect
- Connects to RTSP/HTTP video streams
- Real-time feed processing
- Automatic anomaly detection
- Stream management (start/stop/pause)
```

#### 🤖 **AI Processing Pipeline**
- **Tier 1 Detection**: Basic anomaly patterns
- **Tier 2 Analysis**: Advanced AI processing
- **Model Types**: 
  - Computer Vision (OpenCV + MediaPipe)
  - Audio Analysis (Whisper)
  - Scene Understanding (CLIP + BLIP)

#### 👤 **User Management**
```python
POST /auth/login     # User authentication
POST /auth/register  # New user registration
GET /auth/profile    # User profile management
POST /auth/logout    # Session termination
```

#### 📊 **Data Operations**
```python
GET /results         # Get analysis results
GET /reports         # Generate reports
POST /annotations    # Add manual annotations
DELETE /data/{id}    # Delete records
```

### **Key Features**
- ✅ **Session Management**: Secure user sessions with cleanup
- ✅ **File Processing**: Asynchronous video processing
- ✅ **Database Integration**: MongoDB for data persistence
- ✅ **Error Handling**: Comprehensive error management
- ✅ **API Documentation**: Auto-generated Swagger docs

---

## 📊 Dashboard Service (Port 8001)

### **Primary Purpose**
Live monitoring interface for real-time anomaly detection and system oversight.

### **Access URL**
- **Local**: `http://localhost:8001`
- **Live Dashboard**: `http://localhost:8001/dashboard`
- **System Status**: `http://localhost:8001/status`

### **Core Responsibilities**

#### 🔴 **Live Stream Monitoring**
```python
GET /live/streams    # Active stream list
GET /live/feed/{id}  # Live video feed
POST /live/alert     # Send alert notification
```

#### ⚡ **Real-time Alerts**
- **Instant Notifications**: Immediate anomaly alerts
- **Alert Types**: 
  - 🚨 Critical: Immediate attention required
  - ⚠️ Warning: Suspicious activity detected
  - ℹ️ Info: General system notifications

#### 📈 **System Monitoring**
```python
GET /system/health   # System health status
GET /system/stats    # Performance statistics
GET /system/logs     # Recent system logs
```

#### 🎛️ **Quick Controls**
```python
POST /control/emergency-stop  # Emergency system stop
POST /control/pause          # Pause processing
POST /control/resume         # Resume operations
POST /control/reset          # Reset system state
```

### **Dashboard Features**
- 🔄 **Auto-refresh**: Real-time data updates
- 📱 **Responsive**: Works on mobile devices
- 🎨 **Visual Alerts**: Color-coded notifications
- ⚡ **Fast Access**: No login required for emergencies

---

## 🔗 Service Communication

### **Internal Communication**
```
API Service (8000) ←→ Dashboard Service (8001)
        ↓
   MongoDB (27017)
```

### **Data Flow**
1. **API Service** processes videos and detects anomalies
2. **Results stored** in MongoDB database
3. **Dashboard Service** reads results for live display
4. **Real-time updates** pushed to dashboard interface

### **Shared Resources**
- **Database**: Both services access same MongoDB
- **Model Cache**: AI models shared between services
- **File Storage**: Common file system for uploads

---

## 🛠️ Configuration

### **Environment Variables**
```bash
# Service Configuration
SERVICE_TYPE=api        # For API service
SERVICE_TYPE=dashboard  # For Dashboard service

# Database
MONGODB_URL=mongodb://mongo:27017
DATABASE_NAME=anomaly_detection

# API Keys
GROQ_API_KEY=your_api_key_here

# Performance
TRANSFORMERS_CACHE=/app/model_cache
TORCH_HOME=/app/model_cache
```

### **Port Configuration**
```yaml
# docker-compose.yml
backend:
  ports:
    - "8000:8000"  # API Service

dashboard:
  ports:
    - "8001:8001"  # Dashboard Service
```

---

## 🔍 Monitoring & Debugging

### **Health Checks**
```bash
# Check API service
curl http://localhost:8000/health

# Check Dashboard service
curl http://localhost:8001/health

# View service logs
docker logs anomaly-backend
docker logs anomaly-dashboard
```

### **Performance Monitoring**
```python
# API Metrics
GET /metrics/api      # API performance stats
GET /metrics/models   # AI model performance
GET /metrics/database # Database statistics

# Dashboard Metrics
GET /metrics/streams  # Stream statistics
GET /metrics/alerts   # Alert frequency
GET /metrics/uptime   # Service uptime
```

### **Common Issues & Solutions**

#### **Port Conflicts**
```bash
# Check if ports are in use
lsof -i :8000
lsof -i :8001

# Solution: Stop conflicting services or change ports
```

#### **Database Connection**
```bash
# Test MongoDB connection
docker exec anomaly-backend ping mongo

# Check database status
curl http://localhost:8000/health
```

#### **Model Loading Issues**
```bash
# Check model cache
docker exec anomaly-backend ls -la /app/model_cache/

# Verify models loaded
curl http://localhost:8000/models/status
```

---

## 🚀 Development

### **Local Development**
```bash
# Start both services in development mode
./manage.sh dev

# API service only
docker-compose up backend

# Dashboard service only
docker-compose up dashboard
```

### **API Testing**
```bash
# Test API endpoints
curl -X POST http://localhost:8000/upload/test
curl -X GET http://localhost:8000/docs

# Test Dashboard
curl -X GET http://localhost:8001/dashboard
curl -X GET http://localhost:8001/status
```

### **Code Changes**
- **Live Reload**: Both services support live code updates
- **Volume Mapping**: Code changes reflect immediately
- **No Rebuild**: Modify Python files without container rebuild

---

## 📋 API Reference Quick Start

### **Authentication**
```python
# Login
POST /auth/login
{
  "username": "user@example.com",
  "password": "password123"
}

# Get token for API access
Response: {"access_token": "...", "token_type": "bearer"}
```

### **Video Upload**
```python
# Upload video file
POST /upload/video
Content-Type: multipart/form-data
File: video.mp4

Response: {"upload_id": "123", "status": "processing"}
```

### **Live Stream Connection**
```python
# Connect CCTV stream
POST /stream/connect
{
  "stream_url": "rtsp://camera.local/stream",
  "stream_name": "Front Door Camera"
}
```

### **Get Results**
```python
# Get analysis results
GET /results?upload_id=123

Response: {
  "anomalies": [...],
  "confidence": 0.95,
  "processing_time": "2.3s"
}
```
