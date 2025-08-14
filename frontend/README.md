# Anomaly Detection Frontend

A modern React-based dashboard for real-time anomaly detection monitoring.

## Features

### 🎥 Live Video Monitoring
- Real-time MJPEG video stream from backend
- Anomaly status indicators with color-coded alerts
- Auto-refresh to prevent stale streams
- **WebRTC Ready**: Architecture designed for easy WebRTC upgrade

### 🚨 Real-time Anomaly Detection
- WebSocket connection for live status updates
- Visual anomaly indicators with threat severity levels
- Collapsible JSON data panel for detailed information
- Automatic anomaly logging and storage

### 📹 Video Playback
- Load and play recorded sessions
- Jump to specific timestamps
- Quick navigation to anomaly events
- Full video controls

### 📊 Anomaly Management
- Comprehensive anomaly list with thumbnails
- Severity-based color coding (red/orange/green)
- Detailed anomaly information and AI analysis
- Sortable by time or severity

### 🎛️ System Controls
- Start/Stop monitoring (WebSocket management)
- Toggle video stream display
- Show/Hide JSON output panel
- Refresh anomaly data

## Architecture

### Component Structure
```
src/
├── App.jsx                 # Main application & state management
├── components/
│   ├── LiveFeed.jsx        # Live video stream & status
│   ├── AnomalyList.jsx     # Anomaly history & management
│   ├── VideoPlayback.jsx   # Video player controls
│   ├── JsonOutput.jsx      # Real-time data display
│   └── VideoControls.jsx   # System control panel
├── index.css               # Tailwind & custom styles
└── index.js                # React app entry point
```

### State Management
- **React Hooks**: `useState` and `useEffect` for component state
- **WebSocket Management**: Centralized in App.jsx
- **Auto-refresh**: 5-second intervals for anomaly data, 30-second video refresh
- **Responsive Design**: Tailwind CSS with mobile-first approach

## Installation & Setup

### Prerequisites
- Node.js 16+ 
- Backend anomaly detection server running on `localhost:8000`

### Install Dependencies
```bash
cd frontend
npm install
```

### Development Mode
```bash
npm start
```
Runs on `http://localhost:3000` with proxy to backend on `localhost:8000`

### Production Build
```bash
npm run build
```

## WebRTC Migration Path

The current implementation uses MJPEG streams but is architected for easy WebRTC upgrade:

### Current Implementation (MJPEG)
```jsx
// In LiveFeed.jsx
<img
  src={`/video_stream?t=${videoKey}`}
  alt="Live Video Stream"
  className="video-stream-classes"
/>
```

### Future WebRTC Implementation
```jsx
// Replace <img> with:
<video
  ref={videoRef}
  autoPlay
  muted
  className="video-stream-classes"
/>

// Add WebRTC connection logic:
useEffect(() => {
  const setupWebRTC = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({video: true});
    videoRef.current.srcObject = stream;
  };
  setupWebRTC();
}, []);
```

### Migration Checklist
- [ ] Replace `<img>` with `<video>` element in `LiveFeed.jsx`
- [ ] Add WebRTC connection logic
- [ ] Update video refresh mechanism
- [ ] Maintain existing CSS classes and anomaly border logic
- [ ] Test responsive layout with video element

## Configuration

### Backend Integration
- WebSocket: `ws://localhost:8000/stream_video`
- Video Stream: `http://localhost:8000/video_stream`
- Anomaly API: `http://localhost:8000/anomaly_events`

### Customization
- **Colors**: Modify `tailwind.config.js` for custom anomaly colors
- **Refresh Intervals**: Adjust in `App.jsx` (lines 45-50)
- **Video Quality**: Configure in backend video stream endpoint

## Responsive Design

### Breakpoints
- **Mobile**: Single column layout, stacked components
- **Tablet**: Two-column grid for main content
- **Desktop**: Three-column layout with sidebar panels

### Performance
- Conditional rendering for hidden panels
- Optimized re-renders with React hooks
- Custom scrollbars for better UX
- Smooth animations with Tailwind transitions

## Development Notes

### Component Communication
- Props drilling for simple state sharing
- Event handlers passed down from App.jsx
- Callback functions for child-to-parent communication

### Error Handling
- WebSocket connection error recovery
- Video stream fallback displays
- Graceful API failure handling

### Browser Compatibility
- Modern browsers with WebSocket support
- ES6+ features (requires transpilation for older browsers)
- CSS Grid and Flexbox layouts

## Future Enhancements

### Planned Features
- [ ] WebRTC video streaming
- [ ] Real-time alerts/notifications
- [ ] Anomaly export functionality
- [ ] Multi-camera support
- [ ] Historical analytics dashboard
- [ ] User authentication

### Performance Optimizations
- [ ] Virtual scrolling for large anomaly lists
- [ ] Image lazy loading
- [ ] WebSocket message throttling
- [ ] Service worker for offline capability
