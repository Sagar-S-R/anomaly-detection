import React from 'react';

const VideoControls = ({
  isConnected,
  onConnect,
  onDisconnect,
  onToggleStream,
  onToggleJson,
  onRefreshAnomalies,
  showVideoStream,
  showJsonPanel,
  inputMode
}) => {
  return (
    <div className="cyber-card p-8 mb-8 reveal-up">
      {/* Header */}
      <div className="flex items-center gap-6 mb-8">
        <div className="w-16 h-16 bg-gradient-to-br from-cyan-400/20 to-teal-400/20 rounded-2xl flex items-center justify-center border border-cyan-400/30">
          <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
          </svg>
        </div>
        <div>
          <h2 className="cyber-title text-3xl">SYSTEM CONTROLS</h2>
          <p className="cyber-subtitle text-lg">Manage monitoring and display settings</p>
        </div>
      </div>

      {/* Main Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* Connection Controls */}
        <div className="space-y-6">
          <div className="flex items-center gap-3 mb-6">
            <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-xl font-bold text-green-400 font-mono uppercase tracking-wider">
              {inputMode === 'live' && 'LIVE CAMERA'}
              {inputMode === 'cctv' && 'CCTV STREAM'}
              {inputMode === 'upload' && 'VIDEO PROCESSING'}
              {inputMode === 'none' && 'MONITORING'}
            </h3>
          </div>
          <div className="space-y-4">
            {isConnected && (
              <div className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-green-900/30 to-green-800/20 border border-green-400/40 rounded-xl">
                <div className="w-4 h-4 bg-green-400 rounded-full cyber-pulse"></div>
                <span className="text-green-400 font-semibold font-mono text-sm tracking-wider">
                  {inputMode === 'live' && 'CAMERA ACTIVE'}
                  {inputMode === 'cctv' && 'CCTV CONNECTED'}
                  {inputMode === 'upload' && 'PROCESSING VIDEO'}
                </span>
              </div>
            )}
            
            {!isConnected && (
              <button
                onClick={onConnect}
                className="cyber-btn-primary w-full"
              >
                {inputMode === 'live' && 'START LIVE CAMERA'}
                {inputMode === 'cctv' && 'CONNECT TO CCTV'}
                {inputMode === 'upload' && 'START PROCESSING'}
                {!inputMode && 'START MONITORING'}
              </button>
            )}
            
            {isConnected && (
              <button
                onClick={onDisconnect}
                className="cyber-btn cyber-btn-red w-full"
              >
                {inputMode === 'live' && 'STOP CAMERA'}
                {inputMode === 'cctv' && 'DISCONNECT CCTV'}
                {inputMode === 'upload' && 'STOP PROCESSING'}
                {!inputMode && 'STOP MONITORING'}
              </button>
            )}
          </div>
        </div>

        {/* Display Controls */}
        <div className="space-y-6">
          <div className="flex items-center gap-3 mb-6">
            <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <h3 className="text-xl font-bold text-cyan-400 font-mono uppercase tracking-wider">DISPLAY</h3>
          </div>
          <div className="space-y-4">
            <button
              onClick={onToggleStream}
              className={`cyber-btn w-full ${
                showVideoStream ? '' : 'border-gray-600 text-gray-400'
              }`}
            >
              {showVideoStream ? 'HIDE VIDEO' : 'SHOW VIDEO'}
            </button>
            
            <button
              onClick={onToggleJson}
              className={`cyber-btn w-full ${
                showJsonPanel ? 'cyber-btn-purple' : 'border-gray-600 text-gray-400'
              }`}
            >
              {showJsonPanel ? 'HIDE DATA' : 'SHOW DATA'}
            </button>
          </div>
        </div>

        {/* Data Controls */}
        <div className="space-y-6">
          <div className="flex items-center gap-3 mb-6">
            <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
            <h3 className="text-xl font-bold text-yellow-400 font-mono uppercase tracking-wider">DATA</h3>
          </div>
          <div className="space-y-4">
            <button
              onClick={onRefreshAnomalies}
              className="cyber-btn w-full border-yellow-400 text-yellow-400 hover:bg-yellow-400"
            >
              REFRESH ANOMALIES
            </button>
            
            <button
              onClick={() => window.location.reload()}
              className="cyber-btn w-full border-gray-500 text-gray-400 hover:bg-gray-500"
            >
              RELOAD DASHBOARD
            </button>
          </div>
        </div>
      </div>

      {/* Cyber Status Bar */}
      <div className="mt-8 pt-6 border-t border-cyan-400/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className={`w-4 h-4 rounded-full ${
                isConnected ? 'bg-green-400 cyber-pulse' : 'bg-red-400'
              }`}></div>
              <span className="text-sm font-mono text-cyan-300 uppercase tracking-wider">
                WebSocket: {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
              </span>
            </div>
            
            <div className="hidden md:block w-px h-4 bg-cyan-400/30"></div>
            
            <div className="flex items-center gap-4 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span className="font-mono">Stream: {showVideoStream ? 'ON' : 'OFF'}</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span className="font-mono">Data: {showJsonPanel ? 'ON' : 'OFF'}</span>
              </div>
            </div>
          </div>

          <div className="text-xs text-cyan-400/70 hidden lg:block font-mono">
            Backend: localhost:8000
          </div>
        </div>
      </div>

      {/* Cyber Tips Panel */}
      <div className="mt-6 cyber-card bg-gradient-to-r from-blue-900/20 to-purple-900/20 border-blue-400/30">
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-xl flex items-center justify-center flex-shrink-0 border border-blue-400/30">
              <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="font-bold text-blue-400 mb-3 font-mono uppercase tracking-wider">System Tips</p>
              <ul className="text-sm space-y-2 text-gray-300">
                <li className="flex items-start gap-3">
                  <span className="w-2 h-2 bg-cyan-400 rounded-full mt-2 flex-shrink-0"></span>
                  <span>Select input source to begin real-time anomaly detection</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-2 h-2 bg-cyan-400 rounded-full mt-2 flex-shrink-0"></span>
                  <span>Toggle stream display to optimize system performance</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-2 h-2 bg-cyan-400 rounded-full mt-2 flex-shrink-0"></span>
                  <span>Use data panel for detailed detection analytics</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-2 h-2 bg-cyan-400 rounded-full mt-2 flex-shrink-0"></span>
                  <span>Auto-refresh maintains real-time anomaly updates</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Data Controls */}
        <div className="space-y-4">
          <div className="flex items-center gap-3 mb-4">
            <svg className="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
            <h3 className="cyber-subtitle text-lg">DATA OPERATIONS</h3>
          </div>
          <div className="space-y-3">
            <button
              onClick={onRefreshAnomalies}
              className="cyber-btn-secondary w-full px-6 py-4 rounded-xl transition-all duration-300 font-mono font-bold tracking-wider uppercase"
            >
              <div className="flex items-center justify-center gap-3">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh Anomalies
              </div>
            </button>
            
            <button
              onClick={() => window.location.reload()}
              className="cyber-btn-primary w-full px-6 py-4 rounded-xl transition-all duration-300 font-mono font-bold tracking-wider uppercase"
            >
              <div className="flex items-center justify-center gap-3">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Reload Dashboard
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="mt-8 pt-6 border-t border-cyan-400/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${
                isConnected ? 'bg-emerald-400 cyber-pulse' : 'bg-red-400'
              }`}></div>
              <span className="text-sm font-medium text-gray-300 font-mono">
                WebSocket: {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            <div className="hidden md:block w-px h-4 bg-cyan-400/30"></div>
            
            <div className="flex items-center gap-4 text-sm text-gray-400 font-mono">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span>Stream: {showVideoStream ? 'Visible' : 'Hidden'}</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span>Data: {showJsonPanel ? 'Visible' : 'Hidden'}</span>
              </div>
            </div>
          </div>

          <div className="text-xs text-cyan-400/70 hidden lg:block font-mono">
            Backend: localhost:8000
          </div>
        </div>
      </div>

      {/* Quick Tips */}
      <div className="mt-6 cyber-panel p-6">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 bg-gradient-to-br from-cyan-400/20 to-teal-400/20 rounded-xl flex items-center justify-center flex-shrink-0 mt-1 border border-cyan-400/30">
            <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p className="cyber-subtitle text-lg mb-4">SYSTEM TIPS</p>
            <ul className="text-sm space-y-3 text-gray-300 font-mono">
              <li className="flex items-start gap-3">
                <span className="w-2 h-2 bg-cyan-400 rounded-full mt-2 flex-shrink-0 cyber-pulse"></span>
                <span>Start monitoring to begin real-time anomaly detection</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-2 h-2 bg-cyan-400 rounded-full mt-2 flex-shrink-0 cyber-pulse"></span>
                <span>Toggle stream display to save bandwidth when needed</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-2 h-2 bg-cyan-400 rounded-full mt-2 flex-shrink-0 cyber-pulse"></span>
                <span>Use data panel to see detailed detection information</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-2 h-2 bg-cyan-400 rounded-full mt-2 flex-shrink-0 cyber-pulse"></span>
                <span>Auto-refresh keeps anomaly list updated every 5 seconds</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoControls;
