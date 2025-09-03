"""
Dedicated Backend Dashboard Application
Separate from main app.py to avoid frontend conflicts
Focused only on backend dashboard requirements
"""
import asyncio
import base64
import cv2
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List
import queue
import threading

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Import only the functions we need
from tier1.tier1_pipeline import run_tier1_continuous
from tier2.tier2_pipeline import run_tier2_continuous
from dashboard_mode import dashboard_mode

app = FastAPI(title="Backend Dashboard API")

# Simple session management for dashboard only
class DashboardSession:
    def __init__(self):
        self.session_id = None
        self.video_cap = None
        self.is_active = False
        self.websocket = None
        self.video_thread = None
        self.stop_event = threading.Event()
        self.frame_queue = queue.Queue(maxsize=10)
        
    def start_session(self, websocket: WebSocket):
        """Start a new dashboard session"""
        if self.is_active:
            self.stop_session()
            
        self.session_id = str(uuid.uuid4())
        self.websocket = websocket
        self.is_active = True
        self.stop_event.clear()
        
        # Initialize camera
        if self._init_camera():
            # Start video processing thread
            self.video_thread = threading.Thread(
                target=self._video_worker,
                daemon=True
            )
            self.video_thread.start()
            return True
        return False
    
    def stop_session(self):
        """Stop current dashboard session"""
        self.is_active = False
        self.stop_event.set()
        
        # Wait for thread to finish
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=2.0)
            
        # Release camera
        if self.video_cap:
            self.video_cap.release()
            self.video_cap = None
            
        self.websocket = None
        print(f"🛑 Dashboard session {self.session_id} stopped")
        
    def _init_camera(self) -> bool:
        """Initialize camera for dashboard"""
        try:
            self.video_cap = cv2.VideoCapture(0)
            if not self.video_cap.isOpened():
                print("❌ Dashboard: Could not open camera 0")
                return False
                
            # Configure camera
            self.video_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.video_cap.set(cv2.CAP_PROP_FPS, 30)
            
            print("✅ Dashboard: Camera initialized")
            return True
        except Exception as e:
            print(f"❌ Dashboard camera init error: {e}")
            return False
    
    def _video_worker(self):
        """Video processing worker for dashboard"""
        frame_count = 0
        print("🎬 Dashboard video worker started")
        
        while not self.stop_event.is_set() and self.is_active:
            try:
                ret, frame = self.video_cap.read()
                if not ret:
                    print("❌ Dashboard: Failed to read frame")
                    break
                    
                frame_count += 1
                
                # Process every 3rd frame for efficiency
                if frame_count % 3 == 0:
                    current_timestamp = time.time()
                    
                    # Add frame to queue for processing
                    frame_data = {
                        "frame_id": frame_count,
                        "timestamp": current_timestamp,
                        "frame": frame.copy()
                    }
                    
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame_data)
                        
                time.sleep(1/30.0)  # 30 FPS
                
            except Exception as e:
                print(f"❌ Dashboard video worker error: {e}")
                break
                
        print("🛑 Dashboard video worker stopped")

# Global dashboard session
dashboard_session = DashboardSession()

@app.on_event("startup")
async def startup_event():
    """Initialize dashboard on startup"""
    print("🎛️ Backend Dashboard Server Starting...")
    dashboard_mode.start_dashboard_session()

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Backend Dashboard Server Shutting Down...")
    dashboard_session.stop_session()

@app.get("/")
async def root():
    """Root endpoint - redirect to dashboard"""
    return {"message": "Backend Dashboard API", "dashboard": "/dashboard"}

@app.get("/dashboard")
async def serve_dashboard():
    """Serve the simplified dashboard HTML"""
    return FileResponse("simple_dashboard.html")

@app.post("/dashboard/new_session")
async def start_new_session():
    """Start a new monitoring session (clears old frames)"""
    new_session_id = str(uuid.uuid4())
    dashboard_mode.force_new_monitoring_session(new_session_id, f"dashboard_recording_{int(time.time())}.mp4")
    return {
        "success": True,
        "message": "New monitoring session started - old frames cleared",
        "session_id": new_session_id
    }

