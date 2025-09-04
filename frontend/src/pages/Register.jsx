import React, { useState } from 'react';
import { getApiUrl } from '../config/api';

const Register = ({ onRegister, onBackToLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    fullName: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    // Client-side validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      setIsLoading(false);
      return;
    }

    if (formData.username.length < 3) {
      setError('Username must be at least 3 characters');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(getApiUrl('/api/register'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
          email: formData.email,
          full_name: formData.fullName
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      if (data.success) {
        setSuccess('Registration successful! You can now login.');
        setTimeout(() => {
          onRegister(data.user);
        }, 2000);
      } else {
        setError('Registration failed. Please try again.');
      }
    } catch (error) {
      setError(error.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black flex items-center justify-center cyber-grid-bg">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-400/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-400/5 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <div className="relative z-10 w-full max-w-md p-8">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-purple-400/20 to-cyan-400/20 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-purple-400/30 cyber-glow">
            <svg className="w-10 h-10 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h1 className="cyber-title text-4xl mb-2">CREATE ACCOUNT</h1>
          <p className="cyber-subtitle text-lg">Join the Security Team</p>
        </div>

        {/* Registration Form */}
        <div className="cyber-panel p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Full Name Field */}
            <div>
              <label className="cyber-subtitle text-sm mb-2 block">FULL NAME</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <input
                  type="text"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-4 bg-black/40 border border-purple-400/30 rounded-xl text-gray-100 placeholder-gray-500 font-mono focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 focus:outline-none transition-all duration-300"
                  placeholder="Enter your full name"
                  required
                />
              </div>
            </div>

            {/* Username Field */}
            <div>
              <label className="cyber-subtitle text-sm mb-2 block">USERNAME</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m0 0a2 2 0 012 2m-2-2a2 2 0 00-2 2m2-2a2 2 0 012 2M9 7a2 2 0 00-2 2v6a2 2 0 002 2h6a2 2 0 002-2V9a2 2 0 00-2-2H9z" />
                  </svg>
                </div>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-4 bg-black/40 border border-cyan-400/30 rounded-xl text-gray-100 placeholder-gray-500 font-mono focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 focus:outline-none transition-all duration-300"
                  placeholder="Choose a username"
                  required
                />
              </div>
            </div>

            {/* Email Field */}
            <div>
              <label className="cyber-subtitle text-sm mb-2 block">EMAIL</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                  </svg>
                </div>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-4 bg-black/40 border border-green-400/30 rounded-xl text-gray-100 placeholder-gray-500 font-mono focus:border-green-400 focus:ring-2 focus:ring-green-400/20 focus:outline-none transition-all duration-300"
                  placeholder="Enter your email"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="cyber-subtitle text-sm mb-2 block">PASSWORD</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-4 bg-black/40 border border-orange-400/30 rounded-xl text-gray-100 placeholder-gray-500 font-mono focus:border-orange-400 focus:ring-2 focus:ring-orange-400/20 focus:outline-none transition-all duration-300"
                  placeholder="Create a password"
                  required
                />
              </div>
            </div>

            {/* Confirm Password Field */}
            <div>
              <label className="cyber-subtitle text-sm mb-2 block">CONFIRM PASSWORD</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-4 bg-black/40 border border-red-400/30 rounded-xl text-gray-100 placeholder-gray-500 font-mono focus:border-red-400 focus:ring-2 focus:ring-red-400/20 focus:outline-none transition-all duration-300"
                  placeholder="Confirm your password"
                  required
                />
              </div>
            </div>

            {/* Error/Success Messages */}
            {error && (
              <div className="p-4 bg-red-500/20 border border-red-400/40 rounded-xl">
                <p className="text-red-400 text-sm font-mono">{error}</p>
              </div>
            )}

            {success && (
              <div className="p-4 bg-green-500/20 border border-green-400/40 rounded-xl">
                <p className="text-green-400 text-sm font-mono">{success}</p>
              </div>
            )}

            {/* Register Button */}
            <button
              type="submit"
              disabled={isLoading}
              className={`
                w-full py-4 px-6 rounded-xl font-mono font-bold tracking-wider uppercase transition-all duration-300
                ${isLoading 
                  ? 'bg-gray-600/50 border-gray-500/40 text-gray-400 cursor-not-allowed' 
                  : 'cyber-btn-primary hover:scale-105 transform'
                }
              `}
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-3">
                  <div className="w-5 h-5 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin"></div>
                  CREATING ACCOUNT...
                </div>
              ) : (
                <div className="flex items-center justify-center gap-3">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                  CREATE ACCOUNT
                </div>
              )}
            </button>

            {/* Back to Login */}
            <div className="text-center">
              <button
                type="button"
                onClick={onBackToLogin}
                className="text-cyan-400 hover:text-cyan-300 font-mono text-sm transition-colors duration-300"
              >
                <div className="flex items-center justify-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                  BACK TO LOGIN
                </div>
              </button>
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-gray-500 text-xs font-mono">
            ANOMALY DETECTION SYSTEM v2.1.0
          </p>
          <p className="text-purple-400/70 text-xs font-mono mt-1">
            SECURE REGISTRATION PORTAL
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
