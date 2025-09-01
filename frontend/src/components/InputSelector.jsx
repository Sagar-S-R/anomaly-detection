import React, { useState } from 'react';

const InputSelector = ({
  inputMode,
  isConnected,
  onLiveCamera,
  onCCTVConnect,
  onVideoUpload,
  onDisconnect,
  onDownloadData,
  cctvConfig
}) => {
  const [showCCTVForm, setShowCCTVForm] = useState(false);
  const [cctvForm, setCctvForm] = useState({
    ip: '',
    port: 554,
    username: '',
    password: ''
  });

  const handleCCTVSubmit = (e) => {
    e.preventDefault();
    onCCTVConnect(cctvForm);
    setShowCCTVForm(false);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      onVideoUpload(file);
    }
  };

  return (
    <div className="cyber-card p-8 mb-8 reveal-up">
      <div className="flex items-center justify-between mb-8">
        <h2 className="cyber-title text-3xl">INPUT SOURCE</h2>
        {isConnected && (
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 bg-green-400 rounded-full cyber-pulse"></div>
              <span className="text-green-400 font-semibold text-cyber-glow font-mono uppercase tracking-wider">
                {inputMode === 'live' && 'LIVE CAMERA'}
                {inputMode === 'cctv' && 'CCTV STREAM'}
                {inputMode === 'upload' && 'PROCESSING VIDEO'}
              </span>
            </div>
            <button
              onClick={onDownloadData}
              className="cyber-btn cyber-btn-purple flex items-center gap-2 text-sm"
            >
              ⬇ DOWNLOAD DATA
            </button>
          </div>
        )}
      </div>

      {!isConnected ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Live Camera Option */}
          <div className="cyber-card bg-gradient-to-br from-green-900/20 to-green-800/10 border-green-400/30 hover:border-green-400/60 transition-all duration-300 group">
            <div className="text-center p-8">
              <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-green-500 rounded-2xl flex items-center justify-center text-black text-3xl mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                📹
              </div>
              <h3 className="text-xl font-bold text-green-400 mb-3 font-mono">LIVE CAMERA</h3>
              <p className="text-gray-300 mb-6 text-sm leading-relaxed">
                Real-time monitoring using your device camera
              </p>
              <button
                onClick={onLiveCamera}
                className="cyber-btn cyber-btn-green w-full"
              >
                START LIVE FEED
              </button>
            </div>
          </div>

          {/* CCTV Option */}
          <div className="cyber-card bg-gradient-to-br from-cyan-900/20 to-cyan-800/10 border-cyan-400/30 hover:border-cyan-400/60 transition-all duration-300 group">
            <div className="text-center p-8">
              <div className="w-20 h-20 bg-gradient-to-br from-cyan-400 to-cyan-500 rounded-2xl flex items-center justify-center text-black text-3xl mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                🎥
              </div>
              <h3 className="text-xl font-bold text-cyan-400 mb-3 font-mono">CCTV STREAM</h3>
              <p className="text-gray-300 mb-6 text-sm leading-relaxed">
                Connect to IP camera via RTSP protocol
              </p>
              <button
                onClick={() => setShowCCTVForm(true)}
                className="cyber-btn w-full"
              >
                CONNECT CCTV
              </button>
            </div>
          </div>

          {/* Upload Video Option */}
          <div className="cyber-card bg-gradient-to-br from-purple-900/20 to-purple-800/10 border-purple-400/30 hover:border-purple-400/60 transition-all duration-300 group">
            <div className="text-center p-8">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-400 to-purple-500 rounded-2xl flex items-center justify-center text-black text-3xl mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                📁
              </div>
              <h3 className="text-xl font-bold text-purple-400 mb-3 font-mono">UPLOAD VIDEO</h3>
              <p className="text-gray-300 mb-6 text-sm leading-relaxed">
                Analyze pre-recorded video files
              </p>
              <label className="cyber-btn cyber-btn-purple w-full cursor-pointer block">
                SELECT VIDEO FILE
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </div>
          </div>
        </div>
      ) : (
        /* Connected State */
        <div className="flex items-center justify-between p-6 bg-gradient-to-r from-green-900/30 to-green-800/20 border border-green-400/40 rounded-xl backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-green-500 rounded-xl flex items-center justify-center text-black text-2xl">
              {inputMode === 'live' && '📹'}
              {inputMode === 'cctv' && '🎥'}
              {inputMode === 'upload' && '📁'}
            </div>
            <div>
              <h3 className="text-xl font-bold text-green-400 font-mono">
                {inputMode === 'live' && 'LIVE CAMERA ACTIVE'}
                {inputMode === 'cctv' && `CCTV CONNECTED (${cctvConfig.ip})`}
                {inputMode === 'upload' && 'PROCESSING UPLOADED VIDEO'}
              </h3>
              <p className="text-green-300 text-sm">System monitoring for anomalies...</p>
            </div>
          </div>
          <button
            onClick={onDisconnect}
            className="cyber-btn cyber-btn-red"
          >
            DISCONNECT
          </button>
        </div>
      )}

      {/* CCTV Configuration Modal */}
      {showCCTVForm && (
        <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="cyber-modal p-8 w-full max-w-md mx-4">
            <h3 className="cyber-title text-2xl mb-6">CONNECT TO CCTV</h3>
            <form onSubmit={handleCCTVSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-cyan-400 mb-2 font-mono uppercase">
                  IP Address *
                </label>
                <input
                  type="text"
                  required
                  placeholder="192.168.1.100"
                  value={cctvForm.ip}
                  onChange={(e) => setCctvForm({...cctvForm, ip: e.target.value})}
                  className="cyber-input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-cyan-400 mb-2 font-mono uppercase">
                  Port
                </label>
                <input
                  type="number"
                  placeholder="554"
                  value={cctvForm.port}
                  onChange={(e) => setCctvForm({...cctvForm, port: parseInt(e.target.value) || 554})}
                  className="cyber-input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-cyan-400 mb-2 font-mono uppercase">
                  Username (optional)
                </label>
                <input
                  type="text"
                  placeholder="admin"
                  value={cctvForm.username}
                  onChange={(e) => setCctvForm({...cctvForm, username: e.target.value})}
                  className="cyber-input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-cyan-400 mb-2 font-mono uppercase">
                  Password (optional)
                </label>
                <input
                  type="password"
                  placeholder="password"
                  value={cctvForm.password}
                  onChange={(e) => setCctvForm({...cctvForm, password: e.target.value})}
                  className="cyber-input w-full"
                />
              </div>
              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCCTVForm(false)}
                  className="cyber-btn flex-1 border-gray-500 text-gray-400 hover:bg-gray-500"
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  className="cyber-btn flex-1"
                >
                  CONNECT
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default InputSelector;
