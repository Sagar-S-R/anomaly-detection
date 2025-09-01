# API Routes Documentation

## Available Endpoints

### 1. **Live Camera Stream** (Existing)
- **Endpoint:** `WS /stream_video`
- **Type:** WebSocket
- **Purpose:** Real-time anomaly detection from device camera
- **Usage:** `ws://localhost:8000/stream_video`

### 2. **Upload Video File** (New)
- **Endpoint:** `POST /upload_video`
- **Type:** HTTP POST
- **Purpose:** Upload video files for anomaly analysis
- **Body:** `multipart/form-data` with video file
- **Validation:** 
  - Max size: 500MB
  - Min duration: 10 minutes
  - Formats: mp4, avi, mov, mkv, webm
- **Response:** Success message with filename
- **Usage:** 
  ```
  POST http://localhost:8000/upload_video
  Content-Type: multipart/form-data
  Body: video file
  ```

### 3. **Process Uploaded Video** (New)
- **Endpoint:** `GET /process_uploaded_video/{filename}`
- **Type:** HTTP GET
- **Purpose:** Analyze uploaded video for anomalies
- **Parameters:** `filename` - name of uploaded video file
- **Response:** JSON with anomaly detection results
- **Usage:**
  ```
  GET http://localhost:8000/process_uploaded_video/my_video.mp4
  ```

### 4. **Connect CCTV Stream** (New)
- **Endpoint:** `POST /connect_cctv`
- **Type:** HTTP POST
- **Purpose:** Connect to live CCTV cameras via RTSP
- **Body:** JSON with RTSP credentials
- **Response:** Real-time anomaly detection results
- **Usage:**
  ```
  POST http://localhost:8000/connect_cctv
  Content-Type: application/json
  Body: {
    "rtsp_url": "rtsp://camera-ip:554/stream",
    "username": "admin",
    "password": "password123"
  }
  ```

## Server Information
- **Base URL:** `http://localhost:8000`
- **WebSocket URL:** `ws://localhost:8000`
- **Framework:** FastAPI
- **AI Pipeline:** Tier 1 (fast detection) → Tier 2 (heavy analysis)

## For Frontend Development
All routes use the same anomaly detection pipeline with:
- Pose analysis
- Scene understanding  
- Audio transcription
- AI reasoning with LLM

Create frontend components to interact with these endpoints for a complete video analysis system.
