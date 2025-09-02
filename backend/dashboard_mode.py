"""
Dashboard Mode Manager - Simplified session management for backend dashboard
Bypasses user-specific complexity for direct dashboard access
"""
import time
from datetime import datetime

class DashboardMode:
    """Simplified mode for backend dashboard - no login, direct access"""
    
    def __init__(self):
        self.dashboard_anomalies = []  # Simple list for dashboard display
        self.max_anomalies = 20  # Keep last 20 for display
        self.dashboard_username = "dashboard_user"
        self.session_metadata = {
            'total_anomalies': 0,
            'session_start': None,
            'last_anomaly': None
        }
    
    def is_dashboard_user(self, username: str) -> bool:
        """Check if this is a dashboard user (no login required)"""
        return username in ["dashboard_user", "demo_user", None, ""]
    
    def add_dashboard_anomaly(self, anomaly_data: dict) -> dict:
        """Add anomaly for dashboard display (simplified)"""
        # Simplified anomaly data for dashboard
        dashboard_anomaly = {
            'id': str(time.time()),
            'timestamp': anomaly_data.get('timestamp', time.time()),
            'frame_id': anomaly_data.get('frame_id', 0),
            'details': anomaly_data.get('details', ''),
            'frame_file': anomaly_data.get('frame_file'),
            'video_file': anomaly_data.get('video_file'),
            'tier1_result': anomaly_data.get('tier1_result', {}),
            'tier2_analysis': anomaly_data.get('tier2_analysis'),
            'threat_level': anomaly_data.get('tier2_analysis', {}).get('threat_severity_index', 0.5),
            'reasoning_summary': anomaly_data.get('tier2_analysis', {}).get('reasoning_summary', ''),
            'visual_score': anomaly_data.get('tier1_result', {}).get('confidence', 0.5),
            'audio_score': anomaly_data.get('tier1_result', {}).get('audio_detected', 0) * 0.5,
            'created_at': datetime.now().isoformat()
        }
        
        # Add to dashboard list
        self.dashboard_anomalies.insert(0, dashboard_anomaly)  # Most recent first
        
        # Keep only last N anomalies
        if len(self.dashboard_anomalies) > self.max_anomalies:
            self.dashboard_anomalies = self.dashboard_anomalies[:self.max_anomalies]
        
        # Update metadata
        self.session_metadata['total_anomalies'] += 1
        self.session_metadata['last_anomaly'] = dashboard_anomaly['created_at']
        
        return dashboard_anomaly
    
    def get_dashboard_anomalies(self) -> list:
        """Get anomalies for dashboard display"""
        return self.dashboard_anomalies
    
    def get_dashboard_stats(self) -> dict:
        """Get simple stats for dashboard"""
        return {
            'total_anomalies': self.session_metadata['total_anomalies'],
            'recent_anomalies': len(self.dashboard_anomalies),
            'session_start': self.session_metadata['session_start'],
            'last_anomaly': self.session_metadata['last_anomaly']
        }
    
    def clear_dashboard_data(self):
        """Clear dashboard data"""
        self.dashboard_anomalies.clear()
        self.session_metadata['total_anomalies'] = 0
        self.session_metadata['last_anomaly'] = None
    
    def start_dashboard_session(self):
        """Start a new dashboard session"""
        self.session_metadata['session_start'] = datetime.now().isoformat()

# Global dashboard mode instance
dashboard_mode = DashboardMode()
