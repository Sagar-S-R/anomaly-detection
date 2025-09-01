import React, { useState, useEffect } from 'react';

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
      const response = await fetch('http://localhost:8000/api/sessions');
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
      const response = await fetch(`http://localhost:8000/api/anomalies?session_id=${sessionId}`);
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
      const response = await fetch('http://localhost:8000/api/stats');
      const data = await response.json();
      setSystemStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Download session data
  const downloadSession = async (sessionId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/download_session/${sessionId}`);
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
    <div className="database-manager bg-white rounded-lg shadow-lg p-6 h-full overflow-hidden">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">📊 Database Manager</h2>
      
      {/* System Stats */}
      {systemStats && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-700 mb-2">System Status</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                systemStats.mongodb_connected ? 'bg-green-500' : 'bg-red-500'
              }`}></span>
              MongoDB: {systemStats.mongodb_connected ? 'Connected' : 'Disconnected'}
            </div>
            <div>Total Anomalies: {systemStats.total_stored_anomalies}</div>
            <div>Total Sessions: {systemStats.total_sessions}</div>
            <div>Current Status: {systemStats.current_status}</div>
          </div>
        </div>
      )}

      {/* Sessions List */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-semibold text-gray-700">Sessions</h3>
          <button 
            onClick={fetchSessions}
            className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
        
        <div className="max-h-40 overflow-y-auto">
          {sessions.length === 0 ? (
            <p className="text-gray-500 text-sm">No sessions found</p>
          ) : (
            sessions.map((session) => (
              <div 
                key={session.session_id} 
                className={`p-3 border rounded mb-2 cursor-pointer hover:bg-gray-50 ${
                  selectedSession === session.session_id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}
                onClick={() => fetchAnomalies(session.session_id)}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium text-sm">{session.session_id}</div>
                    <div className="text-xs text-gray-500">
                      {new Date(session.start_time).toLocaleString()}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <span className={`px-2 py-1 text-xs rounded ${
                      session.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {session.status}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        downloadSession(session.session_id);
                      }}
                      className="px-2 py-1 bg-green-500 text-white rounded text-xs hover:bg-green-600"
                    >
                      📥 Download
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
        <div>
          <h3 className="font-semibold text-gray-700 mb-3">
            Anomalies in {selectedSession} ({anomalies.length})
          </h3>
          
          <div className="max-h-60 overflow-y-auto">
            {anomalies.length === 0 ? (
              <p className="text-gray-500 text-sm">No anomalies found for this session</p>
            ) : (
              anomalies.map((anomaly, index) => (
                <div key={index} className="p-3 border border-gray-200 rounded mb-2">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-medium text-sm text-red-600">
                        🚨 Anomaly #{index + 1}
                      </div>
                      <div className="text-xs text-gray-500 mb-1">
                        {new Date(anomaly.timestamp).toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-700">
                        {anomaly.details || 'No details available'}
                      </div>
                      {anomaly.tier2_analysis && (
                        <div className="mt-2 p-2 bg-yellow-50 rounded text-xs">
                          <strong>AI Analysis:</strong> {anomaly.tier2_analysis.reasoning || 'Analysis completed'}
                        </div>
                      )}
                    </div>
                    {anomaly.frame_base64 && (
                      <img 
                        src={`data:image/jpeg;base64,${anomaly.frame_base64}`}
                        alt="Anomaly frame"
                        className="w-16 h-12 object-cover rounded ml-3"
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
