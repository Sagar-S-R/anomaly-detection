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
      alert('NO VIDEO RECORDING AVAILABLE. START MONITORING FIRST.');
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
      alert('NO ANOMALIES DETECTED YET OR NO VIDEO AVAILABLE.');
    }
  };

  const handleJumpToTime = () => {
    const timestamp = parseFloat(customTimestamp);
    if (isNaN(timestamp)) {
      alert('PLEASE ENTER A VALID TIMESTAMP IN SECONDS');
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
    <div className="cyber-card p-6 reveal-up">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <div className="w-10 h-10 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl flex items-center justify-center border border-purple-400/30">
          <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h2 className="cyber-title text-xl">VIDEO PLAYBACK</h2>
          <p className="cyber-subtitle text-sm">Review recorded sessions</p>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="space-y-3 mb-6">
        <button
          onClick={handleLoadLatest}
          className="cyber-btn-primary w-full px-6 py-4 rounded-xl font-mono font-bold tracking-wider uppercase"
        >
          <div className="flex items-center justify-center gap-3">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v2H8V5z" />
            </svg>
            LOAD LATEST RECORDING
          </div>
        </button>
        
        <button
          onClick={handleJumpToAnomaly}
          className="cyber-btn-danger w-full px-6 py-4 rounded-xl font-mono font-bold tracking-wider uppercase"
        >
          <div className="flex items-center justify-center gap-3">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            JUMP TO LAST ANOMALY
          </div>
        </button>
      </div>

      {/* Custom Timestamp Jump */}
      <div className="border-t border-cyan-400/20 pt-6 mb-6">
        <label className="block text-sm font-bold text-gray-300 mb-3 font-mono tracking-wide">
          JUMP TO SPECIFIC TIME
        </label>
        <div className="flex gap-3">
          <input
            type="number"
            step="0.1"
            placeholder="Time in seconds"
            value={customTimestamp}
            onChange={(e) => setCustomTimestamp(e.target.value)}
            className="cyber-input flex-1 px-4 py-3 rounded-xl text-sm bg-gray-900/50 border border-cyan-400/30 text-cyan-400 font-mono"
          />
          <button
            onClick={handleJumpToTime}
            className="cyber-btn-secondary px-6 py-3 rounded-xl text-sm font-mono font-bold tracking-wider uppercase"
          >
            GO
          </button>
        </div>
      </div>

      {/* Video Player */}
      <div className="bg-black/90 rounded-2xl overflow-hidden border border-cyan-400/20 cyber-grid-bg">
        {videoError ? (
          <div className="aspect-video flex items-center justify-center bg-gray-900/80 text-white">
            <div className="text-center p-8">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-xl mb-2 font-bold font-mono text-red-400">VIDEO COULD NOT BE LOADED</p>
              <p className="text-sm text-gray-400 mt-1 font-mono">
                {currentVideoFile ? `FILE: ${currentVideoFile}` : 'NO VIDEO FILE SPECIFIED'}
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
          <div className="aspect-video flex items-center justify-center bg-gray-900/50 text-gray-300 border-2 border-dashed border-purple-400/30 cyber-grid-bg rounded-xl">
            <div className="text-center p-8">
              <svg className="w-16 h-16 text-purple-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 011 1v1a1 1 0 01-1 1v9a1 1 0 01-1 1H4a1 1 0 01-1-1V7a1 1 0 01-1-1V5a1 1 0 011-1h3z" />
              </svg>
              <p className="text-xl font-bold mb-2 font-mono text-purple-400">NO VIDEO LOADED</p>
              <p className="text-sm text-gray-400 font-mono">Load a recording to begin playback</p>
            </div>
          </div>
        )}
      </div>

      {/* Video Info */}
      {currentVideoFile && (
        <div className="mt-6 cyber-panel p-4">
          <div className="flex items-center gap-3 mb-3">
            <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 011 1v1a1 1 0 01-1 1v9a1 1 0 01-1 1H4a1 1 0 01-1-1V7a1 1 0 01-1-1V5a1 1 0 011-1h3z" />
            </svg>
            <p className="cyber-subtitle text-sm">CURRENT VIDEO FILE:</p>
          </div>
          <p className="text-gray-300 break-all text-sm bg-black/40 p-3 rounded-lg border border-purple-400/20 font-mono">{currentVideoFile}</p>
        </div>
      )}

      {/* Playback Tips */}
            {/* Playback Tips */}
      <div className="mt-6 cyber-panel p-6">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-xl flex items-center justify-center flex-shrink-0 mt-1 border border-purple-400/30">
            <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p className="cyber-subtitle text-lg mb-4">PLAYBACK TIPS</p>
            <ul className="text-sm space-y-3 text-gray-300 font-mono">
              <li className="flex items-start gap-3">
                <span className="w-2 h-2 bg-purple-400 rounded-full mt-2 flex-shrink-0 cyber-pulse"></span>
                <span>Use video controls for play/pause/seek operations</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-2 h-2 bg-purple-400 rounded-full mt-2 flex-shrink-0 cyber-pulse"></span>
                <span>Jump to specific times using the timestamp input above</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-2 h-2 bg-purple-400 rounded-full mt-2 flex-shrink-0 cyber-pulse"></span>
                <span>Click anomaly "View in Video" buttons for quick navigation</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayback;
