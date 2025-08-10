# Anomaly Detection API Testing Guide

## 🚀 Quick Start

Your anomaly detection API is ready! Here's how to test it:

### 1. Start the Server
```bash
cd /Users/samrudhp/Projects-git/anomaly-detection/backend
venv/bin/python -m uvicorn app:app --reload
```

### 2. Test Methods

#### Method A: Interactive API Documentation
Open in your browser: http://127.0.0.1:8000/docs

This will show you:
- Available endpoints
- WebSocket documentation
- Interactive testing interface

#### Method B: WebSocket Real-time Testing
```bash
# In a new terminal, while server is running:
cd /Users/samrudhp/Projects-git/anomaly-detection/backend
venv/bin/python test_websocket.py
```

This will:
- Connect to your webcam
- Stream video frames to the API
- Show real-time anomaly detection results
- Display Tier 1 and Tier 2 analysis

#### Method C: Browser WebSocket Test
You can also test WebSockets using browser developer tools:
```javascript
// Open browser console at any webpage and run:
const ws = new WebSocket('ws://127.0.0.1:8000/stream_video');
ws.onmessage = function(event) {
    console.log('Received:', JSON.parse(event.data));
};
ws.onerror = function(error) {
    console.log('WebSocket Error:', error);
};
```

### 3. What to Expect

#### Normal Operation:
```json
{
  "status": "Normal",
  "frame_id": 123,
  "pose_summary": "No anomalies detected",
  "audio_summary": "Normal audio levels",
  "scene_summary": "Normal scene activity"
}
```

#### Anomaly Detection:
```json
{
  "status": "Suspected Anomaly",
  "frame_id": 456,
  "tier2_result": {
    "threat_severity_index": 0.75,
    "reasoning_summary": "Detected unusual movement patterns",
    "visual_score": 0.8,
    "audio_score": 0.6
  }
}
```

### 4. Testing Scenarios

1. **Normal Activity**: Sit normally in front of camera
2. **Movement Test**: Move around, wave hands
3. **Audio Test**: Make noise, speak loudly
4. **Combined Test**: Move and make noise simultaneously

### 5. Troubleshooting

#### If WebSocket connection fails:
- Ensure server is running on port 8000
- Check that your webcam is accessible
- Verify no other app is using the webcam

#### If you get import errors:
Run the setup test:
```bash
venv/bin/python test_setup.py
```

#### If server won't start:
Check for missing dependencies:
```bash
venv/bin/python -c "import app; print('Success')"
```

### 6. Performance Notes

- The system processes frames at ~1 FPS for real-time analysis
- Tier 1 analysis is fast (pose + audio + scene)
- Tier 2 analysis triggers only when anomalies are detected
- TensorFlow warnings are normal and can be ignored

### 7. Next Steps

Once testing is successful, you can:
- Integrate with security cameras (RTSP streams)
- Add database logging
- Implement alert notifications
- Fine-tune detection thresholds
- Add more anomaly types

## 🎯 Ready to Test!

Your anomaly detection system is fully set up and ready for testing!
