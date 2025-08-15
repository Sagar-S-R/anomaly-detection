import React, { useState, useEffect, useCallback } from 'react';
import LiveFeed from './components/LiveFeed';
import AnomalyList from './components/AnomalyList';
import VideoPlayback from './components/VideoPlayback';
import JsonOutput from './components/JsonOutput';
import VideoControls from './components/VideoControls';
import './index.css';

function App() {
  // Main state management
  const [isConnected, setIsConnected] = useState(false);
  const [anomalyStatus, setAnomalyStatus] = useState('Normal');
  const [currentDetails, setCurrentDetails] = useState('Ready to monitor...');
  const [anomalies, setAnomalies] = useState([]);
  const [jsonData, setJsonData] = useState(null);
  const [currentVideoFile, setCurrentVideoFile] = useState(null);
  const [showJsonPanel, setShowJsonPanel] = useState(false);
  const [showVideoStream, setShowVideoStream] = useState(true);
  
  // WebSocket management
  const [ws, setWs] = useState(null);

  // WebSocket connection handler
  const connectWebSocket = useCallback(() => {
    if (ws) {
      ws.close();
    }

    const newWs = new WebSocket('ws://localhost:8000/stream_video');
    
    newWs.onopen = () => {
      setIsConnected(true);
      setCurrentDetails('Connected - Monitoring for anomalies...');
      console.log('WebSocket connected');
    };

    newWs.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setJsonData(data);

        if (data.error) {
          setCurrentDetails(`Error: ${data.error}`);
          return;
        }

        // Update current video file
        if (data.video_file) {
          setCurrentVideoFile(data.video_file);
        }

        // Handle anomaly detection
        if (data.status === 'Suspected Anomaly') {
          setAnomalyStatus('Anomaly Detected');
          setCurrentDetails(data.details || 'Anomaly detected!');
          
          // Add to anomalies list if it has frame info
          if (data.frame_count) {
            setAnomalies(prev => [...prev, {
              ...data,
              id: Date.now(), // Add unique ID
              timestamp: data.timestamp || Date.now() / 1000
            }]);
          }
        } else {
          setAnomalyStatus('Normal');
          setCurrentDetails(data.details || 'Monitoring...');
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        setCurrentDetails('Error parsing data from server');
      }
    };

    newWs.onclose = () => {
      setIsConnected(false);
      setAnomalyStatus('Normal');
      setCurrentDetails('Disconnected from monitoring service');
      console.log('WebSocket disconnected');
    };

    newWs.onerror = (error) => {
      setCurrentDetails('Connection error occurred');
      console.error('WebSocket error:', error);
    };

    setWs(newWs);
  }, [ws]);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (ws) {
      ws.close();
      setWs(null);
    }
  }, [ws]);

  // Refresh anomalies from backend
  const refreshAnomalies = useCallback(async () => {
    try {
      const response = await fetch('/anomaly_events');
      const data = await response.json();
      setAnomalies(data.anomaly_events || []);
    } catch (error) {
      console.error('Error fetching anomalies:', error);
    }
  }, []);

  // Auto-refresh anomalies every 5 seconds when connected
  useEffect(() => {
    let interval;
    if (isConnected) {
      interval = setInterval(refreshAnomalies, 5000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isConnected, refreshAnomalies]);

  // Control handlers
  const handleToggleStream = () => setShowVideoStream(!showVideoStream);
  const handleToggleJson = () => setShowJsonPanel(!showJsonPanel);
  
  const handleJumpToAnomaly = (anomaly) => {
    if (currentVideoFile && anomaly.timestamp) {
      // This will be handled by VideoPlayback component
      return { videoFile: currentVideoFile, timestamp: anomaly.timestamp };
    }
    return null;
  };

  const handleLoadLatestVideo = () => {
    if (currentVideoFile) {
      return currentVideoFile;
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-6 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center text-white text-2xl font-bold shadow-lg">
              A
            </div>
            <div>
              <h1 className="text-4xl font-bold text-slate-900 tracking-tight">
                Anomaly Detection System
              </h1>
              <p className="text-slate-600 mt-1 text-lg">
                Real-time AI-powered security monitoring and threat detection
              </p>
            </div>
          </div>
          <div className="h-1 bg-blue-100 rounded-full w-full">
            <div className="h-1 bg-blue-600 rounded-full w-1/4 transition-all duration-300"></div>
          </div>
        </div>

        {/* Main Controls */}
        <VideoControls
          isConnected={isConnected}
          onConnect={connectWebSocket}
          onDisconnect={disconnectWebSocket}
          onToggleStream={handleToggleStream}
          onToggleJson={handleToggleJson}
          onRefreshAnomalies={refreshAnomalies}
          showVideoStream={showVideoStream}
          showJsonPanel={showJsonPanel}
        />

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8 mb-8">
          {/* Live Feed - Takes up 3 columns on extra large screens */}
          <div className="xl:col-span-3">
            <LiveFeed
              anomalyStatus={anomalyStatus}
              currentDetails={currentDetails}
              isConnected={isConnected}
              showVideoStream={showVideoStream}
            />
          </div>

          {/* Side Panel */}
          <div className="space-y-6">
            {/* JSON Output Panel */}
            {showJsonPanel && (
              <JsonOutput jsonData={jsonData} />
            )}
            
            {/* Video Playback Controls */}
            <VideoPlayback
              currentVideoFile={currentVideoFile}
              onLoadLatest={handleLoadLatestVideo}
              onJumpToAnomaly={() => {
                const lastAnomaly = anomalies[anomalies.length - 1];
                return handleJumpToAnomaly(lastAnomaly);
              }}
            />
          </div>
        </div>

        {/* Anomaly List - Full width */}
        <AnomalyList
          anomalies={anomalies}
          onJumpToAnomaly={handleJumpToAnomaly}
          onRefresh={refreshAnomalies}
        />
      </div>
    </div>
  );
}

export default App;
