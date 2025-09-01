import React, { useState, useEffect, useCallback } from 'react';
import LiveFeed from './components/LiveFeed';
import AnomalyList from './components/AnomalyList';
import VideoPlayback from './components/VideoPlayback';
import JsonOutput from './components/JsonOutput';
import VideoControls from './components/VideoControls';
import InputSelector from './components/InputSelector';
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
  
  // Input method management
  const [inputMode, setInputMode] = useState('none'); // 'none', 'live', 'cctv', 'upload'
  const [cctvConfig, setCctvConfig] = useState({ ip: '', port: 554, username: '', password: '' });
  
  // WebSocket management
  const [ws, setWs] = useState(null);

  // WebSocket connection handler
  const connectWebSocket = useCallback((endpoint = '/stream_video') => {
    if (ws) {
      ws.close();
    }

    const newWs = new WebSocket(`ws://localhost:8000${endpoint}`);
    
    newWs.onopen = () => {
      setIsConnected(true);
      setCurrentDetails('Connected - Monitoring for anomalies...');
      console.log(`WebSocket connected to ${endpoint}`);
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

        // Handle Tier 2 analysis results
        if (data.type === 'tier2_analysis') {
          console.log('� Received Tier 2 Analysis:', data);
          
          if (data.error) {
            setCurrentDetails(`❌ AI Analysis Failed: ${data.error}`);
          } else {
            const threatLevel = data.threat_severity_index || 0.5;
            const threatPercent = (threatLevel * 100).toFixed(0);
            const severity = threatLevel > 0.7 ? 'HIGH' : threatLevel > 0.4 ? 'MEDIUM' : 'LOW';
            
            setCurrentDetails(`✅ AI Analysis Complete: ${data.reasoning_summary || 'Analysis complete'} [Threat: ${severity} ${threatPercent}%]`);
          }
          
          // Update the latest anomaly with tier2 analysis
          setAnomalies(prev => {
            const updated = [...prev];
            
            // Try multiple matching strategies
            let matchingIndex = -1;
            
            // 1. First try exact frame_id match
            if (data.frame_id) {
              matchingIndex = updated.findIndex(anomaly => anomaly.frame_id === data.frame_id);
            }
            
            // 2. Find the most recent anomaly without Tier 2 analysis
            if (matchingIndex === -1) {
              // Look from newest to oldest for anomaly without tier2_analysis
              for (let i = updated.length - 1; i >= 0; i--) {
                if (!updated[i].tier2_analysis) {
                  matchingIndex = i;
                  break;
                }
              }
            }
            
            // 3. Last resort: use most recent anomaly
            if (matchingIndex === -1 && updated.length > 0) {
              matchingIndex = updated.length - 1;
            }
            
            if (matchingIndex !== -1) {
              const matchingAnomaly = updated[matchingIndex];
              matchingAnomaly.tier2_analysis = data;
              matchingAnomaly.reasoning_summary = data.reasoning_summary;
              matchingAnomaly.threat_severity_index = data.threat_severity_index;
              matchingAnomaly.visual_score = data.visual_score;
              matchingAnomaly.audio_score = data.audio_score;
              matchingAnomaly.text_alignment_score = data.text_alignment_score;
              matchingAnomaly.multimodal_agreement = data.multimodal_agreement;
              console.log('✅ Updated anomaly with Tier 2 analysis');
            } else {
              console.warn('⚠️ No matching anomaly found for Tier 2 analysis');
            }
            return updated;
          });
          return;
        }

        // Handle anomaly detection (Tier 1)
        if (data.status === 'Suspected Anomaly') {
          setAnomalyStatus('Anomaly Detected');
          setCurrentDetails(`🚨 ${data.details || 'Anomaly detected!'} - Triggering AI analysis...`);
          
          // Add to anomalies list if it has frame info
          if (data.frame_count || data.frame_id) {
            setAnomalies(prev => [...prev, {
              ...data,
              id: Date.now(), // Add unique ID
              timestamp: data.timestamp || Date.now() / 1000,
              tier2_analysis: null // Will be populated when Tier 2 completes
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

  // Input method handlers
  const handleLiveCamera = () => {
    setInputMode('live');
    connectWebSocket('/stream_video');
  };

  const handleCCTVConnect = (config) => {
    setCctvConfig(config);
    setInputMode('cctv');
    const query = new URLSearchParams({
      ip: config.ip,
      port: config.port,
      ...(config.username && { username: config.username }),
      ...(config.password && { password: config.password })
    });
    connectWebSocket(`/connect_cctv?${query}`);
  };

  const handleVideoUpload = async (file) => {
    setInputMode('upload');
    
    // Upload the file first
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setCurrentDetails('Uploading video...');
      const uploadResponse = await fetch('/upload_video', {
        method: 'POST',
        body: formData
      });
      
      if (!uploadResponse.ok) {
        throw new Error('Upload failed');
      }
      
      const uploadResult = await uploadResponse.json();
      setCurrentDetails('Video uploaded, starting analysis...');
      
      // Connect to processing WebSocket
      connectWebSocket(`/process_uploaded_video/${uploadResult.filename}`);
      
    } catch (error) {
      setCurrentDetails(`Upload failed: ${error.message}`);
      setInputMode('none');
    }
  };

  const handleDisconnect = () => {
    disconnectWebSocket();
    setInputMode('none');
    setCurrentDetails('Disconnected');
  };

  const handleDownloadData = async () => {
    try {
      setCurrentDetails('Preparing download...');
      const response = await fetch('/download-session-data');
      
      if (!response.ok) {
        throw new Error('Download failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `anomaly_data_${new Date().toISOString().split('T')[0]}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setCurrentDetails('Download complete!');
    } catch (error) {
      setCurrentDetails(`Download failed: ${error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 relative">
      {/* Cyber Grid Overlay */}
      <div className="fixed inset-0 opacity-20 pointer-events-none z-0">
        <div 
          className="w-full h-full" 
          style={{
            backgroundImage: `
              linear-gradient(rgba(0,255,255,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0,255,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
            animation: 'gridMove 20s linear infinite'
          }}
        />
      </div>

      <div className="container mx-auto px-6 py-8 max-w-7xl relative z-10">
        {/* Cyber Header */}
        <div className="mb-10">
          <div className="flex items-center gap-6 mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-teal-400 rounded-xl flex items-center justify-center text-black text-2xl font-bold shadow-lg cyber-glow border border-cyan-400">
              <span className="font-mono">⚡</span>
            </div>
            <div>
              <h1 className="cyber-title text-5xl mb-2">
                ANOMALY DETECTION SYSTEM
              </h1>
              <p className="cyber-subtitle text-xl text-cyan-300">
                Advanced AI-Powered Security Monitoring Platform
              </p>
            </div>
          </div>
          
          {/* Cyber Progress Bar */}
          <div className="cyber-progress h-2 w-full">
            <div className="cyber-progress-fill" style={{ width: '75%' }}></div>
          </div>
        </div>

        {/* Input Method Selection */}
        <InputSelector
          inputMode={inputMode}
          isConnected={isConnected}
          onLiveCamera={handleLiveCamera}
          onCCTVConnect={handleCCTVConnect}
          onVideoUpload={handleVideoUpload}
          onDisconnect={handleDisconnect}
          onDownloadData={handleDownloadData}
          cctvConfig={cctvConfig}
        />

        {/* Main Controls */}
        <VideoControls
          isConnected={isConnected}
          onConnect={() => {}} // Handled by InputSelector now
          onDisconnect={handleDisconnect}
          onToggleStream={handleToggleStream}
          onToggleJson={handleToggleJson}
          onRefreshAnomalies={refreshAnomalies}
          showVideoStream={showVideoStream}
          showJsonPanel={showJsonPanel}
          inputMode={inputMode}
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
