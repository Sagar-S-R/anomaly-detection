// API Configuration for deployment flexibility
const API_CONFIG = {
  // Use environment variables with fallback to localhost for development
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8000',
  
  // API endpoints
  ENDPOINTS: {
    LOGIN: '/api/login',
    REGISTER: '/api/register',
    UPLOAD_VIDEO: '/upload_video',
    STATS: '/api/stats',
    SESSIONS: '/api/sessions',
    ANOMALIES: '/api/anomalies',
    DOWNLOAD_SESSION: '/api/download_session',
    VIDEO_STREAM: '/video_stream',
    DOWNLOAD_SESSION_DATA: '/download-session-data'
  },
  
  // WebSocket endpoints
  WS_ENDPOINTS: {
    LIVE_MONITORING: '/ws/live_monitoring',
    CCTV_MONITORING: '/ws/cctv_monitoring',
    UPLOAD_MONITORING: '/ws/upload_monitoring'
  }
};

// Helper functions to build URLs
export const getApiUrl = (endpoint) => `${API_CONFIG.BASE_URL}${endpoint}`;
export const getWsUrl = (endpoint, username) => {
  const separator = endpoint.includes('?') ? '&' : '?';
  return `${API_CONFIG.WS_URL}${endpoint}${separator}username=${encodeURIComponent(username)}`;
};

export default API_CONFIG;
