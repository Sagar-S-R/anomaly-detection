from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from tier1.tier1_pipeline import run_tier1_continuous
from tier2.tier2_pipeline import run_tier2_continuous
from utils.audio_processing import AudioStream
import cv2
import asyncio
import queue
import os
import time
import json
from datetime import datetime
from threading import Thread
import numpy as np
import warnings
from collections import deque

# Suppress various warnings and set environment variables
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "ERROR"  # Reduce OpenCV FFmpeg warnings
warnings.filterwarnings("ignore", category=UserWarning)

app = FastAPI()

# Mount static files for anomaly frames and videos
app.mount("/anomaly_frames", StaticFiles(directory="anomaly_frames"), name="anomaly_frames")
app.mount("/recorded_videos", StaticFiles(directory="recorded_videos"), name="recorded_videos")

# Global storage for anomaly events with structured logging
anomaly_events = []

# Global asynchronous queues for multimodal fusion
video_queue = queue.Queue(maxsize=30)  # Store video embeddings + timestamps
audio_queue = queue.Queue(maxsize=50)  # Store audio transcripts + timestamps
fusion_results_queue = queue.Queue(maxsize=20)  # Store fused results for Tier 1

# Performance monitoring counters
performance_stats = {
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
    "pipeline_start_time": None
}

# Global anomaly tracking to prevent duplicates
last_anomaly_time = 0
anomaly_cooldown_period = 1.0  # 1 second cooldown between anomalies (reduced from 3)
current_anomaly_event = None  # Track current ongoing anomaly

# Global status for live stream overlay
current_status = "Normal"
current_details = "Initializing..."
frame_counter = 0  # Global frame counter for consistent logging

