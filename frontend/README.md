# Anomaly Detection System

A comprehensive multi-modal anomaly detection system with real-time video analysis, audio processing, and AI-powered threat assessment. Built with FastAPI backend and React frontend.

## 🚀 Features

### 🎥 Multi-Input Source Support
- **Live Camera Monitoring**: Real-time webcam analysis with OpenCV
- **CCTV Stream Integration**: Connect to IP cameras and RTSP streams
- **Video Upload Analysis**: Process pre-recorded video files
- **Session-Based Processing**: Isolated processing sessions for each input source

### 🧠 Advanced AI Pipeline
- **Tier 1 Analysis**: Scene analysis, pose detection, and basic anomaly detection
- **Tier 2 Analysis**: Multi-modal fusion with audio transcription and AI reasoning
- **Real-time Processing**: Concurrent video, audio, and fusion workers
- **Threat Severity Scoring**: Intelligent risk assessment with multimodal agreement

### � Comprehensive Dashboard
- **User Authentication**: Secure login/registration system
- **Real-time Monitoring**: Live status updates via WebSocket
- **Anomaly History**: Detailed anomaly tracking with thumbnails
- **Performance Metrics**: System health and processing statistics
- **Database Integration**: MongoDB for persistent anomaly storage

### 🎛️ Input Source Management
- **Input Selector**: Choose between Live Camera, CCTV, or Video Upload
- **CCTV Configuration**: Easy setup for IP cameras with authentication
- **Session Management**: Clean thread lifecycle management
- **Resource Cleanup**: Automatic camera release and thread termination

### 🔧 Technical Features
- **WebSocket Communication**: Real-time bidirectional data flow
- **MJPEG Streaming**: Low-latency video streaming
- **Audio Processing**: Real-time speech-to-text with Whisper AI
- **Pose Detection**: MediaPipe-powered human pose analysis
- **Fusion Logic**: Intelligent combination of video and audio analysis

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── app.py                 # Main FastAPI application
├── routes/
│   └── user_data.py       # User authentication endpoints
├── tier1/
│   └── tier1_pipeline.py  # Scene & pose analysis
├── tier2/
│   └── tier2_pipeline.py  # AI-powered multimodal fusion
├── utils/
│   ├── audio_processing.py # Audio capture & transcription
│   ├── pose_processing.py  # Pose detection utilities
│   ├── scene_processing.py # Scene analysis
│   └── fusion_logic.py     # Multimodal fusion
├── anomaly_frames/        # Stored anomaly screenshots
├── recorded_videos/       # Video recordings
├── uploaded_videos/       # User-uploaded videos
└── temp_audio/           # Temporary audio chunks
```

### Frontend (React)
```
frontend/src/
├── App.jsx                # Main application & routing
├── components/
│   ├── LiveFeed.jsx       # Live video stream display
│   ├── AnomalyList.jsx    # Anomaly history management
│   ├── VideoPlayback.jsx  # Video player with controls
│   ├── JsonOutput.jsx     # Real-time data visualization
│   ├── VideoControls.jsx  # System control panel
│   └── DatabaseManager.jsx # Database status monitoring
├── pages/
│   ├── Login.jsx          # User authentication
│   ├── Register.jsx       # User registration
│   ├── UserDashboard.jsx  # Main dashboard
│   ├── InputSelector.jsx  # Input source selection
│   ├── LiveCameraMonitoring.jsx # Live camera interface
│   ├── CCTVMonitoring.jsx # CCTV stream interface
│   ├── VideoUploadMonitoring.jsx # Video upload interface
│   └── Welcome.jsx        # Welcome screen
├── index.css              # Tailwind CSS & custom styles
└── index.js               # React app entry point
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance async web framework
- **OpenCV**: Computer vision and video processing
- **MediaPipe**: Pose detection and landmark tracking
- **OpenAI Whisper**: Speech-to-text transcription
- **Groq API**: AI-powered threat analysis
- **MongoDB**: Document database for anomaly storage
- **WebSocket**: Real-time bidirectional communication

### Frontend
- **React 18**: Modern component-based UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **WebSocket**: Real-time data updates
- **Responsive Design**: Mobile-first approach

## 📋 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 16+
- MongoDB (optional, falls back to memory storage)
- Webcam or IP camera for live monitoring

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your MongoDB URL and other settings

# Start the server
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Usage Guide

### 1. User Registration/Login
- Register a new account or login with existing credentials
- Access the main dashboard with system overview

### 2. Input Source Selection
- Choose from three input sources:
  - **Live Camera**: Real-time webcam monitoring
  - **CCTV Stream**: Connect to IP cameras
  - **Video Upload**: Analyze pre-recorded videos

### 3. Live Monitoring
- Start monitoring to begin real-time analysis
- View live video stream with anomaly overlays
- Monitor system status and performance metrics
- Review detected anomalies in real-time

### 4. CCTV Configuration
- Enter IP camera details (IP address, port, credentials)
- Test connection before starting monitoring
- Save frequently used camera configurations

### 5. Video Upload Analysis
- Upload video files for offline analysis
- Monitor processing progress via WebSocket
- Review detected anomalies with timestamps
- Jump to specific anomaly locations in video

## 🔧 Configuration

### Environment Variables
```bash
# .env file
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=anomaly_detection
GROQ_API_KEY=your_groq_api_key_here
```

### CCTV Stream Formats
- **RTSP**: `rtsp://username:password@ip:port/stream`
- **HTTP**: `http://ip:port/video`
- **Authentication**: Username/password support for secured cameras

### Performance Tuning
- Adjust video resolution in backend configuration
- Modify WebSocket message frequency
- Configure anomaly detection sensitivity
- Set audio chunk processing intervals

## 📊 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User authentication
- `GET /profile` - Get user profile

### Monitoring
- `WebSocket /stream_video` - Live video monitoring
- `WebSocket /process_uploaded_video/{filename}` - Video upload processing
- `GET /video_stream` - MJPEG video stream
- `GET /anomaly_events` - Get anomaly history

### Data Management
- `GET /api/stats` - System statistics
- `GET /api/anomalies` - List all anomalies
- `DELETE /api/anomalies/{id}` - Delete anomaly
- `GET /api/performance` - Performance metrics

## 🚨 Error Handling

### Common Issues
- **WebSocket Connection Failed**: Check backend server status
- **Camera Not Accessible**: Verify camera permissions and connection
- **Audio Processing Errors**: Ensure microphone permissions
- **MongoDB Connection Failed**: Falls back to memory storage

### Troubleshooting
- Check browser console for frontend errors
- Review backend logs for server-side issues
- Verify network connectivity for WebSocket connections
- Ensure all dependencies are properly installed

## 🔮 Future Enhancements

### Planned Features
- [ ] WebRTC video streaming for lower latency
- [ ] Multi-camera simultaneous monitoring
- [ ] Advanced analytics dashboard
- [ ] Mobile app companion
- [ ] Cloud deployment support
- [ ] Custom anomaly detection models
- [ ] Integration with security systems
- [ ] Automated alert notifications

### Performance Improvements
- [ ] GPU acceleration for video processing
- [ ] Distributed processing for multiple cameras
- [ ] Optimized AI model inference
- [ ] Advanced caching mechanisms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenCV for computer vision capabilities
- MediaPipe for pose detection
- OpenAI Whisper for speech recognition
- FastAPI for the robust backend framework
- React for the modern frontend experience
