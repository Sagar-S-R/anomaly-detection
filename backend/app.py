from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from tier1.tier1_pipeline import run_tier1_continuous
from tier2.tier2_pipeline import run_tier2_continuous
from utils.audio_processing import AudioStream
import cv2
import asyncio
import queue
import os
import time
import json
import base64
import zipfile
import tempfile
from datetime import datetime
from threading import Thread
import threading
import numpy as np
import warnings
from collections import deque
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Suppress various warnings and set environment variables
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "ERROR"  # Reduce OpenCV FFmpeg warnings
warnings.filterwarnings("ignore", category=UserWarning)

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "anomaly_detection"

# Initialize MongoDB client
mongodb_client = None
database = None

# Memory storage for when MongoDB is not available
memory_users = {}  # Dictionary to store users when DB is unavailable

async def connect_to_mongodb():
    """Connect to MongoDB database"""
    global mongodb_client, database
    try:
        mongodb_client = AsyncIOMotorClient(MONGODB_URL)
        # Test the connection with a shorter timeout
        await mongodb_client.admin.command('ping', serverSelectionTimeoutMS=5000)
        database = mongodb_client[DATABASE_NAME]
        print("✅ Connected to MongoDB successfully")
        return True
    except Exception as e:
        print(f"⚠️  MongoDB not available: {e}")
        print("📝 Running in local-only mode (no database storage)")
        mongodb_client = None
        database = None
        return False

async def close_mongodb_connection():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("📊 MongoDB connection closed")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for anomaly frames and videos
app.mount("/anomaly_frames", StaticFiles(directory="anomaly_frames"), name="anomaly_frames")
app.mount("/recorded_videos", StaticFiles(directory="recorded_videos"), name="recorded_videos")

