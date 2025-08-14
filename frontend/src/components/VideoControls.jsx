import React from 'react';

const VideoControls = ({
  isConnected,
  onConnect,
  onDisconnect,
  onToggleStream,
  onToggleJson,
  onRefreshAnomalies,
  showVideoStream,
  showJsonPanel
}) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      {/* Header */}
      <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        🎛️ System Controls
      </h2>

      {/* Main Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        
        {/* Connection Controls */}
        <div className="space-y-2">
          <h3 className="font-medium text-gray-700 text-sm uppercase tracking-wide">
            Monitoring
          </h3>
          <div className="space-y-2">
            <button
              onClick={onConnect}
              disabled={isConnected}
              className={`
                w-full px-4 py-2 rounded-md font-medium transition-all duration-200
                ${isConnected 
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                  : 'bg-green-600 text-white hover:bg-green-700 hover:scale-105 shadow-md'
                }
              `}
            >
              {isConnected ? '✅ Connected' : '🟢 Start Monitoring'}
            </button>
            
            <button
              onClick={onDisconnect}
              disabled={!isConnected}
              className={`
                w-full px-4 py-2 rounded-md font-medium transition-all duration-200
                ${!isConnected 
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                  : 'bg-red-600 text-white hover:bg-red-700 hover:scale-105 shadow-md'
                }
              `}
            >
              {!isConnected ? '⭕ Disconnected' : '🔴 Stop Monitoring'}
            </button>
          </div>
        </div>

        {/* Display Controls */}
        <div className="space-y-2">
          <h3 className="font-medium text-gray-700 text-sm uppercase tracking-wide">
            Display
          </h3>
          <div className="space-y-2">
            <button
              onClick={onToggleStream}
              className={`
                w-full px-4 py-2 rounded-md font-medium transition-all duration-200
                ${showVideoStream 
                  ? 'bg-blue-600 text-white hover:bg-blue-700' 
                  : 'bg-gray-600 text-white hover:bg-gray-700'
                } hover:scale-105 shadow-md
              `}
            >
              {showVideoStream ? '📹 Hide Stream' : '📷 Show Stream'}
            </button>
            
            <button
              onClick={onToggleJson}
              className={`
                w-full px-4 py-2 rounded-md font-medium transition-all duration-200
                ${showJsonPanel 
                  ? 'bg-purple-600 text-white hover:bg-purple-700' 
                  : 'bg-gray-600 text-white hover:bg-gray-700'
                } hover:scale-105 shadow-md
              `}
            >
              {showJsonPanel ? '📊 Hide JSON' : '📈 Show JSON'}
            </button>
          </div>
        </div>

        {/* Data Controls */}
        <div className="space-y-2">
          <h3 className="font-medium text-gray-700 text-sm uppercase tracking-wide">
            Data
          </h3>
          <div className="space-y-2">
            <button
              onClick={onRefreshAnomalies}
              className="w-full px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-all duration-200 font-medium hover:scale-105 shadow-md"
            >
              🔄 Refresh Anomalies
            </button>
            
            <button
              onClick={() => window.location.reload()}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-all duration-200 font-medium hover:scale-105 shadow-md"
            >
              ⟳ Reload Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`}></div>
              <span className="text-sm font-medium text-gray-700">
                WebSocket: {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            <div className="text-sm text-gray-500 hidden md:block">
              |
            </div>
            
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span>Stream: {showVideoStream ? 'Visible' : 'Hidden'}</span>
              <span>•</span>
              <span>JSON: {showJsonPanel ? 'Visible' : 'Hidden'}</span>
            </div>
          </div>

          <div className="text-xs text-gray-400 hidden lg:block">
            Backend: localhost:8000
          </div>
        </div>
      </div>

      {/* Quick Tips */}
      <div className="mt-4 p-3 bg-blue-50 rounded-md">
        <div className="text-sm text-blue-800">
          <p className="font-medium mb-1">💡 Quick Tips:</p>
          <ul className="text-xs space-y-1 text-blue-700">
            <li>• Start monitoring to begin real-time anomaly detection</li>
            <li>• Toggle stream display to save bandwidth</li>
            <li>• Use JSON panel to see detailed detection data</li>
            <li>• Auto-refresh keeps anomaly list updated every 5 seconds</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VideoControls;
