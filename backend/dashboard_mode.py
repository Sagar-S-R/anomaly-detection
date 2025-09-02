"""
Dashboard Mode Manager - Simplified session management for backend dashboard
Bypasses user-specific complexity for direct dashboard access
"""
import time
from datetime import datetime

class DashboardMode:
    """Simplified mode for backend dashboard - no login, direct access"""
    
    def __init__(self):
        self.current_session_anomalies = []  # ONLY current session anomalies
        self.max_session_anomalies = 50  # Keep more for current session
        self.dashboard_username = "dashboard_user"
        self.current_session_id = None
        self.current_video_file = None
        self.session_metadata = {
            'session_anomalies': 0,  # Current session only
            'session_start': None,
            'last_anomaly': None,
            'monitoring_active': False
        }
    
    def is_dashboard_user(self, username: str) -> bool:
        """Check if this is a dashboard user (no login required)"""
        return username in ["dashboard_user", "demo_user", None, ""]
    
    def add_dashboard_anomaly(self, anomaly_data: dict) -> dict:
        """Add anomaly for CURRENT SESSION dashboard display only"""
        # Only add if we have an active monitoring session
        if not self.session_metadata.get('monitoring_active', False):
            print("⚠️ Dashboard: Ignoring anomaly - no active monitoring session")
            return None
            
        # Simplified anomaly data for current session dashboard
        dashboard_anomaly = {
            'id': str(time.time()),
            'timestamp': anomaly_data.get('timestamp', time.time()),
            'frame_id': anomaly_data.get('frame_id', 0),
            'session_id': anomaly_data.get('session_id', self.current_session_id),
            'details': anomaly_data.get('details', ''),
            'frame_file': anomaly_data.get('frame_file'),
            'video_file': anomaly_data.get('video_file', self.current_video_file),
            'tier1_result': anomaly_data.get('tier1_result', {}),
            'tier2_analysis': anomaly_data.get('tier2_analysis'),
            'threat_level': anomaly_data.get('tier2_analysis', {}).get('threat_severity_index', 0.5),
            'reasoning_summary': anomaly_data.get('tier2_analysis', {}).get('reasoning_summary', ''),
            'visual_score': anomaly_data.get('tier1_result', {}).get('confidence', 0.5),
            'audio_score': anomaly_data.get('tier1_result', {}).get('audio_detected', 0) * 0.5,
            'created_at': datetime.now().isoformat()
        }
        
        # Add to CURRENT SESSION list (most recent first)
        self.current_session_anomalies.insert(0, dashboard_anomaly)
        
        # Keep only recent anomalies from current session
        if len(self.current_session_anomalies) > self.max_session_anomalies:
            self.current_session_anomalies = self.current_session_anomalies[:self.max_session_anomalies]
        
        # Update current session metadata
        self.session_metadata['session_anomalies'] += 1
        self.session_metadata['last_anomaly'] = dashboard_anomaly['created_at']
        
        print(f"📊 Dashboard: Added anomaly #{self.session_metadata['session_anomalies']} to current session")
        
        return dashboard_anomaly
    
    def get_dashboard_anomalies(self) -> list:
        """Get CURRENT SESSION anomalies for dashboard display"""
        return self.current_session_anomalies
    
    def get_dashboard_stats(self) -> dict:
        """Get current session stats for dashboard"""
        return {
            'session_anomalies': self.session_metadata['session_anomalies'],
            'current_session_frames': len(self.current_session_anomalies),
            'session_start': self.session_metadata['session_start'],
            'last_anomaly': self.session_metadata['last_anomaly'],
            'monitoring_active': self.session_metadata.get('monitoring_active', False),
            'current_session_id': self.current_session_id,
            'current_video_file': self.current_video_file
        }
    
    def should_continue_session(self) -> bool:
        """Check if we should continue current session or start new one"""
        if not self.session_metadata.get('monitoring_active', False):
            return False
        
        # If session started recently (within last 2 minutes), continue it
        session_start = self.session_metadata.get('session_start')
        if session_start:
            try:
                start_time = datetime.fromisoformat(session_start)
                time_diff = datetime.now() - start_time
                # Continue session if it's been less than 2 minutes since start
                return time_diff.total_seconds() < 120
            except:
                return False
        
        return False
    
    def force_new_monitoring_session(self, session_id: str, video_file: str = None):
        """Force start a NEW monitoring session - always clears previous anomalies"""
        print(f"🔄 Dashboard: FORCE starting NEW monitoring session {session_id}")
        
        # Clear previous session data
        self.current_session_anomalies.clear()
        
        # Set new session info
        self.current_session_id = session_id
        self.current_video_file = video_file
        self.session_metadata = {
            'session_anomalies': 0,
            'session_start': datetime.now().isoformat(),
            'last_anomaly': None,
            'monitoring_active': True
        }
        
        print(f"✅ Dashboard: FORCED new session ready - anomaly frames cleared")
    
    def start_new_monitoring_session(self, session_id: str, video_file: str = None):
        """Start a NEW monitoring session - clears previous anomalies"""
        print(f"🔄 Dashboard: Starting NEW monitoring session {session_id}")
        
        # Clear previous session data
        self.current_session_anomalies.clear()
        
        # Set new session info
        self.current_session_id = session_id
        self.current_video_file = video_file
        self.session_metadata = {
            'session_anomalies': 0,
            'session_start': datetime.now().isoformat(),
            'last_anomaly': None,
            'monitoring_active': True
        }
        
        print(f"✅ Dashboard: New session ready - anomaly frames cleared")
        
    def stop_monitoring_session(self):
        """Stop current monitoring session"""
        print(f"🛑 Dashboard: Stopping monitoring session {self.current_session_id}")
        self.session_metadata['monitoring_active'] = False
        
    def get_current_session_video(self) -> str:
        """Get current session video file for playback"""
        return self.current_video_file
    
    def clear_dashboard_data(self):
        """Clear current session dashboard data"""
        self.current_session_anomalies.clear()
        self.session_metadata['session_anomalies'] = 0
        self.session_metadata['last_anomaly'] = None
        self.session_metadata['monitoring_active'] = False
        print("🧹 Dashboard: Current session data cleared")
    
    def start_dashboard_session(self):
        """Start dashboard session - REMOVED sample population"""
        # Just initialize metadata - no sample data
        if not self.session_metadata.get('session_start'):
            self.session_metadata['session_start'] = datetime.now().isoformat()
        
        print("✅ Dashboard: Ready for live monitoring (no sample data)")
    
    # REMOVED _populate_sample_anomalies - we only want LIVE session data

# Global dashboard mode instance
dashboard_mode = DashboardMode()
