## 🚨 Real-Time Anomaly Detection System

# Samsung GenAI hackathon 2025
# Team : TriFusion
Team members :

- 1.Samrudh P : 1ms23cs162@msrit.edu
- 2.Sagar S R : 1ms23cs158@msrit.edu
- 3.Ranjita V Nayak : 1ms23cs150@msrit.edu

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112.0-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A sophisticated multi-modal AI-powered anomaly detection system that provides real-time monitoring and analysis using computer vision, audio processing, and advanced AI reasoning.

## 🌟 Features

### 🎯 **Multi-Modal Detection**
- **🏃 Pose Analysis**: Real-time human pose detection using MediaPipe for movement anomalies
- **🎤 Audio Processing**: Live audio transcription with Whisper AI for verbal indicators
- **👁️ Visual Scene Analysis**: CLIP/BLIP models for comprehensive scene understanding
- **🧠 AI Reasoning**: Advanced threat assessment using Groq LLaMA models

### 🔄 **Real-Time Processing**
- **📡 WebSocket Streaming**: Live video feed with 1 FPS anomaly detection
- **📹 Video Recording**: Continuous MP4 recording with anomaly frame capture
- **⚡ Live Dashboard**: Web-based monitoring interface with JSON output
- **🖼️ Frame Saving**: Automatic anomaly frame extraction and storage

### 🎛️ **Advanced Analysis**
- **🔗 Multi-Modal Fusion**: Intelligent correlation of pose, audio, and visual data
- **📊 Threat Scoring**: Comprehensive threat severity assessment (0-1 scale)
- **🎯 Anomaly Classification**: Detection of falls, aggression, medical emergencies
- **📈 Confidence Assessment**: AI-powered uncertainty quantification

### 🖥️ **Modern React Frontend** 🆕
- **📱 Responsive Design**: Mobile-first Tailwind CSS interface
- **🎥 Live Video Feed**: MJPEG stream with WebRTC-ready architecture
- **🚨 Real-time Alerts**: Instant anomaly notifications with severity indicators
- **📊 Interactive JSON Panel**: Collapsible real-time data display
- **📹 Video Playback**: Full control video player with timestamp navigation
- **📋 Anomaly Management**: Sortable list with thumbnails and detailed views
- **🎛️ System Controls**: WebSocket management and display toggles

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Live Camera   │    │   Audio Stream  │    │  Web Dashboard  │
│    Feed (CV2)   │    │   (PyAudio)     │    │   (FastAPI)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TIER 1 PIPELINE                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Pose      │  │   Audio     │  │    Scene Analysis       │ │
│  │ Processing  │  │ Processing  │  │   (CLIP/BLIP Models)    │ │
│  │ (MediaPipe) │  │ (Whisper)   │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                            │                                   │
│                    ┌───────▼───────┐                          │
│                    │ Fusion Logic  │                          │
│                    │  (Threshold)  │                          │
│                    └───────────────┘                          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────▼───────────────┐
          │         Anomaly Detected?     │
          └───────────────┬───────────────┘
                          │ YES
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TIER 2 PIPELINE                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Enhanced    │  │ Large Model │  │   Advanced Scene        │ │
│  │ Audio       │  │ Transcript  │  │   Captioning            │ │
│  │ Analysis    │  │ (Whisper)   │  │   (BLIP Model)          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                            │                                   │
│                    ┌───────▼───────┐                          │
│                    │  AI Reasoning │                          │
│                    │ (Groq LLaMA)  │                          │
│                    └───────────────┘                          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
                ┌─────────────────┐
                │ Detailed Report │
                │ + Threat Score  │
                └─────────────────┘
```

## 🚀 Quick Start

### 📋 Prerequisites

- **Python 3.10+**
- **Camera/Webcam** for video input
- **Microphone** for audio input
- **GROQ API Key** (free at [console.groq.com](https://console.groq.com))

### 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/anomaly-detection.git
cd anomaly-detection
```

2. **Set up Python environment**
```bash
# Using pyenv (recommended)
pyenv install 3.10.11
pyenv local 3.10.11
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n anomaly-detection python=3.10
conda activate anomaly-detection
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Download required models**
```bash
# MediaPipe Pose Model (should auto-download)
# Whisper models will download automatically on first use
# CLIP/BLIP models will download from HuggingFace automatically
```

5. **Set up environment variables**
```bash
# Create .env file in backend directory
cp .env.example .env

# Add your GROQ API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

### 🏃 Running the System