# FastAPI Events
@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection on startup"""
    await connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_mongodb_connection()

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

# MongoDB Helper Functions
async def save_anomaly_to_db(anomaly_event):
    """Save anomaly event to MongoDB"""
    if not database:
        return None
    
    try:
        # Convert frame to base64 if exists
        if "frame" in anomaly_event and anomaly_event["frame"] is not None:
            frame = anomaly_event["frame"]
            if isinstance(frame, np.ndarray):
                _, buffer = cv2.imencode('.jpg', frame)
                anomaly_event["frame_base64"] = base64.b64encode(buffer).decode('utf-8')
                # Remove the numpy array to avoid serialization issues
                del anomaly_event["frame"]
        
        # Insert into anomalies collection
        result = await database.anomalies.insert_one(anomaly_event)
        print(f"📊 Saved anomaly to MongoDB: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"❌ Error saving anomaly to MongoDB: {e}")
        return None

async def save_session_metadata(session_data):
    """Save session metadata to MongoDB"""
    if not database:
        return None
    
    try:
        result = await database.sessions.insert_one(session_data)
        print(f"📊 Saved session metadata to MongoDB: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"❌ Error saving session to MongoDB: {e}")
        return None

async def get_anomalies_from_db(session_id=None, limit=100):
    """Retrieve anomalies from MongoDB"""
    if not database:
        return []
    
    try:
        query = {"session_id": session_id} if session_id else {}
        cursor = database.anomalies.find(query).sort("timestamp", -1).limit(limit)
        anomalies = await cursor.to_list(length=limit)
        return anomalies
    except Exception as e:
        print(f"❌ Error retrieving anomalies from MongoDB: {e}")
        return []

async def get_all_sessions():
    """Get all session metadata"""
    if not database:
        return []
    
    try:
        cursor = database.sessions.find().sort("start_time", -1)
        sessions = await cursor.to_list(length=None)
        return sessions
    except Exception as e:
        print(f"❌ Error retrieving sessions from MongoDB: {e}")
        return []

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

# MongoDB API Endpoints
@app.post("/api/register")
async def register_user(request: dict):
    """User registration endpoint"""
    username = request.get('username', '').strip()
    password = request.get('password', '').strip()
    email = request.get('email', '').strip()
    full_name = request.get('full_name', '').strip()
    
    # Validation
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    if '@' not in email or '.' not in email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    if len(full_name) < 2:
        raise HTTPException(status_code=400, detail="Full name must be at least 2 characters")
    
    # Check if user already exists (in memory first, then DB)
    existing_users = ['admin', 'demo_user', 'security']  # Default users
    
    if database:
        try:
            # Check if username already exists in database
            existing_user = await database.users.find_one({"username": username})
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already exists")
            
            # Check if email already exists
            existing_email = await database.users.find_one({"email": email})
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already registered")
        except Exception as e:
            print(f"Database check error: {e}")
    else:
        # Check memory storage when database is not available
        if username in memory_users:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email already exists in memory
        for stored_user in memory_users.values():
            if stored_user.get("email") == email:
                raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check against hardcoded users
    if username in existing_users:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    new_user = {
        "username": username,
        "password": password,  # In production, hash this!
        "email": email,
        "full_name": full_name,
        "role": "operator",
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    # Save to MongoDB if available
    if database:
        try:
            result = await database.users.insert_one(new_user)
            user_id = str(result.inserted_id)
            print(f"✅ User registered successfully: {username} (ID: {user_id})")
        except Exception as e:
            print(f"❌ Error saving user to database: {e}")
            raise HTTPException(status_code=500, detail="Failed to save user")
    else:
        # Store in memory when database is not available
        memory_users[username] = new_user
        print(f"⚠️  User registered in memory only: {username}")
    
    return {
        "success": True,
        "message": "User registered successfully",
        "user": {
            "username": username,
            "email": email,
            "full_name": full_name,
            "role": "operator"
        }
    }

@app.post("/api/login")
async def login(request: dict):
    """User authentication endpoint"""
    username = request.get('username', '').strip()
    password = request.get('password', '').strip()
    
    # Simple validation
    if len(username) < 3 or len(password) < 6:
        raise HTTPException(status_code=400, detail="Invalid username or password length")
    
    user_found = False
    user_role = "operator"
    user_email = None
    user_full_name = None
    
    # Check demo/default credentials first
    default_users = {
        'admin': 'password123',
        'demo_user': 'demo123',
        'security': 'secure456'
    }
    
    if username in default_users and default_users[username] == password:
        user_found = True
        user_role = "admin" if username == "admin" else "operator"
    
    # Check database users if not found in defaults
    if not user_found and database:
        try:
            db_user = await database.users.find_one({"username": username})
            if db_user and db_user.get("password") == password:
                user_found = True
                user_role = db_user.get("role", "operator")
                user_email = db_user.get("email")
                user_full_name = db_user.get("full_name")
        except Exception as e:
            print(f"Database login check error: {e}")
    
    # Check memory users if not found in defaults and database is not available
    if not user_found and not database:
        if username in memory_users:
            memory_user = memory_users[username]
            if memory_user.get("password") == password:
                user_found = True
                user_role = memory_user.get("role", "operator")
                user_email = memory_user.get("email")
                user_full_name = memory_user.get("full_name")
                print(f"✅ Memory user login successful: {username}")
    
    if user_found:
        # Create user session
        user_data = {
            "username": username,
            "login_time": datetime.now().isoformat(),
            "session_id": f"session_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "role": user_role
        }
        
        # Save user session to MongoDB if available
        if database:
            try:
                await database.user_sessions.insert_one(user_data)
            except Exception as e:
                print(f"Warning: Could not save user session to DB: {e}")
        
        return {
            "success": True,
            "user": {
                "username": username,
                "session_id": user_data["session_id"],
                "role": user_role,
                "email": user_email,
                "full_name": user_full_name
            },
            "message": "Login successful"
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/logout")
async def logout(request: dict):
    """User logout endpoint"""
    session_id = request.get('session_id')
    
    if database and session_id:
        try:
            await database.user_sessions.update_one(
                {"session_id": session_id},
                {"$set": {"logout_time": datetime.now().isoformat()}}
            )
        except Exception as e:
            print(f"Warning: Could not update logout time: {e}")
    
    return {"success": True, "message": "Logout successful"}

@app.get("/api/anomalies")
async def get_anomalies(session_id: str = None, limit: int = 100):
    """Get anomalies from database"""
    anomalies = await get_anomalies_from_db(session_id, limit)
    return {"anomalies": anomalies, "count": len(anomalies)}

@app.get("/api/sessions")
async def get_sessions():
    """Get all sessions"""
    sessions = await get_all_sessions()
    return {"sessions": sessions, "count": len(sessions)}

@app.get("/api/download_session/{session_id}")
async def download_session_data(session_id: str):
    """Download all session data as a zip file"""
    try:
        # Get session anomalies
        anomalies = await get_anomalies_from_db(session_id)
        
        if not anomalies:
            raise HTTPException(status_code=404, detail="No data found for this session")
        
        # Create temporary zip file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            zip_path = tmp_file.name
        
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            # Add anomaly metadata as JSON
            metadata = {
                "session_id": session_id,
                "total_anomalies": len(anomalies),
                "export_time": datetime.now().isoformat(),
                "anomalies": []
            }
            
            # Create folders in zip
            frames_folder = "frames/"
            
            for i, anomaly in enumerate(anomalies):
                # Add frame image if available
                if "frame_base64" in anomaly:
                    try:
                        frame_data = base64.b64decode(anomaly["frame_base64"])
                        frame_filename = f"{frames_folder}anomaly_{i+1}_{anomaly.get('timestamp', 'unknown')}.jpg"
                        zip_file.writestr(frame_filename, frame_data)
                        
                        # Add frame reference to metadata
                        anomaly_meta = anomaly.copy()
                        del anomaly_meta["frame_base64"]  # Remove base64 data from metadata
                        anomaly_meta["frame_file"] = frame_filename
                        metadata["anomalies"].append(anomaly_meta)
                    except Exception as e:
                        print(f"Error processing frame {i}: {e}")
                        metadata["anomalies"].append(anomaly)
                else:
                    metadata["anomalies"].append(anomaly)
            
            # Add metadata JSON
            zip_file.writestr("session_metadata.json", json.dumps(metadata, indent=2))
            
            # Add summary report
            summary = f"""Anomaly Detection Session Report
