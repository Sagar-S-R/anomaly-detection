# 🎯 Anomaly Detection System - Project Overview

## System Description

The **Anomaly Detection System** is a comprehensive AI-powered platform for real-time video analysis and anomaly detection. It provides multiple access points for different user types and use cases.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 Web Interface                         │
│  ┌─────────────────┐  ┌─────────────────┐ ┌──────────────┐ │
│  │   Frontend      │  │   Dashboard     │ │    Admin     │ │
│  │   Port 3000     │  │   Port 8001     │ │   Access     │ │
│  │   User Login    │  │   Live Stream   │ │              │ │
│  └─────────────────┘  └─────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   🔀 Nginx Proxy    │
                    │     Port 80/443     │
                    └──────────┬──────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                    🤖 Backend Services                       │
│  ┌─────────────────┐              ┌─────────────────────┐   │
│  │   API Service   │              │ Dashboard Service   │   │
│  │   Port 8000     │◄────────────►│    Port 8001        │   │
│  │   • File Upload │              │ • Live Monitoring   │   │
│  │   • CCTV Feed   │              │ • Real-time Stats   │   │
│  │   • Processing  │              │ • System Control    │   │
│  └─────────────────┘              └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   🗄️ MongoDB        │
                    │    Port 27017       │
                    │   • User Data       │
                    │   • Anomaly Records │
                    │   • System Logs     │
                    └─────────────────────┘
```

## 🚪 Access Points & User Types

### 1. 🌐 **Frontend Web Application** (Port 3000)
**Purpose**: Main user interface for general users
**Access**: `http://localhost:3000`
**Features**:
- **User Authentication**: Login/Register system
- **File Upload**: Upload video files for analysis
- **CCTV Integration**: Connect live CCTV feeds
- **Results Dashboard**: View anomaly detection results
- **User Profile**: Manage account settings

**User Flow**:
```
Login → Upload Video/Connect CCTV → View Analysis → Download Reports
```

### 2. 📊 **Live Dashboard** (Port 8001)
**Purpose**: Real-time monitoring for operators/security personnel
**Access**: `http://localhost:8001`
**Features**:
- **Live Streaming**: Real-time video feed monitoring
- **Instant Alerts**: Immediate anomaly notifications
- **System Status**: Live system health monitoring
- **Quick Controls**: Emergency stop, pause, resume
- **Direct Access**: No login required for emergency access

**User Flow**:
```
Direct Access → Live Stream → Real-time Alerts → Quick Actions
```

### 3. 🔧 **API Service** (Port 8000)
**Purpose**: Backend processing and data management
**Access**: `http://localhost:8000`
**Features**:
- **Video Processing**: AI-powered anomaly detection
- **CCTV Feed Handling**: Real-time stream processing
- **Database Operations**: Store and retrieve data
- **Authentication**: User management
- **File Management**: Upload/download operations

## 🎯 Use Cases

### **Scenario 1: Security Office - Live Monitoring**
```
Security Guard → Direct Dashboard Access (Port 8001)
              → Live CCTV Feeds
              → Real-time Anomaly Alerts
              → Immediate Response
```

### **Scenario 2: Investigation Team - File Analysis**
```
Investigator → Frontend Login (Port 3000)
            → Upload Video Evidence
            → Run AI Analysis
            → Download Detailed Reports
```

### **Scenario 3: System Administrator - Management**
```
Admin → Frontend Admin Panel (Port 3000)
      → System Configuration
      → User Management
      → Analytics Dashboard
```

## 🔐 Authentication & Security

### **Frontend (Port 3000)**
- ✅ **Login Required**: Username/Password authentication
- ✅ **User Roles**: Admin, Operator, Viewer
- ✅ **Session Management**: Secure session handling
- ✅ **Data Protection**: Encrypted data transmission

### **Dashboard (Port 8001)**
- ⚡ **Direct Access**: No login for emergency situations
- 🔒 **IP Restrictions**: Can be configured for specific IPs
- 👀 **Read-Only**: View-only access to live streams
- 🚨 **Alert System**: Immediate notifications

### **API (Port 8000)**
- 🔑 **API Keys**: Secure API access
- 🛡️ **Rate Limiting**: Prevent abuse
- 📊 **Audit Logging**: Track all operations
- 🔐 **Data Encryption**: Secure data storage

## 🚀 Quick Start

### **For End Users (Frontend)**
1. Open browser: `http://localhost:3000`
2. Create account or login
3. Upload video or connect CCTV
4. View analysis results

### **For Security Personnel (Dashboard)**
1. Open browser: `http://localhost:8001`
2. Monitor live feeds
3. Respond to alerts
4. Use quick controls

### **For Developers (API)**
1. Access API: `http://localhost:8000`
2. Check API documentation: `http://localhost:8000/docs`
3. Use API endpoints for integration

## 🛠️ System Administration

### **Deployment**
```bash
# Start full system
./manage.sh build
./manage.sh start

# Development mode
./manage.sh dev

# View logs
./manage.sh logs
```

### **Configuration**
- **Environment**: Edit `.env` file
- **Database**: MongoDB configuration
- **AI Models**: Pre-loaded during build
- **Networking**: Port configuration in docker-compose

### **Monitoring**
- **Health Checks**: Built-in service monitoring
- **Logs**: Centralized logging system
- **Metrics**: Performance monitoring
- **Alerts**: System notifications

## 📱 Integration Capabilities

### **CCTV Systems**
- **RTSP Streams**: Direct camera integration
- **Multiple Formats**: Support various video formats
- **Real-time Processing**: Live stream analysis
- **Recording**: Automatic anomaly recording

### **External Systems**
- **REST API**: Easy integration with other systems
- **Webhooks**: Event notifications
- **Database Export**: Data export capabilities
- **Third-party Tools**: Extensible architecture

## 🎯 Key Benefits

1. **🚀 Fast Response**: Direct dashboard access for emergencies
2. **👥 Multi-User**: Different interfaces for different user types
3. **🔄 Real-time**: Live monitoring and instant alerts
4. **📊 Comprehensive**: Full analysis and reporting capabilities
5. **🔒 Secure**: Role-based access and data protection
6. **⚡ Scalable**: Docker-based deployment for easy scaling
