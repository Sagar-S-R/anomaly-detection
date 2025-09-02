import React, { useState, useEffect } from 'react';

const LiveFeed = ({ anomalyStatus, currentDetails, isConnected, showVideoStream, videoFrame, ws, tier2InProgress }) => {
  const [videoError, setVideoError] = useState(false);
  const [videoKey, setVideoKey] = useState(Date.now());
  const [useWebSocketStream, setUseWebSocketStream] = useState(false);

  // Auto-refresh video stream every 30 seconds to prevent stale streams
  useEffect(() => {
    if (!showVideoStream) return;
    
    const interval = setInterval(() => {
      setVideoKey(Date.now());
    }, 30000);

    return () => clearInterval(interval);
  }, [showVideoStream]);

  // Use WebSocket stream when connected to avoid camera conflicts
  useEffect(() => {
    setUseWebSocketStream(isConnected && ws);
  }, [isConnected, ws]);

  const isAnomalyDetected = anomalyStatus === 'Anomaly Detected';
  
  const statusConfig = {
    'Normal': {
      bgColor: 'from-green-900/20 to-green-800/10',
      textColor: 'text-green-400',
      borderColor: 'border-green-400/40',
      icon: '✅'
    },
    'Anomaly Detected': {
      bgColor: 'from-red-900/20 to-red-800/10',
      textColor: 'text-red-400', 
      borderColor: 'border-red-400/40',
      icon: '🚨'
    }
  };

  const config = statusConfig[anomalyStatus] || statusConfig['Normal'];

  const handleVideoError = () => {
    setVideoError(true);
    console.error('Video stream error');
  };

  const handleVideoLoad = () => {
    setVideoError(false);
  };

  return (
    showVideoStream ? (
    <div className={`
      cyber-card p-8 transition-all duration-500 reveal-up
      ${isAnomalyDetected ? 'border-red-400/60 cyber-glow' : 'border-cyan-400/30'}
    `}>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-gradient-to-br from-cyan-400/20 to-teal-400/20 rounded-2xl flex items-center justify-center border border-cyan-400/30">
            <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h2 className="cyber-title text-3xl">LIVE VIDEO STREAM</h2>
            <p className="cyber-subtitle text-lg">Real-time monitoring feed</p>
          </div>
        </div>
        <div className={`
          px-6 py-3 rounded-xl text-sm font-mono font-bold tracking-wider uppercase border
          ${isConnected ? 'bg-green-900/30 text-green-400 border-green-400/40' : 'bg-gray-900/30 text-gray-400 border-gray-500/40'}
        `}>
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-400 cyber-pulse' : 'bg-gray-500'
            }`}></div>
            {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
          </div>
        </div>
      </div>

      {/* Enhanced Status Display with Tier 2 Progress */}
      <div className={`
        p-6 rounded-xl mb-8 border-l-4 bg-gradient-to-r transition-all duration-500
        ${config.borderColor} ${config.bgColor}
        ${isAnomalyDetected ? 'cyber-pulse' : ''}
      `}>
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
            isAnomalyDetected ? 'bg-red-500/20 border border-red-400/40' : 'bg-green-500/20 border border-green-400/40'
          }`}>
            {isAnomalyDetected ? (
              <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-4 mb-2">
              <p className={`font-bold text-xl ${config.textColor} font-mono tracking-wide`}>
                {anomalyStatus}
              </p>
              {tier2InProgress && (
                <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/20 border border-blue-400/40 rounded-lg">
                  <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
                  <span className="text-blue-400 text-sm font-mono font-semibold">TIER 2 AI ANALYSIS</span>
                </div>
              )}
            </div>
            <div className={`text-sm ${config.textColor} opacity-80 leading-relaxed font-mono whitespace-pre-line`}>
              {currentDetails}
            </div>
          </div>
        </div>
      </div>

      {/* Video Container */}
      <div className="grid lg:grid-cols-2 gap-8">
        <div className="relative">
          <div className="cyber-panel p-6">
            <h3 className="cyber-subtitle text-xl mb-6 flex items-center gap-3">
              <div className="w-2 h-2 bg-cyan-400 rounded-full cyber-pulse"></div>
              VIDEO STREAM
            </h3>
            <div className="video-container bg-black/90 rounded-xl overflow-hidden relative border border-cyan-400/20 cyber-grid-bg">
              {videoError ? (
                <div className="aspect-video flex items-center justify-center bg-gray-900/80">
                  <div className="text-center p-8">
                    <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <p className="text-xl mb-2 font-bold font-mono text-red-400">VIDEO STREAM UNAVAILABLE</p>
                    <p className="text-gray-400 mb-4 font-mono text-sm">Connection to video source lost</p>
                    <button 
                      onClick={() => {
                        setVideoError(false);
                        setVideoKey(Date.now());
                      }}
                      className="cyber-btn-primary px-6 py-3 rounded-xl font-mono font-bold tracking-wider uppercase"
                    >
                      RETRY CONNECTION
                    </button>
                  </div>
                </div>
              ) : (
                <div className="relative">
                  {/* Use WebSocket video frame when available, otherwise fallback to MJPEG stream */}
                  {useWebSocketStream && videoFrame ? (
                    <img
                      src={`data:image/jpeg;base64,${videoFrame}`}
                      alt="Live Video Stream (WebSocket)"
                      className="w-full h-auto max-h-96 object-contain transition-all duration-300 border-4 rounded-xl"
                      style={{
                        borderColor: isAnomalyDetected ? '#ef4444' : '#00d4aa',
                        boxShadow: isAnomalyDetected ? '0 0 30px rgba(239, 68, 68, 0.5)' : '0 0 20px rgba(0, 212, 170, 0.3)'
                      }}
                    />
                  ) : !useWebSocketStream ? (
                    <img
                      key={videoKey}
                      src={`http://127.0.0.1:8000/video_stream?t=${videoKey}`}
                      alt="Live Video Stream (MJPEG)"
                      className="w-full h-auto max-h-96 object-contain transition-all duration-500 border-4 rounded-xl"
                      onError={handleVideoError}
                      onLoad={handleVideoLoad}
                      style={{
                        borderColor: isAnomalyDetected ? '#ef4444' : '#00d4aa',
                        boxShadow: isAnomalyDetected ? '0 0 30px rgba(239, 68, 68, 0.5)' : '0 0 20px rgba(0, 212, 170, 0.3)'
                      }}
                    />
                  ) : (
                    <div className="aspect-video flex items-center justify-center bg-gray-900/80 border-4 rounded-xl" 
                         style={{borderColor: '#00d4aa'}}>
                      <div className="text-center p-8">
                        <svg className="w-12 h-12 text-cyan-400 mx-auto mb-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <p className="text-cyan-400 font-mono text-sm">Waiting for video stream...</p>
                      </div>
                    </div>
                  )}
                  
                  {/* Anomaly Status Overlay */}
                  {isAnomalyDetected && (
                    <div className="absolute top-4 left-4 bg-red-600/90 text-white px-4 py-2 rounded-lg font-bold font-mono text-sm cyber-pulse border border-red-400">
                      ⚠️ ANOMALY DETECTED
                    </div>
                  )}
                  
                  {/* Connection Status Overlay */}
                  <div className="absolute top-4 right-4 flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full cyber-pulse ${
                      isConnected ? 'bg-green-400' : 'bg-gray-400'
                    }`}></div>
                    <span className={`text-xs font-mono font-bold ${
                      isConnected ? 'text-green-400' : 'text-gray-400'
                    }`}>
                      {isConnected ? 'LIVE' : 'OFFLINE'}
                    </span>
                  </div>
                </div>
              )}
              
              {/* Stream indicator */}
              <div className="absolute top-4 right-4">
                <div className={`
                  px-3 py-2 rounded-xl text-xs font-bold font-mono tracking-wider uppercase border backdrop-blur-md
                  ${isConnected ? 'bg-red-500/20 text-red-400 border-red-400/40 cyber-pulse' : 'bg-gray-500/20 text-gray-400 border-gray-500/40'}
                `}>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-red-400 animate-pulse' : 'bg-gray-400'}`}></div>
                    {isConnected ? 'LIVE' : 'OFFLINE'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Analysis */}
        <div className="space-y-6">
          {/* Real-time Stats */}
          <div className="cyber-panel p-6">
            <h3 className="cyber-subtitle text-xl mb-6">SYSTEM METRICS</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-300 font-mono text-sm">Frame Rate</span>
                <span className="text-cyan-400 font-mono font-bold">30 FPS</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300 font-mono text-sm">Resolution</span>
                <span className="text-cyan-400 font-mono font-bold">1920x1080</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300 font-mono text-sm">Latency</span>
                <span className="text-green-400 font-mono font-bold">45ms</span>
              </div>
              <div className="h-px bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent"></div>
              <div className="flex justify-between items-center">
                <span className="text-gray-300 font-mono text-sm">Quality</span>
                <span className="text-teal-400 font-mono font-bold">Adaptive HD</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    ) : (
      <div className="aspect-video bg-gray-900/50 rounded-xl flex items-center justify-center border-2 border-dashed border-cyan-400/30 cyber-grid-bg">
        <div className="text-center p-8">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <p className="text-xl font-bold mb-2 font-mono text-gray-300">VIDEO STREAM HIDDEN</p>
          <p className="text-sm text-gray-400 font-mono">Use controls to show live stream</p>
        </div>
      </div>
    </div>
    ) : null
  );
};

export default LiveFeed;
