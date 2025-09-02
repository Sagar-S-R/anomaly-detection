import React, { useState, useEffect, useCallback } from 'react';
import Login from './pages/Login';
import Register from './pages/Register';
import Welcome from './pages/Welcome';
import LiveFeed from './components/LiveFeed';
import AnomalyList from './components/AnomalyList';
import JsonOutput from './components/JsonOutput';
import VideoControls from './components/VideoControls';
import InputSelector from './pages/InputSelector';
import LiveCameraMonitoring from './pages/LiveCameraMonitoring';
import CCTVMonitoring from './pages/CCTVMonitoring';
import VideoPlayback from './components/VideoPlayback';
import UserDashboard from './pages/UserDashboard';
import DatabaseManager from './components/DatabaseManager';
import VideoUploadMonitoring from './pages/VideoUploadMonitoring';
import './index.css';

function App() {
  // Authentication state
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('login'); // 'login', 'register', 'welcome', 'dashboard', 'input-selector', 'live-monitoring', 'upload-monitoring', 'cctv-monitoring', 'monitoring'
  
  // Debug/Demo mode - set to true to skip login
  const DEMO_MODE = false; // Change to true to skip authentication
  
  // Initialize demo user if in demo mode
  useEffect(() => {
    if (DEMO_MODE && !user) {
      setUser({ username: 'demo_user', timestamp: new Date() });
      setCurrentPage('input-selector');
    }
  }, [DEMO_MODE, user]);
  
  // Main state management
  const [isConnected, setIsConnected] = useState(false);
  const [anomalyStatus, setAnomalyStatus] = useState('Normal');
  const [currentDetails, setCurrentDetails] = useState('Ready to monitor...');
  const [anomalies, setAnomalies] = useState([]);
  const [jsonData, setJsonData] = useState(null);
  const [currentVideoFile, setCurrentVideoFile] = useState(null);
  const [showJsonPanel, setShowJsonPanel] = useState(false);
  const [showVideoStream, setShowVideoStream] = useState(true);
  const [videoFrame, setVideoFrame] = useState(null); // Store current video frame from WebSocket
  const [tier2InProgress, setTier2InProgress] = useState(false); // Track if Tier 2 analysis is running
  const [tier2Timeout, setTier2Timeout] = useState(null); // Track timeout for Tier 2 analysis
  
  // Input method management
  const [inputMode, setInputMode] = useState('none'); // 'none', 'live', 'cctv', 'upload'
  const [cctvConfig, setCctvConfig] = useState({ ip: '', port: 554, username: '', password: '' });
  const [uploadedFile, setUploadedFile] = useState(null);
  
  // WebSocket management
  const [ws, setWs] = useState(null);

  // Authentication handlers
  const handleLogin = (userData) => {
    setUser(userData);
    setCurrentPage('welcome');
  };

  const handleRegister = (userData) => {
    // After successful registration, show login page
    setCurrentPage('login');
  };

  const handleGoToRegister = () => {
    setCurrentPage('register');
  };

  const handleBackToLogin = () => {
    setCurrentPage('login');
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentPage('login');
    // Clean up any WebSocket connections
    if (ws) {
      ws.close();
      setWs(null);
    }
    setIsConnected(false);
    setInputMode('none');
  };

  const handleWelcomeContinue = () => {
    // Ensure clean state when navigating to dashboard
    if (ws && ws.readyState === WebSocket.OPEN) {
      console.log('🔌 Disconnecting WebSocket before going to dashboard');
      disconnectWebSocket();
    }
    setInputMode('none');
    setIsConnected(false);
    setVideoFrame(null);
    setCurrentPage('dashboard');
  };

  const handleInputModeSelect = async (mode, config = null) => {
    setInputMode(mode);
    
    // Route to specific monitoring pages instead of unified monitoring
    if (mode === 'live') {
      setCurrentPage('live-monitoring');
      connectWebSocket('/stream_video');
    } else if (mode === 'cctv') {
      setCurrentPage('cctv-monitoring');
      if (config) {
        setCctvConfig(config);
        const query = new URLSearchParams({
          ip: config.ip,
          port: config.port,
          ...(config.username && { username: config.username }),
          ...(config.password && { password: config.password })
        });
        connectWebSocket(`/connect_cctv?${query}`);
      }
    } else if (mode === 'upload') {
      setCurrentPage('upload-monitoring');
      setInputMode('upload');
      if (config && config instanceof File) {
        // For upload mode with file, config contains the file
        const file = config;
        setUploadedFile(file);
        const formData = new FormData();
        formData.append('file', file);
        
        try {
          setCurrentDetails('Uploading video...');
          const uploadResponse = await fetch('http://127.0.0.1:8000/upload_video', {
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
          setUploadedFile(null);
          setCurrentPage('input-selector');
        }
      } else {
        // Just navigate to upload monitoring page without file
        setCurrentDetails('Select a video file to analyze...');
        setUploadedFile(null);
      }
    }
  };

  const handleBackToInputSelector = () => {
    // Clean up connections
    if (ws) {
      ws.close();
      setWs(null);
    }
    setIsConnected(false);
    setInputMode('none');
    setUploadedFile(null);
    setCctvConfig({ ip: '', port: 554, username: '', password: '' });
    setCurrentPage('input-selector');
  };

  // Handle connect button based on input mode
  const handleConnect = () => {
    console.log('🔌 Connect button clicked! Current inputMode:', inputMode);
    console.log('🔌 Current isConnected:', isConnected);
    console.log('🔌 Current ws state:', ws?.readyState);
    
    if (inputMode === 'live') {
      console.log('📹 Starting live camera connection...');
      connectWebSocket('/stream_video');
    } else if (inputMode === 'cctv' && cctvConfig) {
      const query = new URLSearchParams({
        ip: cctvConfig.ip,
        port: cctvConfig.port.toString(),
        username: cctvConfig.username || '',
        password: cctvConfig.password || ''
      }).toString();
      connectWebSocket(`/connect_cctv?${query}`);
    } else if (inputMode === 'upload' && uploadedFile) {
      // For uploaded files, we should have the processing endpoint available
      // This connects to already processed uploaded file
      setCurrentDetails('Reconnecting to uploaded video processing...');
      connectWebSocket('/stream_video'); // Default fallback, should be updated with correct endpoint
    } else {
      // Default to live camera if no specific mode
      console.log('🔄 No specific input mode, defaulting to live camera');
      connectWebSocket('/stream_video');
    }
  };

  // WebSocket connection handler
  const connectWebSocket = useCallback((endpoint = '/stream_video') => {
    console.log('🌐 connectWebSocket called with endpoint:', endpoint);
    console.log('🌐 Current ws state before connection:', ws?.readyState);
    
    if (ws) {
      console.log('🔌 Closing existing WebSocket connection');
      ws.close(1000, 'Reconnecting');
    }

    // Add a small delay to ensure the previous connection is fully closed
    setTimeout(() => {
      // Add username to WebSocket connection
      const username = user?.username || 'demo_user';
      const separator = endpoint.includes('?') ? '&' : '?';
      const wsUrl = `ws://127.0.0.1:8000${endpoint}${separator}username=${encodeURIComponent(username)}`;
      
      console.log('🌐 Attempting WebSocket connection to:', wsUrl);
      const newWs = new WebSocket(wsUrl);
    
    newWs.onopen = () => {
      console.log('✅ WebSocket connection opened successfully!');
      setIsConnected(true);
      setCurrentDetails('Connected - Monitoring for anomalies...');
      console.log(`WebSocket connected to ${endpoint} for user ${username}`);
    };

    newWs.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setJsonData(data);

        if (data.error) {
          console.error('❌ WebSocket received error:', data.error);
          setCurrentDetails(`Error: ${data.error}`);
          return;
        }

        // Handle video frame data for live display
        if (data.frame_data) {
          setVideoFrame(data.frame_data);
        }

        // Update current video file
        if (data.video_file) {
          setCurrentVideoFile(data.video_file);
        }

        // Handle Tier 2 analysis start notification
        if (data.type === 'tier2_start') {
          console.log('🔬 Tier 2 Analysis STARTING:', data);
          setTier2InProgress(true);
          setCurrentDetails(`🧠 Advanced AI analysis starting for frame ${data.frame_id}...`);
          
          // Set timeout to reset Tier 2 status if analysis takes too long (60 seconds)
          if (tier2Timeout) {
            clearTimeout(tier2Timeout);
          }
          const timeoutId = setTimeout(() => {
            console.warn('⏰ Tier 2 analysis timeout - resetting status');
            setTier2InProgress(false);
            setCurrentDetails('Tier 2 analysis timed out - resuming normal monitoring...');
          }, 60000);
          setTier2Timeout(timeoutId);
          
          return;
        }

        // Handle Tier 2 analysis results
        if (data.type === 'tier2_analysis') {
          console.log('🔬 Received Tier 2 Analysis:', data);
          setTier2InProgress(false); // Analysis completed
          
          // Clear timeout since analysis completed
          if (tier2Timeout) {
            clearTimeout(tier2Timeout);
            setTier2Timeout(null);
          }
          
          if (data.error) {
            setCurrentDetails(`❌ Tier 2 AI Analysis Failed: ${data.error}`);
            setAnomalyStatus('Normal'); // Reset status after failed analysis
          } else {
            const threatLevel = data.threat_severity_index || 0.5;
            const threatPercent = (threatLevel * 100).toFixed(0);
            const severity = threatLevel > 0.7 ? 'HIGH' : threatLevel > 0.4 ? 'MEDIUM' : 'LOW';
            
            // Keep anomaly status active if high severity
            if (threatLevel > 0.6) {
              setAnomalyStatus('Anomaly Detected');
              setCurrentDetails(`🔴 HIGH THREAT DETECTED: ${data.reasoning_summary || 'Severe anomaly confirmed'} [Threat: ${severity} ${threatPercent}%]`);
            } else {
              setAnomalyStatus('Normal');
              setCurrentDetails(`✅ Tier 2 Analysis Complete: ${data.reasoning_summary || 'Analysis complete'} [Threat: ${severity} ${threatPercent}%]`);
            }
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

        // Handle real-time anomaly notifications from backend
        if (data.type === 'new_anomaly') {
          console.log('🚨 REAL-TIME ANOMALY RECEIVED:', data.data);
          
          const anomalyData = data.data;
          setAnomalyStatus('Anomaly Detected');
          setTier2InProgress(true); // Mark Tier 2 as starting
          setCurrentDetails(`🚨 ${anomalyData.details || 'New anomaly detected!'} - Starting Tier 2 AI analysis...`);
          
          // Add to anomalies list immediately for real-time display
          setAnomalies(prev => {
            // Check if this anomaly already exists to prevent duplicates
            const exists = prev.some(anomaly => 
              anomaly.id === anomalyData.id || 
              (anomaly.frame_id === anomalyData.frame_id && 
               Math.abs((anomaly.timestamp || 0) - (anomalyData.timestamp || 0)) < 2)
            );
            
            if (!exists) {
              const newAnomaly = {
                ...anomalyData,
                id: anomalyData.id || Date.now(),
                receivedAt: Date.now(),
                source: 'real_time',
                status: 'new' // Mark for UI highlighting
              };
              console.log('✅ Added real-time anomaly to UI:', newAnomaly);
              return [newAnomaly, ...prev]; // Add to beginning for immediate visibility
            }
            console.log('⚠️ Duplicate anomaly detected, skipping');
            return prev;
          });
          return;
        }

        // Handle regular anomaly detection (Tier 1 - enhanced component display)
        if (data.status === 'Suspected Anomaly') {
          console.log('🔍 Tier 1 anomaly detected:', data);
          
          // Extract detailed component information
          let detailedStatus = data.details || 'Anomaly detected';
          
          if (data.tier1_components) {
            const components = data.tier1_components;
            console.log('🔬 Processing Tier 1 components:', components);
            
            // Build detailed breakdown string
            const componentBreakdown = [];
            
            if (components.pose_analysis) {
              const pose = components.pose_analysis;
              if (pose.anomaly_detected) {
                componentBreakdown.push(`📸 POSE: ${pose.summary || 'Anomaly detected'}`);
              }
            }
            
            if (components.audio_analysis) {
              const audio = components.audio_analysis;
              if (audio.available && audio.transcript_text) {
                componentBreakdown.push(`🎙️ AUDIO: "${audio.transcript_text}"`);
              } else if (audio.summary) {
                componentBreakdown.push(`🎙️ AUDIO: ${audio.summary}`);
              }
            }
            
            if (components.scene_analysis) {
              const scene = components.scene_analysis;
              if (scene.anomaly_probability > 0.1) {
                componentBreakdown.push(`🎬 SCENE: ${scene.summary || `Anomaly probability: ${scene.anomaly_probability.toFixed(3)}`}`);
              }
            }
            
            if (components.fusion_logic) {
              const fusion = components.fusion_logic;
              if (fusion.details) {
                componentBreakdown.push(`🧠 FUSION: ${fusion.details}`);
              }
            }
            
            // Update status with detailed breakdown
            if (componentBreakdown.length > 0) {
              detailedStatus = `🚨 TIER 1 DETECTION:\n${componentBreakdown.join('\n')}\n\n🔬 Triggering Tier 2 AI Analysis...`;
            }
          }
          
          setAnomalyStatus('Anomaly Detected');
          setTier2InProgress(true); // Mark Tier 2 as starting
          setCurrentDetails(detailedStatus);
          
          // Add to anomalies list if it has frame info and doesn't already exist
          if (data.frame_count || data.frame_id) {
            setAnomalies(prev => {
              // Check if this anomaly already exists (might be from real-time broadcast)
              const exists = prev.some(anomaly => 
                (anomaly.frame_id === data.frame_id && 
                 Math.abs((anomaly.timestamp || 0) - (data.timestamp || Date.now() / 1000)) < 2) ||
                (anomaly.id === data.id)
              );
              
              if (!exists) {
                const newAnomaly = {
                  ...data,
                  id: data.id || Date.now(),
                  timestamp: data.timestamp || Date.now() / 1000,
                  tier2_analysis: null,
                  source: 'websocket_legacy',
                  status: 'detecting'
                };
                console.log('✅ Added legacy anomaly to UI:', newAnomaly);
                return [newAnomaly, ...prev];
              }
              console.log('⚠️ Legacy anomaly already exists, skipping');
              return prev;
            });
          }
        } else if (data.status === 'Normal' || data.status === 'No Anomaly') {
          // Only update status to Normal if no Tier 2 analysis is in progress
          if (!tier2InProgress) {
            setAnomalyStatus('Normal');
          }
          
          // Show detailed real-time analysis information
          const displayDetails = data.details || 'Monitoring...';
          
          // Only update details if no Tier 2 analysis is in progress (to preserve analysis status)
          if (!tier2InProgress) {
            // Extract scene and pose confidence from details if available
            let enhancedDetails = displayDetails;
            if (data.tier1_components) {
              const sceneData = data.tier1_components.scene_analysis || {};
              const poseData = data.tier1_components.pose_analysis || {};
              
              const sceneProb = sceneData.scene_probability || 0;
              const poseDetected = poseData.anomaly_detected || false;
              
              enhancedDetails = `Real-time monitoring: Scene confidence ${(sceneProb * 100).toFixed(1)}%, Pose anomaly: ${poseDetected ? 'Yes' : 'No'} | ${displayDetails}`;
            } else if (data.fusion_status) {
              enhancedDetails = `Fusion: ${data.fusion_status} | ${displayDetails}`;
            }
            
            setCurrentDetails(enhancedDetails);
          }
          
          // Log the actual data being received for debugging
          console.log('📊 Real-time normal data:', {
            status: data.status,
            details: data.details,
            fusion_status: data.fusion_status,
            tier1_components: data.tier1_components,
            timestamp: data.timestamp
          });
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        setCurrentDetails('Error parsing data from server');
      }
    };

    newWs.onclose = (event) => {
      console.log('🔌 WebSocket connection closed:', event.code, event.reason, event.wasClean);
      setIsConnected(false);
      setAnomalyStatus('Normal');
      setVideoFrame(null);
      setCurrentDetails('Disconnected from monitoring service');
      console.log('WebSocket disconnected:', event.code, event.reason);
      
      // Only auto-reconnect if it was an unexpected disconnection (not manual disconnect)
      if (event.code !== 1000 && !event.wasClean && inputMode !== 'none') {
        console.log('Attempting to reconnect in 3 seconds...');
        setTimeout(() => {
          if (!ws || ws.readyState === WebSocket.CLOSED) {
            console.log('Reconnecting WebSocket...');
            connectWebSocket(endpoint);
          }
        }, 3000);
      }
    };

    newWs.onerror = (error) => {
      console.error('❌ WebSocket connection error:', error);
      console.error('❌ WebSocket readyState:', newWs.readyState);
      console.error('❌ WebSocket URL was:', wsUrl);
      setCurrentDetails('Connection error - Check camera access and backend server');
      console.error('WebSocket error details:', error);
    };

    setWs(newWs);
    }, 1000); // Close the setTimeout function with 1 second delay
  }, [ws, user?.username, inputMode, tier2InProgress, tier2Timeout]); // Added tier2Timeout dependency

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (ws) {
      console.log('🔌 Properly disconnecting WebSocket...');
      ws.close(1000, 'User initiated disconnect'); // Normal closure
      setWs(null);
    }
    setIsConnected(false);
    setVideoFrame(null);
    // Add a small delay to ensure backend properly cleans up
    setTimeout(() => {
      console.log('🔌 WebSocket cleanup complete');
    }, 1000);
  }, [ws]);

  // Refresh anomalies from backend
  const refreshAnomalies = useCallback(async () => {
    try {
      const username = user?.username || 'demo_user';
      const response = await fetch(`/anomaly_events?username=${encodeURIComponent(username)}`);
      const data = await response.json();
      setAnomalies(data.anomaly_events || []);
    } catch (error) {
      console.error('Error fetching anomalies:', error);
    }
  }, [user]);

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

  // Auto-mark new anomalies as "seen" after 10 seconds
  useEffect(() => {
    const markAnomaliesAsSeen = () => {
      setAnomalies(prev => {
        const now = Date.now();
        return prev.map(anomaly => {
          if (anomaly.status === 'new' && anomaly.receivedAt && (now - anomaly.receivedAt > 10000)) {
            return { ...anomaly, status: 'seen' };
          }
          return anomaly;
        });
      });
    };

    const interval = setInterval(markAnomaliesAsSeen, 5000);
    return () => clearInterval(interval);
  }, []);

  // Cleanup Tier 2 timeout on unmount
  useEffect(() => {
    return () => {
      if (tier2Timeout) {
        clearTimeout(tier2Timeout);
      }
    };
  }, [tier2Timeout]);

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

  const handleDisconnect = () => {
    disconnectWebSocket();
    // Don't reset inputMode to 'none' - keep the current input type for reconnection
    setCurrentDetails('Disconnected - Ready to reconnect');
    setIsConnected(false);
    setVideoFrame(null); // Clear video frame
  };

  const handleDownloadData = async () => {
    try {
      setCurrentDetails('Preparing download...');
      const username = user?.username || 'demo_user';
      const response = await fetch(`http://127.0.0.1:8000/download-session-data?username=${encodeURIComponent(username)}`);
      
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

  // Render based on current page
  if (currentPage === 'login') {
    return <Login onLogin={handleLogin} onGoToRegister={handleGoToRegister} />;
  }

  if (currentPage === 'register') {
    return <Register onRegister={handleRegister} onBackToLogin={handleBackToLogin} />;
  }

  if (currentPage === 'welcome') {
    return (
      <Welcome 
        user={user}
        onContinue={handleWelcomeContinue}
        onLogout={handleLogout}
      />
    );
  }

  if (currentPage === 'dashboard') {
    return (
      <UserDashboard 
        user={user}
        onLogout={handleLogout}
        onStartMonitoring={() => setCurrentPage('input-selector')}
      />
    );
  }

  if (currentPage === 'input-selector') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black cyber-grid-bg">
        <div className="container mx-auto px-6 py-8">
          {/* Header with User Info */}
          <div className="flex justify-between items-center mb-12">
            <div className="flex items-center gap-6">
              <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-teal-400 rounded-xl flex items-center justify-center text-black text-2xl font-bold shadow-lg cyber-glow border border-cyan-400">
                <span className="font-mono">⚡</span>
              </div>
              <div>
                <h1 className="cyber-title text-5xl mb-2">
                  MONITORING SYSTEM
                </h1>
                <p className="cyber-subtitle text-xl text-cyan-300">
                  Select your input source to begin
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="cyber-panel px-4 py-3">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-green-400 rounded-full cyber-pulse"></div>
                  <span className="text-green-400 font-mono font-bold">
                    {user.username.toUpperCase()}
                  </span>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="cyber-btn-secondary px-6 py-3 rounded-xl font-mono font-bold tracking-wider uppercase"
              >
                LOGOUT
              </button>
            </div>
          </div>

          {/* Input Method Selection */}
          <InputSelector
            inputMode={inputMode}
            isConnected={isConnected}
            onLiveCamera={(mode) => handleInputModeSelect(mode)}
            onCCTVConnect={(mode, config) => handleInputModeSelect(mode, config)}
            onVideoUpload={(file) => handleInputModeSelect('upload', file)}
            onDisconnect={handleDisconnect}
            onDownloadData={handleDownloadData}
            cctvConfig={cctvConfig}
          />
        </div>
      </div>
    );
  }

  // Live Camera Monitoring Page
  if (currentPage === 'live-monitoring') {
    return (
      <LiveCameraMonitoring
        user={user}
        onLogout={handleLogout}
        onBackToSelector={handleBackToInputSelector}
        onConnect={handleConnect}
        ws={ws}
        isConnected={isConnected}
        anomalyStatus={anomalyStatus}
        currentDetails={currentDetails}
        anomalies={anomalies}
        jsonData={jsonData}
        showJsonPanel={showJsonPanel}
        onToggleJson={handleToggleJson}
        onDisconnect={handleDisconnect}
        onDownloadData={handleDownloadData}
        videoFrame={videoFrame}
        tier2InProgress={tier2InProgress}
      />
    );
  }

  // Video Upload Monitoring Page
  if (currentPage === 'upload-monitoring') {
    return (
      <VideoUploadMonitoring
        user={user}
        onLogout={handleLogout}
        onBackToSelector={handleBackToInputSelector}
        onVideoUpload={(file) => handleInputModeSelect('upload', file)}
        ws={ws}
        isConnected={isConnected}
        anomalyStatus={anomalyStatus}
        currentDetails={currentDetails}
        anomalies={anomalies}
        jsonData={jsonData}
        showJsonPanel={showJsonPanel}
        currentVideoFile={currentVideoFile}
        onToggleJson={handleToggleJson}
        onDisconnect={handleDisconnect}
        onDownloadData={handleDownloadData}
      />
    );
  }

  // CCTV Monitoring Page
  if (currentPage === 'cctv-monitoring') {
    return (
      <CCTVMonitoring
        user={user}
        onLogout={handleLogout}
        onBackToSelector={handleBackToInputSelector}
        onCCTVConnect={(config) => handleInputModeSelect('cctv', config)}
        ws={ws}
        isConnected={isConnected}
        anomalyStatus={anomalyStatus}
        currentDetails={currentDetails}
        anomalies={anomalies}
        jsonData={jsonData}
        showJsonPanel={showJsonPanel}
        onToggleJson={handleToggleJson}
        onDisconnect={handleDisconnect}
        onDownloadData={handleDownloadData}
      />
    );
  }

  // Main monitoring interface
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
        {/* Header with User Info and Back Button */}
        <div className="flex justify-between items-center mb-10">
          <div className="flex items-center gap-6">
            <button
              onClick={handleBackToInputSelector}
              className="cyber-btn-secondary px-4 py-3 rounded-xl font-mono font-bold tracking-wider uppercase"
            >
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                BACK
              </div>
            </button>
            <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-teal-400 rounded-xl flex items-center justify-center text-black text-2xl font-bold shadow-lg cyber-glow border border-cyan-400">
              <span className="font-mono">⚡</span>
            </div>
            <div>
              <h1 className="cyber-title text-5xl mb-2">
                ANOMALY DETECTION SYSTEM
              </h1>
              <p className="cyber-subtitle text-xl text-cyan-300">
                {inputMode === 'live' ? 'Live Camera Monitoring' : 
                 inputMode === 'cctv' ? 'CCTV Stream Monitoring' : 
                 inputMode === 'upload' ? 'Video Upload Analysis' : 'Real-time Security Monitoring'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="cyber-panel px-4 py-3">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-green-400 rounded-full cyber-pulse"></div>
                <span className="text-green-400 font-mono font-bold">
                  {user.username.toUpperCase()}
                </span>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="cyber-btn-secondary px-6 py-3 rounded-xl font-mono font-bold tracking-wider uppercase"
            >
              LOGOUT
            </button>
          </div>
        </div>
        
        {/* Cyber Progress Bar */}
        <div className="cyber-progress h-2 w-full mb-10">
          <div className="cyber-progress-fill" style={{ width: '75%' }}></div>
        </div>

        {/* Main Controls */}
        <VideoControls
          isConnected={isConnected}
          onConnect={handleConnect}
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
              tier2InProgress={tier2InProgress}
            />
          </div>

          {/* Side Panel - Fixed height with scroll */}
          <div className="max-h-[80vh] overflow-y-auto space-y-6">
            {/* Input Type Specific Info */}
            {inputMode && (
              <div className="cyber-panel p-4">
                <h3 className="cyber-title text-lg mb-3">
                  {inputMode === 'live' && '📹 LIVE CAMERA'}
                  {inputMode === 'cctv' && '📡 CCTV STREAM'}
                  {inputMode === 'upload' && '📁 VIDEO UPLOAD'}
                </h3>
                <div className="space-y-2 text-sm">
                  {inputMode === 'live' && (
                    <>
                      <div className="text-gray-300 font-mono">• Real-time camera feed</div>
                      <div className="text-gray-300 font-mono">• Instant anomaly detection</div>
                      <div className="text-gray-300 font-mono">• Live pose analysis</div>
                    </>
                  )}
                  {inputMode === 'cctv' && cctvConfig.ip && (
                    <>
                      <div className="text-cyan-400 font-mono">IP: {cctvConfig.ip}:{cctvConfig.port}</div>
                      <div className="text-gray-300 font-mono">• Remote camera monitoring</div>
                      <div className="text-gray-300 font-mono">• Network stream processing</div>
                    </>
                  )}
                  {inputMode === 'upload' && (
                    <>
                      <div className="text-gray-300 font-mono">• Video file analysis</div>
                      <div className="text-gray-300 font-mono">• Batch processing</div>
                      <div className="text-gray-300 font-mono">• Historical review</div>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Database Manager Panel - Compact */}
            <div className="max-h-96">
              <DatabaseManager />
            </div>
            
            {/* JSON Output Panel */}
            {showJsonPanel && (
              <div className="max-h-80">
                <JsonOutput jsonData={jsonData} />
              </div>
            )}
            
            {/* Video Playback Controls - Compact */}
            <div className="max-h-64">
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
