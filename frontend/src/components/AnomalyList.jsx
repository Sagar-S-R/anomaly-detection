import React, { useState } from 'react';

const AnomalyList = ({ anomalies, onJumpToAnomaly, onRefresh }) => {
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);
  const [sortBy, setSortBy] = useState('timestamp'); // timestamp, severity

  // Sort anomalies
  const sortedAnomalies = [...anomalies].sort((a, b) => {
    if (sortBy === 'severity') {
      return (b.threat_severity_index || 0.5) - (a.threat_severity_index || 0.5);
    }
    return (b.timestamp || 0) - (a.timestamp || 0); // Most recent first
  });

  const getThreatLevel = (severity) => {
    const threat = severity || 0.5;
    if (threat > 0.7) return { level: 'High', color: 'bg-red-500', textColor: 'text-red-700', bgColor: 'bg-red-50' };
    if (threat > 0.4) return { level: 'Medium', color: 'bg-orange-500', textColor: 'text-orange-700', bgColor: 'bg-orange-50' };
    return { level: 'Low', color: 'bg-green-500', textColor: 'text-green-700', bgColor: 'bg-green-50' };
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    return new Date(timestamp * 1000).toLocaleString();
  };

  const handleViewInVideo = (anomaly) => {
    const jumpData = onJumpToAnomaly(anomaly);
    if (!jumpData) {
      alert('No video loaded. Please load a recording first.');
    }
  };

  const handleShowDetails = (anomaly) => {
    setSelectedAnomaly(anomaly);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          🚨 Detected Anomalies
          <span className="bg-red-100 text-red-800 text-sm font-medium px-2.5 py-0.5 rounded-full">
            {anomalies.length}
          </span>
        </h2>
        <div className="flex gap-2">
          {/* Sort Controls */}
          <select 
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="timestamp">Sort by Time</option>
            <option value="severity">Sort by Severity</option>
          </select>
          
          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium flex items-center gap-2"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Anomaly List */}
      {sortedAnomalies.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="text-4xl mb-4">🛡️</div>
          <p className="text-xl text-gray-600 mb-2">No anomalies detected</p>
          <p className="text-gray-500">System is running normally</p>
        </div>
      ) : (
        <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar">
          {sortedAnomalies.map((anomaly, index) => {
            const threat = getThreatLevel(anomaly.threat_severity_index);
            
            return (
              <div
                key={anomaly.id || index}
                className={`
                  border-l-4 p-4 rounded-lg transition-all duration-200 hover:shadow-md
                  ${threat.bgColor} border-l-${threat.color.split('-')[1]}-500
                `}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-bold text-lg text-gray-900">
                        Anomaly #{sortedAnomalies.length - index}
                      </h4>
                      <span className={`
                        px-2 py-1 rounded-full text-xs font-medium ${threat.color} text-white
                      `}>
                        {threat.level} - {((anomaly.threat_severity_index || 0.5) * 100).toFixed(0)}%
                      </span>
                    </div>

                    <div className="space-y-1 text-sm">
                      <p className="flex items-center gap-2">
                        <span className="font-medium">Time:</span>
                        <span className="text-gray-600">
                          {formatTimestamp(anomaly.timestamp)} 
                          {anomaly.frame_count && ` (Frame ${anomaly.frame_count})`}
                        </span>
                      </p>
                      
                      {anomaly.details && (
                        <p className="flex items-start gap-2">
                          <span className="font-medium">Details:</span>
                          <span className="text-gray-600">{anomaly.details}</span>
                        </p>
                      )}
                      
                      {anomaly.reasoning_summary && (
                        <p className="flex items-start gap-2">
                          <span className="font-medium">AI Analysis:</span>
                          <span className="text-gray-600 italic">{anomaly.reasoning_summary}</span>
                        </p>
                      )}

                      {/* Scores */}
                      <div className="flex gap-4 mt-2">
                        {anomaly.visual_score !== undefined && (
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            Visual: {(anomaly.visual_score * 100).toFixed(0)}%
                          </span>
                        )}
                        {anomaly.audio_score !== undefined && (
                          <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                            Audio: {(anomaly.audio_score * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Thumbnail */}
                  {anomaly.frame_file && (
                    <div className="ml-4">
                      <img
                        src={`/${anomaly.frame_file}`}
                        alt="Anomaly frame"
                        className="w-24 h-18 object-cover rounded border shadow-sm"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => handleViewInVideo(anomaly)}
                    className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                  >
                    📹 View in Video
                  </button>
                  <button
                    onClick={() => handleShowDetails(anomaly)}
                    className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700 transition-colors"
                  >
                    📋 Show Details
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Details Modal */}
      {selectedAnomaly && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Anomaly Details</h3>
              <button
                onClick={() => setSelectedAnomaly(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="font-medium">Frame:</span> {selectedAnomaly.frame_count || 'Unknown'}
                </div>
                <div>
                  <span className="font-medium">Timestamp:</span> {selectedAnomaly.timestamp?.toFixed(2) || 'Unknown'}s
                </div>
                <div>
                  <span className="font-medium">Threat Level:</span> {((selectedAnomaly.threat_severity_index || 0.5) * 100).toFixed(0)}%
                </div>
                <div>
                  <span className="font-medium">Visual Score:</span> {((selectedAnomaly.visual_score || 0.5) * 100).toFixed(0)}%
                </div>
                <div>
                  <span className="font-medium">Audio Score:</span> {((selectedAnomaly.audio_score || 0.5) * 100).toFixed(0)}%
                </div>
                <div>
                  <span className="font-medium">Video File:</span> {selectedAnomaly.video_file || 'Unknown'}
                </div>
              </div>
              
              {selectedAnomaly.frame_file && (
                <div>
                  <span className="font-medium">Frame File:</span> {selectedAnomaly.frame_file}
                </div>
              )}
              
              {selectedAnomaly.reasoning_summary && (
                <div>
                  <span className="font-medium">AI Analysis:</span>
                  <p className="mt-1 p-2 bg-gray-50 rounded italic">{selectedAnomaly.reasoning_summary}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnomalyList;
