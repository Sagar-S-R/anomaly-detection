import React, { useState, useEffect } from 'react';
import { getApiUrl } from '../config/api';

const DatabaseManager = () => {
  const [sessions, setSessions] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [systemStats, setSystemStats] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch all sessions
  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await fetch(getApiUrl('/api/sessions'));
      const data = await response.json();
      setSessions(data.sessions);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch anomalies for a specific session
  const fetchAnomalies = async (sessionId) => {
    try {
      setLoading(true);
      const response = await fetch(getApiUrl(`/api/anomalies?session_id=${sessionId}`));
      const data = await response.json();
      setAnomalies(data.anomalies);
      setSelectedSession(sessionId);
    } catch (error) {
      console.error('Error fetching anomalies:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch system stats
  const fetchSystemStats = async () => {
    try {
      const response = await fetch(getApiUrl('/api/stats'));
      const data = await response.json();
      setSystemStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Download session data
  const downloadSession = async (sessionId) => {
    try {
      const response = await fetch(getApiUrl(`/api/download_session/${sessionId}`));
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `anomaly_session_${sessionId}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } else {
        console.error('Download failed');
      }
    } catch (error) {
      console.error('Error downloading session:', error);
    }
  };

  useEffect(() => {
    fetchSessions();
    fetchSystemStats();
  }, []);

  return (
    <div className="cyber-panel p-6 h-full overflow-hidden border-2 border-cyan-400/40 rounded-xl bg-gradient-to-br from-gray-900/50 to-black/80 backdrop-blur-sm shadow-2xl shadow-cyan-400/10">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-gradient-to-br from-cyan-400/20 to-teal-400/20 rounded-lg flex items-center justify-center border border-cyan-400/30">
          <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 1.79 4 4 4h8c0-1.1.9-2 2-2h-4c-1.1 0-2-.9-2-2V7c0-1.1.9-2 2-2h4c-1.1 0-2-.9-2-2H8c-2.21 0-4 1.79-4 4z" />
          </svg>
        </div>
        <h2 className="cyber-title text-2xl">📊 DATABASE MANAGER</h2>
      </div>
      
      {/* System Stats */}
      {systemStats && (
        <div className="mb-6 p-4 bg-gradient-to-r from-cyan-900/20 to-teal-900/20 border-2 border-cyan-400/40 rounded-xl backdrop-blur-sm shadow-lg shadow-cyan-400/20">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-6 h-6 bg-cyan-400/20 rounded-full flex items-center justify-center">
              <div className="w-3 h-3 bg-cyan-400 rounded-full cyber-pulse"></div>
            </div>
            <h3 className="font-semibold text-cyan-400 font-mono uppercase tracking-wide">System Status</h3>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center">
              <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                systemStats.mongodb_connected ? 'bg-green-400' : 'bg-red-400'
              }`}></span>
              <span className="text-gray-300 font-mono">MongoDB: {systemStats.mongodb_connected ? 'Connected' : 'Disconnected'}</span>
            </div>
            <div className="text-gray-300 font-mono">Total Anomalies: <span className="text-cyan-400">{systemStats.total_stored_anomalies}</span></div>
            <div className="text-gray-300 font-mono">Total Sessions: <span className="text-cyan-400">{systemStats.total_sessions}</span></div>
            <div className="text-gray-300 font-mono">Current Status: <span className="text-green-400">{systemStats.current_status}</span></div>
          </div>
        </div>
      )}

      {/* Sessions List */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 bg-purple-400/20 rounded-full flex items-center justify-center">
              <svg className="w-3 h-3 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14-4l-7 7-7-7m14 8l-7-7-7 7" />
              </svg>
            </div>
            <h3 className="font-semibold text-purple-400 font-mono uppercase tracking-wide">Sessions</h3>
          </div>
          <button 
            onClick={fetchSessions}
            className="cyber-btn-primary px-4 py-2 rounded-xl font-mono font-bold tracking-wider uppercase text-sm border-2 border-cyan-400/60 hover:border-cyan-400 transition-all duration-300"
            disabled={loading}
          >
            {loading ? 'LOADING...' : 'REFRESH'}
          </button>
        </div>
        
        <div className="max-h-40 overflow-y-auto border-2 border-gray-600/40 rounded-xl bg-black/20 p-2">
          {sessions.length === 0 ? (
            <p className="text-gray-500 text-sm font-mono">No sessions found</p>
          ) : (
            sessions.map((session) => (
                <div key={session.session_id} 
                className={`p-4 border-2 rounded-xl mb-3 cursor-pointer transition-all duration-300 ${
                  selectedSession === session.session_id 
                    ? 'border-cyan-400 bg-cyan-400/10 shadow-lg shadow-cyan-400/30' 
                    : 'border-gray-600/40 bg-black/20 hover:border-cyan-400/60 hover:bg-cyan-400/5 hover:shadow-md hover:shadow-cyan-400/20'
                }`}
                onClick={() => fetchAnomalies(session.session_id)}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium text-sm text-cyan-400 font-mono">{session.session_id}</div>
                    <div className="text-xs text-gray-500 font-mono">
                      {new Date(session.start_time).toLocaleString()}
                    </div>
                  </div>
                  <div className="flex space-x-3">
                    <span className={`px-3 py-1 text-xs rounded-lg font-mono font-bold ${
                      session.status === 'active' 
                        ? 'bg-green-400/20 text-green-400 border border-green-400/40' 
                        : 'bg-gray-600/20 text-gray-400 border border-gray-600/40'
                    }`}>
                      {session.status.toUpperCase()}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        downloadSession(session.session_id);
                      }}
                      className="px-3 py-1 bg-purple-500/20 border border-purple-400/40 text-purple-400 rounded-lg text-xs hover:bg-purple-500/30 transition-all duration-300 font-mono font-bold"
                    >
                      📥 DOWNLOAD
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Selected Session Anomalies */}
      {selectedSession && (
        <div className="border-2 border-red-400/40 rounded-xl bg-red-500/5 p-4">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-6 h-6 bg-red-400/20 rounded-full flex items-center justify-center">
              <svg className="w-3 h-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="font-semibold text-red-400 font-mono uppercase tracking-wide">
              Anomalies in {selectedSession} ({anomalies.length})
            </h3>
          </div>
          
          <div className="max-h-60 overflow-y-auto">
            {anomalies.length === 0 ? (
              <p className="text-gray-500 text-sm font-mono">No anomalies found for this session</p>
            ) : (
              anomalies.map((anomaly, index) => (
                <div key={index} className="p-4 border-2 border-red-400/40 bg-red-500/10 rounded-xl mb-3 hover:border-red-400/60 hover:bg-red-500/15 transition-all duration-300 shadow-lg shadow-red-400/10">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-medium text-sm text-red-400 font-mono">
                        🚨 ANOMALY #{String(index + 1).padStart(3, '0')}
                      </div>
                      <div className="text-xs text-gray-500 mb-2 font-mono">
                        {new Date(anomaly.timestamp).toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-300 font-mono">
                        {anomaly.details || 'No details available'}
                      </div>
                      {anomaly.tier2_analysis && (
                        <div className="mt-3 p-3 bg-yellow-500/10 border-2 border-yellow-400/30 rounded-lg text-xs shadow-md shadow-yellow-400/10">
                          <div className="text-yellow-400 font-mono font-bold mb-1">AI ANALYSIS:</div>
                          <div className="text-gray-300 font-mono">{anomaly.tier2_analysis.reasoning || 'Analysis completed'}</div>
                        </div>
                      )}
                    </div>
                    {anomaly.frame_base64 && (
                      <img 
                        src={`data:image/jpeg;base64,${anomaly.frame_base64}`}
                        alt="Anomaly frame"
                        className="w-20 h-16 object-cover rounded-lg ml-4 border-2 border-cyan-400/30 shadow-lg shadow-cyan-400/20"
                      />
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DatabaseManager;