Session ID: {session_id}
Total Anomalies Detected: {len(anomalies)}
Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Anomaly Summary:
""" + "\n".join([f"- {i+1}. {a.get('timestamp', 'Unknown time')}: {a.get('details', 'No details')}" 
                 for i, a in enumerate(anomalies)])
            
            zip_file.writestr("README.txt", summary)
        
        # Return zip file
        def cleanup():
            try:
                os.unlink(zip_path)
            except:
                pass
        
        return FileResponse(
            zip_path,
            media_type='application/zip',
            filename=f'anomaly_session_{session_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
            background=cleanup
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating download: {str(e)}")

@app.get("/api/stats")
async def get_system_stats():
    """Get current system statistics"""
    return {
        "mongodb_connected": database is not None,
        "performance_stats": performance_stats,
        "current_status": current_status,
        "total_stored_anomalies": await database.anomalies.count_documents({}) if database else 0,
        "total_sessions": await database.sessions.count_documents({}) if database else 0
    }

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
    session_id = f"live_session_{timestamp}"
    video_filename = f"recorded_videos/session_{timestamp}.mp4"
    
    # Save session metadata to MongoDB
    session_metadata = {
        "session_id": session_id,
        "session_type": "live_camera",
        "start_time": datetime.now().isoformat(),
        "video_file": video_filename,
        "status": "active"
    }
    await save_session_metadata(session_metadata)
    
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
                            "session_id": session_id,
                            "end_time": timestamp,  # Will be updated if incident continues
                            "duration": 0.0,  # Will be calculated
                            "frame_count": 1,  # Will be incremented if incident continues
                            "frame": frame,  # Will be converted to base64 in MongoDB save
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
                        
                        # Save to MongoDB (async)
                        await save_anomaly_to_db(anomaly_event.copy())
                        
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
    except asyncio.CancelledError:
        print("WebSocket connection cancelled")
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

@app.get("/download-session-data")
async def download_session_data():
    """Create downloadable zip with all session data"""
    import zipfile
    import io
    import base64
    from datetime import datetime
    
    # Create in-memory zip file
    zip_buffer = io.BytesIO()
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Create session summary
            session_summary = {
                "session_info": {
                    "total_anomalies": len(anomaly_events),
                    "generation_time": datetime.now().isoformat(),
                    "performance_stats": performance_stats
                },
                "anomaly_events": anomaly_events
            }
            
            # Add metadata
            zip_file.writestr("metadata/session_summary.json", 
                            json.dumps(session_summary, indent=2, default=str))
            
            # Add individual anomaly frames if they exist
            for i, anomaly in enumerate(anomaly_events):
                if "frame_file" in anomaly and os.path.exists(anomaly["frame_file"]):
                    zip_file.write(anomaly["frame_file"], f"frames/anomaly_{i+1:03d}.jpg")
                
                # Add individual anomaly metadata
                anomaly_meta = {
                    "anomaly_id": i + 1,
                    "timestamp": anomaly.get("timestamp"),
                    "details": anomaly.get("details"),
                    "tier1_result": anomaly.get("tier1_result"),
                    "tier2_analysis": anomaly.get("tier2_analysis")
                }
                zip_file.writestr(f"metadata/anomaly_{i+1:03d}.json", 
                                json.dumps(anomaly_meta, indent=2, default=str))
            
            # Add video files if they exist
            if len(anomaly_events) > 0:
                video_files = set()
                for anomaly in anomaly_events:
                    if "video_file" in anomaly and anomaly["video_file"]:
                        video_files.add(anomaly["video_file"])
                
                for video_file in video_files:
                    if os.path.exists(video_file):
                        zip_file.write(video_file, f"videos/{os.path.basename(video_file)}")
        
        zip_buffer.seek(0)
        
        # Create response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"anomaly_session_{timestamp}.zip"
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create download: {str(e)}")

# VIDEO INPUT CONFIGURATION
VIDEO_UPLOAD_DIR = "uploaded_videos"
VIDEO_MIN_DURATION = 10  # seconds (configurable)
VIDEO_MAX_SIZE = 500 * 1024 * 1024  # 500MB (configurable)
ALLOWED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv", ".webm"]

os.makedirs(VIDEO_UPLOAD_DIR, exist_ok=True)

@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    """Upload and process a video file through the same anomaly detection pipeline"""
    
    # Validate file format
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_VIDEO_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file format. Allowed formats: {ALLOWED_VIDEO_FORMATS}"
        )
    
    # Check file size
    contents = await file.read()
    if len(contents) > VIDEO_MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {VIDEO_MAX_SIZE // (1024*1024)}MB"
        )
    
    # Save uploaded file
    upload_timestamp = int(time.time())
    safe_filename = f"upload_{upload_timestamp}_{file.filename}"
    file_path = os.path.join(VIDEO_UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    try:
        # Validate video duration using OpenCV
        temp_cap = cv2.VideoCapture(file_path)
        if not temp_cap.isOpened():
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Invalid video file")
        
        fps = temp_cap.get(cv2.CAP_PROP_FPS)
        frame_count = temp_cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps if fps > 0 else 0
        temp_cap.release()
        
        if duration < VIDEO_MIN_DURATION:
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"Video too short. Minimum duration: {VIDEO_MIN_DURATION} seconds"
            )
        
        return {
            "message": "Video uploaded successfully",
            "filename": safe_filename,
            "duration": duration,
            "file_path": file_path,
            "process_endpoint": f"/process_uploaded_video/{safe_filename}"
        }
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Video validation failed: {str(e)}")

@app.websocket("/process_uploaded_video/{filename}")
async def process_uploaded_video(websocket: WebSocket, filename: str):
    """Process uploaded video through the same anomaly detection pipeline"""
    await websocket.accept()
    
    file_path = os.path.join(VIDEO_UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        await websocket.send_json({"error": "Video file not found"})
        return
    
    # Use the same processing pipeline as live stream
    video_cap = cv2.VideoCapture(file_path)
    if not video_cap.isOpened():
        await websocket.send_json({"error": "Could not open video file"})
        return
    
    try:
        # Reset global state for new video processing session
        global anomaly_events, performance_stats, last_anomaly_time, current_anomaly_event
        anomaly_events = []
        current_anomaly_event = None
        last_anomaly_time = 0
        performance_stats = {
            "pipeline_start_time": time.time(),
            "frames_processed": 0,
            "frames_captured": 0,
            "audio_transcribed": 0,
            "tier1_anomalies_detected": 0,
            "tier2_analyses_triggered": 0,
            "tier2_analyses_completed": 0,
            "tier2_analyses_failed": 0,
            "fusion_video_audio": 0,
            "fusion_video_only": 0
        }
        
        print(f"📹 Processing uploaded video: {filename}")
        await websocket.send_json({"status": "Processing started", "filename": filename})
        
        # Start the processing threads (same as live stream)
        audio_stream = AudioStream()
        audio_stream.start()
        
        # Create queues
        video_queue = queue.Queue(maxsize=50)
        audio_queue = queue.Queue(maxsize=100)
        fusion_results_queue = queue.Queue(maxsize=20)
        
        # Start worker threads
        video_thread = threading.Thread(target=video_capture_worker_uploaded, 
                                       args=(video_queue, video_cap, filename))
        audio_thread = threading.Thread(target=audio_capture_worker, 
                                       args=(audio_queue, audio_stream))
        fusion_thread = threading.Thread(target=fusion_worker, 
                                        args=(video_queue, audio_queue, fusion_results_queue))
        
        video_thread.daemon = True
        audio_thread.daemon = True  
        fusion_thread.daemon = True
        
        video_thread.start()
        audio_thread.start()
        fusion_thread.start()
        
        # Process fusion results (same logic as live stream)
        last_stats_time = time.time()
        
        while True:
            try:
                # Get fused result from fusion worker (faster timeout)
                fused_result = fusion_results_queue.get(timeout=0.5)
            except queue.Empty:
                # Check if video processing is complete
                if not video_thread.is_alive():
                    print("📹 Video processing completed")
                    await websocket.send_json({"status": "Processing completed", "total_anomalies": len(anomaly_events)})
                    break
                continue
            
            # Process the fused result (same logic as live stream)
            frame_id = fused_result.get("frame_id", "unknown")
            timestamp = fused_result.get("timestamp", time.time())
            fusion_status = fused_result.get("fusion_status", "unknown")
            frame = fused_result.get("frame")
            audio_chunk_path = fused_result.get("audio_chunk_path")
            
            # Get detection results
            tier1_result = run_tier1_continuous(fused_result)
            
            status = tier1_result.get("status", "Normal")
            details = tier1_result.get("details", "Monitoring...")
            
            if status == "Suspected Anomaly":
                # Same anomaly processing logic as live stream
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
                        "status": "Normal",
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
                    
                    # Save Tier 1 anomaly snapshot
                    anomaly_frame_filename = f"anomaly_frames/uploaded_anomaly_{int(timestamp)}_{frame_id}.jpg"
                    cv2.imwrite(anomaly_frame_filename, frame)
                    
                    # Store NEW anomaly event
                    anomaly_event = {
                        "frame_id": frame_id,
                        "timestamp": timestamp,
                        "end_time": timestamp,
                        "duration": 0.0,
                        "frame_count": 1,
                        "frame_file": anomaly_frame_filename,
                        "video_file": filename,
                        "details": details,
                        "fusion_status": fusion_status,
                        "session_time": datetime.now().isoformat(),
                        "tier1_result": tier1_result,
                        "tier2_analysis": None
                    }
                    anomaly_events.append(anomaly_event)
                    current_anomaly_event = anomaly_event
                    
                    # TRIGGER TIER 2 ANALYSIS
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
            else:
                # No anomaly detected - reset cooldown tracking
                current_anomaly_event = None
            
            # Add fusion metadata to result
            tier1_result.update({
                "frame_id": frame_id,
                "fusion_status": fusion_status,
                "timestamp": timestamp,
                "video_file": filename
            })
            
            # Send result via WebSocket
            try:
                if websocket.client_state.name == "CONNECTED":
                    await websocket.send_json(tier1_result)
            except WebSocketDisconnect:
                print("WebSocket disconnected during video processing")
                break
            except Exception as e:
                print(f"WebSocket send error: {e}")
                break
                
    except WebSocketDisconnect:
        print("WebSocket disconnected during video processing")
    except asyncio.CancelledError:
        print("Video processing WebSocket connection cancelled")
    except Exception as e:
        print(f"Video processing error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
    finally:
        video_cap.release()
        audio_stream.stop()
        print(f"📹 Video processing session ended: {filename}")

@app.websocket("/connect_cctv")
async def connect_cctv(websocket: WebSocket, ip: str, port: int = 554, username: str = None, password: str = None):
    """Connect to CCTV camera via RTSP and process through the same anomaly detection pipeline"""
    await websocket.accept()
    
    # Construct RTSP URL
    if username and password:
        rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}/stream"
    else:
        rtsp_url = f"rtsp://{ip}:{port}/stream"
    
    print(f"🎥 Attempting CCTV connection: {rtsp_url}")
    
    # Try to connect to CCTV stream
    video_cap = cv2.VideoCapture(rtsp_url)
    video_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not video_cap.isOpened():
        await websocket.send_json({"error": f"Could not connect to CCTV at {ip}:{port}"})
        return
    
    # Test connection
    ret, test_frame = video_cap.read()
    if not ret:
        video_cap.release()
        await websocket.send_json({"error": "CCTV connection established but no video feed"})
        return
    
    try:
        # Reset global state for new CCTV session
        global anomaly_events, performance_stats, last_anomaly_time, current_anomaly_event
        anomaly_events = []
        current_anomaly_event = None
        last_anomaly_time = 0
        performance_stats = {
            "pipeline_start_time": time.time(),
            "frames_processed": 0,
            "frames_captured": 0,
            "audio_transcribed": 0,
            "tier1_anomalies_detected": 0,
            "tier2_analyses_triggered": 0,
            "tier2_analyses_completed": 0,
            "tier2_analyses_failed": 0,
            "fusion_video_audio": 0,
            "fusion_video_only": 0
        }
        
        print(f"🎥 CCTV connection successful: {ip}:{port}")
        await websocket.send_json({"status": "CCTV connected", "rtsp_url": rtsp_url})
        
        # Use the same processing pipeline as live stream but for CCTV
        # Note: Most CCTV streams don't have audio, so primarily video-only processing
        
        # Create queues
        video_queue = queue.Queue(maxsize=50)
        audio_queue = queue.Queue(maxsize=100)  # Will be mostly empty for CCTV
        fusion_results_queue = queue.Queue(maxsize=20)
        
        # Start worker threads (same as live stream but adapted for CCTV)
        video_thread = threading.Thread(target=video_capture_worker_cctv, 
                                       args=(video_queue, video_cap, rtsp_url))
        # For CCTV, we'll use a dummy audio worker since most CCTV don't have audio
        audio_thread = threading.Thread(target=dummy_audio_worker, args=(audio_queue,))
        fusion_thread = threading.Thread(target=fusion_worker, 
                                        args=(video_queue, audio_queue, fusion_results_queue))
        
        video_thread.daemon = True
        audio_thread.daemon = True
        fusion_thread.daemon = True
        
        video_thread.start()
        audio_thread.start()
        fusion_thread.start()
        
        # Process fusion results (same logic as live stream)
        last_stats_time = time.time()
        
        while True:
            try:
                # Get fused result from fusion worker
                fused_result = fusion_results_queue.get(timeout=0.5)
            except queue.Empty:
                # Print stats if no results for a while
                if time.time() - last_stats_time > 30.0:  # Every 30 seconds
                    elapsed = time.time() - performance_stats["pipeline_start_time"]
                    if elapsed > 30:  # Only after 30 seconds
                        fps_processed = performance_stats["frames_processed"] / elapsed if elapsed > 0 else 0
                        print(f"\n📊 CCTV PIPELINE (Runtime: {elapsed:.1f}s)")
                        print(f"🎬 Video: {fps_processed:.1f} FPS | 🚨 Anomalies: {performance_stats['tier1_anomalies_detected']}")
                    last_stats_time = time.time()
                continue
            
            # Process the fused result (same logic as live stream)
            frame_id = fused_result.get("frame_id", "unknown")
            timestamp = fused_result.get("timestamp", time.time())
            fusion_status = fused_result.get("fusion_status", "video-only")  # Usually video-only for CCTV
            frame = fused_result.get("frame")
            audio_chunk_path = fused_result.get("audio_chunk_path")  # Usually None for CCTV
            
            # Get detection results
            tier1_result = run_tier1_continuous(fused_result)
            
            status = tier1_result.get("status", "Normal")
            details = tier1_result.get("details", "Monitoring...")
            
            if status == "Suspected Anomaly":
                # Same anomaly processing logic as live stream
                time_since_last = timestamp - last_anomaly_time
                
                if time_since_last < anomaly_cooldown_period:
                    if current_anomaly_event:
                        current_anomaly_event["end_time"] = timestamp
                        current_anomaly_event["duration"] = timestamp - current_anomaly_event["timestamp"]
                        current_anomaly_event["frame_count"] += 1
                    tier1_result.update({
                        "status": "Normal",
                        "details": "Monitoring...",
                        "incident_continuation": True
                    })
                else:
                    # NEW anomaly incident
                    last_anomaly_time = timestamp
                    performance_stats["tier1_anomalies_detected"] += 1
                    print(f"\n🚨 CCTV ANOMALY #{performance_stats['tier1_anomalies_detected']}")
                    print(f"📍 Details: {details}")
                    print(f"🔀 Fusion: {fusion_status} | Frame: {frame_id}")
                    
                    # Save CCTV anomaly snapshot
                    anomaly_frame_filename = f"anomaly_frames/cctv_anomaly_{int(timestamp)}_{frame_id}.jpg"
                    cv2.imwrite(anomaly_frame_filename, frame)
                    
                    # Store anomaly event
                    anomaly_event = {
                        "frame_id": frame_id,
                        "timestamp": timestamp,
                        "end_time": timestamp,
                        "duration": 0.0,
                        "frame_count": 1,
                        "frame_file": anomaly_frame_filename,
                        "video_source": rtsp_url,
                        "details": details,
                        "fusion_status": fusion_status,
                        "session_time": datetime.now().isoformat(),
                        "tier1_result": tier1_result,
                        "tier2_analysis": None
                    }
                    anomaly_events.append(anomaly_event)
                    current_anomaly_event = anomaly_event
                    
                    # TRIGGER TIER 2 ANALYSIS
                    performance_stats["tier2_analyses_triggered"] += 1
                    print(f"🔬 TRIGGERING TIER 2 ANALYSIS #{performance_stats['tier2_analyses_triggered']}...")
                    
                    try:
                        tier2_result = run_tier2_continuous(frame.copy(), audio_chunk_path, tier1_result.copy())
                        performance_stats["tier2_analyses_completed"] += 1
                        
                        anomaly_event["tier2_analysis"] = tier2_result
                        tier1_result["tier2_analysis"] = tier2_result
                        
                        print(f"✅ TIER 2 ANALYSIS COMPLETE")
                        print(f"📋 Summary: {tier2_result.get('reasoning_summary', 'Analysis complete')}")
                        
                        # Send Tier 2 WebSocket message
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
                        except Exception as send_error:
                            print(f"❌ Tier 2 WebSocket error: {send_error}")
                            
                    except Exception as tier2_error:
                        performance_stats["tier2_analyses_failed"] += 1
                        print(f"❌ TIER 2 ANALYSIS FAILED: {tier2_error}")
            else:
                current_anomaly_event = None
            
            # Add metadata to result
            tier1_result.update({
                "frame_id": frame_id,
                "fusion_status": fusion_status,
                "timestamp": timestamp,
                "video_source": rtsp_url
            })
            
            # Send result via WebSocket
            try:
                if websocket.client_state.name == "CONNECTED":
                    await websocket.send_json(tier1_result)
            except WebSocketDisconnect:
                print("WebSocket disconnected from CCTV")
                break
            except Exception as e:
                print(f"CCTV WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        print("WebSocket disconnected from CCTV")
    except asyncio.CancelledError:
        print("CCTV WebSocket connection cancelled")
    except Exception as e:
        print(f"CCTV processing error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
    finally:
        video_cap.release()
        print(f"🎥 CCTV session ended: {ip}:{port}")

# Helper worker functions for uploaded video and CCTV
def video_capture_worker_uploaded(video_queue, video_cap, filename):
    """Video capture worker for uploaded video files"""
    global performance_stats
    print(f"📹 Video worker started for: {filename}")
    
    frame_count = 0
    fps = video_cap.get(cv2.CAP_PROP_FPS) or 30
    frame_delay = 1.0 / fps  # Maintain original video FPS
    
    start_time = time.time()
    
    while True:
        ret, frame = video_cap.read()
        if not ret:
            print(f"📹 End of video reached: {filename}")
            break
            
        performance_stats["frames_captured"] += 1
        frame_count += 1
        
        # Process every 3rd frame for faster processing while maintaining quality
        if frame_count % 3 == 0:
            current_timestamp = time.time()
            
            try:
                video_data = {
                    "frame_id": frame_count,
                    "timestamp": current_timestamp,
                    "frame": frame.copy(),
                    "session_time": current_timestamp - start_time
                }
                
                if not video_queue.full():
                    video_queue.put(video_data)
                    performance_stats["frames_processed"] += 1
                    
            except Exception as e:
                print(f"📹 Video processing error: {e}")
                break
        
        # Maintain video timing (optional - can be removed for faster processing)
        time.sleep(max(0, frame_delay - 0.01))
    
    print(f"📹 Video worker ended: {filename}")

def video_capture_worker_cctv(video_queue, video_cap, rtsp_url):
    """Video capture worker for CCTV RTSP streams"""
    global performance_stats
    print(f"🎥 CCTV worker started: {rtsp_url}")
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = video_cap.read()
        if not ret:
            print(f"🎥 CCTV stream interrupted: {rtsp_url}")
            time.sleep(1)  # Wait before retrying
            continue
            
        performance_stats["frames_captured"] += 1
        frame_count += 1
        
        # Process every 5th frame (~6 FPS) for real-time performance
        if frame_count % 5 == 0:
            current_timestamp = time.time()
            
            try:
                video_data = {
                    "frame_id": frame_count,
                    "timestamp": current_timestamp,
                    "frame": frame.copy(),
                    "session_time": current_timestamp - start_time
                }
                
                if not video_queue.full():
                    video_queue.put(video_data)
                    performance_stats["frames_processed"] += 1
                else:
                    # Drop frames if queue is full (real-time processing)
                    pass
                    
            except Exception as e:
                print(f"🎥 CCTV processing error: {e}")
                break
        
        time.sleep(0.05)  # ~20 FPS max capture rate
    
    print(f"🎥 CCTV worker ended: {rtsp_url}")

def dummy_audio_worker(audio_queue):
    """Dummy audio worker for CCTV (most CCTV streams don't have audio)"""
    print("🎤 Dummy audio worker started (CCTV mode)")
    
    while True:
        # CCTV streams typically don't have audio, so we just add empty audio data periodically
        try:
            audio_data = {
                "timestamp": time.time(),
                "audio_chunk_path": None,
                "transcripts": []
            }
            
            if not audio_queue.full():
                audio_queue.put(audio_data)
            
            time.sleep(1.0)  # Add empty audio data every second
            
        except Exception as e:
            print(f"🎤 Dummy audio worker error: {e}")
            break