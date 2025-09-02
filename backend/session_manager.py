"""
Session Manager - Centralized session and resource management
Replaces scattered global variables with thread-safe session management
HANDLES ALL CLEANUP AND RESOURCE MANAGEMENT
"""
import threading
import uuid
import time
import cv2
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import queue
import os

class SessionManager:
    """Thread-safe session manager - SINGLE SOURCE OF TRUTH for all session management"""
    
    def __init__(self):
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._camera_lock = threading.Lock()
        self._active_cameras = set()
        self._websocket_connections: Dict[str, Any] = {}
        
        # Shared queues for multimodal fusion
        self.video_queue = queue.Queue(maxsize=30)
        self.audio_queue = queue.Queue(maxsize=50) 
        self.fusion_results_queue = queue.Queue(maxsize=20)
        
        # Performance statistics - SINGLE SOURCE
        self.performance_stats = {
            "frames_captured": 0,
            "frames_processed": 0,
            "audio_chunks_captured": 0,
            "audio_transcribed": 0,
            "fusion_video_audio": 0,
            "fusion_video_only": 0,
            "tier1_anomalies_detected": 0,
            "tier2_analyses_triggered": 0,
            "tier2_analyses_completed": 0,
            "tier2_analyses_failed": 0,
            "sessions_created": 0,
            "sessions_completed": 0,
            "pipeline_start_time": None
        }
        
        # Standard timeout for ALL operations
        self.STANDARD_TIMEOUT = 3.0
        
        print("🏗️ SessionManager initialized - ready for session management")
    
    def create_session(self, username: str, session_type: str = "live_stream") -> str:
        """Create a new processing session with all required resources"""
        with self._lock:
            session_id = str(uuid.uuid4())
            
            session_data = {
                'session_id': session_id,
                'username': username,
                'session_type': session_type,
                'created_at': datetime.now(),
                'status': 'initializing',
                'stop_event': threading.Event(),
                'threads': [],
                'resources': {
                    'video_cap': None,
                    'video_writer': None,
                    'audio_stream': None,
                    'camera_index': None,
                    'video_filename': None
                },
                'metadata': {
                    'video_file': None,
                    'start_time': time.time(),
                    'frame_count': 0,
                    'anomaly_count': 0,
                    'last_activity': time.time()
                },
                'cleanup_callbacks': []  # Custom cleanup functions
            }
            
            self._sessions[session_id] = session_data
            self.performance_stats["sessions_created"] += 1
            
            # Initialize pipeline timer if first session
            if self.performance_stats["pipeline_start_time"] is None:
                self.performance_stats["pipeline_start_time"] = time.time()
            
            print(f"✅ Session created: {session_id} for user {username} ({session_type})")
            return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                # Update last activity
                session['metadata']['last_activity'] = time.time()
            return session
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data with automatic activity tracking"""
        with self._lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                
                # Handle nested updates
                for key, value in updates.items():
                    if key in ['resources', 'metadata'] and isinstance(value, dict):
                        session[key].update(value)
                    else:
                        session[key] = value
                
                # Always update activity
                session['metadata']['last_activity'] = time.time()
                return True
            return False
    
    def add_session_thread(self, session_id: str, thread: threading.Thread) -> bool:
        """Add a thread to session tracking with automatic management"""
        with self._lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session['threads'].append(thread)
                
                # Set thread name for better debugging
                if not thread.name or thread.name.startswith('Thread-'):
                    thread.name = f"{session['session_type']}_{len(session['threads'])}_{session_id[:8]}"
                
                print(f"📎 Thread added to session {session_id}: {thread.name}")
                return True
            
            print(f"❌ Cannot add thread - session {session_id} not found")
            return False
    
    def add_cleanup_callback(self, session_id: str, callback_func, *args) -> bool:
        """Add custom cleanup function for session"""
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id]['cleanup_callbacks'].append((callback_func, args))
                return True
            return False
    
    def set_session_resources(self, session_id: str, **resources) -> bool:
        """Set multiple session resources at once"""
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id]['resources'].update(resources)
                print(f"📦 Resources updated for session {session_id}: {list(resources.keys())}")
                return True
            return False
    
    def acquire_camera(self, session_id: str, camera_index: int = 0) -> bool:
        """Thread-safe camera acquisition with automatic management"""
        with self._camera_lock:
            if camera_index in self._active_cameras:
                print(f"❌ Camera {camera_index} already in use by another session")
                return False
            
            # Try to actually open the camera before claiming it
            test_cap = None
            try:
                test_cap = cv2.VideoCapture(camera_index)
                if not test_cap.isOpened():
                    print(f"❌ Camera {camera_index} cannot be opened")
                    return False
                
                # Quick test read
                ret, _ = test_cap.read()
                if not ret:
                    print(f"❌ Camera {camera_index} cannot read frames")
                    return False
                
                test_cap.release()
                
            except Exception as e:
                print(f"❌ Camera {camera_index} test failed: {e}")
                if test_cap:
                    test_cap.release()
                return False
            
            # Camera is working - claim it
            self._active_cameras.add(camera_index)
            
            # Update session with camera info
            with self._lock:
                if session_id in self._sessions:
                    self._sessions[session_id]['resources']['camera_index'] = camera_index
                    self._sessions[session_id]['status'] = 'camera_acquired'
            
            print(f"📷 Camera {camera_index} acquired by session {session_id}")
            return True
    
    def release_camera(self, session_id: str) -> None:
        """Release camera for session with cleanup"""
        with self._camera_lock:
            with self._lock:
                if session_id in self._sessions:
                    camera_index = self._sessions[session_id]['resources'].get('camera_index')
                    if camera_index is not None:
                        self._active_cameras.discard(camera_index)
                        self._sessions[session_id]['resources']['camera_index'] = None
                        print(f"📷 Camera {camera_index} released by session {session_id}")
    
    def register_websocket(self, username: str, websocket: Any) -> None:
        """Register WebSocket connection for user"""
        with self._lock:
            # Close any existing connection for this user
            if username in self._websocket_connections:
                print(f"⚠️ Replacing existing WebSocket for user: {username}")
            
            self._websocket_connections[username] = websocket
            print(f"📡 WebSocket registered for user: {username}")
    
    def unregister_websocket(self, username: str) -> None:
        """Unregister WebSocket connection"""
        with self._lock:
            if username in self._websocket_connections:
                del self._websocket_connections[username]
                print(f"📡 WebSocket unregistered for user: {username}")
    
    def get_websocket(self, username: str) -> Optional[Any]:
        """Get WebSocket connection for user"""
        with self._lock:
            return self._websocket_connections.get(username)
    
    def stop_session(self, session_id: str) -> bool:
        """Stop a specific session - SINGLE ENTRY POINT"""
        with self._lock:
            if session_id not in self._sessions:
                print(f"⚠️ Session {session_id} not found for stopping")
                return False
            
            session = self._sessions[session_id]
            if session['status'] == 'stopping':
                print(f"⚠️ Session {session_id} already stopping")
                return True
                
            session['status'] = 'stopping'
            
            # Signal threads to stop
            session['stop_event'].set()
            
            print(f"🛑 Stop signal sent to session: {session_id}")
            return True
    
    def cleanup_session(self, session_id: str, timeout: Optional[float] = None) -> bool:
        """CONSOLIDATED CLEANUP - HANDLES EVERYTHING"""
        if timeout is None:
            timeout = self.STANDARD_TIMEOUT
            
        with self._lock:
            if session_id not in self._sessions:
                print(f"⚠️ Session {session_id} not found for cleanup")
                return False
            
            session = self._sessions[session_id]
            cleanup_success = True
            
            print(f"🧹 CONSOLIDATED CLEANUP starting for session: {session_id}")
            
            # STEP 1: Signal stop if not already done
            if not session['stop_event'].is_set():
                session['stop_event'].set()
                print(f"🛑 Stop signal sent during cleanup")
            
            # STEP 2: Stop and wait for threads - GRACEFUL DEGRADATION
            threads = session.get('threads', [])
            if threads:
                print(f"⏳ Stopping {len(threads)} threads (timeout: {timeout}s)...")
                
                for i, thread in enumerate(threads):
                    if thread.is_alive():
                        try:
                            thread.join(timeout=timeout)
                            if thread.is_alive():
                                print(f"⚠️ Thread {thread.name} did not stop in {timeout}s (continuing cleanup)")
                                cleanup_success = False
                            else:
                                print(f"✅ Thread {thread.name} stopped cleanly")
                        except Exception as e:
                            print(f"❌ Error stopping thread {thread.name}: {e} (continuing cleanup)")
                            cleanup_success = False
                    else:
                        print(f"✅ Thread {thread.name} already stopped")
            
            # STEP 3: Release ALL resources - GRACEFUL DEGRADATION
            resources = session.get('resources', {})
            
            # Video capture cleanup
            if resources.get('video_cap'):
                try:
                    resources['video_cap'].release()
                    print("📹 Video capture released")
                except Exception as e:
                    print(f"⚠️ Error releasing video capture: {e} (continuing cleanup)")
                    cleanup_success = False
            
            # Video writer cleanup  
            if resources.get('video_writer'):
                try:
                    resources['video_writer'].release()
                    print("📼 Video writer released")
                except Exception as e:
                    print(f"⚠️ Error releasing video writer: {e} (continuing cleanup)")
                    cleanup_success = False
            
            # Audio stream cleanup
            if resources.get('audio_stream'):
                try:
                    resources['audio_stream'].stop()
                    print("🔊 Audio stream stopped")
                except Exception as e:
                    print(f"⚠️ Error stopping audio stream: {e} (continuing cleanup)")
                    cleanup_success = False
            
            # STEP 4: Custom cleanup callbacks - GRACEFUL DEGRADATION
            cleanup_callbacks = session.get('cleanup_callbacks', [])
            for callback_func, args in cleanup_callbacks:
                try:
                    callback_func(*args)
                    print(f"✅ Custom cleanup callback executed")
                except Exception as e:
                    print(f"⚠️ Custom cleanup callback failed: {e} (continuing cleanup)")
                    cleanup_success = False
            
            # STEP 5: Release camera - ALWAYS SUCCEEDS
            self.release_camera(session_id)
            
            # STEP 6: OpenCV cleanup - ALWAYS SUCCEEDS  
            try:
                cv2.destroyAllWindows()
            except:
                pass  # Silent fail for OpenCV cleanup
            
            # STEP 7: Final session removal
            session['status'] = 'cleaned'
            del self._sessions[session_id]
            self.performance_stats["sessions_completed"] += 1
            
            result_status = "✅ COMPLETE" if cleanup_success else "⚠️ PARTIAL"
            print(f"🧹 CONSOLIDATED CLEANUP {result_status} for session: {session_id}")
            
            return cleanup_success
    
    def stop_all_sessions(self) -> int:
        """Stop all active sessions - SINGLE COMMAND"""
        with self._lock:
            session_ids = list(self._sessions.keys())
            
        stopped_count = 0
        print(f"🛑 Stopping {len(session_ids)} active sessions...")
        
        for session_id in session_ids:
            if self.stop_session(session_id):
                stopped_count += 1
        
        print(f"🛑 Stop signals sent to {stopped_count} sessions")
        return stopped_count
    
    def cleanup_all_sessions(self, timeout: Optional[float] = None) -> bool:
        """MASTER CLEANUP - Handles everything across all sessions"""
        if timeout is None:
            timeout = self.STANDARD_TIMEOUT
            
        with self._lock:
            session_ids = list(self._sessions.keys())
        
        if not session_ids:
            print("🧹 No sessions to clean up")
            return True
        
        print(f"🧹 MASTER CLEANUP starting for {len(session_ids)} sessions...")
        
        # STEP 1: Stop all sessions first
        self.stop_all_sessions()
        
        # STEP 2: Wait a moment for graceful stops
        time.sleep(0.5)
        
        # STEP 3: Clean up each session
        cleanup_success = True
        for session_id in session_ids:
            if not self.cleanup_session(session_id, timeout):
                cleanup_success = False
        
        # STEP 4: Clear shared resources - ALWAYS SUCCEEDS
        self._clear_all_shared_resources()
        
        # STEP 5: Final state reset
        with self._lock:
            self._active_cameras.clear()
            self._websocket_connections.clear()
        
        result_status = "✅ COMPLETE" if cleanup_success else "⚠️ PARTIAL"
        print(f"🧹 MASTER CLEANUP {result_status} - All sessions processed")
        
        return cleanup_success
    
    def _clear_all_shared_resources(self) -> None:
        """Clear all shared queues and resources - ALWAYS SUCCEEDS"""
        try:
            # Clear all queues
            queues = [self.video_queue, self.audio_queue, self.fusion_results_queue]
            for queue_obj in queues:
                try:
                    while not queue_obj.empty():
                        queue_obj.get_nowait()
                except:
                    pass
            
            # Global OpenCV cleanup
            try:
                cv2.destroyAllWindows()
            except:
                pass
            
            print("🧹 Shared resources cleared")
            
        except Exception as e:
            print(f"⚠️ Shared resource cleanup error (non-critical): {e}")
    
    def create_worker_thread(self, session_id: str, target_func, args: tuple, name_suffix: str = "") -> Optional[threading.Thread]:
        """Create and manage worker thread with automatic tracking"""
        with self._lock:
            if session_id not in self._sessions:
                print(f"❌ Cannot create thread - session {session_id} not found")
                return None
            
            session = self._sessions[session_id]
            stop_event = session['stop_event']
            
            # Create thread with stop event automatically added
            thread_args = (*args, stop_event)
            thread = threading.Thread(target=target_func, args=thread_args)
            thread.daemon = True
            thread.name = f"{session['session_type']}_{name_suffix}_{session_id[:8]}"
            
            # Add to session tracking
            session['threads'].append(thread)
            
            print(f"🧵 Worker thread created: {thread.name}")
            return thread
    
    def start_session_workers(self, session_id: str, video_cap, video_writer, fps, audio_stream) -> bool:
        """Start all worker threads for a session - CONSOLIDATED WORKER MANAGEMENT"""
        try:
            session = self.get_session(session_id)
            if not session:
                return False
            
            # Store resources in session
            self.set_session_resources(
                session_id,
                video_cap=video_cap,
                video_writer=video_writer,
                audio_stream=audio_stream
            )
            
            # Import worker functions
            from app import video_capture_worker_session, audio_capture_worker_session, fusion_worker_session
            
            # Create and start video worker
            video_thread = self.create_worker_thread(
                session_id, 
                video_capture_worker_session,
                (video_cap, video_writer, fps),
                "video"
            )
            if video_thread:
                video_thread.start()
                print(f"🎬 Video worker started: {video_thread.name}")
            
            # Create and start audio worker  
            audio_thread = self.create_worker_thread(
                session_id,
                audio_capture_worker_session, 
                (self.audio_queue, audio_stream),
                "audio"
            )
            if audio_thread:
                audio_thread.start()
                print(f"🎤 Audio worker started: {audio_thread.name}")
            
            # Create and start fusion worker
            fusion_thread = self.create_worker_thread(
                session_id,
                fusion_worker_session,
                (),
                "fusion"
            )
            if fusion_thread:
                fusion_thread.start()
                print(f"🔀 Fusion worker started: {fusion_thread.name}")
            
            # Update session status
            self.update_session(session_id, {'status': 'active'})
            
            print(f"🚀 ALL WORKERS STARTED for session {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start workers for session {session_id}: {e}")
            # Cleanup on failure
            self.cleanup_session(session_id)
            return False
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active sessions with enhanced details"""
        with self._lock:
            active = []
            current_time = time.time()
            
            for session_id, session in self._sessions.items():
                if session['status'] in ['active', 'camera_acquired', 'initializing']:
                    # Calculate session uptime
                    uptime = current_time - session['metadata']['start_time']
                    
                    # Count alive threads
                    alive_threads = sum(1 for t in session['threads'] if t.is_alive())
                    
                    active.append({
                        'session_id': session_id,
                        'username': session['username'],
                        'session_type': session['session_type'],
                        'status': session['status'],
                        'created_at': session['created_at'].isoformat(),
                        'uptime_seconds': round(uptime, 1),
                        'total_threads': len(session['threads']),
                        'alive_threads': alive_threads,
                        'camera_index': session['resources'].get('camera_index'),
                        'frame_count': session['metadata'].get('frame_count', 0),
                        'anomaly_count': session['metadata'].get('anomaly_count', 0),
                        'video_file': session['resources'].get('video_filename')
                    })
            return active
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        with self._lock:
            active_sessions = len([s for s in self._sessions.values() if s['status'] in ['active', 'camera_acquired']])
            
            return {
                **self.performance_stats,
                'active_sessions': active_sessions,
                'total_sessions': len(self._sessions),
                'active_cameras': len(self._active_cameras),
                'websocket_connections': len(self._websocket_connections),
                'queue_sizes': {
                    'video': self.video_queue.qsize(),
                    'audio': self.audio_queue.qsize(),
                    'fusion_results': self.fusion_results_queue.qsize()
                }
            }
    
    def increment_stat(self, stat_name: str, amount: int = 1) -> None:
        """Thread-safe increment of performance statistics"""
        with self._lock:
            if stat_name in self.performance_stats:
                self.performance_stats[stat_name] += amount
                
                # Log significant milestones
                if stat_name == "tier1_anomalies_detected" and self.performance_stats[stat_name] % 10 == 0:
                    print(f"📊 Milestone: {self.performance_stats[stat_name]} total anomalies detected")
    
    def update_stats(self, stats_dict: Dict[str, Any]) -> None:
        """Thread-safe update of performance statistics"""
        with self._lock:
            for key, value in stats_dict.items():
                if key in self.performance_stats:
                    self.performance_stats[key] = value
                else:
                    # Add new stats if they don't exist
                    self.performance_stats[key] = value
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        with self._lock:
            health = {
                'status': 'healthy',
                'issues': [],
                'session_health': [],
                'resource_health': {
                    'cameras_available': True,
                    'queues_healthy': True,
                    'memory_usage': 'normal'
                }
            }
            
            # Check each session
            for session_id, session in self._sessions.items():
                session_health = {
                    'session_id': session_id,
                    'status': session['status'],
                    'threads_healthy': True,
                    'resources_healthy': True
                }
                
                # Check thread health
                dead_threads = [t for t in session['threads'] if not t.is_alive()]
                if dead_threads and session['status'] == 'active':
                    session_health['threads_healthy'] = False
                    health['issues'].append(f"Session {session_id} has {len(dead_threads)} dead threads")
                
                # Check resource health
                resources = session['resources']
                if resources.get('video_cap') and not resources['video_cap'].isOpened():
                    session_health['resources_healthy'] = False
                    health['issues'].append(f"Session {session_id} has disconnected video capture")
                
                health['session_health'].append(session_health)
            
            # Check queue health
            if any(q.qsize() > q.maxsize * 0.9 for q in [self.video_queue, self.audio_queue, self.fusion_results_queue]):
                health['resource_health']['queues_healthy'] = False
                health['issues'].append("One or more queues are near capacity")
            
            # Overall health status
            if health['issues']:
                health['status'] = 'degraded' if len(health['issues']) < 3 else 'unhealthy'
            
            return health

# Global session manager instance (thread-safe singleton)
session_manager = SessionManager()
