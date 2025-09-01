import React, { useState } from 'react';
import LiveFeed from '../components/LiveFeed';
import AnomalyList from '../components/AnomalyList';
import JsonOutput from '../components/JsonOutput';

const CCTVMonitoring = ({ 
  user, 
  onLogout, 
  onBackToSelector,
  onCCTVConnect,
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
  const [cctvConfig, setCctvConfig] = useState({
    url: '',
    username: '',
    password: '',
    streamType: 'rtsp',
    port: '554'
  });
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [savedStreams, setSavedStreams] = useState([
    {
      id: 1,
      name: 'Main Entrance',
      url: 'rtsp://admin:password@192.168.1.100:554/stream1',
      status: 'offline'
    },
    {
      id: 2,
      name: 'Parking Lot',
      url: 'rtsp://admin:password@192.168.1.101:554/stream1',
      status: 'offline'
    }
  ]);

  const handleConfigChange = (field, value) => {
    setCctvConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleConnect = async () => {
    if (!cctvConfig.url.trim()) return;
    
    setIsConnecting(true);
    setConnectionStatus('connecting');
    
    // Simulate connection process
    setTimeout(() => {
      setIsConnecting(false);
      setConnectionStatus('connected');
      onCCTVConnect(cctvConfig);
    }, 2000);
  };

  const handleDisconnect = () => {
    setConnectionStatus('disconnected');
    onDisconnect();
  };

  const handleSaveStream = () => {
    if (!cctvConfig.url.trim()) return;
    
    const newStream = {
      id: Date.now(),
      name: `CCTV Stream ${savedStreams.length + 1}`,
      url: cctvConfig.url,
      status: 'offline'
    };
    
    setSavedStreams(prev => [...prev, newStream]);
  };

  const handleLoadStream = (stream) => {
    const url = new URL(stream.url);
    setCctvConfig({
      url: stream.url,
      username: '',
      password: '',
      streamType: url.protocol.replace(':', ''),
      port: url.port || '554'
    });
  };

  const handleRemoveStream = (streamId) => {
    setSavedStreams(prev => prev.filter(stream => stream.id !== streamId));
  };

  const buildStreamUrl = () => {
    const { url, username, password, streamType, port } = cctvConfig;
    
    if (!url) return '';
    
    try {
      if (url.startsWith('http') || url.startsWith('rtsp')) {
        return url;
      }
      
      const auth = username && password ? `${username}:${password}@` : '';
      return `${streamType}://${auth}${url}:${port}/stream1`;
    } catch {
      return url;
    }
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
              <h1 className="text-3xl font-bold text-cyan-400 font-mono">CCTV MONITORING</h1>
              <p className="text-gray-400 font-mono mt-2">Connect to IP cameras and CCTV streams for real-time anomaly detection</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className={`w-4 h-4 rounded-full cyber-pulse ${
                connectionStatus === 'connected' && isConnected ? 'bg-green-400' : 
                connectionStatus === 'connecting' ? 'bg-yellow-400' : 'bg-gray-400'
              }`}></div>
              <span className={`font-semibold text-cyber-glow font-mono uppercase tracking-wider ${
                connectionStatus === 'connected' && isConnected ? 'text-green-400' : 
                connectionStatus === 'connecting' ? 'text-yellow-400' : 'text-gray-400'
              }`}>
                {connectionStatus === 'connected' && isConnected ? 'STREAM ACTIVE' : 
                 connectionStatus === 'connecting' ? 'CONNECTING...' : 'DISCONNECTED'}
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

        {/* Connection Configuration */}
        {connectionStatus !== 'connected' && (
          <div className="mb-8">
            <div className="cyber-card p-8">
              <h2 className="cyber-title text-xl mb-6">CCTV STREAM CONFIGURATION</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                
                {/* Connection Settings */}
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-mono text-gray-400 mb-2">STREAM URL / IP ADDRESS</label>
                    <input
                      type="text"
                      value={cctvConfig.url}
                      onChange={(e) => handleConfigChange('url', e.target.value)}
                      placeholder="192.168.1.100 or rtsp://192.168.1.100:554/stream1"
                      className="cyber-input w-full"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-mono text-gray-400 mb-2">STREAM TYPE</label>
                      <select
                        value={cctvConfig.streamType}
                        onChange={(e) => handleConfigChange('streamType', e.target.value)}
                        className="cyber-input w-full"
                      >
                        <option value="rtsp">RTSP</option>
                        <option value="http">HTTP</option>
                        <option value="https">HTTPS</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-mono text-gray-400 mb-2">PORT</label>
                      <input
                        type="text"
                        value={cctvConfig.port}
                        onChange={(e) => handleConfigChange('port', e.target.value)}
                        placeholder="554"
                        className="cyber-input w-full"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-mono text-gray-400 mb-2">USERNAME (Optional)</label>
                      <input
                        type="text"
                        value={cctvConfig.username}
                        onChange={(e) => handleConfigChange('username', e.target.value)}
                        placeholder="admin"
                        className="cyber-input w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-mono text-gray-400 mb-2">PASSWORD (Optional)</label>
                      <input
                        type="password"
                        value={cctvConfig.password}
                        onChange={(e) => handleConfigChange('password', e.target.value)}
                        placeholder="••••••••"
                        className="cyber-input w-full"
                      />
                    </div>
                  </div>
                  
                  <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4">
                    <h4 className="font-mono text-sm text-gray-400 mb-2">GENERATED STREAM URL:</h4>
                    <p className="font-mono text-cyan-400 text-sm break-all">
                      {buildStreamUrl() || 'Enter stream details above'}
                    </p>
                  </div>
                  
                  <div className="flex gap-3">
                    <button
                      onClick={handleConnect}
                      disabled={!cctvConfig.url.trim() || isConnecting}
                      className="cyber-btn cyber-btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isConnecting ? (
                        <>
                          <div className="w-4 h-4 border-2 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin"></div>
                          CONNECTING...
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                          </svg>
                          CONNECT TO STREAM
                        </>
                      )}
                    </button>
                    <button
                      onClick={handleSaveStream}
                      disabled={!cctvConfig.url.trim()}
                      className="cyber-btn cyber-btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      SAVE STREAM
                    </button>
                  </div>
                </div>

                {/* Saved Streams */}
                <div>
                  <h3 className="cyber-title text-lg mb-4">SAVED STREAMS</h3>
                  <div className="space-y-3">
                    {savedStreams.map((stream) => (
                      <div key={stream.id} className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full ${
                              stream.status === 'online' ? 'bg-green-400' : 'bg-gray-400'
                            }`}></div>
                            <div>
                              <h4 className="font-mono text-white font-bold">{stream.name}</h4>
                              <p className="font-mono text-xs text-gray-400 truncate max-w-[200px]">{stream.url}</p>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleLoadStream(stream)}
                              className="text-cyan-400 hover:text-cyan-300 text-sm font-mono"
                            >
                              LOAD
                            </button>
                            <button
                              onClick={() => handleRemoveStream(stream.id)}
                              className="text-red-400 hover:text-red-300 text-sm font-mono"
                            >
                              REMOVE
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                    
                    {savedStreams.length === 0 && (
                      <div className="text-center py-8 text-gray-400 font-mono">
                        No saved streams. Configure and save a stream above.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Processing Status */}
        {connectionStatus === 'connected' && isConnected && (
          <div className="mb-8">
            <div className="bg-green-500/10 border-2 border-green-400/30 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-2xl text-green-400">📺</div>
                  <div>
                    <h3 className="font-bold font-mono text-green-400">CCTV STREAM MONITORING ACTIVE</h3>
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
                    onClick={handleDisconnect}
                    className="cyber-btn cyber-btn-danger text-sm"
                  >
                    DISCONNECT STREAM
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

        {/* Main Content - Only show when connected */}
        {connectionStatus === 'connected' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Live Feed - Takes 2 columns */}
            <div className="lg:col-span-2">
              <div className="cyber-card p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="cyber-title text-xl">LIVE CCTV FEED</h2>
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
                
                <LiveFeed 
                  ws={ws}
                  isConnected={isConnected}
                  anomalies={anomalies}
                  streamSource="cctv"
                />
              </div>
            </div>

            {/* Data Panel */}
            <div className="space-y-6">
              {showJsonPanel && (
                <div className="cyber-card p-6">
                  <h3 className="cyber-title text-lg mb-4">STREAM DATA</h3>
                  <JsonOutput 
                    jsonData={jsonData}
                    isVisible={showJsonPanel}
                  />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analysis Results - Only show when connected */}
        {connectionStatus === 'connected' && (
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
        )}

      </div>
    </div>
  );
};

export default CCTVMonitoring;
