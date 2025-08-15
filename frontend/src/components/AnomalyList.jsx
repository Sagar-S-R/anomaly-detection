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
    <div className="card-modern p-8 reveal-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Detected Anomalies</h2>
            <p className="text-slate-500 text-sm">Security threats and unusual activities</p>
          </div>
          <div className="bg-red-100 text-red-800 text-sm font-bold px-4 py-2 rounded-full shadow-sm">
            {anomalies.length}
          </div>
        </div>
        <div className="flex gap-3">
          {/* Sort Controls */}
          <select 
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-3 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 bg-white shadow-professional"
          >
            <option value="timestamp">Sort by Time</option>
            <option value="severity">Sort by Severity</option>
          </select>
          
          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            className="btn-modern px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all duration-300 text-sm font-semibold flex items-center gap-2 shadow-professional hover:shadow-lg transform hover:-translate-y-0.5"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Anomaly List */}
      {sortedAnomalies.length === 0 ? (
        <div className="text-center py-16 bg-slate-50 rounded-2xl">
          <div className="w-20 h-20 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <p className="text-2xl text-slate-700 mb-3 font-semibold">All Clear</p>
          <p className="text-slate-500 text-lg">No security anomalies detected</p>
          <p className="text-slate-400 text-sm mt-2">System is operating normally</p>
        </div>
      ) : (
        <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar">
          {sortedAnomalies.map((anomaly, index) => {
            const threat = getThreatLevel(anomaly.threat_severity_index);
            
            return (
              <div
                key={anomaly.id || index}
                className={`
                  border-l-4 p-6 rounded-xl transition-all duration-300 hover:shadow-lg transform hover:-translate-y-1
                  ${threat.bgColor} border-l-${threat.color.split('-')[1]}-500 shadow-professional
                `}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg ${threat.color} flex items-center justify-center`}>
                          <span className="text-white text-sm font-bold">
                            {sortedAnomalies.length - index}
                          </span>
                        </div>
                        <h4 className="font-bold text-xl text-slate-900">
                          Security Alert #{sortedAnomalies.length - index}
                        </h4>
                      </div>
                      <span className={`
                        px-3 py-2 rounded-full text-sm font-bold ${threat.color} text-white shadow-sm
                      `}>
                        {threat.level} - {((anomaly.threat_severity_index || 0.5) * 100).toFixed(0)}%
                      </span>
                    </div>

                    <div className="space-y-3 text-sm">
                      <div className="flex items-center gap-3">
                        <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="font-medium text-slate-700">Time:</span>
                        <span className="text-slate-600">
                          {formatTimestamp(anomaly.timestamp)} 
                          {anomaly.frame_count && ` (Frame ${anomaly.frame_count})`}
                        </span>
                      </div>
                      
                      {anomaly.details && (
                        <div className="flex items-start gap-3">
                          <svg className="w-4 h-4 text-slate-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <div>
                            <span className="font-medium text-slate-700">Details:</span>
                            <p className="text-slate-600 mt-1">{anomaly.details}</p>
                          </div>
                        </div>
                      )}
                      
                      {anomaly.reasoning_summary && (
                        <div className="flex items-start gap-3">
                          <svg className="w-4 h-4 text-slate-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                          </svg>
                          <div>
                            <span className="font-medium text-slate-700">AI Analysis:</span>
                            <p className="text-slate-600 italic mt-1 bg-slate-100 p-3 rounded-lg">{anomaly.reasoning_summary}</p>
                          </div>
                        </div>
                      )}

                      {/* Scores */}
                      <div className="flex gap-3 mt-4">
                        {anomaly.visual_score !== undefined && (
                          <div className="bg-blue-100 text-blue-800 px-3 py-2 rounded-lg text-xs font-semibold">
                            <div className="flex items-center gap-2">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                              </svg>
                              Visual: {(anomaly.visual_score * 100).toFixed(0)}%
                            </div>
                          </div>
                        )}
                        {anomaly.audio_score !== undefined && (
                          <div className="bg-purple-100 text-purple-800 px-3 py-2 rounded-lg text-xs font-semibold">
                            <div className="flex items-center gap-2">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M6.343 6.343a1 1 0 011.414 0L12 10.586l4.243-4.243a1 1 0 011.414 1.414L13.414 12l4.243 4.243a1 1 0 01-1.414 1.414L12 13.414l-4.243 4.243a1 1 0 01-1.414-1.414L10.586 12 6.343 7.757a1 1 0 010-1.414z" />
                              </svg>
                              Audio: {(anomaly.audio_score * 100).toFixed(0)}%
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Thumbnail */}
                  {anomaly.frame_file && (
                    <div className="ml-6">
                      <img
                        src={`/${anomaly.frame_file}`}
                        alt="Anomaly frame"
                        className="w-32 h-24 object-cover rounded-xl border border-slate-200 shadow-professional"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 mt-6">
                  <button
                    onClick={() => handleViewInVideo(anomaly)}
                    className="btn-modern px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-all duration-300 font-medium shadow-professional hover:shadow-lg transform hover:-translate-y-0.5"
                  >
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      View in Video
                    </div>
                  </button>
                  <button
                    onClick={() => handleShowDetails(anomaly)}
                    className="btn-modern px-4 py-2 bg-slate-600 text-white text-sm rounded-lg hover:bg-slate-700 transition-all duration-300 font-medium shadow-professional hover:shadow-lg transform hover:-translate-y-0.5"
                  >
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Show Details
                    </div>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Details Modal */}
      {selectedAnomaly && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="card-modern max-w-3xl w-full max-h-[80vh] overflow-y-auto p-8">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-slate-900">Anomaly Details</h3>
              <button
                onClick={() => setSelectedAnomaly(null)}
                className="w-10 h-10 bg-slate-100 hover:bg-slate-200 rounded-xl flex items-center justify-center transition-colors"
              >
                <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-slate-50 p-4 rounded-xl">
                  <span className="font-semibold text-slate-700">Frame:</span>
                  <p className="text-slate-900 text-lg">{selectedAnomaly.frame_count || 'Unknown'}</p>
                </div>
                <div className="bg-slate-50 p-4 rounded-xl">
                  <span className="font-semibold text-slate-700">Timestamp:</span>
                  <p className="text-slate-900 text-lg">{selectedAnomaly.timestamp?.toFixed(2) || 'Unknown'}s</p>
                </div>
                <div className="bg-slate-50 p-4 rounded-xl">
                  <span className="font-semibold text-slate-700">Threat Level:</span>
                  <p className="text-slate-900 text-lg">{((selectedAnomaly.threat_severity_index || 0.5) * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-slate-50 p-4 rounded-xl">
                  <span className="font-semibold text-slate-700">Visual Score:</span>
                  <p className="text-slate-900 text-lg">{((selectedAnomaly.visual_score || 0.5) * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-slate-50 p-4 rounded-xl">
                  <span className="font-semibold text-slate-700">Audio Score:</span>
                  <p className="text-slate-900 text-lg">{((selectedAnomaly.audio_score || 0.5) * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-slate-50 p-4 rounded-xl">
                  <span className="font-semibold text-slate-700">Video File:</span>
                  <p className="text-slate-900 text-sm break-all">{selectedAnomaly.video_file || 'Unknown'}</p>
                </div>
              </div>
              
              {selectedAnomaly.frame_file && (
                <div className="bg-slate-50 p-4 rounded-xl">
                  <span className="font-semibold text-slate-700">Frame File:</span>
                  <p className="text-slate-900 text-sm break-all">{selectedAnomaly.frame_file}</p>
                </div>
              )}
              
              {selectedAnomaly.reasoning_summary && (
                <div className="bg-slate-50 p-6 rounded-xl">
                  <span className="font-semibold text-slate-700 block mb-3">AI Analysis:</span>
                  <p className="text-slate-700 italic leading-relaxed">{selectedAnomaly.reasoning_summary}</p>
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
