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
from datetime import datetime
from threading import Thread
import numpy as np
import warnings

# Suppress various warnings and set environment variables
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "ERROR"  # Reduce OpenCV FFmpeg warnings
warnings.filterwarnings("ignore", category=UserWarning)

app = FastAPI()

# Mount static files for anomaly frames and videos
app.mount("/anomaly_frames", StaticFiles(directory="anomaly_frames"), name="anomaly_frames")
app.mount("/recorded_videos", StaticFiles(directory="recorded_videos"), name="recorded_videos")

# Global storage for anomaly events
anomaly_events = []

# Global status for live stream overlay
current_status = "Normal"
current_details = "Initializing..."

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

@app.websocket("/stream_video")
async def stream_video(websocket: WebSocket):
    await websocket.accept()
    
    # Try multiple times to open camera
    video_cap = None
    
    # Suppress OpenCV warnings during camera setup
    cv2.setLogLevel(0)
    
    for attempt in range(3):
        video_cap = cv2.VideoCapture(0)
        video_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to minimize lag
        
        if video_cap.isOpened():
            # Test if we can actually read a frame
            ret, test_frame = video_cap.read()
            if ret:
                print(f"✅ Camera opened successfully on attempt {attempt + 1}")
                break
            else:
                video_cap.release()
                video_cap = None
        else:
            video_cap = None
        
        if attempt < 2:  # Don't sleep on last attempt
            await asyncio.sleep(1)
    
    if video_cap is None or not video_cap.isOpened():
        await websocket.send_json({"error": "Could not open video stream after multiple attempts"})
        return

    # Get video properties for recording
    width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video_cap.get(cv2.CAP_PROP_FPS) or 30
    
    # Setup video recording with better codec settings
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"recorded_videos/session_{timestamp}.mp4"
    
    # Use more compatible codec settings to reduce FFmpeg warnings
    try:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Try XVID first
        video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
        if not video_writer.isOpened():
            # Fallback to mp4v if XVID fails
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
    except:
        # Final fallback
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
    
    print(f"📹 Recording video to: {video_filename}")

    audio_stream = AudioStream()  # Start audio capture
    audio_stream.start()

    frame_queue = queue.Queue(maxsize=10)  # Buffer for frames
    anomaly_detected = False

    def capture_frames():
        while True:
            ret, frame = video_cap.read()
            if not ret:
                break
            if not frame_queue.full():
                frame_queue.put(frame)

    frame_thread = Thread(target=capture_frames)
    frame_thread.start()

    try:
        frame_interval = int(fps)  # For 1 FPS
        frame_count = 0
        session_start_time = time.time()
        
        while True:
            if frame_queue.empty():
                await asyncio.sleep(0.01)
                continue

            frame = frame_queue.get()
            frame_count += 1
            
            # Record every frame to video with error handling
            try:
                if video_writer.isOpened():
                    video_writer.write(frame)
            except Exception as e:
                # Silently handle video writing errors to avoid spam
                pass
            
            # Process only every Nth frame for anomaly detection
            if frame_count % frame_interval != 0:
                continue

            # Calculate current timestamp in video
            current_timestamp = (frame_count / fps)
            
            # Get audio chunk (2-sec window)
            audio_chunk = audio_stream.get_chunk()  # Get latest 2-sec audio
            print(f"🎤 Audio chunk available: {bool(audio_chunk)}")

            # Run Tier 1 on current frame and audio
            try:
                tier1_result = run_tier1_continuous(frame, audio_chunk)
                
                # Update global status for live stream overlay
                global current_status, current_details
                current_status = tier1_result["status"]
                current_details = tier1_result["details"]
                
                # Add frame info to result
                tier1_result["frame_count"] = frame_count
                tier1_result["timestamp"] = current_timestamp
                tier1_result["video_file"] = video_filename
                
                # Send result with WebSocket disconnect handling
                try:
                    if websocket.client_state.name == "CONNECTED":
                        await websocket.send_json(tier1_result)
                    else:
                        print("WebSocket not connected, skipping send")
                        break
                except WebSocketDisconnect:
                    print("WebSocket disconnected during Tier 1 result send")
                    break
                except Exception as e:
                    print(f"WebSocket send error: {e}")
                    break
                except Exception as send_error:
                    print(f"WebSocket send error: {send_error}")
                    break
                    
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"Tier 1 processing error: {e}")
                print(f"Full error traceback: {error_details}")
                
                # Send basic result without audio processing
                tier1_result = {
                    "status": "Normal", 
                    "details": "Video processing only (audio error)",
                    "error": f"Audio processing failed: {str(e)}",
                    "frame_count": frame_count,
                    "timestamp": current_timestamp,
                    "video_file": video_filename
                }
                
                # Send error result with WebSocket disconnect handling
                try:
                    await websocket.send_json(tier1_result)
                except WebSocketDisconnect:
                    print("WebSocket disconnected during error result send")
                    break
                except Exception as send_error:
                    print(f"WebSocket send error during error handling: {send_error}")
                    break

            if tier1_result["status"] == "Suspected Anomaly":
                anomaly_detected = True
                
                # Save anomaly frame
                anomaly_frame_filename = f"anomaly_frames/anomaly_{timestamp}_{frame_count}.jpg"
                cv2.imwrite(anomaly_frame_filename, frame)
                
                # Store anomaly event
                anomaly_event = {
                    "timestamp": current_timestamp,
                    "frame_count": frame_count,
                    "frame_file": anomaly_frame_filename,
                    "video_file": video_filename,
                    "details": tier1_result["details"],
                    "session_time": datetime.now().isoformat()
                }
                anomaly_events.append(anomaly_event)
                
                print(f"🚨 ANOMALY SAVED: Frame {frame_count} at {current_timestamp:.2f}s -> {anomaly_frame_filename}")
                
                # Run Tier 2 on current frame/audio for reasoning
                tier2_result = run_tier2_continuous(frame, audio_chunk, tier1_result)
                
                # Add frame info to tier2 result
                tier2_result["frame_count"] = frame_count
                tier2_result["timestamp"] = current_timestamp
                tier2_result["video_file"] = video_filename
                tier2_result["frame_file"] = anomaly_frame_filename
                
                # Update anomaly event with tier2 info
                anomaly_event.update({
                    "threat_severity_index": tier2_result.get("threat_severity_index", 0.5),
                    "reasoning_summary": tier2_result.get("reasoning_summary", ""),
                    "visual_score": tier2_result.get("visual_score", 0.5)
                })
                
                # Send Tier 2 result with WebSocket disconnect handling
                try:
                    await websocket.send_json(tier2_result)
                except WebSocketDisconnect:
                    print("WebSocket disconnected during Tier 2 result send")
                    break
                except Exception as send_error:
                    print(f"WebSocket send error during Tier 2: {send_error}")
                    break

            await asyncio.sleep(1 / fps)  # Control rate
    except WebSocketDisconnect:
        print("WebSocket client disconnected - stopping video stream")
    except Exception as e:
        print(f"Unexpected error in video stream: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except (WebSocketDisconnect, Exception):
            print("Could not send error message - WebSocket already closed")
    finally:
        # Cleanup resources
        try:
            video_cap.release()
            video_writer.release()  # Close video recording
            audio_stream.stop()
            frame_thread.join()
            print(f"📹 Video saved: {video_filename}")
            print(f"🚨 Anomalies detected: {len([e for e in anomaly_events if e['video_file'] == video_filename])}")
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")

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