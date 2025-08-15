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
    <div className="card-modern p-8 mb-8 reveal-up">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center">
          <svg className="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
          </svg>
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-900">System Controls</h2>
          <p className="text-slate-500 text-sm">Manage monitoring and display settings</p>
        </div>
      </div>

      {/* Main Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Connection Controls */}
        <div className="space-y-4">
          <div className="flex items-center gap-3 mb-4">
            <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="font-semibold text-slate-800 text-lg">Monitoring</h3>
          </div>
          <div className="space-y-3">
            <button
              onClick={onConnect}
              disabled={isConnected}
              className={`
                btn-modern w-full px-6 py-4 rounded-xl font-semibold transition-all duration-300 shadow-professional
                ${isConnected 
                  ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
                  : 'bg-emerald-600 text-white hover:bg-emerald-700 hover:shadow-lg transform hover:-translate-y-0.5'
                }
              `}
            >
              <div className="flex items-center justify-center gap-3">
                {isConnected ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                )}
                {isConnected ? 'Connected' : 'Start Monitoring'}
              </div>
            </button>
            
            <button
              onClick={onDisconnect}
              disabled={!isConnected}
              className={`
                btn-modern w-full px-6 py-4 rounded-xl font-semibold transition-all duration-300 shadow-professional
                ${!isConnected 
                  ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
                  : 'bg-red-500 text-white hover:bg-red-600 hover:shadow-lg transform hover:-translate-y-0.5'
                }
              `}
            >
              <div className="flex items-center justify-center gap-3">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 9l6 6m0-6l-6 6" />
                </svg>
                {!isConnected ? 'Disconnected' : 'Stop Monitoring'}
              </div>
            </button>
          </div>
        </div>

        {/* Display Controls */}
        <div className="space-y-4">
          <div className="flex items-center gap-3 mb-4">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <h3 className="font-semibold text-slate-800 text-lg">Display</h3>
          </div>
          <div className="space-y-3">
            <button
              onClick={onToggleStream}
              className={`
                btn-modern w-full px-6 py-4 rounded-xl font-semibold transition-all duration-300 shadow-professional
                ${showVideoStream 
                  ? 'bg-blue-600 text-white hover:bg-blue-700' 
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                } hover:shadow-lg transform hover:-translate-y-0.5
              `}
            >
              <div className="flex items-center justify-center gap-3">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                {showVideoStream ? 'Hide Stream' : 'Show Stream'}
              </div>
            </button>
            
            <button
              onClick={onToggleJson}
              className={`
                btn-modern w-full px-6 py-4 rounded-xl font-semibold transition-all duration-300 shadow-professional
                ${showJsonPanel 
                  ? 'bg-purple-600 text-white hover:bg-purple-700' 
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                } hover:shadow-lg transform hover:-translate-y-0.5
              `}
            >
              <div className="flex items-center justify-center gap-3">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                {showJsonPanel ? 'Hide Data' : 'Show Data'}
              </div>
            </button>
          </div>
        </div>

        {/* Data Controls */}
        <div className="space-y-4">
          <div className="flex items-center gap-3 mb-4">
            <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
            <h3 className="font-semibold text-slate-800 text-lg">Data</h3>
          </div>
          <div className="space-y-3">
            <button
              onClick={onRefreshAnomalies}
              className="btn-modern w-full px-6 py-4 bg-orange-500 text-white rounded-xl hover:bg-orange-600 transition-all duration-300 font-semibold shadow-professional hover:shadow-lg transform hover:-translate-y-0.5"
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
              className="btn-modern w-full px-6 py-4 bg-slate-600 text-white rounded-xl hover:bg-slate-700 transition-all duration-300 font-semibold shadow-professional hover:shadow-lg transform hover:-translate-y-0.5"
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
      <div className="mt-8 pt-6 border-t border-slate-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full status-indicator ${
                isConnected ? 'bg-emerald-500' : 'bg-red-500'
              }`}></div>
              <span className="text-sm font-medium text-slate-700">
                WebSocket: {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            <div className="hidden md:block w-px h-4 bg-slate-300"></div>
            
            <div className="flex items-center gap-4 text-sm text-slate-500">
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

          <div className="text-xs text-slate-400 hidden lg:block font-mono">
            Backend: localhost:8000
          </div>
        </div>
      </div>

      {/* Quick Tips */}
      <div className="mt-6 p-6 bg-blue-50 rounded-xl border border-blue-200">
        <div className="flex items-start gap-4">
          <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p className="font-semibold text-blue-900 mb-3">Quick Tips</p>
            <ul className="text-sm space-y-2 text-blue-800">
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                <span>Start monitoring to begin real-time anomaly detection</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                <span>Toggle stream display to save bandwidth when needed</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                <span>Use data panel to see detailed detection information</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
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