#### Backend (Core Detection Engine)
1. **Start the backend server**
```bash
cd backend
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

#### Frontend (Modern React Dashboard) - **NEW** 🆕
1. **Install frontend dependencies**
```bash
cd frontend
npm install
```

2. **Start the React development server**
```bash
npm start
# OR use the convenience scripts:
# Windows: start.bat
# Unix/Mac: ./start.sh
```

3. **Access the dashboards**
- **React Dashboard** (Recommended): `http://localhost:3000`
- **Legacy HTML Dashboard**: `http://localhost:8000/dashboard`

#### 🎯 Monitoring Features
- **Live Video Stream**: Real-time MJPEG feed with anomaly detection
- **WebSocket Updates**: Instant anomaly notifications and JSON data
- **Video Playback**: Load and review recorded sessions
- **Anomaly Management**: Browse, sort, and analyze detected events
- **System Controls**: Start/stop monitoring, toggle displays

## 📁 Project Structure

```
anomaly-detection/
├── README.md
├── .gitignore
├── backend/
│   ├── app.py                 # Main FastAPI application
│   ├── dashboard.html         # Legacy web interface
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── pose_landmarker_heavy.task  # MediaPipe model
│   ├── tier1/
│   │   ├── __init__.py
│   │   └── tier1_pipeline.py  # Real-time anomaly detection
│   ├── tier2/
│   │   ├── __init__.py
│   │   └── tier2_pipeline.py  # Advanced AI analysis
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── audio_processing.py    # Whisper audio transcription
│   │   ├── pose_processing.py     # MediaPipe pose analysis
│   │   ├── scene_processing.py    # CLIP/BLIP visual analysis
│   │   └── fusion_logic.py        # Multi-modal fusion & AI reasoning
│   ├── anomaly_frames/        # Saved anomaly images
│   └── recorded_videos/       # Recorded video sessions
└── frontend/                  # Modern React Dashboard 🆕
    ├── package.json          # Node.js dependencies  
    ├── tailwind.config.js    # Tailwind CSS configuration
    ├── start.bat / start.sh  # Platform-specific startup scripts
    ├── public/
    │   └── index.html        # HTML template
    └── src/
        ├── App.jsx           # Main React application
        ├── index.js          # React entry point
        ├── index.css         # Styles (Tailwind + custom)
        └── components/       # React components
            ├── LiveFeed.jsx      # Live video stream & status
            ├── AnomalyList.jsx   # Anomaly history & management  
            ├── VideoPlayback.jsx # Video player controls
            ├── JsonOutput.jsx    # Real-time data display
            └── VideoControls.jsx # System control panel
```

## 🔧 Configuration

### 🎚️ Detection Sensitivity

Adjust thresholds in `utils/fusion_logic.py`:

```python
# Tier 1 Thresholds
scene_threshold = 0.20      # Scene anomaly sensitivity (0.0-1.0)
pose_threshold = 0.15       # Pose movement sensitivity
cooldown_ms = 1000          # Anomaly detection cooldown

# Scene Processing Threshold
anomaly_threshold = 0.8     # CLIP model sensitivity multiplier
```

### 🎬 Pose Detection

Modify sensitivity in `utils/pose_processing.py`:

```python
# Movement Thresholds
wrist_speed_threshold = 0.15    # Rapid arm movements
head_movement_threshold = 0.08  # Head position changes
torso_change_threshold = 0.05   # Bending/postural changes
```

### 🔊 Audio Processing

Configure in `utils/audio_processing.py`:

```python
# Audio Settings
sample_rate = 16000         # Whisper-compatible rate
buffer_size = 32            # ~2 second audio buffer
chunk_size = 1024           # Audio chunk size
```

## 📊 API Endpoints

### 🌐 Web Interface
- `GET /dashboard.html` - Main monitoring dashboard
- `GET /video_stream` - Live video stream with overlays

### 📡 WebSocket
- `WS /stream_video` - Real-time anomaly detection stream

### 📋 REST API
- `GET /anomaly_events` - Latest anomaly detections
- `GET /anomaly_frames/{filename}` - Anomaly frame images
- `GET /recorded_videos/{filename}` - Recorded video files

## 🧪 Example Output

### 📄 Tier 1 Detection
```json
{
  "status": "Suspected Anomaly",
  "details": "Pose anomaly: True, Scene probability: 0.26",
  "frame_count": 2850,
  "timestamp": 95.0,
  "tier1_components": {
    "pose_analysis": {
      "anomaly_detected": true,
      "summary": "Pose anomaly detected: True"
    },
    "audio_analysis": {
      "transcripts": ["Help me!", "Something's wrong"],
      "transcript_text": "Help me! | Something's wrong"
    },
    "scene_analysis": {
      "anomaly_probability": 0.26,
      "summary": "Scene anomaly probability: 0.26"
    }
  }
}
```

