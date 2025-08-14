# Setup Instructions for Anomaly Detection React Frontend

## ✅ Complete Installation

Your modern React frontend has been successfully created! Here's what you have:

### 📁 Created Files:
```
frontend/
├── package.json              # Dependencies & scripts
├── tailwind.config.js        # Tailwind CSS configuration  
├── postcss.config.js         # PostCSS configuration
├── start.bat                 # Windows startup script
├── start.sh                  # Linux/Mac startup script
├── README.md                 # Detailed documentation
├── public/
│   └── index.html            # HTML template
└── src/
    ├── App.jsx               # Main React app
    ├── index.js              # React entry point
    ├── index.css             # Tailwind + custom styles
    └── components/           # React components
        ├── LiveFeed.jsx          # Live video stream
        ├── AnomalyList.jsx       # Anomaly management
        ├── VideoPlayback.jsx     # Video player
        ├── JsonOutput.jsx        # Real-time data panel
        └── VideoControls.jsx     # System controls
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start the Frontend
**Option A - NPM Command:**
```bash
npm start
```

**Option B - Convenience Scripts:**
- Windows: Double-click `start.bat` OR run `start.bat` in terminal
- Linux/Mac: Run `./start.sh` in terminal (may need `chmod +x start.sh` first)

### 3. Access the Dashboard
- **React Dashboard**: http://localhost:3000 (recommended)
- **Legacy Dashboard**: http://localhost:8000/dashboard

## 🔧 Features Overview

### 📱 Modern UI Components:
- **LiveFeed**: Real-time video stream with anomaly indicators
- **AnomalyList**: Sortable list with severity indicators and thumbnails
- **VideoPlayback**: Full-featured video player with timestamp navigation
- **JsonOutput**: Collapsible real-time data display
- **VideoControls**: System management and display toggles

### 🎨 Design Features:
- Tailwind CSS with custom anomaly color scheme
- Responsive layout (mobile → tablet → desktop)
- Smooth animations and transitions
- Dark/light themed components
- Custom scrollbars and modern UI elements

### ⚡ Technical Features:
- WebSocket connection management
- Auto-refresh intervals (5s anomalies, 30s video)
- Error handling and fallback displays
- Performance optimized rendering
- WebRTC-ready architecture

## 🔄 WebRTC Migration Path

The current implementation uses MJPEG but is designed for easy WebRTC upgrade:

### Current (MJPEG):
```jsx
<img src="/video_stream" />
```

### Future (WebRTC):
```jsx
<video ref={videoRef} autoPlay />
// + WebRTC connection logic
```

All styling, anomaly detection, and UI logic will remain the same!

## 🛠️ Development

### File Structure:
- **App.jsx**: Main state management and WebSocket handling
- **Components**: Modular, reusable React components
- **Tailwind**: Utility-first CSS with custom extensions
- **Responsive**: Mobile-first design approach

### Key State Management:
- WebSocket connection status
- Anomaly detection results
- Video playback controls
- UI display toggles

## 🎯 Next Steps

1. **Start Backend**: Ensure your Python backend is running on `localhost:8000`
2. **Install & Start Frontend**: Follow quick start steps above
3. **Test Integration**: Verify WebSocket connection and video stream
4. **Customize**: Modify colors, intervals, or layout as needed

## 📝 Notes

- The frontend expects backend on `localhost:8000`
- WebSocket endpoint: `ws://localhost:8000/stream_video`
- Video stream: `http://localhost:8000/video_stream`
- Proxy configuration handles CORS automatically
- All components are well-documented with inline comments

Enjoy your modern anomaly detection dashboard! 🚀
