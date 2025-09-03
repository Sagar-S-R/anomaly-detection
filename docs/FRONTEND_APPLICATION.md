# 🌐 Frontend Application Documentation

## Overview

The frontend is a React-based web application providing the main user interface for the Anomaly Detection System. It offers comprehensive functionality for user authentication, video management, and results visualization.

## 🚪 Access Information

### **URL & Port**
- **Local Access**: `http://localhost:3000`
- **Production**: `http://your-domain.com` (via Nginx proxy)
- **Container**: `anomaly-frontend`

### **Browser Requirements**
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- 📱 Mobile browsers supported

---

## 👤 User Authentication System

### **Login Process**
```
User Access → Login Page → Authentication → Dashboard
```

#### **Login Features**
- 📧 **Email/Username**: Support for both login methods
- 🔒 **Secure Password**: Encrypted authentication
- 🔄 **Remember Me**: Persistent login option
- 🔐 **Password Recovery**: Reset password functionality
- 🚨 **Account Lockout**: Protection against brute force

#### **User Registration**
```javascript
// Registration form fields
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePass123!",
  "confirmPassword": "SecurePass123!",
  "firstName": "John",
  "lastName": "Doe",
  "organization": "Security Corp"
}
```

### **User Roles & Permissions**

#### 👑 **Administrator**
- ✅ Full system access
- ✅ User management
- ✅ System configuration
- ✅ Analytics and reports
- ✅ Emergency controls

#### 👮 **Operator**
- ✅ Upload videos
- ✅ Connect CCTV feeds
- ✅ View all results
- ✅ Generate reports
- ❌ User management

#### 👁️ **Viewer**
- ✅ View assigned results
- ✅ Basic analytics
- ❌ Upload capabilities
- ❌ System configuration

---

## 📤 Video Upload & CCTV Integration

### **File Upload Interface**

#### **Supported Formats**
```
Video: MP4, AVI, MOV, MKV, WMV
Audio: MP3, WAV, M4A
Maximum Size: 500MB per file
Batch Upload: Up to 5 files simultaneously
```

#### **Upload Process**
```
Select Files → Preview → Upload → Processing → Results
```

#### **Upload Features**
- 📁 **Drag & Drop**: Easy file selection
- 📋 **File Preview**: Preview before upload
- 📊 **Progress Bar**: Real-time upload progress
- ⏸️ **Pause/Resume**: Control upload process
- 🔄 **Retry Failed**: Automatic retry mechanism

### **CCTV Stream Integration**

#### **Supported Protocols**
```
RTSP: rtsp://camera.ip/stream
HTTP: http://camera.ip/mjpeg
RTMP: rtmp://server/stream
WebRTC: Direct browser connection
```

#### **Stream Configuration**
```javascript
// CCTV connection form
{
  "streamName": "Front Door Camera",
  "streamUrl": "rtsp://192.168.1.100/stream",
  "username": "admin",        // Optional
  "password": "password",     // Optional
  "resolution": "1920x1080",
  "frameRate": 30,
  "recordingEnabled": true
}
```

#### **Stream Features**
- 🔴 **Live Preview**: Real-time stream preview
- ⚙️ **Quality Settings**: Adjustable resolution/framerate
- 📹 **Recording**: Automatic anomaly recording
- 🔊 **Audio Support**: Audio stream processing
- 📱 **Multi-stream**: Multiple camera support

---

## 📊 Results Dashboard

### **Analysis Results Display**

#### **Anomaly Detection Results**
```javascript
// Result object structure
{
  "analysisId": "uuid-123",
  "fileName": "security_footage.mp4",
  "timestamp": "2024-03-15T10:30:00Z",
  "duration": "05:23",
  "anomalies": [
    {
      "type": "suspicious_behavior",
      "confidence": 0.89,
      "timeRange": "02:15-02:45",
      "description": "Unusual movement pattern detected",
      "severity": "high"
    }
  ],
  "summary": {
    "totalAnomalies": 3,
    "highRisk": 1,
    "mediumRisk": 2,
    "lowRisk": 0
  }
}
```

#### **Visualization Components**
- 📈 **Timeline View**: Anomaly timeline with markers
- 🎥 **Video Player**: Integrated video playback
- 📊 **Charts & Graphs**: Statistical visualizations
- 🏷️ **Tags & Labels**: Categorized anomaly types
- 📝 **Detailed Reports**: Comprehensive analysis reports

### **Real-time Monitoring**

#### **Live Dashboard Features**
- 🔴 **Live Streams**: Multiple camera feeds
- ⚡ **Instant Alerts**: Real-time notifications
- 📊 **System Status**: Health monitoring
- 🎛️ **Quick Controls**: Emergency actions
- 📱 **Mobile View**: Responsive design

#### **Alert System**
```javascript
// Alert types and styling
{
  "critical": {
    "color": "red",
    "sound": "alarm.mp3",
    "action": "immediate_response"
  },
  "warning": {
    "color": "orange", 
    "sound": "beep.mp3",
    "action": "review_required"
  },
  "info": {
    "color": "blue",
    "sound": "none",
    "action": "log_only"
  }
}
```

