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
    <div className="card-modern p-6 reveal-up">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <div className="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center">
          <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-900">Video Playback</h2>
          <p className="text-slate-500 text-sm">Review recorded sessions</p>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="space-y-3 mb-6">
        <button
          onClick={handleLoadLatest}
          className="btn-modern w-full px-6 py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all duration-300 font-semibold shadow-professional hover:shadow-lg transform hover:-translate-y-0.5"
        >
          <div className="flex items-center justify-center gap-3">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v2H8V5z" />
            </svg>
            Load Latest Recording
          </div>
        </button>
        
        <button
          onClick={handleJumpToAnomaly}
          className="btn-modern w-full px-6 py-4 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-all duration-300 font-semibold shadow-professional hover:shadow-lg transform hover:-translate-y-0.5"
        >
          <div className="flex items-center justify-center gap-3">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            Jump to Last Anomaly
          </div>
        </button>
      </div>

      {/* Custom Timestamp Jump */}
      <div className="border-t pt-6 mb-6">
        <label className="block text-sm font-semibold text-slate-700 mb-3">
          Jump to Specific Time
        </label>
        <div className="flex gap-3">
          <input
            type="number"
            step="0.1"
            placeholder="Time in seconds"
            value={customTimestamp}
            onChange={(e) => setCustomTimestamp(e.target.value)}
            className="flex-1 px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 text-sm bg-white shadow-professional"
          />
          <button
            onClick={handleJumpToTime}
            className="btn-modern px-6 py-3 bg-slate-600 text-white rounded-xl hover:bg-slate-700 transition-all duration-300 text-sm font-semibold shadow-professional hover:shadow-lg transform hover:-translate-y-0.5"
          >
            Go
          </button>
        </div>
      </div>

      {/* Video Player */}
      <div className="bg-slate-900 rounded-2xl overflow-hidden shadow-professional-lg">
        {videoError ? (
          <div className="aspect-video flex items-center justify-center bg-slate-800 text-white">
            <div className="text-center p-8">
              <svg className="w-16 h-16 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-xl mb-2 font-medium">Video could not be loaded</p>
              <p className="text-sm text-slate-400 mt-1">
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
          <div className="aspect-video flex items-center justify-center bg-slate-100 text-slate-500">
            <div className="text-center p-8">
              <svg className="w-16 h-16 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 011 1v1a1 1 0 01-1 1v9a1 1 0 01-1 1H4a1 1 0 01-1-1V7a1 1 0 01-1-1V5a1 1 0 011-1h3z" />
              </svg>
              <p className="text-xl font-medium mb-2">No video loaded</p>
              <p className="text-sm text-slate-400">Load a recording to begin playback</p>
            </div>
          </div>
        )}
      </div>

      {/* Video Info */}
      {currentVideoFile && (
        <div className="mt-6 p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center gap-3 mb-2">
            <svg className="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 011 1v1a1 1 0 01-1 1v9a1 1 0 01-1 1H4a1 1 0 01-1-1V7a1 1 0 01-1-1V5a1 1 0 011-1h3z" />
            </svg>
            <p className="font-semibold text-slate-700">Current Video:</p>
          </div>
          <p className="text-slate-600 break-all text-sm bg-white p-3 rounded-lg">{currentVideoFile}</p>
        </div>
      )}

      {/* Playback Tips */}
      <div className="mt-6 p-6 bg-blue-50 rounded-xl border border-blue-200">
        <div className="flex items-start gap-4">
          <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p className="font-semibold text-blue-900 mb-3">Playback Tips</p>
            <ul className="text-sm space-y-2 text-blue-800">
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                <span>Use video controls for play/pause/seek operations</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                <span>Jump to specific times using the timestamp input above</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
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
