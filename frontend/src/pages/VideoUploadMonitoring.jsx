import React, { useState } from 'react';
import VideoPlayback from '../components/VideoPlayback';
import AnomalyList from '../components/AnomalyList';
import JsonOutput from '../components/JsonOutput';

const VideoUploadMonitoring = ({ 
  user, 
  onLogout, 
  onBackToSelector,
  onVideoUpload,
  ws,
  isConnected,
  anomalyStatus,
  currentDetails,
  anomalies,
  jsonData,
  showJsonPanel,
  currentVideoFile,
  onToggleJson,
  onDisconnect,
  onDownloadData 
}) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    setIsUploading(true);
    setUploadProgress(0);
    
    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsUploading(false);
          
          // Use setTimeout to avoid setState during render cycle
          setTimeout(() => {
            onVideoUpload(selectedFile);
          }, 0);
          
          return 100;
        }
        return prev + 10;
      });
    }, 300);
  };

  const isVideoSupported = (file) => {
    const supportedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/webm'];
    return supportedTypes.includes(file?.type);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black cyber-grid-bg">
      <div className="container mx-auto px-6 py-8">
        
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
            <div>
              <h1 className="text-3xl font-bold text-cyan-400 font-mono">VIDEO UPLOAD ANALYSIS</h1>
              <p className="text-gray-400 font-mono mt-2">Upload and analyze video files for anomaly detection</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className={`w-4 h-4 rounded-full cyber-pulse ${
                isConnected ? 'bg-green-400' : selectedFile ? 'bg-yellow-400' : 'bg-gray-400'
              }`}></div>
              <span className={`font-semibold text-cyber-glow font-mono uppercase tracking-wider ${
                isConnected ? 'text-green-400' : selectedFile ? 'text-yellow-400' : 'text-gray-400'
              }`}>
                {isConnected ? 'PROCESSING VIDEO' : selectedFile ? 'VIDEO READY' : 'NO VIDEO SELECTED'}
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

        {/* Upload Section */}
        <div className="mb-8">
          <div className="cyber-card p-8">
            <h2 className="cyber-title text-xl mb-6">VIDEO UPLOAD</h2>
            
            {!selectedFile ? (
              <div className="border-2 border-dashed border-gray-600 rounded-xl p-12 text-center">
                <div className="mb-6">
                  <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <h3 className="text-xl font-bold text-gray-300 font-mono mb-2">UPLOAD VIDEO FILE</h3>
                  <p className="text-gray-400 font-mono">Select a video file to analyze for anomalies</p>
                </div>
                
                <div className="mb-6">
                  <input
                    type="file"
                    id="video-upload"
                    accept="video/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <label
                    htmlFor="video-upload"
                    className="cyber-btn cyber-btn-primary inline-flex items-center gap-3 cursor-pointer"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    SELECT VIDEO FILE
                  </label>
                </div>
                
                <p className="text-sm text-gray-500 font-mono">
                  Supported formats: MP4, AVI, MOV, WMV, WebM
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* File Info */}
                <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-cyan-500/20 border border-cyan-400/30 rounded-xl flex items-center justify-center">
                        <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-bold text-white font-mono">{selectedFile.name}</h3>
                        <div className="flex items-center gap-4 text-sm text-gray-400 font-mono">
                          <span>Size: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
                          <span>Type: {selectedFile.type}</span>
                          <span className={`${isVideoSupported(selectedFile) ? 'text-green-400' : 'text-red-400'}`}>
                            {isVideoSupported(selectedFile) ? '✓ Supported' : '✗ Unsupported'}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <button
                        onClick={() => setSelectedFile(null)}
                        className="cyber-btn cyber-btn-secondary text-sm"
                      >
                        CHANGE FILE
                      </button>
                      <button
                        onClick={handleUpload}
                        disabled={!isVideoSupported(selectedFile) || isUploading}
                        className="cyber-btn cyber-btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isUploading ? 'UPLOADING...' : 'START ANALYSIS'}
                      </button>
                    </div>
                  </div>
                  
                  {/* Upload Progress */}
                  {isUploading && (
                    <div className="mt-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-mono text-gray-400">Upload Progress</span>
                        <span className="text-sm font-mono text-cyan-400">{uploadProgress}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-cyan-400 h-2 rounded-full transition-all duration-300 cyber-glow"
                          style={{ width: `${uploadProgress}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Processing Status */}
        {isConnected && (
          <div className="mb-8">
            <div className="bg-green-500/10 border-2 border-green-400/30 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-2xl text-green-400">🔍</div>
                  <div>
                    <h3 className="font-bold font-mono text-green-400">VIDEO PROCESSING ACTIVE</h3>
                    <p className="text-gray-300 font-mono text-sm">{currentDetails}</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={onToggleJson}
                    className="cyber-btn cyber-btn-secondary text-sm"
                  >
                    {showJsonPanel ? 'HIDE DATA' : 'SHOW DATA'}
                  </button>
                  <button
                    onClick={onDisconnect}
                    className="cyber-btn cyber-btn-danger text-sm"
                  >
                    STOP PROCESSING
                  </button>
                  <button
                    onClick={onDownloadData}
                    className="cyber-btn cyber-btn-purple text-sm"
                  >
                    DOWNLOAD RESULTS
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Video Playback - Takes 2 columns */}
          <div className="lg:col-span-2">
            <div className="cyber-card p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="cyber-title text-xl">VIDEO ANALYSIS</h2>
                <div className="flex items-center gap-3">
                  <div className={`text-sm font-mono px-3 py-1 rounded ${
                    anomalyStatus === 'Anomaly Detected' 
                      ? 'bg-red-500/20 text-red-400 border border-red-400/30' 
                      : 'bg-gray-500/20 text-gray-400 border border-gray-400/30'
                  }`}>
                    {anomalyStatus.toUpperCase()}
                  </div>
                </div>
              </div>
              
              {currentVideoFile ? (
                <VideoPlayback 
                  currentVideoFile={currentVideoFile}
                  onLoadLatest={() => {
                    // For video uploads, return the current video file
                    return currentVideoFile;
                  }}
                  onJumpToAnomaly={() => {
                    // Find the latest anomaly and return jump data
                    if (anomalies && anomalies.length > 0) {
                      const lastAnomaly = anomalies[anomalies.length - 1];
                      return {
                        videoFile: currentVideoFile,
                        timestamp: lastAnomaly.timestamp || 0
                      };
                    }
                    return null;
                  }}
                />
              ) : (
                <div className="aspect-video bg-gray-800/50 border border-gray-700/50 rounded-xl flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-4xl text-gray-500 mb-4">📹</div>
                    <p className="text-gray-400 font-mono">No video selected for analysis</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Data Panel */}
          <div className="space-y-6">
            {showJsonPanel && (
              <div className="cyber-card p-6">
                <h3 className="cyber-title text-lg mb-4">ANALYSIS DATA</h3>
                <JsonOutput 
                  jsonData={jsonData}
                  isVisible={showJsonPanel}
                />
              </div>
            )}
          </div>
        </div>

        {/* Analysis Results */}
        <div className="mt-8">
          <div className="cyber-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="cyber-title text-xl">DETECTED ANOMALIES</h2>
              <div className="text-sm font-mono text-gray-400">
                Total Detected: {anomalies.length}
              </div>
            </div>
            <AnomalyList anomalies={anomalies} />
          </div>
        </div>

      </div>
    </div>
  );
};

export default VideoUploadMonitoring;
