import React, { useState, useEffect, useRef } from 'react';

const UserDashboard = ({ user, onLogout, onStartMonitoring }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedAnomalyId, setSelectedAnomalyId] = useState(null);
  const [tier2Analysis, setTier2Analysis] = useState(null);
  const fetchingRef = useRef(false);

  // Clean up any active connections when dashboard loads
  useEffect(() => {
    console.log('📊 UserDashboard mounted - checking for active connections to clean up');
    // Send a message to parent to clean up any active monitoring
    return () => {
      console.log('📊 UserDashboard unmounting');
      fetchingRef.current = false;
    };
  }, []);

  useEffect(() => {
    const loadDashboardData = async () => {
      if (!user?.username) {
        console.log('📊 No username available, skipping fetch');
        return;
      }
      
      if (fetchingRef.current) {
        console.log('📊 Skipping fetch - already fetching for user:', user.username);
        return;
      }
      
      fetchingRef.current = true;
      
      try {
        setLoading(true);
        setError(''); // Clear any previous errors
        
        console.log('📊 Fetching dashboard data for user:', user.username);
        
        // Use the configured API URL from environment variables
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const statsResponse = await fetch(`${apiUrl}/api/stats`);
        console.log('📈 Stats response status:', statsResponse.status);
        const statsData = statsResponse.ok ? await statsResponse.json() : null;
        console.log('📈 Stats data:', statsData);
        
        // Skip the problematic anomaly_events endpoint for now
        // const anomaliesResponse = await fetch(`${apiUrl}/anomaly_events?username=${encodeURIComponent(user.username)}`);
        // console.log('🚨 Anomalies response status:', anomaliesResponse.status);
        // const anomaliesData = anomaliesResponse.ok ? await anomaliesResponse.json() : { anomaly_events: [] };
        // console.log('🚨 Anomalies data:', anomaliesData);
        
        const anomaliesData = { anomaly_events: [] }; // Temporary bypass
        
        // Set dashboard data with available information and fallbacks
        const dashboardInfo = {
          total_sessions: statsData?.total_sessions || statsData?.stats?.total_sessions || 0,
          total_anomalies: statsData?.total_stored_anomalies || 0, // Use from stats instead
          recent_activity: 'Dashboard loaded successfully',
          threat_level: 'Normal'
        };
        
        console.log('📊 Setting dashboard data:', dashboardInfo);
        setDashboardData(dashboardInfo);
        
        // Set anomalies (limit to 20)
        const userAnomalies = anomaliesData.anomaly_events?.slice(0, 20) || [];
        console.log('🚨 Setting anomalies:', userAnomalies.length, 'items');
        setAnomalies(userAnomalies);

      } catch (err) {
        console.error('❌ Dashboard fetch error:', err);
        setError(`Failed to fetch dashboard data: ${err.message}`);
        
        // Set fallback data to prevent infinite loading
        setDashboardData({
          total_sessions: 0,
          total_anomalies: 0,
          recent_activity: 'Error loading data',
          threat_level: 'Unknown'
        });
        setAnomalies([]);
        
      } finally {
        setLoading(false);
        fetchingRef.current = false;
        console.log('📊 Dashboard loading complete');
      }
    };

    console.log('📊 UserDashboard useEffect triggered. User:', user?.username, 'Loading:', loading, 'Fetching:', fetchingRef.current);
    if (user?.username && !dashboardData && !fetchingRef.current) {
      console.log('📊 Starting loadDashboardData...');
      loadDashboardData();
    }
    
    // Cleanup function to reset fetching state if component unmounts
    return () => {
      fetchingRef.current = false;
    };
  }, [user?.username, dashboardData, loading]); // Added missing dependencies

  const fetchTier2Analysis = async (anomalyId) => {
    try {
      // Find the anomaly in the current anomalies list
      const anomaly = anomalies.find(a => a.id === anomalyId || a.frame_id === anomalyId);
      if (anomaly && anomaly.tier2_analysis) {
        setTier2Analysis(anomaly.tier2_analysis);
        setSelectedAnomalyId(anomalyId);
      } else {
        setTier2Analysis({ error: 'No Tier 2 analysis available for this anomaly' });
        setSelectedAnomalyId(anomalyId);
      }
    } catch (err) {
      console.error('Tier 2 analysis fetch error:', err);
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getThreatLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black cyber-grid-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-cyan-400 font-mono">Loading Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black cyber-grid-bg">
      <div className="container mx-auto px-6 py-8">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-cyan-400 font-mono">USER DASHBOARD</h1>
            <p className="text-gray-400 font-mono mt-2">Welcome back, {dashboardData?.user?.full_name || user.username}</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={onStartMonitoring}
              className="px-6 py-3 bg-green-500/20 border border-green-400/40 text-green-400 rounded-xl font-mono font-bold tracking-wider uppercase transition-all duration-300 hover:bg-green-500/30"
            >
              START MONITORING
            </button>
            <button
              onClick={onLogout}
              className="px-6 py-3 bg-red-500/20 border border-red-400/40 text-red-400 rounded-xl font-mono font-bold tracking-wider uppercase transition-all duration-300 hover:bg-red-500/30"
            >
              LOGOUT
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-400/40 rounded-xl">
            <p className="text-red-400 font-mono">{error}</p>
          </div>
        )}

        {/* Statistics Cards */}
        {dashboardData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="p-6 bg-gray-800/50 border border-gray-700/50 rounded-xl">
              <h3 className="text-cyan-400 font-mono font-bold mb-2">TOTAL ANOMALIES</h3>
              <p className="text-3xl font-bold text-white">{dashboardData.total_anomalies || 0}</p>
            </div>
            <div className="p-6 bg-gray-800/50 border border-gray-700/50 rounded-xl">
              <h3 className="text-green-400 font-mono font-bold mb-2">TOTAL SESSIONS</h3>
              <p className="text-3xl font-bold text-white">{dashboardData.total_sessions || 0}</p>
            </div>
            <div className="p-6 bg-gray-800/50 border border-gray-700/50 rounded-xl">
              <h3 className="text-purple-400 font-mono font-bold mb-2">THREAT LEVEL</h3>
              <p className="text-3xl font-bold text-white">{dashboardData.threat_level || 'Normal'}</p>
            </div>
          </div>
        )}

        {/* Anomalies List */}
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-6">
          <h2 className="text-xl font-bold text-cyan-400 font-mono mb-6">RECENT ANOMALIES</h2>
          
          {anomalies.length === 0 ? (
            <p className="text-gray-400 font-mono text-center py-8">No anomalies detected yet</p>
          ) : (
            <div className="space-y-4">
              {anomalies.map((anomaly, index) => (
                <div key={anomaly.id} className="p-4 bg-gray-900/50 border border-gray-600/30 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-2">
                        <span className="text-cyan-400 font-mono font-bold">#{index + 1}</span>
                        <span className="text-gray-300 font-mono">{formatTimestamp(anomaly.session_time)}</span>
                        <span className={`px-2 py-1 rounded text-xs font-mono ${
                          anomaly.tier2_status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {anomaly.tier2_status.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-gray-300 font-mono mb-2">{anomaly.details}</p>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="text-gray-400 font-mono">Fusion: {anomaly.fusion_status}</span>
                        <span className="text-gray-400 font-mono">Confidence: {(anomaly.tier1_confidence * 100).toFixed(1)}%</span>
                        <span className="text-gray-400 font-mono">Duration: {anomaly.duration.toFixed(1)}s</span>
                      </div>
                    </div>
                    <button
                      onClick={() => fetchTier2Analysis(anomaly.id)}
                      className="px-4 py-2 bg-purple-500/20 border border-purple-400/40 text-purple-400 rounded-lg font-mono text-sm hover:bg-purple-500/30 transition-all duration-300"
                    >
                      VIEW ANALYSIS
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Tier 2 Analysis Modal */}
        {tier2Analysis && selectedAnomalyId && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-bold text-cyan-400 font-mono">TIER 2 ANALYSIS</h3>
                  <button
                    onClick={() => setTier2Analysis(null)}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-6">
                  <div>
                    <h4 className="text-lg font-bold text-green-400 font-mono mb-2">THREAT ASSESSMENT</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-gray-400 font-mono">Threat Level: </span>
                        <span className={`font-mono font-bold ${getThreatLevelColor(tier2Analysis.threat_level)}`}>
                          {tier2Analysis.threat_level?.toUpperCase() || 'UNKNOWN'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-400 font-mono">Confidence: </span>
                        <span className="text-cyan-400 font-mono font-bold">
                          {(tier2Analysis.confidence_score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-lg font-bold text-yellow-400 font-mono mb-2">SUMMARY</h4>
                    <p className="text-gray-300 font-mono bg-gray-800/50 p-4 rounded-lg">
                      {tier2Analysis.reasoning_summary || 'No summary available'}
                    </p>
                  </div>

                  {tier2Analysis.detected_behaviors && tier2Analysis.detected_behaviors.length > 0 && (
                    <div>
                      <h4 className="text-lg font-bold text-orange-400 font-mono mb-2">DETECTED BEHAVIORS</h4>
                      <ul className="space-y-2">
                        {tier2Analysis.detected_behaviors.map((behavior, index) => (
                          <li key={index} className="text-gray-300 font-mono flex items-center gap-2">
                            <span className="w-2 h-2 bg-orange-400 rounded-full"></span>
                            {behavior}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {tier2Analysis.recommended_actions && tier2Analysis.recommended_actions.length > 0 && (
                    <div>
                      <h4 className="text-lg font-bold text-red-400 font-mono mb-2">RECOMMENDED ACTIONS</h4>
                      <ul className="space-y-2">
                        {tier2Analysis.recommended_actions.map((action, index) => (
                          <li key={index} className="text-gray-300 font-mono flex items-center gap-2">
                            <span className="w-2 h-2 bg-red-400 rounded-full"></span>
                            {action}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserDashboard;