---

## 📱 User Interface Components

### **Navigation Structure**
```
Main Dashboard
├── 📤 Upload
│   ├── File Upload
│   ├── CCTV Setup
│   └── Batch Processing
├── 📊 Results
│   ├── Recent Analysis
│   ├── Anomaly Archive
│   └── Custom Reports
├── 🔴 Live Monitoring
│   ├── Active Streams
│   ├── Real-time Alerts
│   └── System Status
├── 👤 Profile
│   ├── Account Settings
│   ├── Preferences
│   └── API Keys
└── ⚙️ Admin (Admin only)
    ├── User Management
    ├── System Config
    └── Analytics
```

### **Key UI Features**

#### **Dark/Light Theme**
- 🌙 **Dark Mode**: Optimized for 24/7 monitoring
- ☀️ **Light Mode**: Standard interface
- 🔄 **Auto Switch**: Time-based theme switching
- 💾 **User Preference**: Saved theme selection

#### **Responsive Design**
- 💻 **Desktop**: Full-featured interface
- 📱 **Mobile**: Touch-optimized controls
- 📊 **Tablet**: Balanced layout
- 🖥️ **Large Screens**: Multi-panel view

#### **Accessibility**
- ♿ **Screen Reader**: ARIA compliance
- ⌨️ **Keyboard Navigation**: Full keyboard support
- 🎨 **High Contrast**: Accessibility themes
- 📏 **Font Scaling**: Adjustable text size

---

## 🔧 Configuration & Settings

### **User Preferences**
```javascript
// User settings object
{
  "notifications": {
    "email": true,
    "browser": true,
    "sound": true,
    "mobile": false
  },
  "display": {
    "theme": "dark",
    "language": "en",
    "timezone": "UTC-5",
    "dateFormat": "MM/DD/YYYY"
  },
  "privacy": {
    "shareAnalytics": false,
    "saveHistory": true,
    "autoLogout": 30  // minutes
  }
}
```

### **System Configuration** (Admin Only)
```javascript
// System settings
{
  "upload": {
    "maxFileSize": "500MB",
    "allowedFormats": ["mp4", "avi", "mov"],
    "virusScanning": true
  },
  "processing": {
    "autoProcess": true,
    "qualityThreshold": 0.7,
    "alertThreshold": 0.8
  },
  "retention": {
    "logsDays": 90,
    "videoDays": 30,
    "resultsDays": 365
  }
}
```

---

## 🚀 Getting Started Guide

### **For New Users**

#### **Step 1: Account Setup**
1. Navigate to `http://localhost:3000`
2. Click "Register" for new account
3. Fill in required information
4. Verify email address
5. Complete profile setup

#### **Step 2: First Upload**
1. Click "Upload" in navigation
2. Select video file or drag & drop
3. Add description/tags (optional)
4. Click "Start Analysis"
5. Wait for processing completion

#### **Step 3: View Results**
1. Go to "Results" section
2. Click on completed analysis
3. Review anomaly timeline
4. Watch detected segments
5. Export report if needed

### **For CCTV Integration**

#### **Step 1: Camera Setup**
1. Go to "Upload" → "CCTV Setup"
2. Enter camera details:
   - Stream URL (RTSP/HTTP)
   - Authentication (if required)
   - Stream name
3. Test connection
4. Save configuration

#### **Step 2: Live Monitoring**
1. Navigate to "Live Monitoring"
2. View active streams
3. Enable real-time processing
4. Configure alert preferences
5. Monitor for anomalies

---

## 🔍 Troubleshooting

### **Common Issues**

#### **Login Problems**
```
Issue: Cannot login
Solutions:
- Check username/password
- Clear browser cache
- Disable browser extensions
- Try incognito mode
```

#### **Upload Failures**
```
Issue: Video upload fails
Solutions:
- Check file format (MP4, AVI, MOV)
- Verify file size < 500MB
- Ensure stable internet connection
- Try different browser
```

#### **CCTV Connection Issues**
```
Issue: Cannot connect to camera
Solutions:
- Verify camera IP and port
- Check network connectivity
- Confirm RTSP/HTTP URL format
- Test camera credentials
```

#### **Slow Performance**
```
Issue: Interface is slow
Solutions:
- Close other browser tabs
- Check internet speed
- Update browser to latest version
- Clear browser cache and cookies
```

### **Browser Console Debugging**
```javascript
// Enable debug mode
localStorage.setItem('debug', 'true');

// View API calls
localStorage.setItem('logAPI', 'true');

// Check connection status
fetch('/api/health').then(r => console.log('API Status:', r.status));
```

---

## 📞 Support & Help

### **In-App Help**
- ❓ **Help Button**: Context-sensitive help
- 📖 **User Guide**: Built-in documentation
- 🎥 **Video Tutorials**: Step-by-step guides
- 💬 **Live Chat**: Real-time support (if enabled)

### **Contact Information**
- 📧 **Email Support**: support@anomaly-detection.com
- 📞 **Phone**: 1-800-ANOMALY
- 💻 **Web**: https://docs.anomaly-detection.com
- 🐛 **Bug Reports**: GitHub Issues