### 🧠 Tier 2 Analysis
```json
{
  "visual_score": 0.75,
  "audio_score": 0.85,
  "text_alignment_score": 0.80,
  "multimodal_agreement": 0.78,
  "reasoning_summary": "The pose anomaly suggests unusual body position potentially indicating distress. Audio transcript contains explicit calls for help suggesting genuine emergency. Visual scene shows person in compromised position. All modalities strongly correlate indicating high-confidence genuine anomaly requiring immediate attention.",
  "threat_severity_index": 0.85,
  "tier2_components": {
    "audio_analysis": {
      "full_transcript": "Help me! Something's wrong, I need assistance!",
      "available": true,
      "length": 45
    },
    "visual_analysis": {
      "captions": ["person on ground reaching for help"],
      "visual_anomaly_score": 0.75,
      "description": "person on ground reaching for help"
    }
  }
}
```

## 🤖 AI Models Used

### 🏃 Pose Detection
- **MediaPipe Pose Landmarker Heavy** - 33-point skeletal tracking
- **Real-time processing** at 30 FPS with 1 FPS anomaly analysis

### 🎤 Audio Processing
- **OpenAI Whisper Tiny** - Fast transcription for Tier 1
- **OpenAI Whisper Large** - Accurate transcription for Tier 2

### 👁️ Visual Analysis
- **CLIP ViT-Base-Patch32** - Scene classification and anomaly detection
- **CLIP ViT-Large-Patch14** - Enhanced analysis for Tier 2
- **BLIP Image Captioning** - Detailed scene descriptions

### 🧠 AI Reasoning
- **Groq LLaMA 3 8B** - Fast inference for real-time analysis
- **Groq LLaMA 3 70B** - Detailed reasoning for complex cases

## 🔍 Anomaly Types Detected

### 🚨 Physical Anomalies
- **Falls and collapses**
- **Aggressive movements** (punching, fighting)
- **Medical emergencies** (seizures, distress)
- **Unusual postures** (crawling, crouching)

### 🗣️ Audio Anomalies
- **Distress calls** ("Help!", "Emergency!")
- **Aggressive language** (threats, shouting)
- **Medical indicators** (pain expressions, confusion)
- **Abnormal speech patterns**

### 🎬 Visual Anomalies
- **Environmental hazards**
- **Weapon detection**
- **Unusual object placement**
- **Scene context changes**

## 🛡️ Security & Privacy

- **Local Processing** - All AI inference runs locally
- **No Cloud Storage** - Videos and frames stored locally only
- **API Key Security** - GROQ API key stored in environment variables
- **Data Retention** - Configurable retention policies for recordings

## 🚀 Performance

### ⚡ Real-Time Metrics
- **Video Processing**: 30 FPS capture, 1 FPS analysis
- **Audio Processing**: 2-second rolling buffer
- **Detection Latency**: < 2 seconds end-to-end
- **Memory Usage**: ~2-4GB depending on models loaded

### 🖥️ System Requirements
- **CPU**: Multi-core processor (Intel i5+ or AMD equivalent)
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: Optional (CUDA support for faster inference)
- **Storage**: 10GB free space for models and recordings

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

## � Documentation

### **📖 Project Documentation**
- [**Project Overview**](docs/PROJECT_OVERVIEW.md) - Complete system architecture and user access patterns
- [**Backend Services**](docs/BACKEND_SERVICES.md) - API (8000) and Dashboard (8001) detailed documentation
- [**Frontend Application**](docs/FRONTEND_APPLICATION.md) - Web interface, authentication, and user features
- [**Development Workflow**](docs/DEVELOPMENT_WORKFLOW.md) - Development process and code updates

### **🐳 Docker Documentation**
- [**Docker Overview**](docs/docker/README.md) - Docker documentation index
- [**Architecture**](docs/docker/docker-architecture.md) - System architecture and service overview
- [**Build Process**](docs/docker/docker-build-process.md) - Build process and model pre-loading
- [**Services**](docs/docker/docker-services.md) - Individual service configurations
- [**Commands**](docs/docker/docker-commands.md) - Quick command reference

### **🚀 Quick Access**
```bash
# View all documentation
./manage.sh docs

# View Docker documentation  
./manage.sh docker-docs

# Open specific guides
./manage.sh guide project-overview
./manage.sh guide backend-services
./manage.sh guide frontend-application
```

## �📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MediaPipe** team for pose detection models
- **OpenAI** for Whisper audio processing
- **Hugging Face** for CLIP/BLIP vision models
- **Groq** for fast LLaMA inference
- **FastAPI** for the web framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Samrudhp/anomaly-detection/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Samrudhp/anomaly-detection/discussions)
- **Email**: your.email@example.com

---

<div align="center">
  <strong>Built with ❤️ using Python, AI, and Computer Vision</strong>
</div>
