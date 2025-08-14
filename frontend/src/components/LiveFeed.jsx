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
      rounded-lg p-6 border-2 transition-all duration-300 shadow-lg
      ${isAnomalyDetected ? 'border-red-500 bg-red-50 animate-pulse' : 'border-green-500 bg-white'}
    `}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          📹 Live Video Stream
        </h2>
        <div className={`
          px-3 py-1 rounded-full text-sm font-medium
          ${isConnected ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}
        `}>
          {isConnected ? '🟢 Connected' : '⭕ Disconnected'}
        </div>
      </div>

      {/* Status Display */}
      <div className={`
        p-4 rounded-lg mb-4 border-l-4 ${config.borderColor} ${config.bgColor}
        transition-all duration-300
      `}>
        <div className="flex items-center gap-3">
          <span className="text-2xl">{config.icon}</span>
          <div>
            <p className={`font-bold text-lg ${config.textColor}`}>
              Status: {anomalyStatus}
            </p>
            <p className={`text-sm ${config.textColor} opacity-80`}>
              {currentDetails}
            </p>
          </div>
        </div>
      </div>

      {/* Video Stream */}
      {showVideoStream ? (
        <div className="video-container bg-black rounded-lg overflow-hidden relative">
          {videoError ? (
            <div className="aspect-video flex items-center justify-center bg-gray-800 text-white">
              <div className="text-center">
                <p className="text-xl mb-2">📷</p>
                <p>Video stream unavailable</p>
                <button 
                  onClick={() => {
                    setVideoError(false);
                    setVideoKey(Date.now());
                  }}
                  className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : (
            <img
              key={videoKey}
              src={`/video_stream?t=${videoKey}`}
              alt="Live Video Stream"
              className={`
                w-full h-auto max-h-96 object-contain transition-all duration-300
                ${isAnomalyDetected ? 'anomaly-border' : 'normal-border'}
                border-4 rounded-lg
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
                
                borderColor: isAnomalyDetected ? '#ff4444' : '#22c55e',
                boxShadow: isAnomalyDetected ? '0 0 20px rgba(255, 68, 68, 0.5)' : 'none'
              }}
            />
          )}
          
          {/* Stream indicator */}
          <div className="absolute top-4 right-4">
            <div className={`
              px-2 py-1 rounded text-xs font-medium
              ${isConnected ? 'bg-red-600 text-white' : 'bg-gray-600 text-white'}
            `}>
              {isConnected ? '🔴 LIVE' : '⭕ OFFLINE'}
            </div>
          </div>
        </div>
      ) : (
        <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300">
          <div className="text-center text-gray-500">
            <p className="text-4xl mb-2">📷</p>
            <p className="text-lg">Video stream hidden</p>
            <p className="text-sm">Use controls to show stream</p>
          </div>
        </div>
      )}

      {/* Stream Info */}
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="bg-gray-50 p-3 rounded">
          <p className="font-medium text-gray-700">Stream Type</p>
          <p className="text-gray-600">MJPEG Stream</p>
          <p className="text-xs text-gray-500 mt-1">
            {/* WebRTC ready - upgrade path available */}
            Ready for WebRTC upgrade
          </p>
        </div>
        <div className="bg-gray-50 p-3 rounded">
          <p className="font-medium text-gray-700">Resolution</p>
          <p className="text-gray-600">Auto</p>
          <p className="text-xs text-gray-500 mt-1">
            Adaptive quality
          </p>
        </div>
      </div>
    </div>
  );
};

export default LiveFeed;
