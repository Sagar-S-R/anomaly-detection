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
    <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-slate-200">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-900">Input Source</h2>
        {isConnected && (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-green-600 font-medium">
                {inputMode === 'live' && 'Live Camera'}
                {inputMode === 'cctv' && 'CCTV Stream'}
                {inputMode === 'upload' && 'Processing Video'}
              </span>
            </div>
            <button
              onClick={onDownloadData}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 text-sm"
            >
              📥 Download Data
            </button>
          </div>
        )}
      </div>

      {!isConnected ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Live Camera Option */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center text-white text-2xl mx-auto mb-4">
                📹
              </div>
              <h3 className="text-lg font-semibold text-green-800 mb-2">Live Camera</h3>
              <p className="text-sm text-green-600 mb-4">
                Real-time monitoring using your device camera
              </p>
              <button
                onClick={onLiveCamera}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                Start Live Feed
              </button>
            </div>
          </div>

          {/* CCTV Option */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl mx-auto mb-4">
                🎥
              </div>
              <h3 className="text-lg font-semibold text-blue-800 mb-2">CCTV Stream</h3>
              <p className="text-sm text-blue-600 mb-4">
                Connect to IP camera via RTSP
              </p>
              <button
                onClick={() => setShowCCTVForm(true)}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Connect CCTV
              </button>
            </div>
          </div>

          {/* Upload Video Option */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center text-white text-2xl mx-auto mb-4">
                📁
              </div>
              <h3 className="text-lg font-semibold text-purple-800 mb-2">Upload Video</h3>
              <p className="text-sm text-purple-600 mb-4">
                Analyze pre-recorded video files
              </p>
              <label className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium cursor-pointer block">
                Select Video File
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
        <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center text-white text-xl">
              {inputMode === 'live' && '📹'}
              {inputMode === 'cctv' && '🎥'}
              {inputMode === 'upload' && '📁'}
            </div>
            <div>
              <h3 className="font-semibold text-green-800">
                {inputMode === 'live' && 'Live Camera Active'}
                {inputMode === 'cctv' && `CCTV Connected (${cctvConfig.ip})`}
                {inputMode === 'upload' && 'Processing Uploaded Video'}
              </h3>
              <p className="text-sm text-green-600">Monitoring for anomalies...</p>
            </div>
          </div>
          <button
            onClick={onDisconnect}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
          >
            Disconnect
          </button>
        </div>
      )}

      {/* CCTV Configuration Modal */}
      {showCCTVForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-bold text-slate-900 mb-4">Connect to CCTV</h3>
            <form onSubmit={handleCCTVSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  IP Address *
                </label>
                <input
                  type="text"
                  required
                  placeholder="192.168.1.100"
                  value={cctvForm.ip}
                  onChange={(e) => setCctvForm({...cctvForm, ip: e.target.value})}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Port
                </label>
                <input
                  type="number"
                  placeholder="554"
                  value={cctvForm.port}
                  onChange={(e) => setCctvForm({...cctvForm, port: parseInt(e.target.value) || 554})}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Username (optional)
                </label>
                <input
                  type="text"
                  placeholder="admin"
                  value={cctvForm.username}
                  onChange={(e) => setCctvForm({...cctvForm, username: e.target.value})}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Password (optional)
                </label>
                <input
                  type="password"
                  placeholder="password"
                  value={cctvForm.password}
                  onChange={(e) => setCctvForm({...cctvForm, password: e.target.value})}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCCTVForm(false)}
                  className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Connect
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
