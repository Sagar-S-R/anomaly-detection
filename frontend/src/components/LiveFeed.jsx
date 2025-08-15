import React, { useState, useEffect } from 'react';

const LiveFeed = ({ anomalyStatus, currentDetails, isConnected, showVideoStream }) => {
  const [videoError, setVideoError] = useState(false);
  const [videoKey, setVideoKey] = useState(Date.now());

  // Auto-refresh video stream every 30 seconds to prevent stale streams
  useEffect(() => {
    if (!showVideoStream) return;
    
    const interval = setInterval(() => {
      setVideoKey(Date.now());
    }, 30000);

    return () => clearInterval(interval);
  }, [showVideoStream]);

  const isAnomalyDetected = anomalyStatus === 'Anomaly Detected';
  
  const statusConfig = {
    'Normal': {
      bgColor: 'bg-green-100',
      textColor: 'text-green-800',
      borderColor: 'border-green-500',
      icon: '✅'
    },
    'Anomaly Detected': {
      bgColor: 'bg-red-100',
      textColor: 'text-red-800', 
      borderColor: 'border-red-500',
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
    <div className={`
      card-modern p-8 transition-all duration-500 reveal-up
      ${isAnomalyDetected ? 'anomaly-border bg-red-50/50' : 'normal-border bg-white'}
    `}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Live Video Stream</h2>
            <p className="text-slate-500 text-sm">Real-time monitoring feed</p>
          </div>
        </div>
        <div className={`
          px-4 py-2 rounded-full text-sm font-semibold shadow-sm
          ${isConnected ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'}
        `}>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full status-indicator ${
              isConnected ? 'bg-emerald-500' : 'bg-slate-400'
            }`}></div>
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </div>

      {/* Status Display */}
      <div className={`
        p-6 rounded-xl mb-6 border-l-4 shadow-professional
        ${config.borderColor} ${config.bgColor} transition-all duration-500
        ${isAnomalyDetected ? 'anomaly-pulse' : ''}
      `}>
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
            isAnomalyDetected ? 'bg-red-100' : 'bg-emerald-100'
          }`}>
            {isAnomalyDetected ? (
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
          </div>
          <div className="flex-1">
            <p className={`font-bold text-xl ${config.textColor} mb-1`}>
              {anomalyStatus}
            </p>
            <p className={`text-sm ${config.textColor} opacity-80 leading-relaxed`}>
              {currentDetails}
            </p>
          </div>
        </div>
      </div>

      {/* Video Stream */}
      {showVideoStream ? (
        <div className="video-container bg-slate-900 rounded-2xl overflow-hidden relative shadow-professional-lg">
          {videoError ? (
            <div className="aspect-video flex items-center justify-center bg-slate-800 text-white">
              <div className="text-center p-8">
                <svg className="w-16 h-16 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <p className="text-xl mb-2 font-medium">Video stream unavailable</p>
                <p className="text-slate-400 mb-4">Connection to video source lost</p>
                <button 
                  onClick={() => {
                    setVideoError(false);
                    setVideoKey(Date.now());
                  }}
                  className="btn-modern px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all duration-300 font-medium shadow-lg"
                >
                  Retry Connection
                </button>
              </div>
            </div>
          ) : (
            <img
              key={videoKey}
              src={`/video_stream?t=${videoKey}`}
              alt="Live Video Stream"
              className={`
                w-full h-auto max-h-96 object-contain transition-all duration-500
                ${isAnomalyDetected ? 'anomaly-border' : 'normal-border'}
                border-4 rounded-xl
              `}
              onError={handleVideoError}
              onLoad={handleVideoLoad}
              style={{
                // IMPORTANT: This is where MJPEG stream is implemented
                // To replace with WebRTC later, replace this <img> element with:
                // 1. A <video> element with ref for WebRTC stream attachment
                // 2. WebRTC connection logic in useEffect
                // 3. Keep the same CSS classes and container structure
                // 4. The anomaly border logic can remain the same
                
                borderColor: isAnomalyDetected ? '#ef4444' : '#10b981',
                boxShadow: isAnomalyDetected ? '0 0 30px rgba(239, 68, 68, 0.3)' : 'none'
              }}
            />
          )}
          
          {/* Stream indicator */}
          <div className="absolute top-4 right-4">
            <div className={`
              px-3 py-2 rounded-xl text-xs font-bold shadow-lg backdrop-blur-md
              ${isConnected ? 'bg-red-500/90 text-white' : 'bg-slate-600/90 text-white'}
            `}>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-white animate-pulse' : 'bg-slate-300'}`}></div>
                {isConnected ? 'LIVE' : 'OFFLINE'}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="aspect-video bg-slate-100 rounded-2xl flex items-center justify-center border-2 border-dashed border-slate-300 shadow-professional">
          <div className="text-center text-slate-500 p-8">
            <svg className="w-16 h-16 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <p className="text-xl font-medium mb-2">Video stream hidden</p>
            <p className="text-sm text-slate-400">Use controls to show live stream</p>
          </div>
        </div>
      )}

      {/* Stream Info */}
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
          <div className="flex items-center gap-3 mb-2">
            <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="font-semibold text-slate-700">Stream Type</p>
          </div>
          <p className="text-slate-900 font-medium">MJPEG Stream</p>
          <p className="text-xs text-slate-500 mt-1">
            WebRTC upgrade available
          </p>
        </div>
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
          <div className="flex items-center gap-3 mb-2">
            <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="font-semibold text-slate-700">Resolution</p>
          </div>
          <p className="text-slate-900 font-medium">Auto</p>
          <p className="text-xs text-slate-500 mt-1">
            Adaptive quality
          </p>
        </div>
      </div>
    </div>
  );
};

export default LiveFeed;
