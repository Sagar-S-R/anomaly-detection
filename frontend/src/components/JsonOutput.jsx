import React, { useState } from 'react';

const JsonOutput = ({ jsonData }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatJson = (data) => {
    if (!data) return 'Waiting for data...';
    return JSON.stringify(data, null, 2);
  };

  const getDataSummary = (data) => {
    if (!data) return 'No data';
    
    const keys = Object.keys(data);
    const summary = [];
    
    if (data.status) summary.push(`Status: ${data.status}`);
    if (data.timestamp) summary.push(`Time: ${data.timestamp.toFixed(2)}s`);
    if (data.frame_count) summary.push(`Frame: ${data.frame_count}`);
    if (data.threat_severity_index) summary.push(`Threat: ${(data.threat_severity_index * 100).toFixed(0)}%`);
    
    return summary.length > 0 ? summary.join(' • ') : `${keys.length} fields`;
  };

  return (
    <div className="cyber-card overflow-hidden reveal-up border border-cyan-400/30">
      {/* Header */}
      <div 
        className="p-6 bg-gray-900/90 text-white cursor-pointer flex items-center justify-between hover:bg-gray-800/90 transition-all duration-300 border-b border-cyan-400/20"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gray-800/50 rounded-lg flex items-center justify-center border border-cyan-400/30">
            <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h2 className="cyber-subtitle text-lg">REAL-TIME DATA STREAM</h2>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-300 font-mono">
            {getDataSummary(jsonData)}
          </span>
          <div className="w-6 h-6 bg-gray-800/50 rounded-lg flex items-center justify-center border border-cyan-400/30">
            <svg className={`w-3 h-3 text-cyan-400 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>

      {/* Collapsible Content */}
      {isExpanded && (
        <div className="animate-slide-down">
          {/* Quick Info Bar */}
          {jsonData && (
            <div className="p-4 bg-gray-900/50 border-b border-cyan-400/20 grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-3">
                <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="font-semibold text-gray-300 font-mono">STATUS:</span>
                <span className={`px-3 py-1 rounded-xl text-xs font-bold font-mono tracking-wider uppercase border ${
                  jsonData.status === 'Suspected Anomaly' 
                    ? 'bg-red-500/20 text-red-400 border-red-400/40' 
                    : 'bg-green-500/20 text-green-400 border-green-400/40'
                }`}>
                  {jsonData.status || 'UNKNOWN'}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="font-semibold text-gray-300 font-mono">LAST UPDATE:</span>
                <span className="text-cyan-400 font-mono font-bold">
                  {new Date().toLocaleTimeString()}
                </span>
              </div>
            </div>
          )}

          {/* JSON Display */}
          <div className="p-6">
            <pre className="
              bg-black/90 text-green-400 p-6 rounded-xl text-xs overflow-x-auto
              max-h-64 cyber-scrollbar font-mono leading-relaxed shadow-inner border border-gray-700/30
            ">
              {formatJson(jsonData)}
            </pre>
          </div>

          {/* Data Insights */}
          {jsonData && (
            <div className="p-6 bg-gray-900/30 border-t border-cyan-400/20">
              <div className="flex items-center gap-3 mb-4">
                <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <h4 className="cyber-subtitle text-lg">DATA INSIGHTS</h4>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {jsonData.threat_severity_index !== undefined && (
                  <div className="bg-black/40 p-4 rounded-xl border border-red-400/30">
                    <div className="flex items-center gap-3 mb-2">
                      <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                      <div className="cyber-subtitle text-sm text-red-400">Threat Level</div>
                    </div>
                    <div className={`text-2xl font-bold font-mono ${
                      jsonData.threat_severity_index > 0.7 ? 'text-red-400' :
                      jsonData.threat_severity_index > 0.4 ? 'text-orange-400' : 'text-emerald-400'
                    }`}>
                      {(jsonData.threat_severity_index * 100).toFixed(0)}%
                    </div>
                  </div>
                )}
                
                {jsonData.visual_score !== undefined && (
                  <div className="bg-black/40 p-4 rounded-xl border border-purple-400/30">
                    <div className="flex items-center gap-3 mb-2">
                      <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      <div className="cyber-subtitle text-sm text-purple-400">Visual Score</div>
                    </div>
                    <div className="text-2xl font-bold text-purple-400 font-mono">
                      {(jsonData.visual_score * 100).toFixed(0)}%
                    </div>
                  </div>
                )}
                
                {jsonData.audio_score !== undefined && (
                  <div className="bg-black/40 p-4 rounded-xl border border-teal-400/30">
                    <div className="flex items-center gap-3 mb-2">
                      <svg className="w-5 h-5 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M6.343 6.343a1 1 0 011.414 0L12 10.586l4.243-4.243a1 1 0 011.414 1.414L13.414 12l4.243 4.243a1 1 0 01-1.414 1.414L12 13.414l-4.243 4.243a1 1 0 01-1.414-1.414L10.586 12 6.343 7.757a1 1 0 010-1.414z" />
                      </svg>
                      <div className="cyber-subtitle text-sm text-teal-400">Audio Score</div>
                    </div>
                    <div className="text-2xl font-bold text-teal-400 font-mono">
                      {(jsonData.audio_score * 100).toFixed(0)}%
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Status Indicator */}
      <div className="px-6 py-4 bg-black/40 border-t border-cyan-400/20 flex items-center justify-between text-sm">
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${
            jsonData ? 'bg-emerald-400 cyber-pulse' : 'bg-gray-500'
          }`}></div>
          <span className="text-gray-300 font-mono font-medium">
            {jsonData ? 'Receiving live data' : 'Waiting for data stream'}
          </span>
        </div>
        <span className="text-slate-500 text-xs">
          Click header to {isExpanded ? 'collapse' : 'expand'}
        </span>
      </div>
    </div>
  );
};

export default JsonOutput;
