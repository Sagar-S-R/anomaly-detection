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
    if (threat > 0.7) return { 
      level: 'CRITICAL', 
      color: 'bg-red-500', 
      textColor: 'text-red-400', 
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-400/40'
    };
    if (threat > 0.4) return { 
      level: 'WARNING', 
      color: 'bg-orange-500', 
      textColor: 'text-orange-400', 
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-400/40'
    };
    return { 
      level: 'LOW', 
      color: 'bg-green-500', 
      textColor: 'text-green-400', 
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-400/40'
    };
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
    <div className="cyber-card p-8 reveal-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-2xl flex items-center justify-center border border-red-400/30">
            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div>
            <h2 className="cyber-title text-3xl">THREAT DETECTION LOG</h2>
            <p className="cyber-subtitle text-lg">Security anomalies and unusual activities</p>
          </div>
          <div className="bg-red-500/20 text-red-400 text-sm font-bold font-mono px-6 py-2 rounded-xl border border-red-400/40">
            {anomalies.length}
          </div>
        </div>
        <div className="flex gap-3">
          {/* Sort Controls */}
          <select 
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="cyber-input px-4 py-3 rounded-xl text-sm bg-gray-900/50 border border-cyan-400/30 text-cyan-400 font-mono"
          >
            <option value="timestamp">Sort by Time</option>
            <option value="severity">Sort by Severity</option>
          </select>
          
          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            className="cyber-btn-secondary px-6 py-3 rounded-xl text-sm font-mono font-bold tracking-wider uppercase flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            REFRESH
          </button>
        </div>
      </div>

      {/* Anomaly List */}
      {sortedAnomalies.length === 0 ? (
        <div className="text-center py-16 bg-gray-900/30 rounded-2xl border border-green-400/20">
          <div className="w-20 h-20 bg-green-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-green-400/40">
            <svg className="w-10 h-10 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <p className="text-2xl text-green-400 mb-3 font-bold font-mono">ALL SYSTEMS SECURE</p>
          <p className="text-gray-300 text-lg font-mono">No security anomalies detected</p>
          <p className="text-gray-400 text-sm mt-2 font-mono">System operating within normal parameters</p>
        </div>
      ) : (
        <div className="space-y-4 max-h-96 overflow-y-auto cyber-scrollbar">
          {sortedAnomalies.map((anomaly, index) => {
            const threat = getThreatLevel(anomaly.threat_severity_index);
            
            return (
              <div
                key={anomaly.id || index}
                className={`
                  cyber-panel p-6 border-l-4 transition-all duration-300 hover:cyber-glow cursor-pointer
                  ${threat.bgColor} ${threat.borderColor}
                `}
                onClick={() => handleShowDetails(anomaly)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg ${threat.color} flex items-center justify-center border ${threat.borderColor}`}>
                          <span className="text-white text-sm font-bold font-mono">
                            {sortedAnomalies.length - index}
                          </span>
                        </div>
                        <h4 className="font-bold text-xl text-gray-100 font-mono tracking-wide">
                          THREAT #{sortedAnomalies.length - index}
                        </h4>
                      </div>
                      <span className={`
                        px-4 py-2 rounded-xl text-sm font-bold font-mono tracking-wider uppercase border
                        ${threat.textColor} ${threat.bgColor} ${threat.borderColor}
                      `}>
                        {threat.level} - {((anomaly.threat_severity_index || 0.5) * 100).toFixed(0)}%
                      </span>
                      
                      {/* Tier 2 Analysis Status */}
                      {anomaly.tier2_analysis ? (
                        <span className="px-3 py-2 rounded-xl text-sm font-bold font-mono bg-green-500/20 text-green-400 border border-green-400/40">
                          ✅ AI ANALYZED
                        </span>
                      ) : (
                        <span className="px-3 py-2 rounded-xl text-sm font-bold font-mono bg-yellow-500/20 text-yellow-400 border border-yellow-400/40 cyber-pulse">
                          ⏳ ANALYZING...
                        </span>
                      )}
                    </div>

                    <div className="space-y-3 text-sm">
                      <div className="flex items-center gap-3">
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="font-medium text-gray-300 font-mono">TIME:</span>
                        <span className="text-cyan-400 font-mono">
                          {formatTimestamp(anomaly.timestamp)} 
                          {anomaly.frame_count && ` (Frame ${anomaly.frame_count})`}
                        </span>
                      </div>
                      
                      {anomaly.details && (
                        <div className="flex items-start gap-3">
                          <svg className="w-4 h-4 text-gray-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <div>
                            <span className="font-medium text-gray-300 font-mono">DETAILS:</span>
                            <p className="text-gray-400 mt-1 font-mono text-sm">{anomaly.details}</p>
                          </div>
                        </div>
                      )}
                      
                      {anomaly.reasoning_summary && (
                        <div className="flex items-start gap-3">
                          <svg className="w-4 h-4 text-gray-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                          </svg>
                          <div>
                            <span className="font-medium text-gray-300 font-mono">AI ANALYSIS:</span>
                            <p className="text-gray-400 italic mt-1 bg-gray-900/50 p-3 rounded-lg border border-cyan-400/20 font-mono text-sm">{anomaly.reasoning_summary}</p>
                          </div>
                        </div>
                      )}

                      {/* Scores */}
                      <div className="flex flex-wrap gap-2 mt-4">
                        {anomaly.visual_score !== undefined && (
                          <div className="bg-blue-500/20 text-blue-400 px-3 py-2 rounded-lg text-xs font-bold font-mono border border-blue-400/40">
                            <div className="flex items-center gap-2">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                              </svg>
                              VISUAL: {(anomaly.visual_score * 100).toFixed(0)}%
                            </div>
                          </div>
                        )}
                        {anomaly.audio_score !== undefined && (
                          <div className="bg-purple-500/20 text-purple-400 px-3 py-2 rounded-lg text-xs font-bold font-mono border border-purple-400/40">
                            <div className="flex items-center gap-2">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728" />
                              </svg>
                              AUDIO: {(anomaly.audio_score * 100).toFixed(0)}%
                            </div>
                          </div>
                        )}
                        {anomaly.text_alignment_score !== undefined && (
                          <div className="bg-green-500/20 text-green-400 px-3 py-2 rounded-lg text-xs font-bold font-mono border border-green-400/40">
                            <div className="flex items-center gap-2">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                              TEXT: {(anomaly.text_alignment_score * 100).toFixed(0)}%
                            </div>
                          </div>
                        )}
                        {anomaly.multimodal_agreement !== undefined && (
                          <div className="bg-orange-500/20 text-orange-400 px-3 py-2 rounded-lg text-xs font-bold font-mono border border-orange-400/40">
                            <div className="flex items-center gap-2">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                              </svg>
                              MULTIMODAL: {(anomaly.multimodal_agreement * 100).toFixed(0)}%
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
                        className="w-32 h-24 object-cover rounded-xl border border-cyan-400/30 shadow-lg"
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
                    className="cyber-btn-primary px-4 py-2 text-sm rounded-xl font-mono font-bold tracking-wider uppercase"
                  >
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      VIEW VIDEO
                    </div>
                  </button>
                  <button
                    onClick={() => handleShowDetails(anomaly)}
                    className="cyber-btn-secondary px-4 py-2 text-sm rounded-xl font-mono font-bold tracking-wider uppercase"
                  >
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      DETAILS
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
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="cyber-panel max-w-3xl w-full max-h-[80vh] overflow-y-auto p-8 border border-cyan-400/30">
            <div className="flex justify-between items-center mb-6">
              <h3 className="cyber-title text-2xl">THREAT ANALYSIS</h3>
              <button
                onClick={() => setSelectedAnomaly(null)}
                className="w-10 h-10 bg-gray-800/50 hover:bg-red-500/20 rounded-xl flex items-center justify-center transition-colors border border-gray-600/30 hover:border-red-400/40"
              >
                <svg className="w-5 h-5 text-gray-400 hover:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-black/40 p-4 rounded-xl border border-red-400/30">
                  <span className="cyber-subtitle text-sm text-red-400">Frame:</span>
                  <p className="text-gray-200 text-lg font-mono">{selectedAnomaly.frame_count || 'Unknown'}</p>
                </div>
                <div className="bg-black/40 p-4 rounded-xl border border-cyan-400/30">
                  <span className="cyber-subtitle text-sm text-cyan-400">Timestamp:</span>
                  <p className="text-gray-200 text-lg font-mono">{selectedAnomaly.timestamp?.toFixed(2) || 'Unknown'}s</p>
                </div>
                <div className="bg-black/40 p-4 rounded-xl border border-red-400/30">
                  <span className="cyber-subtitle text-sm text-red-400">Threat Level:</span>
                  <p className="text-red-400 text-lg font-mono font-bold">{((selectedAnomaly.threat_severity_index || 0.5) * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-black/40 p-4 rounded-xl border border-purple-400/30">
                  <span className="cyber-subtitle text-sm text-purple-400">Visual Score:</span>
                  <p className="text-purple-400 text-lg font-mono font-bold">{((selectedAnomaly.visual_score || 0.5) * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-black/40 p-4 rounded-xl border border-teal-400/30">
                  <span className="cyber-subtitle text-sm text-teal-400">Audio Score:</span>
                  <p className="text-teal-400 text-lg font-mono font-bold">{((selectedAnomaly.audio_score || 0.5) * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-black/40 p-4 rounded-xl border border-gray-400/30">
                  <span className="cyber-subtitle text-sm text-gray-400">Video File:</span>
                  <p className="text-gray-300 text-sm break-all font-mono">{selectedAnomaly.video_file || 'Unknown'}</p>
                </div>
              </div>
              
              {selectedAnomaly.frame_file && (
                <div className="bg-black/40 p-4 rounded-xl border border-cyan-400/30">
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
