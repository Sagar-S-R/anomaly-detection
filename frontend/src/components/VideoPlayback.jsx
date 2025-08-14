import React, { useRef, useState } from 'react';

const VideoPlayback = ({ currentVideoFile, onLoadLatest, onJumpToAnomaly }) => {
  const videoRef = useRef(null);
  const [isVideoLoaded, setIsVideoLoaded] = useState(false);
  const [videoError, setVideoError] = useState(false);
  const [customTimestamp, setCustomTimestamp] = useState('');

  const handleLoadLatest = () => {
    const videoFile = onLoadLatest();
    if (videoFile) {
      const video = videoRef.current;
      if (video) {
        video.src = `/${videoFile}`;
        setIsVideoLoaded(true);
        setVideoError(false);
        video.style.display = 'block';
      }
    } else {
      alert('No video recording available. Start monitoring first.');
    }
  };

  const handleJumpToAnomaly = () => {
    const jumpData = onJumpToAnomaly();
    if (jumpData && jumpData.videoFile && jumpData.timestamp) {
      const video = videoRef.current;
      if (video) {
        video.src = `/${jumpData.videoFile}`;
        video.style.display = 'block';
        setIsVideoLoaded(true);
        setVideoError(false);
        
        // Wait for metadata to load before setting time
        video.onloadedmetadata = () => {
          video.currentTime = jumpData.timestamp;
          video.play();
        };
      }
    } else {
      alert('No anomalies detected yet or no video available.');
    }
  };

  const handleJumpToTime = () => {
    const timestamp = parseFloat(customTimestamp);
    if (isNaN(timestamp)) {
      alert('Please enter a valid timestamp in seconds');
      return;
    }
    
    const video = videoRef.current;
    if (video && isVideoLoaded) {
      video.currentTime = timestamp;
      video.play();
    } else {
      alert('Please load a video first');
    }
  };

  const handleVideoError = () => {
    setVideoError(true);
    setIsVideoLoaded(false);
  };

  const handleVideoLoad = () => {
    setVideoError(false);
    setIsVideoLoaded(true);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        📹 Video Playback
      </h2>

      {/* Control Buttons */}
      <div className="space-y-3 mb-4">
        <button
          onClick={handleLoadLatest}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
        >
          📂 Load Latest Recording
        </button>
        
        <button
          onClick={handleJumpToAnomaly}
          className="w-full px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors font-medium"
        >
          🚨 Jump to Last Anomaly
        </button>
      </div>

      {/* Custom Timestamp Jump */}
      <div className="border-t pt-4 mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Jump to Specific Time
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            step="0.1"
            placeholder="Time in seconds"
            value={customTimestamp}
            onChange={(e) => setCustomTimestamp(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
          <button
            onClick={handleJumpToTime}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors text-sm"
          >
            Go
          </button>
        </div>
      </div>

      {/* Video Player */}
      <div className="bg-black rounded-lg overflow-hidden">
        {videoError ? (
          <div className="aspect-video flex items-center justify-center bg-gray-800 text-white">
            <div className="text-center">
              <p className="text-xl mb-2">⚠️</p>
              <p>Video could not be loaded</p>
              <p className="text-sm text-gray-400 mt-1">
                {currentVideoFile ? `File: ${currentVideoFile}` : 'No video file specified'}
              </p>
            </div>
          </div>
        ) : (
          <video
            ref={videoRef}
            controls
            className="w-full h-auto max-h-64"
            style={{ display: isVideoLoaded ? 'block' : 'none' }}
            onError={handleVideoError}
            onLoadedData={handleVideoLoad}
          >
            Your browser does not support the video tag.
          </video>
        )}

        {!isVideoLoaded && !videoError && (
          <div className="aspect-video flex items-center justify-center bg-gray-100 text-gray-500">
            <div className="text-center">
              <p className="text-4xl mb-2">🎬</p>
              <p className="text-lg">No video loaded</p>
              <p className="text-sm">Load a recording to begin playback</p>
            </div>
          </div>
        )}
      </div>

      {/* Video Info */}
      {currentVideoFile && (
        <div className="mt-4 p-3 bg-gray-50 rounded-md">
          <div className="text-sm">
            <p className="font-medium text-gray-700">Current Video:</p>
            <p className="text-gray-600 break-all">{currentVideoFile}</p>
          </div>
        </div>
      )}

      {/* Playback Tips */}
      <div className="mt-4 p-3 bg-blue-50 rounded-md">
        <div className="text-sm text-blue-800">
          <p className="font-medium mb-1">💡 Playback Tips:</p>
          <ul className="text-xs space-y-1 text-blue-700">
            <li>• Use video controls for play/pause/seek</li>
            <li>• Jump to specific times using the timestamp input</li>
            <li>• Click anomaly "View in Video" buttons for quick navigation</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayback;
