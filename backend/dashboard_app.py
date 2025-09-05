"""
Dedicated Backend Dashboard A# Import only the functions we need
from tier1.tier1_pipeline import run_tier1_continuous
from tier2.tier2_pipeline import run_tier2_continuous
from dashboard_mode import dashboard_modeication
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
import numpy as np

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Import only the functions we@app.get("/debug/latency_stats")
async def get_latency_stats():
    """Get current latency statistics"""
    return {
        "total_frames_processed": latency_stats['total_frames'],
        "avg_decode_time": sum(latency_stats['decode_times'][-100:]) / len(latency_stats['decode_times'][-100:]) if latency_stats['decode_times'] else 0,
        "avg_analysis_time": sum(latency_stats['analysis_times'][-100:]) / len(latency_stats['analysis_times'][-100:]) if latency_stats['analysis_times'] else 0,
        "avg_compression_time": sum(latency_stats['compression_times'][-100:]) / len(latency_stats['compression_times'][-100:]) if latency_stats['compression_times'] else 0,
        "avg_transmission_time": sum(latency_stats['transmission_times'][-100:]) / len(latency_stats['transmission_times'][-100:]) if latency_stats['transmission_times'] else 0,
        "avg_total_processing_time": sum(latency_stats['total_processing_times'][-100:]) / len(latency_stats['total_processing_times'][-100:]) if latency_stats['total_processing_times'] else 0,
        "current_fps": 15.0,  # Target FPS
        "timestamp": datetime.now().isoformat()
    }

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
        """Initialize for browser camera streaming (no local hardware)"""
        try:
            # Remove local camera initialization - will receive streams from browser
            print("✅ Dashboard: Ready for browser camera streaming")
            return True  # Always return True since we don't need local camera
        except Exception as e:
            print(f"❌ Dashboard camera init error: {e}")
            return False
    
    def _video_worker(self):
        """Video processing worker for dashboard (browser streaming)"""
        print("🎬 Dashboard video worker started (waiting for browser frames)")
        
        # Remove local camera reading loop - frames will come from WebSocket/browser
        while not self.stop_event.is_set() and self.is_active:
            # Just keep the worker alive for session management
            time.sleep(1.0)

# Global dashboard session
dashboard_session = DashboardSession()

# Global latency monitoring
latency_stats = {
    'total_frames': 0,
    'decode_times': [],
    'analysis_times': [],
    'compression_times': [],
    'transmission_times': [],
    'total_processing_times': []
}

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
    """Serve the dashboard HTML"""
    return FileResponse("dashboard.html")

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

@app.websocket("/stream_browser_video")
async def websocket_stream(websocket: WebSocket, username: str = "dashboard_user"):
    """WebSocket endpoint for browser-streamed real-time anomaly detection"""
    await websocket.accept()
    print(f"🔌 Dashboard WebSocket connected for: {username}")
    
    # Start dashboard session (no camera hardware needed)
    if not dashboard_session.start_session(websocket):
        await websocket.send_json({"error": "Failed to initialize session"})
        return
    
    # Start monitoring session in dashboard_mode
    dashboard_mode.start_new_monitoring_session(
        dashboard_session.session_id, 
        f"dashboard_recording_{int(time.time())}.mp4"
    )
    
    try:
        # Main processing loop
        processed_frames = 0
        last_frame_time = time.time()
        frame_interval = 1.0 / 15.0  # Limit to 15 FPS for smooth streaming
        
        while dashboard_session.is_active:
            frame_start_time = time.time()
            try:
                # Wait for browser frame data via WebSocket
                try:
                    message = await websocket.receive_text()
                    frame_data = json.loads(message)
                    
                    # Handle ping messages
                    if frame_data.get('type') == 'ping':
                        print(f"💓 Ping received from client at {frame_data.get('timestamp', time.time())}")
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": frame_data.get('timestamp', time.time())
                        })
                        print(f"💓 Pong sent to client")
                        continue
                    
                    if frame_data.get('type') == 'video_frame':
                        # Rate limiting - skip frames if too fast
                        current_time = time.time()
                        if current_time - last_frame_time < frame_interval:
                            continue  # Skip this frame to maintain smooth rate
                        
                        last_frame_time = current_time
                        
                        # ⏱️ LATENCY: Frame decode timing
                        decode_start = time.time()
                        frame_b64 = frame_data['frame']
                        frame_bytes = base64.b64decode(frame_b64)
                        nparr = np.frombuffer(frame_bytes, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        decode_time = time.time() - decode_start
                        latency_stats['decode_times'].append(decode_time)
                        
                        # Create frame data structure
                        frame_id = processed_frames + 1
                        timestamp = frame_data.get('timestamp', time.time())
                        
                    else:
                        continue  # Skip non-video messages
                        
                except Exception as e:
                    print(f"❌ Error receiving browser frame: {e}")
                    continue
                
                processed_frames += 1
                
                # OPTIMIZED: Run analysis less frequently for better performance
                tier1_result = None
                frame_reasoning = "Initializing analysis..."
                frame_status = "Processing"
                confidence_score = 0.0
                detected_objects = []
                
                try:
                    # ⏱️ LATENCY: Analysis timing
                    analysis_start = time.time()
                    # Run Tier 1 analysis on every 5th frame (instead of every 3rd)
                    if processed_frames % 5 == 0:
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
                    else:
                        # For non-analysis frames, provide basic status
                        frame_reasoning = f"Frame {processed_frames} - Live streaming active"
                        frame_status = "Live"
                        confidence_score = 0.0
                        detected_objects = []
                    
                    analysis_time = time.time() - analysis_start
                    latency_stats['analysis_times'].append(analysis_time)
                    
                except Exception as e:
                    frame_reasoning = f"Analysis Error: {str(e)}"
                    frame_status = "Error"
                
                # OPTIMIZED: Compress frame more aggressively for faster transmission
                try:
                    # ⏱️ LATENCY: Compression timing
                    compression_start = time.time()
                    display_frame = cv2.resize(frame, (640, 480))
                    _, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])  # Reduced quality
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    compression_time = time.time() - compression_start
                    latency_stats['compression_times'].append(compression_time)
                    
                    # OPTIMIZED: Send lighter frame data for smooth streaming
                    frame_data = {
                        "type": "continuous_frame",
                        "frame_data": frame_base64,
                        "frame_id": frame_id,
                        "timestamp": timestamp,
                        "status": frame_status,
                        "reasoning": frame_reasoning[:200] if len(frame_reasoning) > 200 else frame_reasoning,  # Limit text length
                        "confidence": confidence_score,
                        "detected_objects": detected_objects[:5] if len(detected_objects) > 5 else detected_objects,  # Limit objects
                        "is_anomaly": frame_status == "Suspected Anomaly",
                        "session_id": dashboard_session.session_id,
                        "analysis_time": datetime.now().strftime("%H:%M:%S")
                    }
                    
                    # Check WebSocket connection state before sending
                    if websocket.client_state.name != 'CONNECTED':
                        print(f"🔌 WebSocket not connected (state: {websocket.client_state.name}), stopping frame processing")
                        break
                    
                    # ⏱️ LATENCY: Transmission timing
                    transmission_start = time.time()
                    await websocket.send_json(frame_data)
                    transmission_time = time.time() - transmission_start
                    latency_stats['transmission_times'].append(transmission_time)
                    
                    # ⏱️ LATENCY: Total processing time
                    total_processing_time = time.time() - frame_start_time
                    latency_stats['total_processing_times'].append(total_processing_time)
                    latency_stats['total_frames'] += 1
                    
                    # ⏱️ LATENCY: End-to-end latency (browser to server)
                    browser_timestamp = frame_data.get('timestamp', time.time())
                    end_to_end_latency = time.time() - browser_timestamp
                    print(f"⏱️ Frame {frame_id} - E2E: {end_to_end_latency:.3f}s | Decode: {decode_time:.3f}s | Analysis: {analysis_time:.3f}s | Compress: {compression_time:.3f}s | Transmit: {transmission_time:.3f}s | Total: {total_processing_time:.3f}s")
                    
                except Exception as e:
                    print(f"❌ Error sending frame: {e}")
                    print(f"🔌 WebSocket state: {websocket.client_state if hasattr(websocket, 'client_state') else 'unknown'}")
                    # Raise WebSocketDisconnect to trigger proper cleanup
                    raise WebSocketDisconnect(code=1011, reason=f"Frame send error: {e}")
                
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
                    
                    # 🚨 CRITICAL: Send tier1_detection message to create pipeline card
                    tier1_message = {
                        "type": "tier1_detection",
                        "frame_id": frame_id,
                        "timestamp": timestamp,
                        "status": tier1_result.get("status", "Suspected Anomaly"),
                        "details": frame_reasoning,
                        "tier1_components": tier1_result.get("tier1_components", {}),
                        "confidence": confidence_score,
                        "detected_objects": detected_objects,
                        "fusion_status": "live-detection",
                        "video_file": f"dashboard_recording_{int(time.time())}.mp4",
                        "frame_file": anomaly_frame_path,
                        "session_id": dashboard_session.session_id,
                        "analysis_time": datetime.now().strftime("%H:%M:%S")
                    }
                    
                    # Check WebSocket connection before sending tier1 message
                    if websocket.client_state.name != 'CONNECTED':
                        print(f"🔌 WebSocket not connected for tier1 message (state: {websocket.client_state.name})")
                        raise WebSocketDisconnect(code=1011, reason="WebSocket not connected for tier1 message")
                    
                    try:
                        await websocket.send_json(tier1_message)
                        print(f"📡 Dashboard: Sent tier1_detection message for pipeline card creation")
                    except Exception as e:
                        print(f"❌ Error sending tier1 message: {e}")
                        raise WebSocketDisconnect(code=1011, reason=f"Tier1 message send error: {e}")
                    
                    # Run Tier 2 analysis in background
                    asyncio.create_task(run_tier2_for_dashboard(frame, frame_id, timestamp, websocket))
                
                # ⏱️ LATENCY: Periodic performance report
                if processed_frames % 50 == 0 and latency_stats['total_frames'] > 0:
                    avg_decode = sum(latency_stats['decode_times'][-50:]) / len(latency_stats['decode_times'][-50:])
                    avg_analysis = sum(latency_stats['analysis_times'][-50:]) / len(latency_stats['analysis_times'][-50:]) if latency_stats['analysis_times'] else 0
                    avg_compress = sum(latency_stats['compression_times'][-50:]) / len(latency_stats['compression_times'][-50:])
                    avg_transmit = sum(latency_stats['transmission_times'][-50:]) / len(latency_stats['transmission_times'][-50:])
                    avg_total = sum(latency_stats['total_processing_times'][-50:]) / len(latency_stats['total_processing_times'][-50:])
                    
                    print(f"📊 LATENCY REPORT (Last 50 frames):")
                    print(f"   Decode: {avg_decode:.3f}s | Analysis: {avg_analysis:.3f}s | Compress: {avg_compress:.3f}s")
                    print(f"   Transmit: {avg_transmit:.3f}s | Total: {avg_total:.3f}s | FPS: {50/avg_total:.1f}")
                    
                    # Clear old stats to prevent memory buildup
                    for key in latency_stats:
                        if isinstance(latency_stats[key], list) and len(latency_stats[key]) > 100:
                            latency_stats[key] = latency_stats[key][-50:]
                
                # OPTIMIZED: Slightly longer delay for better performance
                await asyncio.sleep(0.066)  # ~15 FPS instead of 30 FPS
                
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
        
        # Send Tier 2 start notification
        await websocket.send_json({
            "type": "tier2_start",
            "frame_id": frame_id,
            "timestamp": timestamp,
            "message": "Starting Tier 2 AI analysis..."
        })
        
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
        print(f"📊 Dashboard: Tier 2 result: {tier2_result}")
        
        # Update anomaly in dashboard_mode
        anomalies = dashboard_mode.get_dashboard_anomalies()
        for anomaly in anomalies:
            if anomaly.get("frame_id") == frame_id:
                anomaly["tier2_analysis"] = tier2_result
                break
        
        # 🚨 CRITICAL: Send Tier 2 results to frontend via WebSocket
        tier2_message = {
            "type": "tier2_results",
            "frame_id": frame_id,
            "timestamp": timestamp,
            "threat_severity_index": tier2_result.get("threat_severity_index", 0.5),
            "reasoning_summary": tier2_result.get("reasoning_summary", "Analysis complete"),
            "visual_score": tier2_result.get("visual_score", 0.5),
            "audio_score": tier2_result.get("audio_score", 0.5),
            "multimodal_agreement": tier2_result.get("multimodal_agreement", 0.5),
            "detailed_analysis": tier2_result.get("detailed_analysis", ""),
            "analysis_time": datetime.now().strftime("%H:%M:%S")
        }
        
        await websocket.send_json(tier2_message)
        print(f"📡 Dashboard: Sent Tier 2 results to frontend for frame {frame_id}")
        
    except Exception as e:
        print(f"❌ Dashboard Tier 2 error: {e}")
        # Send error notification to frontend
        try:
            await websocket.send_json({
                "type": "tier2_error",
                "frame_id": frame_id,
                "timestamp": timestamp,
                "error": str(e)
            })
        except:
            pass

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
