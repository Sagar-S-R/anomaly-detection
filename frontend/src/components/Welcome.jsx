import React from 'react';

const Welcome = ({ user, onContinue, onLogout }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black cyber-grid-bg">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/6 left-1/6 w-96 h-96 bg-cyan-400/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/6 right-1/6 w-96 h-96 bg-purple-400/5 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-teal-400/3 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s'}}></div>
      </div>

      <div className="relative z-10 container mx-auto px-6 py-12">
        {/* Header */}
        <div className="flex justify-between items-center mb-12">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-cyan-400/20 to-teal-400/20 rounded-2xl flex items-center justify-center border border-cyan-400/30 cyber-glow">
              <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h1 className="cyber-title text-4xl">ANOMALY DETECTION</h1>
              <p className="cyber-subtitle text-lg">Advanced Security Monitoring System</p>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="cyber-btn-secondary px-6 py-3 rounded-xl font-mono font-bold tracking-wider uppercase"
          >
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              LOGOUT
            </div>
          </button>
        </div>

        {/* Welcome Section */}
        <div className="text-center mb-16">
          <div className="cyber-panel p-12 max-w-4xl mx-auto">
            <div className="mb-8">
              <h2 className="cyber-title text-5xl mb-4 bg-gradient-to-r from-cyan-400 to-teal-400 bg-clip-text text-transparent">
                WELCOME BACK
              </h2>
              <div className="flex items-center justify-center gap-3 mb-6">
                <div className="w-3 h-3 bg-green-400 rounded-full cyber-pulse"></div>
                <p className="cyber-subtitle text-2xl text-green-400">
                  {user.username.toUpperCase()}
                </p>
              </div>
              <p className="text-gray-300 text-lg font-mono leading-relaxed max-w-2xl mx-auto">
                Access granted to advanced security monitoring system. 
                Choose your monitoring mode to begin threat detection and analysis.
              </p>
            </div>

            {/* System Status */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
              <div className="bg-black/40 p-6 rounded-xl border border-green-400/30">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center border border-green-400/40">
                    <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="cyber-subtitle text-sm text-green-400">SYSTEM STATUS</p>
                </div>
                <p className="text-green-400 font-mono font-bold text-xl">OPERATIONAL</p>
              </div>

              <div className="bg-black/40 p-6 rounded-xl border border-cyan-400/30">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-cyan-500/20 rounded-lg flex items-center justify-center border border-cyan-400/40">
                    <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <p className="cyber-subtitle text-sm text-cyan-400">AI MODULES</p>
                </div>
                <p className="text-cyan-400 font-mono font-bold text-xl">ACTIVE</p>
              </div>

              <div className="bg-black/40 p-6 rounded-xl border border-purple-400/30">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center border border-purple-400/40">
                    <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <p className="cyber-subtitle text-sm text-purple-400">SECURITY</p>
                </div>
                <p className="text-purple-400 font-mono font-bold text-xl">SECURED</p>
              </div>
            </div>

            {/* Continue Button */}
            <button
              onClick={onContinue}
              className="cyber-btn-primary px-12 py-6 rounded-xl font-mono font-bold tracking-wider uppercase text-xl hover:scale-105 transform transition-all duration-300"
            >
              <div className="flex items-center gap-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
                ENTER MONITORING SYSTEM
              </div>
            </button>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="cyber-card p-6 text-center">
            <div className="w-12 h-12 bg-gradient-to-br from-cyan-400/20 to-teal-400/20 rounded-xl flex items-center justify-center mx-auto mb-4 border border-cyan-400/30">
              <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="cyber-subtitle text-lg mb-2">LIVE MONITORING</h3>
            <p className="text-gray-400 text-sm font-mono">Real-time video stream analysis</p>
          </div>

          <div className="cyber-card p-6 text-center">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-xl flex items-center justify-center mx-auto mb-4 border border-purple-400/30">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 className="cyber-subtitle text-lg mb-2">CCTV INTEGRATION</h3>
            <p className="text-gray-400 text-sm font-mono">RTSP stream monitoring</p>
          </div>

          <div className="cyber-card p-6 text-center">
            <div className="w-12 h-12 bg-gradient-to-br from-orange-400/20 to-red-400/20 rounded-xl flex items-center justify-center mx-auto mb-4 border border-orange-400/30">
              <svg className="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
            </div>
            <h3 className="cyber-subtitle text-lg mb-2">VIDEO UPLOAD</h3>
            <p className="text-gray-400 text-sm font-mono">Batch processing analysis</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Welcome;
