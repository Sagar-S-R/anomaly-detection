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
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div 
        className="p-4 bg-gray-800 text-white cursor-pointer flex items-center justify-between hover:bg-gray-700 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">📊</span>
          <h2 className="text-lg font-bold">Real-time JSON Data</h2>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-300">
            {getDataSummary(jsonData)}
          </span>
          <span className="text-xl">
            {isExpanded ? '▼' : '▶'}
          </span>
        </div>
      </div>

      {/* Collapsible Content */}
      {isExpanded && (
        <div className="animate-slide-down">
          {/* Quick Info Bar */}
          {jsonData && (
            <div className="p-3 bg-gray-50 border-b grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-600">Status:</span>
                <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                  jsonData.status === 'Suspected Anomaly' 
                    ? 'bg-red-100 text-red-800' 
                    : 'bg-green-100 text-green-800'
                }`}>
                  {jsonData.status || 'Unknown'}
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-600">Last Update:</span>
                <span className="ml-2 text-gray-800">
                  {new Date().toLocaleTimeString()}
                </span>
              </div>
            </div>
          )}

          {/* JSON Display */}
          <div className="p-4">
            <pre className="
              bg-gray-900 text-green-400 p-4 rounded-lg text-xs overflow-x-auto
              max-h-64 custom-scrollbar font-mono leading-relaxed
            ">
              {formatJson(jsonData)}
            </pre>
          </div>

          {/* Data Insights */}
          {jsonData && (
            <div className="p-4 bg-blue-50 border-t">
              <h4 className="font-medium text-blue-900 mb-2">📈 Data Insights</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                {jsonData.threat_severity_index !== undefined && (
                  <div className="bg-white p-2 rounded">
                    <div className="font-medium text-gray-700">Threat Level</div>
                    <div className={`text-lg font-bold ${
                      jsonData.threat_severity_index > 0.7 ? 'text-red-600' :
                      jsonData.threat_severity_index > 0.4 ? 'text-orange-600' : 'text-green-600'
                    }`}>
                      {(jsonData.threat_severity_index * 100).toFixed(0)}%
                    </div>
                  </div>
                )}
                
                {jsonData.visual_score !== undefined && (
                  <div className="bg-white p-2 rounded">
                    <div className="font-medium text-gray-700">Visual Score</div>
                    <div className="text-lg font-bold text-blue-600">
                      {(jsonData.visual_score * 100).toFixed(0)}%
                    </div>
                  </div>
                )}
                
                {jsonData.audio_score !== undefined && (
                  <div className="bg-white p-2 rounded">
                    <div className="font-medium text-gray-700">Audio Score</div>
                    <div className="text-lg font-bold text-purple-600">
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
      <div className="px-4 py-2 bg-gray-100 flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            jsonData ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
          }`}></div>
          <span className="text-gray-600">
            {jsonData ? 'Receiving data' : 'Waiting for data'}
          </span>
        </div>
        <span className="text-gray-500 text-xs">
          Click header to {isExpanded ? 'collapse' : 'expand'}
        </span>
      </div>
    </div>
  );
};

export default JsonOutput;