@app.get("/anomaly_events")
async def get_anomaly_events(username: str = "dashboard_user"):
    """Get current session anomaly events"""
    anomalies = dashboard_mode.get_dashboard_anomalies()
    return {"anomalies": anomalies}

@app.get("/video_stream")
async def video_stream():
    """Serve current frame as JPEG"""
    try:
        if not dashboard_session.is_active or not dashboard_session.video_cap:
            # Return placeholder image
            placeholder = create_placeholder_frame("No Video Feed")
            _, buffer = cv2.imencode('.jpg', placeholder)
            return buffer.tobytes()
            
        # Get latest frame
        ret, frame = dashboard_session.video_cap.read()
        if ret:
            # Resize for web display
            frame = cv2.resize(frame, (640, 480))
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            return buffer.tobytes()
        else:
            placeholder = create_placeholder_frame("Camera Error")
            _, buffer = cv2.imencode('.jpg', placeholder)
            return buffer.tobytes()
            
    except Exception as e:
        print(f"❌ Video stream error: {e}")
        placeholder = create_placeholder_frame("Stream Error")
        _, buffer = cv2.imencode('.jpg', placeholder)
        return buffer.tobytes()

def create_placeholder_frame(message: str):
    """Create a placeholder frame with message"""
    import numpy as np
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, message, (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    return frame

@app.websocket("/stream_video")
async def websocket_stream(websocket: WebSocket, username: str = "dashboard_user"):
    """WebSocket endpoint for real-time anomaly detection and streaming"""
    await websocket.accept()
    print(f"🔌 Dashboard WebSocket connected for: {username}")
    
    # Start dashboard session
    if not dashboard_session.start_session(websocket):
        await websocket.send_json({"error": "Failed to initialize camera"})
        return
    
    # Start monitoring session in dashboard_mode
    dashboard_mode.start_new_monitoring_session(
        dashboard_session.session_id, 
        f"dashboard_recording_{int(time.time())}.mp4"
    )
    
    try:
        # Main processing loop
        processed_frames = 0
        
        while dashboard_session.is_active:
            try:
                # Get frame from queue
                try:
                    frame_data = dashboard_session.frame_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                frame = frame_data["frame"]
                frame_id = frame_data["frame_id"]
                timestamp = frame_data["timestamp"]
                
                processed_frames += 1
                
                # Always run Tier 1 analysis for continuous reasoning
                tier1_result = None
                frame_reasoning = "Initializing analysis..."
                frame_status = "Processing"
                confidence_score = 0.0
                detected_objects = []
                
                try:
                    # Run Tier 1 analysis on every 3rd frame for continuous monitoring
                    tier1_result = run_tier1_continuous(frame, None)
                    frame_status = tier1_result.get("status", "Normal")
                    
                    # Extract FULL reasoning details from tier1_components
                    tier1_components = tier1_result.get("tier1_components", {})
                    
                    # Get FULL detailed analysis (not truncated summaries)
                    pose_analysis = tier1_components.get("pose_analysis", {}).get("summary", "No pose detected")
                    audio_analysis = tier1_components.get("audio_analysis", {}).get("summary", "No audio analysis") 
                    scene_analysis = tier1_components.get("scene_analysis", {}).get("summary", "Scene analyzed")
                    
                    # Get fusion details for more context
                    fusion_details = tier1_components.get("fusion_logic", {}).get("details", "Analysis complete")
                    
                    # Create COMPREHENSIVE reasoning with FULL details
                    frame_reasoning = f"""🎯 POSE ANALYSIS: {pose_analysis}
🎵 AUDIO ANALYSIS: {audio_analysis} 
🖼️ SCENE ANALYSIS: {scene_analysis}
⚖️ FUSION DECISION: {fusion_details}

📊 DETAILED STATUS: {frame_status}
🔍 FULL ANALYSIS: {tier1_result.get('details', 'No additional details')}"""
                    
                    confidence_score = tier1_result.get("confidence", 0.0)
                    detected_objects = tier1_result.get("detected_objects", [])
                    
                except Exception as e:
                    frame_reasoning = f"Analysis Error: {str(e)}"
                    frame_status = "Error"
                
                # Send EVERY PROCESSED frame with reasoning to WebSocket
                try:
                    display_frame = cv2.resize(frame, (640, 480))
                    _, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Create comprehensive frame data with reasoning
                    frame_data = {
                        "type": "continuous_frame",
                        "frame_data": frame_base64,
                        "frame_id": frame_id,
                        "timestamp": timestamp,
                        "status": frame_status,
                        "reasoning": frame_reasoning,
                        "confidence": confidence_score,
                        "detected_objects": detected_objects,
                        "is_anomaly": frame_status == "Suspected Anomaly",
                        "session_id": dashboard_session.session_id,
                        "analysis_time": datetime.now().strftime("%H:%M:%S")
                    }
                    
                    await websocket.send_json(frame_data)
                    
                except Exception as e:
                    print(f"❌ Error sending frame: {e}")
                    break
                
                # If anomaly detected, save and run Tier 2
                if tier1_result and tier1_result.get("status") == "Suspected Anomaly":
                    print(f"🚨 Dashboard: Anomaly detected at frame {frame_id}")
                    
                    # Save anomaly frame
                    anomaly_frame_path = f"anomaly_frames/dashboard_frame_{frame_id}_{int(timestamp)}.jpg"
                    cv2.imwrite(anomaly_frame_path, frame)
                    
                    # Add to dashboard mode with full reasoning
                    anomaly_data = {
                        "timestamp": timestamp,
                        "frame_id": frame_id,
                        "details": frame_reasoning,
                        "frame_file": anomaly_frame_path,
                        "session_id": dashboard_session.session_id,
                        "tier1_result": tier1_result,
                        "confidence": confidence_score,
                        "detected_objects": detected_objects,
                        "analysis_time": datetime.now().strftime("%H:%M:%S")
                    }
                    
                    dashboard_mode.add_dashboard_anomaly(anomaly_data)
                    
                    # Run Tier 2 analysis in background
                    asyncio.create_task(run_tier2_for_dashboard(frame, frame_id, timestamp, websocket))
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                print(f"❌ Processing error: {e}")
                break
                
    except WebSocketDisconnect:
        print("📡 Dashboard WebSocket disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        # Cleanup
        dashboard_session.stop_session()
        dashboard_mode.stop_monitoring_session()

# SIMPLIFIED - Only send continuous frames with reasoning, no complex Tier 2
async def run_tier2_for_dashboard(frame, frame_id: int, timestamp: float, websocket: WebSocket):
    """Simple Tier 2 analysis for dashboard anomaly"""
    try:
        print(f"🔬 Dashboard: Starting Tier 2 analysis for frame {frame_id}")
        
        # Run Tier 2 analysis  
        # For dashboard, we need to pass proper tier1_result structure
        tier1_result_for_tier2 = {
            "result": "anomaly", 
            "details": "Dashboard anomaly detection - frame analysis",
            "tier1_components": {
                "pose_analysis": {"anomaly_detected": False, "raw_score": 0, "summary": "No pose analysis"},
                "audio_analysis": {"transcript_text": "", "audio_detected": False, "confidence": 0}
            }
        }
        tier2_result = await asyncio.get_event_loop().run_in_executor(
            None, run_tier2_continuous, frame, None, tier1_result_for_tier2  # No audio for dashboard
        )
        
        print(f"✅ Dashboard: Tier 2 complete for frame {frame_id}")
        
        # Update anomaly in dashboard_mode
        anomalies = dashboard_mode.get_dashboard_anomalies()
        for anomaly in anomalies:
            if anomaly.get("frame_id") == frame_id:
                anomaly["tier2_analysis"] = tier2_result
                break
        
    except Exception as e:
        print(f"❌ Dashboard Tier 2 error: {e}")

@app.get("/debug/dashboard_status")
async def debug_dashboard_status():
    """Debug endpoint to check dashboard status"""
    return {
        "session_active": dashboard_session.is_active,
        "session_id": dashboard_session.session_id,
        "camera_active": dashboard_session.video_cap is not None,
        "monitoring_active": dashboard_mode.session_metadata.get('monitoring_active', False),
        "current_anomalies": len(dashboard_mode.get_dashboard_anomalies()),
        "dashboard_stats": dashboard_mode.get_dashboard_stats()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)  # Different port from main app