def log_structured_event(frame_id, pose_state, scene_score, audio_available, status, reasoning="", visual_score=0.0, audio_score=0.0, multimodal_agreement=0.0):
    """Enhanced structured logging for all processing events"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "frame_id": frame_id,
        "pose_state": pose_state,
        "scene_anomaly_score": round(scene_score, 3),
        "visual_score": round(visual_score, 3),
        "audio_available": audio_available,
        "audio_score": round(audio_score, 3),
        "tier1_status": status,
        "reasoning_summary": reasoning,
        "multimodal_agreement": round(multimodal_agreement, 3),
        "processing_pipeline": "tier1_continuous"
    }
    print(f"📊 STRUCTURED_LOG: {json.dumps(log_entry)}")
    return log_entry

def add_status_overlay(frame, status, details=""):
    """Add colored overlay to frame based on anomaly status"""
    height, width = frame.shape[:2]
    
    # Create overlay
    overlay = frame.copy()
    
    # Choose color based on status
    if status == "Suspected Anomaly":
        color = (0, 0, 255)  # Red for anomaly
        status_text = "🚨 ANOMALY DETECTED"
    else:
        color = (0, 255, 0)  # Green for normal
        status_text = "✅ NORMAL"
    
    # Add colored border
    cv2.rectangle(overlay, (0, 0), (width, height), color, 15)
    
    # Add status text background
    text_bg_height = 80
    cv2.rectangle(overlay, (0, 0), (width, text_bg_height), color, -1)
    
    # Add status text
    cv2.putText(overlay, status_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    # Add details text if available
    if details and len(details) > 0:
        detail_text = details[:100] + "..." if len(details) > 100 else details
        cv2.putText(overlay, detail_text, (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Blend overlay with original frame
    alpha = 0.7
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    return frame

def generate_video_stream():
    """Generate video stream with real-time status overlay"""
    global current_status, current_details
    
    # Check if camera is already in use by WebSocket stream
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera for video stream - likely in use by WebSocket")
        # Generate a placeholder stream instead of hanging
        for i in range(100):  # Generate 100 placeholder frames
            placeholder_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Add status overlay to placeholder
            status_color = (0, 0, 255) if current_status == "Suspected Anomaly" else (0, 255, 0)
            cv2.rectangle(placeholder_frame, (0, 0), (640, 480), status_color, 15)
            cv2.putText(placeholder_frame, "Camera in use by monitoring", (50, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(placeholder_frame, f"Status: {current_status}", (50, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(placeholder_frame, current_details[:60], (50, 280), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            ret, buffer = cv2.imencode('.jpg', placeholder_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
            time.sleep(0.1)  # 10 FPS for placeholder
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)  # Lower FPS for stream
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to prevent lag
    
    frame_count = 0
    max_frames = 1000  # Prevent infinite loop
    
    try:
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame from camera")
                break
            
            frame_count += 1
            
            # Add status overlay
            try:
                frame_with_overlay = add_status_overlay(frame, current_status, current_details)
            except Exception as overlay_error:
                print(f"Overlay error: {overlay_error}")
                frame_with_overlay = frame  # Use original frame if overlay fails
            
            # Encode frame to JPEG with error handling
            try:
                ret, buffer = cv2.imencode('.jpg', frame_with_overlay, 
                                          [cv2.IMWRITE_JPEG_QUALITY, 70])  # Lower quality for speed
                if not ret:
                    continue
                
                # Yield frame in multipart format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except Exception as encode_error:
                print(f"Frame encoding error: {encode_error}")
                continue
            
            # Small delay to prevent overwhelming
            time.sleep(0.05)  # ~20 FPS max
    
    except Exception as stream_error:
        print(f"Video stream error: {stream_error}")
    finally:
        cap.release()
        print("📹 Video stream generator closed")

@app.get("/video_stream")
async def video_stream():
    """Live video stream endpoint with status overlay"""
    try:
        return StreamingResponse(
            generate_video_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        print(f"Video stream endpoint error: {e}")
        # Return a simple error response instead of hanging
        return {"error": "Video stream unavailable", "details": str(e)}

@app.get("/test_stream")
async def test_stream():
    """Simple test stream to check if camera works"""
    def generate_test_stream():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return
        
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        for i in range(50):  # Only 50 frames for testing
            ret, frame = cap.read()
            if not ret:
                break
            
            # Simple frame without overlay
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        cap.release()
    
    return StreamingResponse(
        generate_test_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

def print_performance_stats():
    """Print concise performance statistics"""
    if performance_stats["pipeline_start_time"] is None:
        performance_stats["pipeline_start_time"] = time.time()
        return
    
    # Only print stats occasionally, not every 5 seconds
    elapsed = time.time() - performance_stats["pipeline_start_time"]
    if elapsed % 30 < 5:  # Only every 30 seconds
        fps_processed = performance_stats["frames_processed"] / elapsed if elapsed > 0 else 0
        audio_rate = performance_stats["audio_transcribed"] / elapsed if elapsed > 0 else 0
        
        print(f"\n📊 PIPELINE SUMMARY (Runtime: {elapsed:.1f}s)")
        print(f"🎬 Video: {fps_processed:.1f} FPS | 🎤 Audio: {audio_rate:.1f} chunks/s")
        print(f"🚨 T1: {performance_stats['tier1_anomalies_detected']} anomalies | 🔬 T2: {performance_stats['tier2_analyses_completed']}/{performance_stats['tier2_analyses_triggered']} analyses")

@app.websocket("/stream_video")
async def stream_video(websocket: WebSocket):
    await websocket.accept()
    
    # Try multiple times to open camera
    video_cap = None
    cv2.setLogLevel(0)
    
    for attempt in range(3):
        video_cap = cv2.VideoCapture(0)
        video_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if video_cap.isOpened():
            ret, test_frame = video_cap.read()
            if ret:
                print(f"✅ Camera opened successfully on attempt {attempt + 1}")
                break
            else:
                video_cap.release()
                video_cap = None
        else:
            video_cap = None
        
        if attempt < 2:
            await asyncio.sleep(1)
    
    if video_cap is None or not video_cap.isOpened():
        await websocket.send_json({"error": "Could not open video stream after multiple attempts"})
        return

    # Get video properties
    width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video_cap.get(cv2.CAP_PROP_FPS) or 30
    
    # Setup video recording
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"recorded_videos/session_{timestamp}.mp4"
    
    try:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
        if not video_writer.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
    except:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
    
    print(f"📹 Recording video to: {video_filename}")

    # Start the three worker threads
    audio_stream = AudioStream()
    audio_stream.start()
    
    # Start video capture worker
    video_thread = Thread(target=video_capture_worker, args=(video_cap, video_writer, fps))
    video_thread.daemon = True
    video_thread.start()
    
    # Start audio capture worker  
    audio_thread = Thread(target=audio_capture_worker, args=(audio_stream,))
    audio_thread.daemon = True
    audio_thread.start()
    
    # Start fusion worker
    fusion_thread = Thread(target=fusion_worker)
    fusion_thread.daemon = True
    fusion_thread.start()
    
    print("🚀 All workers started - processing fused results")
    
    try:
        last_stats_time = time.time()
        
        while True:
            try:
                # Get fused result from fusion worker (faster timeout)
                fused_result = fusion_results_queue.get(timeout=0.5)
            except queue.Empty:
                # Print stats if no results for a while
                if time.time() - last_stats_time > 5.0:
                    print_performance_stats()
                    last_stats_time = time.time()
                continue
            
            # Extract data from fused result
            frame = fused_result["frame"]
            frame_id = fused_result["frame_id"]
            audio_chunk_path = fused_result["audio_chunk_path"]
            fusion_status = fused_result["fusion_status"]
            timestamp = fused_result["timestamp"]
            
            # Run Tier 1 anomaly detection
            try:
                tier1_result = run_tier1_continuous(frame, audio_chunk_path)
                
                status = tier1_result["status"]
                details = tier1_result["details"]
                
                if status == "Suspected Anomaly":
                    # Check cooldown period to prevent duplicate anomalies
                    global last_anomaly_time, current_anomaly_event
                    time_since_last = timestamp - last_anomaly_time
                    
                    if time_since_last < anomaly_cooldown_period:
                        # This is part of the same incident - update but don't process fully
                        if current_anomaly_event:
                            current_anomaly_event["end_time"] = timestamp
                            current_anomaly_event["duration"] = timestamp - current_anomaly_event["timestamp"]
                            current_anomaly_event["frame_count"] += 1
                            print(f"🔄 Continuing incident (cooldown: {time_since_last:.1f}s)")
                        # Still send to frontend but mark as continuation
                        tier1_result.update({
                            "status": "Normal",  # Don't trigger new anomaly alert
                            "details": "Monitoring...",
                            "incident_continuation": True
                        })
                    else:
                        # This is a NEW anomaly incident - process fully
                        last_anomaly_time = timestamp
                        performance_stats["tier1_anomalies_detected"] += 1
                        print(f"\n🚨 NEW ANOMALY INCIDENT #{performance_stats['tier1_anomalies_detected']}")
                        print(f"📍 Details: {details}")
                        print(f"🔀 Fusion: {fusion_status} | Frame: {frame_id} | Time: {timestamp:.2f}s")
                        
                        # Save Tier 1 anomaly snapshot and metadata
                        anomaly_frame_filename = f"anomaly_frames/tier1_anomaly_{int(timestamp)}_{frame_id}.jpg"
                        cv2.imwrite(anomaly_frame_filename, frame)
                        
                        # Store NEW anomaly event with Tier 1 data
                        anomaly_event = {
                            "frame_id": frame_id,
                            "timestamp": timestamp,
                            "end_time": timestamp,  # Will be updated if incident continues
                            "duration": 0.0,  # Will be calculated
                            "frame_count": 1,  # Will be incremented if incident continues
                            "frame_file": anomaly_frame_filename,
                            "video_file": video_filename,
                            "details": details,
                            "fusion_status": fusion_status,
                            "session_time": datetime.now().isoformat(),
                            "tier1_result": tier1_result,
                            "tier2_analysis": None  # Will be populated when Tier 2 completes
                        }
                        anomaly_events.append(anomaly_event)
                        current_anomaly_event = anomaly_event  # Track current incident
                        
                        # TRIGGER TIER 2 ANALYSIS (synchronous but optimized)
                        performance_stats["tier2_analyses_triggered"] += 1
                        print(f"🔬 TRIGGERING TIER 2 ANALYSIS #{performance_stats['tier2_analyses_triggered']}...")
                        
                        try:
                            tier2_result = run_tier2_continuous(frame.copy(), audio_chunk_path, tier1_result.copy())
                            performance_stats["tier2_analyses_completed"] += 1
                            
                            # Update anomaly event with Tier 2 analysis
                            anomaly_event["tier2_analysis"] = tier2_result
                            tier1_result["tier2_analysis"] = tier2_result
                            
                            print(f"✅ TIER 2 ANALYSIS COMPLETE")
                            print(f"📋 Summary: {tier2_result.get('reasoning_summary', 'Analysis complete')}")
                            
                            # Send separate Tier 2 WebSocket message
                            tier2_websocket_result = {
                                "type": "tier2_analysis",
                                "frame_id": frame_id,
                                "timestamp": timestamp,
                                "fusion_status": fusion_status,
                                **tier2_result
                            }
                            
                            try:
                                if websocket.client_state.name == "CONNECTED":
                                    await websocket.send_json(tier2_websocket_result)
                                    print(f"📤 Tier 2 results sent to frontend")
                            except Exception as send_error:
                                print(f"❌ Tier 2 WebSocket error: {send_error}")
                                
                        except Exception as tier2_error:
                            performance_stats["tier2_analyses_failed"] += 1
                            print(f"❌ TIER 2 ANALYSIS FAILED: {tier2_error}")
                            
                            # Send error tier2 result
                            tier2_error_result = {
                                "type": "tier2_analysis",
                                "frame_id": frame_id,
                                "timestamp": timestamp,
                                "fusion_status": fusion_status,
                                "error": str(tier2_error),
                                "status": "Error",
                                "reasoning_summary": f"Tier 2 analysis failed: {str(tier2_error)}"
                            }
                            try:
                                if websocket.client_state.name == "CONNECTED":
                                    await websocket.send_json(tier2_error_result)
                            except:
                                pass
                else:
                    # No anomaly detected - reset cooldown tracking
                    current_anomaly_event = None
                
                # Add fusion metadata to result
                tier1_result.update({
                    "frame_id": frame_id,
                    "fusion_status": fusion_status,
                    "timestamp": timestamp,
                    "video_file": video_filename
                })
                
                # Send result via WebSocket
                try:
                    if websocket.client_state.name == "CONNECTED":
                        await websocket.send_json(tier1_result)
                    else:
                        print("WebSocket not connected, stopping")
                        break
                except WebSocketDisconnect:
                    print("WebSocket disconnected")
                    break
                except Exception as e:
                    print(f"WebSocket send error: {e}")
                    break
                    
            except Exception as e:
                print(f"❌ Tier 1 processing error: {e}")
                continue
                
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"Unexpected error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
    finally:
        # Cleanup resources
        try:
            video_cap.release()
            video_writer.release()
            audio_stream.stop()
            print(f"📹 Video saved: {video_filename}")
            print(f"🚨 Final Tier 1 anomalies: {performance_stats['tier1_anomalies_detected']}")
            print(f"🔬 Final Tier 2 analyses: {performance_stats['tier2_analyses_completed']}")
            print_performance_stats()
        except Exception as e:
            print(f"Cleanup error: {e}")

def video_capture_worker(video_cap, video_writer, fps):
    """Video Thread: Capture frames at 30 FPS, process every 5th frame (~6 FPS)"""
    global performance_stats
    frame_count = 0
    processed_count = 0
    start_time = time.time()
    
    print("🎬 Video capture worker started")
    
    while True:
        ret, frame = video_cap.read()
        if not ret:
            print("❌ Video capture failed")
            break
            
        performance_stats["frames_captured"] += 1
        frame_count += 1
        
        # Record every frame to video
        try:
            if video_writer.isOpened():
                video_writer.write(frame)
        except Exception as e:
            pass  # Silent video writing errors
        
        # Process every 5th frame (~6 FPS)
        if frame_count % 5 == 0:
            current_timestamp = time.time()
            
            try:
                # Create video embedding/data packet
                video_data = {
                    "frame_id": frame_count,
                    "timestamp": current_timestamp,
                    "frame": frame.copy(),  # Make a copy for thread safety
                    "session_time": current_timestamp - start_time
                }
                
                # Add to video queue (non-blocking)
                if not video_queue.full():
                    video_queue.put(video_data)
                    performance_stats["frames_processed"] += 1
                    processed_count += 1
                else:
                    # Only log queue full occasionally
                    if frame_count % 300 == 0:
                        print("⚠️ Video queue full, dropping frames")
                    
            except Exception as e:
                print(f"❌ Video processing error: {e}")
        
        # REMOVED SPAM: Only log stats every 30 seconds instead of every 10 seconds

def audio_capture_worker(audio_stream):
    """Audio Thread: Capture and transcribe audio continuously"""
    global performance_stats
    from utils.audio_processing import chunk_and_transcribe_tiny
    
    chunk_count = 0
    transcribed_count = 0
    start_time = time.time()
    
    print("🎤 Audio capture worker started")
    
    while True:
        try:
            # Get audio chunk (blocks until available)
            audio_chunk_path = audio_stream.get_chunk()
            
            if audio_chunk_path:
                performance_stats["audio_chunks_captured"] += 1
                chunk_count += 1
                current_timestamp = time.time()
                
                # Transcribe audio
                transcripts = chunk_and_transcribe_tiny(audio_chunk_path)
                
                if transcripts:
                    audio_text = " | ".join(transcripts)
                    performance_stats["audio_transcribed"] += 1
                    transcribed_count += 1
                    
                    # Create audio data packet
                    audio_data = {
                        "timestamp": current_timestamp,
                        "audio_text": audio_text,
                        "transcripts": transcripts,
                        "chunk_path": audio_chunk_path
                    }
                    
                    # Add to audio queue (non-blocking)
                    if not audio_queue.full():
                        audio_queue.put(audio_data)
                    else:
                        # Only log queue full occasionally
                        if chunk_count % 100 == 0:
                            print("⚠️ Audio queue full, dropping transcripts")
                
                # REMOVED SPAM: No more regular audio logging
            else:
                time.sleep(0.05)  # Brief pause if no audio available
                
        except Exception as e:
            print(f"❌ Audio worker error: {e}")
            time.sleep(0.1)

def fusion_worker():
    """Fusion Worker: Align video and audio streams with temporal matching"""
    global performance_stats
    
    print("🔀 Fusion worker started")
    
    # Keep recent audio data for temporal matching
    recent_audio = deque(maxlen=20)  # Store last 20 audio chunks (~5 seconds)
    
    while True:
        try:
            # Get video frame (blocking with shorter timeout)
            try:
                video_data = video_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            
            video_timestamp = video_data["timestamp"]
            
            # Update recent audio buffer
            while not audio_queue.empty():
                try:
                    audio_data = audio_queue.get_nowait()
                    recent_audio.append(audio_data)
                except queue.Empty:
                    break
            
            # Find nearest audio within ±0.5s
            best_audio = None
            min_time_diff = float('inf')
            
            for audio_data in recent_audio:
                time_diff = abs(video_timestamp - audio_data["timestamp"])
                if time_diff <= 0.5 and time_diff < min_time_diff:
                    best_audio = audio_data
                    min_time_diff = time_diff
            
            # Create fused result
            if best_audio:
                fused_result = {
                    "frame_id": video_data["frame_id"],
                    "timestamp": video_timestamp,
                    "frame": video_data["frame"],
                    "audio_text": best_audio["audio_text"],
                    "audio_chunk_path": best_audio["chunk_path"],
                    "fusion_status": "video+audio",
                    "time_sync_diff": min_time_diff
                }
                performance_stats["fusion_video_audio"] += 1
                # REMOVED SPAM: No more fusion success logging
            else:
                fused_result = {
                    "frame_id": video_data["frame_id"],
                    "timestamp": video_timestamp,
                    "frame": video_data["frame"],
                    "audio_text": None,
                    "audio_chunk_path": None,
                    "fusion_status": "video-only",
                    "time_sync_diff": None
                }
                performance_stats["fusion_video_only"] += 1
                # REMOVED SPAM: No more fusion miss logging
            
            # Add to fusion results queue
            if not fusion_results_queue.full():
                fusion_results_queue.put(fused_result)
            # Silently drop if queue is full
                
        except Exception as e:
            print(f"❌ Fusion worker error: {e}")
            time.sleep(0.1)

@app.get("/anomaly_events")
async def get_anomaly_events():
    """Get all detected anomaly events"""
    return {"anomaly_events": anomaly_events}

@app.get("/anomaly_events/{event_index}")
async def get_anomaly_event(event_index: int):
    """Get specific anomaly event by index"""
    if 0 <= event_index < len(anomaly_events):
        return anomaly_events[event_index]
    return {"error": "Event not found"}

@app.get("/dashboard")
async def dashboard():
    """Serve the anomaly detection dashboard"""
    return FileResponse("dashboard.html")

@app.get("/")
async def root():
    return {"message": "Anomaly Detection API", "total_anomalies": len(anomaly_events), "dashboard": "/dashboard"}