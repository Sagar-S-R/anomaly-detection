import React from 'react';
import LiveFeed from '../components/LiveFeed';
import AnomalyList from '../components/AnomalyList';
import JsonOutput from '../components/JsonOutput';
import VideoControls from '../components/VideoControls';

const LiveCameraMonitoring = ({ 
  user, 
  onLogout, 
  onBackToSelector,
  onConnect,
  ws,
  isConnected,
  anomalyStatus,
  currentDetails,
  anomalies,
  jsonData,
  showJsonPanel,
  onToggleJson,
  onDisconnect,
  onDownloadData 
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black cyber-grid-bg">
      <div className="container mx-auto px-6 py-8 max-w-7xl">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-6">
            <button
              onClick={onBackToSelector}
              className="cyber-btn cyber-btn-secondary flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              BACK TO SOURCES
            </button>
            <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-teal-400 rounded-xl flex items-center justify-center text-black text-2xl font-bold shadow-lg cyber-glow border border-cyan-400">
              <span className="font-mono">📹</span>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-cyan-400 font-mono">LIVE CAMERA MONITORING</h1>
              <p className="text-gray-400 font-mono mt-2">Real-time camera feed with AI anomaly detection</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className={`w-4 h-4 rounded-full cyber-pulse ${isConnected ? 'bg-green-400' : 'bg-gray-400'}`}></div>
              <span className={`font-semibold text-cyber-glow font-mono uppercase tracking-wider ${
                isConnected ? 'text-green-400' : 'text-gray-400'
              }`}>
                {isConnected ? 'LIVE MONITORING' : 'DISCONNECTED'}
              </span>
            </div>
            <button
              onClick={onLogout}
              className="cyber-btn cyber-btn-danger"
            >
              LOGOUT
            </button>
          </div>
        </div>

        {/* Control Panel */}
        <div className="mb-8">
          <VideoControls
            isConnected={isConnected}
            onConnect={onConnect}
            onDisconnect={onDisconnect}
            onToggleJson={onToggleJson}
            onDownloadData={onDownloadData}
            showJsonPanel={showJsonPanel}
            inputMode="live"
          />
        </div>

        {/* Main Content Grid - Proper Layout */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8 mb-8">
          
          {/* Main Video Feed - Takes 3 columns */}
          <div className="xl:col-span-3">
            <div className="cyber-card p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="cyber-title text-2xl">LIVE VIDEO STREAM</h2>
                <div className="flex items-center gap-3">
                  <div className={`text-sm font-mono px-4 py-2 rounded ${
                    anomalyStatus === 'Anomaly Detected' 
                      ? 'bg-red-500/20 text-red-400 border border-red-400/30' 
                      : 'bg-green-500/20 text-green-400 border border-green-400/30'
                  }`}>
                    {anomalyStatus.toUpperCase()}
                  </div>
                </div>
              </div>
              
              {/* Video Stream Component */}
              <div className="bg-black rounded-xl overflow-hidden border border-cyan-400/20">
                <LiveFeed
                  anomalyStatus={anomalyStatus}
                  currentDetails={currentDetails}
                  isConnected={isConnected}
                  showVideoStream={true}
                />
              </div>
            </div>
          </div>

          {/* Side Panel - Takes 1 column */}
          <div className="space-y-6">
            
            {/* System Status */}
            <div className="cyber-card p-6">
              <h3 className="cyber-title text-lg mb-4">SYSTEM STATUS</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300 font-mono text-sm">Connection</span>
                  <span className={`font-mono font-bold ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                    {isConnected ? 'ACTIVE' : 'OFFLINE'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300 font-mono text-sm">Anomalies</span>
                  <span className="text-cyan-400 font-mono font-bold">{anomalies.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300 font-mono text-sm">Status</span>
                  <span className={`font-mono font-bold text-xs ${
                    anomalyStatus === 'Anomaly Detected' ? 'text-red-400' : 'text-green-400'
                  }`}>
                    {anomalyStatus === 'Anomaly Detected' ? 'ALERT' : 'NORMAL'}
                  </span>
                </div>
              </div>
              
              {/* Current Details */}
              <div className="mt-6 p-3 bg-gray-800/50 rounded-lg border border-gray-700/50">
                <h4 className="text-xs font-mono text-gray-400 mb-2">CURRENT ACTIVITY:</h4>
                <p className="text-cyan-400 font-mono text-sm">{currentDetails}</p>
              </div>
            </div>

            {/* JSON Data Panel */}
            {showJsonPanel && (
              <div className="cyber-card p-6">
                <h3 className="cyber-title text-lg mb-4">LIVE DATA</h3>
                <div className="max-h-80 overflow-y-auto">
                  <JsonOutput 
                    jsonData={jsonData}
                    isVisible={showJsonPanel}
                  />
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="cyber-card p-6">
              <h3 className="cyber-title text-lg mb-4">QUICK ACTIONS</h3>
              <div className="space-y-3">
                <button
                  onClick={onToggleJson}
                  className="cyber-btn cyber-btn-secondary w-full text-sm"
                >
                  {showJsonPanel ? 'HIDE DATA' : 'SHOW DATA'}
                </button>
                <button
                  onClick={onDownloadData}
                  className="cyber-btn cyber-btn-purple w-full text-sm"
                >
                  DOWNLOAD RESULTS
                </button>
                <button
                  onClick={onDisconnect}
                  className="cyber-btn cyber-btn-danger w-full text-sm"
                  disabled={!isConnected}
                >
                  STOP MONITORING
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Anomaly Detection Results - Full Width */}
        <div className="cyber-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="cyber-title text-2xl">DETECTED ANOMALIES</h2>
            <div className="text-sm font-mono text-gray-400">
              Total Detected: <span className="text-cyan-400 font-bold">{anomalies.length}</span>
            </div>
          </div>
          
          <AnomalyList 
            anomalies={anomalies}
            onJumpToAnomaly={() => {}} // Add jump functionality if needed
            onRefresh={() => {}} // Add refresh functionality if needed
          />
        </div>

      </div>
    </div>
  );
};

export default LiveCameraMonitoring;
