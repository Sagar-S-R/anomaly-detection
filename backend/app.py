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
import io
from datetime import datetime
from threading import Thread
import threading
import uuid
import numpy as np
import warnings
from collections import deque
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo.errors import ConnectionFailure
    MONGODB_AVAILABLE = True
except ImportError:
    print("⚠️  MongoDB not available - running without database")
    MONGODB_AVAILABLE = False
    AsyncIOMotorClient = None
    ConnectionFailure = Exception

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    print("⚠️  python-dotenv not available - using environment variables directly")
    DOTENV_AVAILABLE = False
    def load_dotenv():
        pass

from session_manager import session_manager
from dashboard_mode import dashboard_mode

# Load environment variables
load_dotenv()

# Global processing control
stop_processing = threading.Event()

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

async def broadcast_anomaly_to_user(username: str, anomaly_data: dict):
    """Broadcast new anomaly to user's active WebSocket connection"""
    print(f"🔍 Attempting to broadcast anomaly to user: {username}")
    websocket = session_manager.get_websocket(username)
    print(f"🔍 WebSocket found for {username}: {websocket is not None}")
    
    if websocket:
        try:
            message = {
                "type": "new_anomaly",
                "data": anomaly_data,
                "timestamp": time.time()
            }
            await websocket.send_text(json.dumps(message))
            print(f"📡 Broadcasted anomaly to user {username}")
            print(f"📨 Message content: {json.dumps(message, indent=2)}")
        except Exception as e:
            print(f"❌ Failed to broadcast to {username}: {e}")
            # Remove disconnected connection
            session_manager.unregister_websocket(username)
    else:
        print(f"🔍 No active WebSocket connection for user {username}")

async def cleanup_all_sessions():
    """MASTER CLEANUP - Single entry point for all session cleanup"""
    print("🧹 MASTER CLEANUP initiated...")
    return session_manager.cleanup_all_sessions()

async def stop_session(session_id: str):
    """Stop a specific processing session - delegates to SessionManager"""
    return session_manager.stop_session(session_id)

async def connect_to_mongodb():
    """Connect to MongoDB database"""
    global mongodb_client, database
    try:
        print(f"🔗 Attempting to connect to MongoDB at: {MONGODB_URL}")
        
        # Create client with proper timeout settings
        mongodb_client = AsyncIOMotorClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            maxPoolSize=50
        )
        
        # Test the connection with a simple ping
        await mongodb_client.admin.command('ping')
        
        # Set the database
        database = mongodb_client[DATABASE_NAME]
        
        # Test database access
        await database.list_collection_names()
        
        print("✅ Connected to MongoDB successfully")
        print(f"📊 Database: {DATABASE_NAME}")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("💡 Make sure MongoDB service is running")
        mongodb_client = None
        database = None
        return False
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

# Include user data routes
from routes.user_data import router as user_data_router
app.include_router(user_data_router)

# MongoDB connection test endpoint
@app.get("/api/test/mongodb")
async def test_mongodb_connection():
    """Test MongoDB connection status"""
    if database is None:
        return {
            "status": "disconnected",
            "message": "MongoDB not connected - running in memory mode",
            "mongodb_url": MONGODB_URL,
            "database_name": DATABASE_NAME
        }
    
    try:
        # Test database access
        collections = await database.list_collection_names()
        
        # Test a simple operation
        result = await database.test_collection.insert_one({"test": "connection", "timestamp": datetime.now().isoformat()})
        await database.test_collection.delete_one({"_id": result.inserted_id})
        
        return {
            "status": "connected",
            "message": "MongoDB connection successful",
            "mongodb_url": MONGODB_URL,
            "database_name": DATABASE_NAME,
            "collections": collections,
            "test_operation": "success"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"MongoDB connection test failed: {str(e)}",
            "mongodb_url": MONGODB_URL,
            "database_name": DATABASE_NAME
        }

# FastAPI Events
@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection on startup"""
    await connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of all resources"""
    print("🔄 Server shutdown initiated - stopping all processing...")
    
    # MASTER CLEANUP using SessionManager - SINGLE ENTRY POINT
    session_manager.stop_all_sessions()
    await asyncio.sleep(0.5)  # Give sessions time to stop
    session_manager.cleanup_all_sessions()
    
    # Close MongoDB connection
    await close_mongodb_connection()
    
    print("✅ Server shutdown complete")

# Global storage for anomaly events with structured logging
# Changed to user-based storage: {username: {live: [], upload: [], cctv: []}}
user_anomaly_data = {}  # User-specific data storage

def get_user_data(username):
    """Get or create user data structure"""
    if username not in user_anomaly_data:
        user_anomaly_data[username] = {
            'live': [],      # Live camera anomalies
            'upload': [],    # Video upload anomalies  
            'cctv': [],      # CCTV stream anomalies
            'sessions': []   # Session metadata
        }
    return user_anomaly_data[username]

def add_user_anomaly(username, anomaly_type, anomaly_data):
    """Add anomaly to user's specific data type"""
    user_data = get_user_data(username)
    if anomaly_type in user_data:
        # Clean anomaly data to ensure JSON serializability
        clean_data = {
            'id': anomaly_data.get('id', str(time.time())),
            'frame_id': anomaly_data.get('frame_id', 0),
            'timestamp': anomaly_data.get('timestamp', time.time()),
            'session_time': anomaly_data.get('session_time', datetime.now().isoformat()),
            'details': str(anomaly_data.get('details', '')),
            'fusion_status': str(anomaly_data.get('fusion_status', '')),
            'frame_count': int(anomaly_data.get('frame_count', 1)),
            'duration': float(anomaly_data.get('duration', 0)),
            'tier1_result': {
                'confidence': float(anomaly_data.get('tier1_result', {}).get('confidence', 0)),
                'scene_detected': bool(anomaly_data.get('tier1_result', {}).get('scene_detected', False)),
                'pose_detected': bool(anomaly_data.get('tier1_result', {}).get('pose_detected', False)),
                'audio_detected': bool(anomaly_data.get('tier1_result', {}).get('audio_detected', False)),
                'audio_transcription': str(anomaly_data.get('tier1_result', {}).get('audio_transcription', '')),
            },
            'tier2_analysis': anomaly_data.get('tier2_analysis'),
            'frame_file': str(anomaly_data.get('frame_file', '')) if anomaly_data.get('frame_file') else None,
            'video_file': str(anomaly_data.get('video_file', '')) if anomaly_data.get('video_file') else None,
            'anomaly_type': anomaly_type,
            'created_at': time.time(),
            'username': username
        }
        
        user_data[anomaly_type].append(clean_data)
        
        # Keep only last 50 anomalies per type to prevent memory issues
        if len(user_data[anomaly_type]) > 50:
            user_data[anomaly_type] = user_data[anomaly_type][-50:]
        
        # Broadcast to user's active WebSocket connection in background (with error handling)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # CRITICAL FIX: Always attempt to broadcast, don't skip due to loop issues
                asyncio.create_task(broadcast_anomaly_to_user(username, clean_data))
                print(f"📡 Scheduled broadcast for user {username}")
        except Exception as e:
            print(f"⚠️ Could not schedule broadcast (non-critical): {e}")
            # Fallback: try to broadcast directly if possible
            try:
                websocket = session_manager.get_websocket(username)
                if websocket:
                    print(f"🔄 Attempting direct broadcast fallback for {username}")
            except Exception as fallback_error:
                print(f"⚠️ Direct broadcast fallback also failed: {fallback_error}")
        
        print(f"✅ Added anomaly for {username} ({anomaly_type}): {clean_data.get('details', '')}")
        return True
    return False

def get_user_anomalies(username, anomaly_type=None):
    """Get user's anomalies by type or all"""
    user_data = get_user_data(username)
    if anomaly_type and anomaly_type in user_data:
        return user_data[anomaly_type]
    else:
        # Return all anomalies combined
        all_anomalies = []
        for atype in ['live', 'upload', 'cctv']:
            all_anomalies.extend(user_data[atype])
        return sorted(all_anomalies, key=lambda x: x.get('created_at', 0), reverse=True)

# REMOVED: Global variables - SessionManager handles anomaly tracking, status, and statistics
# - last_anomaly_time: SessionManager.get_stats() provides this
# - current_anomaly_event: SessionManager tracks anomaly events
# - current_status/current_details: SessionManager provides session status
# - frame_counter: SessionManager tracks frame statistics
# - camera_in_use: SessionManager.acquire_camera() handles camera usage
# This removes ~10 lines of redundant global state

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
async def save_anomaly_to_db(anomaly_event, username="demo_user"):
    """Save anomaly event to MongoDB with user association"""
    if database is None:
        return None
    
    try:
        # Add username to the anomaly event
        anomaly_event["username"] = username
        
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
        print(f"📊 Saved anomaly to MongoDB for user {username}: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"❌ Error saving anomaly to MongoDB: {e}")
        return None

async def save_session_metadata(session_data):
    """Save session metadata to MongoDB"""
    if database is None:
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
    if database is None:
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
    if database is None:
        return []
    
    try:
        cursor = database.sessions.find().sort("start_time", -1)
        sessions = await cursor.to_list(length=None)
        return sessions
    except Exception as e:
        print(f"❌ Error retrieving sessions from MongoDB: {e}")
        return []

def generate_video_stream():
    """Generate video stream with real-time status overlay using SessionManager"""
    
    # Check if camera is already in use by WebSocket stream
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera for video stream - likely in use by WebSocket")
        # Generate a placeholder stream instead of hanging
        for i in range(100):  # Generate 100 placeholder frames
            placeholder_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # CONSOLIDATED: Get status from SessionManager if available
            current_status = "Normal"
            current_details = "Camera in use by monitoring"
            
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
            
            # Add status overlay using default values (SessionManager would provide real status)
            try:
                current_status = "Normal"  # Default status
                current_details = "Live streaming"  # Default details
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
    """Print concise performance statistics using SessionManager"""
    stats = session_manager.get_stats()
    if stats.get("pipeline_start_time") is None:
        session_manager.performance_stats["pipeline_start_time"] = time.time()
        return
    
    # Only print stats occasionally, not every 5 seconds
    elapsed = time.time() - stats["pipeline_start_time"]
    if elapsed % 30 < 5:  # Only every 30 seconds
        fps_processed = stats["frames_processed"] / elapsed if elapsed > 0 else 0
        audio_rate = stats["audio_transcribed"] / elapsed if elapsed > 0 else 0
        
        print(f"\n📊 PIPELINE SUMMARY (Runtime: {elapsed:.1f}s)")
        print(f"🎬 Video: {fps_processed:.1f} FPS | 🎤 Audio: {audio_rate:.1f} chunks/s")
        print(f"🚨 T1: {stats['tier1_anomalies_detected']} anomalies | 🔬 T2: {stats['tier2_analyses_completed']}/{stats['tier2_analyses_triggered']} analyses")

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
    
    if database is not None:
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
    if database is not None:
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
    if not user_found and database is not None:
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
    if not user_found and database is None:
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
        if database is not None:
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
    
    if database is not None and session_id:
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

@app.post("/api/stop_all_processing")
async def stop_all_processing_endpoint():
    """Emergency stop - MASTER CLEANUP for all processing sessions"""
    try:
        # SINGLE CLEANUP ENTRY POINT
        await cleanup_all_sessions()
        return {"status": "success", "message": "All processing stopped and cleaned up"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/stats")
async def get_system_stats():
    """Get current system statistics"""
    stats = session_manager.get_stats()
    return {
        "mongodb_connected": database is not None,
        "performance_stats": stats,
        "current_status": "Active" if stats['active_sessions'] > 0 else "Idle",
        "total_stored_anomalies": await database.anomalies.count_documents({}) if database is not None else 0,
        "total_sessions": await database.sessions.count_documents({}) if database is not None else 0,
        "active_sessions": stats['active_sessions'],
        "active_cameras": stats['active_cameras']
    }

@app.websocket("/stream_video")
async def stream_video(websocket: WebSocket):
    await websocket.accept()
    
    # Get username from query parameters
    query_params = websocket.query_params
    current_username = query_params.get("username", "dashboard_user")
    
    # Check if this is dashboard mode (simplified)
    is_dashboard = dashboard_mode.is_dashboard_user(current_username)
    
    if is_dashboard:
        print(f"🎛️ DASHBOARD MODE activated for user: {current_username}")
        # Create session with SessionManager first (moved up to fix UnboundLocalError)
        session_id = session_manager.create_session(current_username, "live_stream")
        session = session_manager.get_session(session_id)
        
        if not session:
            await websocket.send_json({"error": "Failed to create session"})
            return
        
        dashboard_mode.start_dashboard_session()
        # Check if we should continue existing session or start new one
        if dashboard_mode.should_continue_session():
            print(f"🔄 Dashboard: Continuing EXISTING monitoring session {dashboard_mode.current_session_id}")
            # Update the session_id for the existing monitoring session but keep frames
            dashboard_mode.current_session_id = session_id
        else:
            print(f"🚀 Dashboard: Starting NEW monitoring session (clearing old frames)")
            dashboard_mode.start_new_monitoring_session(session_id, f"dashboard_recording_{int(time.time())}.mp4")
    else:
        print(f"👤 USER MODE activated for user: {current_username}")
        # Create session for non-dashboard users
        session_id = session_manager.create_session(current_username, "live_stream")
        session = session_manager.get_session(session_id)
        
        if not session:
            await websocket.send_json({"error": "Failed to create session"})
            return
    
    print(f"🔌 WebSocket connected for user: {current_username} ({'Dashboard' if is_dashboard else 'User'} Mode)")
    
    session_stop_event = session['stop_event']
    
    # Register WebSocket connection
    session_manager.register_websocket(current_username, websocket)
    
    # Try to acquire camera
    camera_opened = False
    video_cap = None
    cv2.setLogLevel(0)
    
    # Try different camera indices
    camera_indices_to_try = [0, 1, -1]
    
    for camera_idx in camera_indices_to_try:
        if session_manager.acquire_camera(session_id, camera_idx):
            print(f"🎬 Trying camera index {camera_idx}")
            
            for attempt in range(3):
                try:
                    # Release any existing capture first
                    if video_cap:
                        video_cap.release()
                        time.sleep(0.5)
                    
                    # Try different capture backends
                    if attempt == 0:
                        video_cap = cv2.VideoCapture(camera_idx)
                    elif attempt == 1:
                        video_cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
                    else:
                        video_cap = cv2.VideoCapture(camera_idx, cv2.CAP_V4L2)
                    
                    if video_cap is None:
                        continue
                    
                    # Configure camera
                    video_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    video_cap.set(cv2.CAP_PROP_FPS, 30)
                    
                    # Test if camera works
                    if video_cap.isOpened():
                        ret, test_frame = video_cap.read()
                        if ret and test_frame is not None and test_frame.size > 0:
                            print(f"✅ Camera {camera_idx} opened successfully on attempt {attempt + 1}")
                            camera_opened = True
                            
                            # Store camera in session resources
                            session_manager.update_session(session_id, {
                                'resources': {'video_cap': video_cap}
                            })
                            break
                        else:
                            print(f"⚠️ Camera {camera_idx} opened but failed to read frame")
                            video_cap.release()
                            video_cap = None
                    else:
                        print(f"⚠️ Camera {camera_idx} failed to open")
                        if video_cap:
                            video_cap.release()
                        video_cap = None
                        
                except Exception as e:
                    print(f"❌ Camera {camera_idx} attempt {attempt + 1} failed: {e}")
                    if video_cap:
                        video_cap.release()
                    video_cap = None
                
                if camera_opened:
                    break
            
            if camera_opened:
                break
            else:
                # Release camera if we couldn't open it
                session_manager.release_camera(session_id)
    
    if not camera_opened or video_cap is None:
        error_msg = "Camera unavailable. Please ensure other camera applications are closed and try again."
        await websocket.send_json({"error": error_msg})
        # SINGLE CLEANUP ENTRY POINT
        session_manager.cleanup_session(session_id)
        return

    # Get video properties
    width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video_cap.get(cv2.CAP_PROP_FPS) or 30
    
    # Setup video recording using existing session_id
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"recorded_videos/session_{timestamp}.mp4"
    
    # Save session metadata to MongoDB (use existing session_id)
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

    # CONSOLIDATED WORKER STARTUP - Let SessionManager handle everything
    audio_stream = AudioStream()
    audio_stream.start()
    
    # Start all workers using SessionManager - SINGLE CALL
    if not session_manager.start_session_workers(session_id, video_cap, video_writer, fps, audio_stream):
        error_msg = "Failed to start processing workers"
        await websocket.send_json({"error": error_msg})
        session_manager.cleanup_session(session_id)
        return
    
    print(f"🚀 ALL WORKERS STARTED via SessionManager for session {session_id}")
    
    try:
        last_stats_time = time.time()
        
        while True:
            try:
                # Get fused result from SessionManager fusion queue
                fused_result = session_manager.fusion_results_queue.get(timeout=0.5)
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
                
                # �️ SAFETY CHECK: Ensure tier1_result is valid
                if tier1_result is None:
                    print("❌ tier1_result is None, creating default result")
                    tier1_result = {
                        "status": "Normal",
                        "details": "Default result due to processing error",
                        "tier1_components": {
                            "pose_analysis": {"anomaly_detected": False, "summary": "Error"},
                            "audio_analysis": {"available": False, "summary": "Error"},
                            "scene_analysis": {"anomaly_probability": 0.0, "summary": "Error"},
                            "fusion_logic": {"initial_status": "Normal", "final_status": "Normal"}
                        }
                    }
                
                # �🔍 DETAILED TIER 1 LOGGING
                print(f"🔍 Tier1 Result: {json.dumps(tier1_result, indent=2)}")
                
                status = tier1_result.get("status", "Normal") if tier1_result and isinstance(tier1_result, dict) else "Normal"
                details = tier1_result.get("details", "No details") if tier1_result and isinstance(tier1_result, dict) else "No details"
                
                if status == "Suspected Anomaly":
                    # CONSOLIDATED: Use SessionManager for anomaly cooldown tracking
                    stats = session_manager.get_stats()
                    last_anomaly_time = stats.get("last_anomaly_time", 0)
                    anomaly_cooldown_period = 1.0  # 1 second cooldown
                    
                    time_since_last = timestamp - last_anomaly_time
                    
                    if time_since_last < anomaly_cooldown_period:
                        # This is part of the same incident - update but don't process fully
                        print(f"🔄 Continuing incident (cooldown: {time_since_last:.1f}s)")
                        # Still send to frontend but mark as continuation
                        tier1_result.update({
                            "status": "Normal",  # Don't trigger new anomaly alert
                            "details": "Monitoring...",
                            "incident_continuation": True
                        })
                    else:
                        # This is a NEW anomaly incident - process fully  
                        session_manager.update_stats({"last_anomaly_time": timestamp})
                        session_manager.increment_stat("tier1_anomalies_detected")
                        print(f"\n🚨 NEW ANOMALY INCIDENT #{session_manager.get_stats()['tier1_anomalies_detected']}")
                        print(f"🚨 ANOMALY DETECTED: {details}")
                        
                        # 🔍 DETAILED ANOMALY BREAKDOWN
                        if "tier1_components" in tier1_result:
                            components = tier1_result["tier1_components"]
                            print(f"🔬 TIER 1 COMPONENT ANALYSIS:")
                            print(f"  📸 POSE: {components.get('pose_analysis', {}).get('summary', 'N/A')}")
                            print(f"  🎙️  AUDIO: {components.get('audio_analysis', {}).get('summary', 'N/A')}")
                            print(f"  🎬 SCENE: {components.get('scene_analysis', {}).get('summary', 'N/A')}")
                            print(f"  🧠 FUSION: {components.get('fusion_logic', {}).get('details', 'N/A')}")
                        print(f"🚨 TRIGGERING TIER 2 ANALYSIS FOR FRAME {frame_id}...")
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
                        
                        # CRITICAL FIX: For dashboard users, store in BOTH places for maximum compatibility
                        if is_dashboard:
                            # Store in dashboard mode for dashboard-specific endpoints
                            dashboard_result = dashboard_mode.add_dashboard_anomaly(anomaly_event)
                            print(f"📊 Dashboard anomaly stored: {dashboard_result is not None}")
                            
                            # ALSO store in user anomaly system for /anomaly_events compatibility
                            add_user_anomaly(current_username, 'live', anomaly_event)
                            print(f"📊 User anomaly stored for dashboard user: {current_username}")
                        else:
                            # Use complex user-specific storage for frontend
                            add_user_anomaly(current_username, 'live', anomaly_event)
                        current_anomaly_event = anomaly_event  # Track current incident
                        
                        # Save to MongoDB (async)
                        await save_anomaly_to_db(anomaly_event.copy(), current_username)
                        
                        # TRIGGER TIER 2 ANALYSIS (synchronous but optimized)
                        session_manager.increment_stat("tier2_analyses_triggered")
                        print(f"🔬 TRIGGERING TIER 2 ANALYSIS #{session_manager.get_stats()['tier2_analyses_triggered']}...")
                        print(f"🔬 Tier 2 Analysis Starting for Frame {frame_id} at {timestamp}")
                        
                        # Send immediate Tier 2 start notification to frontend
                        tier2_start_notification = {
                            "type": "tier2_start",
                            "frame_id": frame_id,
                            "timestamp": timestamp,
                            "message": "Starting advanced AI analysis...",
                            "status": "analyzing"
                        }
                        
                        try:
                            if websocket.client_state.name == "CONNECTED":
                                await websocket.send_json(tier2_start_notification)
                                print(f"📤 Tier 2 START notification sent to frontend")
                        except Exception as send_error:
                            print(f"❌ Tier 2 START notification error: {send_error}")
                        
                        try:
                            tier2_result = run_tier2_continuous(frame.copy(), audio_chunk_path, tier1_result.copy())
                            session_manager.increment_stat("tier2_analyses_completed")
                            
                            # Update anomaly event with Tier 2 analysis
                            anomaly_event["tier2_analysis"] = tier2_result
                            tier1_result["tier2_analysis"] = tier2_result
                            
                            print(f"✅ TIER 2 ANALYSIS COMPLETE FOR FRAME {frame_id}")
                            print(f"📋 Summary: {tier2_result.get('reasoning_summary', 'Analysis complete')}")
                            print(f"🎯 Threat Level: {tier2_result.get('threat_severity_index', 0.5):.2f}")
                            print(f"🔍 Tier 2 Full Result: {json.dumps(tier2_result, indent=2)}")
                            
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
                                    print(f"📤 Tier 2 results sent to frontend for frame {frame_id}")
                            except Exception as send_error:
                                print(f"❌ Tier 2 WebSocket error: {send_error}")
                                
                        except Exception as tier2_error:
                            session_manager.increment_stat("tier2_analyses_failed")
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
                
                # Encode frame for live video display
                try:
                    # Resize frame for efficient transmission (optional)
                    display_frame = cv2.resize(frame, (640, 480))
                    ret, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    if ret:
                        frame_base64 = base64.b64encode(buffer).decode('utf-8')
                        tier1_result["frame_data"] = frame_base64
                except Exception as frame_encode_error:
                    print(f"Frame encoding error: {frame_encode_error}")
                
                # Send result via WebSocket
                try:
                    if websocket.client_state.name == "CONNECTED":
                        # 🚨 EXTREME DEBUG: Log ALL WebSocket sends
                        print(f"🔥 SENDING WEBSOCKET MESSAGE:")
                        print(f"📨 Status: {tier1_result.get('status')}")
                        print(f"📨 Details: {tier1_result.get('details')}")
                        print(f"📨 Frame ID: {tier1_result.get('frame_id')}")
                        print(f"📨 Message size: {len(str(tier1_result))} chars")
                        
                        await websocket.send_json(tier1_result)
                        print(f"✅ WEBSOCKET MESSAGE SENT SUCCESSFULLY!")
                        
                        # Log ALL messages, not just anomalies
                        if tier1_result.get("status") == "Suspected Anomaly":
                            print(f"🚨🚨� ANOMALY WEBSOCKET SENT: {tier1_result.get('status')} - {tier1_result.get('details', '')}")
                        else:
                            print(f"ℹ️ Normal WebSocket sent: {tier1_result.get('status')}")
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
        print(f"WebSocket client disconnected: {current_username}")
    except asyncio.CancelledError:
        print(f"WebSocket connection cancelled: {current_username}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
    finally:
        # Cleanup session using SessionManager
        print(f"🧹 Cleaning up session: {session_id}")
        
        # Stop dashboard monitoring session if dashboard mode
        if is_dashboard:
            dashboard_mode.stop_monitoring_session()
            print("🎛️ Dashboard monitoring session stopped")
        
        # Unregister WebSocket connection
        session_manager.unregister_websocket(current_username)
        
        # Clean up session and all its resources - SINGLE CLEANUP ENTRY POINT
        session_manager.cleanup_session(session_id)
        
        print(f"✅ Session {session_id} cleanup complete")

# ========== CONSOLIDATED WORKER FUNCTIONS - SESSION MANAGER ONLY ==========
# These replace all old global-variable-based worker functions

def video_capture_worker_session(video_cap, video_writer, fps, session_stop_event):
    """CONSOLIDATED Session-aware video worker - uses SessionManager only"""
    frame_count = 0
    processed_count = 0
    start_time = time.time()
    
    print("🎬 Session video worker started (CONSOLIDATED)")
    
    while not session_stop_event.is_set():
        ret, frame = video_cap.read()
        if not ret:
            print("❌ Video capture failed")
            break
            
        # Use SessionManager for stats
        session_manager.increment_stat("frames_captured")
        frame_count += 1
        
        # Record every frame to video
        try:
            if video_writer and video_writer.isOpened():
                video_writer.write(frame)
        except Exception as e:
            pass  # Silent video writing errors
        
        # Process every 5th frame (~6 FPS)
        if frame_count % 5 == 0:
            current_timestamp = time.time()
            
            try:
                # Create video data packet
                video_data = {
                    "frame_id": frame_count,
                    "timestamp": current_timestamp,
                    "frame": frame.copy(),  # Thread-safe copy
                    "session_time": current_timestamp - start_time
                }
                
                # Add to SessionManager video queue (non-blocking)
                if not session_manager.video_queue.full():
                    session_manager.video_queue.put(video_data)
                    session_manager.increment_stat("frames_processed")
                    processed_count += 1
                    
                    if processed_count % 50 == 0:
                        print(f"🎬 Processed {processed_count} frames")
                else:
                    pass  # Drop frame if queue full
                    
            except Exception as e:
                print(f"Video processing error: {e}")
                
        time.sleep(1/30.0)  # Maintain ~30 FPS
    
    print("🎬 CONSOLIDATED Session video worker stopped")

def audio_capture_worker_session(audio_queue, audio_stream, session_stop_event):
    """CONSOLIDATED Session-aware audio worker - uses SessionManager only"""
    from utils.audio_processing import chunk_and_transcribe_tiny
    
    chunk_count = 0
    transcribed_count = 0
    start_time = time.time()
    
    print("🎤 Session audio worker started (CONSOLIDATED)")
    
    while not session_stop_event.is_set():
        try:
            # Get audio chunk (blocks until available)
            audio_chunk_path = audio_stream.get_chunk()
            
            if audio_chunk_path:
                try:
                    # Use SessionManager for stats
                    session_manager.increment_stat("audio_chunks_captured")
                except:
                    continue
                    
                chunk_count += 1
                current_timestamp = time.time()
                
                # Transcribe audio
                transcripts = chunk_and_transcribe_tiny(audio_chunk_path)
                
                if transcripts:
                    audio_text = " | ".join(transcripts)
                    session_manager.increment_stat("audio_transcribed")
                    transcribed_count += 1
                    
                    # Create audio data packet
                    audio_data = {
                        "timestamp": current_timestamp,
                        "audio_text": audio_text,
                        "transcripts": transcripts,
                        "chunk_path": audio_chunk_path
                    }
                    
                    # Add to SessionManager audio queue (non-blocking)
                    if not session_manager.audio_queue.full():
                        session_manager.audio_queue.put(audio_data)
                        
                        if transcribed_count % 20 == 0:
                            print(f"🎤 Transcribed {transcribed_count} audio chunks")
                    else:
                        # Only log queue full occasionally
                        if chunk_count % 100 == 0:
                            print("⚠️ Audio queue full, dropping transcripts")
                
            else:
                time.sleep(0.05)  # Brief pause if no audio available
                
        except Exception as e:
            print(f"❌ Session audio worker error: {e}")
    
    print("🎤 CONSOLIDATED Session audio worker stopped")

def fusion_worker_session(session_stop_event, video_queue_param=None, audio_queue_param=None, fusion_results_queue_param=None):
    """CONSOLIDATED Session-aware fusion worker - uses SessionManager only"""
    
    print("🔀 Session fusion worker started (CONSOLIDATED)")
    
    # Keep recent audio data for temporal matching
    recent_audio = deque(maxlen=20)  # Store last 20 audio chunks (~5 seconds)
    fusion_count = 0
    
    while not session_stop_event.is_set():
        try:
            # Get video frame from SessionManager (blocking with timeout)
            try:
                video_data = session_manager.video_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            
            video_timestamp = video_data["timestamp"]
            
            # Update recent audio buffer from SessionManager
            while not session_manager.audio_queue.empty():
                try:
                    audio_data = session_manager.audio_queue.get_nowait()
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
                session_manager.increment_stat("fusion_video_audio")
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
                session_manager.increment_stat("fusion_video_only")
            
            # Add to SessionManager fusion results queue
            if not session_manager.fusion_results_queue.full():
                session_manager.fusion_results_queue.put(fused_result)
                fusion_count += 1
                
                if fusion_count % 30 == 0:
                    print(f"🔀 Processed {fusion_count} fusion results")
            # Silently drop if queue is full
                
        except Exception as e:
            print(f"❌ Session fusion worker error: {e}")
            time.sleep(0.1)
    
    print("🔀 CONSOLIDATED Session fusion worker stopped")

@app.get("/anomaly_events")
async def get_anomaly_events(username: str = None, anomaly_type: str = None):
    """Get anomaly events - simplified for dashboard mode"""
    try:
        if not username:
            username = "dashboard_user"  # Default to dashboard user
        
        # Check if dashboard mode
        if dashboard_mode.is_dashboard_user(username):
            anomalies = dashboard_mode.get_dashboard_anomalies()
            return {
                "anomaly_events": anomalies,
                "mode": "dashboard",
                "total": len(anomalies),
                "stats": dashboard_mode.get_dashboard_stats()
            }
        
        # Original user-specific logic for frontend
        try:
            user_anomalies = get_user_anomalies(username, anomaly_type)
        except Exception as e:
            print(f"Error getting user anomalies: {e}")
            return {"anomaly_events": [], "error": "Failed to fetch user anomalies"}
        
        # Filter out corrupted data
        clean_anomalies = []
        for anomaly in user_anomalies:
            try:
                if isinstance(anomaly, dict) and all(isinstance(k, str) for k in anomaly.keys()):
                    clean_anomalies.append(anomaly)
                else:
                    print(f"Skipping corrupted anomaly data: {type(anomaly)}")
            except Exception as e:
                print(f"Error processing anomaly: {e}")
                continue
        
        return {
            "anomaly_events": clean_anomalies,
            "username": username,
            "anomaly_type": anomaly_type or "all",
            "total_count": len(clean_anomalies)
        }
    except Exception as e:
        print(f"Error in get_anomaly_events: {e}")
        return {"anomaly_events": [], "error": str(e)}

@app.get("/anomaly_events/{event_index}")
async def get_anomaly_event(event_index: int, username: str = None):
    """Get specific anomaly event by index for user"""
    if not username:
        return {"error": "Username required"}
    
    user_anomalies = get_user_anomalies(username)
    if 0 <= event_index < len(user_anomalies):
        return user_anomalies[event_index]
    return {"error": "Event not found"}

@app.get("/dashboard")
async def dashboard():
    """Serve the anomaly detection dashboard"""
    return FileResponse("dashboard.html")

@app.post("/dashboard/new_session")
async def start_new_dashboard_session():
    """Start a new monitoring session (clears old anomaly frames)"""
    import uuid
    new_session_id = str(uuid.uuid4())
    dashboard_mode.force_new_monitoring_session(new_session_id, f"dashboard_recording_{int(time.time())}.mp4")
    
    # CRITICAL FIX: Ensure monitoring is activated
    dashboard_mode.session_metadata['monitoring_active'] = True
    print(f"✅ Dashboard monitoring activated: {dashboard_mode.session_metadata['monitoring_active']}")
    
    return {
        "success": True,
        "message": "New monitoring session started - old frames cleared",
        "session_id": new_session_id,
        "monitoring_active": dashboard_mode.session_metadata['monitoring_active']
    }

@app.get("/")
async def root():
    return {"message": "Anomaly Detection API", "dashboard": "/dashboard"}

@app.get("/debug/test_anomaly")
async def test_anomaly_creation():
    """DEBUG ENDPOINT: Create a test anomaly to verify the system works"""
    import uuid
    
    # Create test anomaly data
    test_anomaly = {
        'id': str(uuid.uuid4()),
        'frame_id': f"test_{int(time.time())}",
        'timestamp': time.time(),
        'session_time': datetime.now().isoformat(),
        'details': "TEST ANOMALY: Manual test anomaly created via debug endpoint",
        'fusion_status': 'test',
        'frame_count': 1,
        'duration': 0.0,
        'tier1_result': {
            'confidence': 0.85,
            'scene_detected': True,
            'pose_detected': True,
            'audio_detected': False,
            'audio_transcription': '',
        },
        'tier2_analysis': {
            'threat_severity_index': 0.75,
            'reasoning_summary': 'Test anomaly for debugging purposes',
            'visual_score': 0.8,
            'audio_score': 0.0,
            'multimodal_agreement': 0.7
        },
        'frame_file': None,
        'video_file': None,
        'anomaly_type': 'test',
        'created_at': time.time(),
        'username': 'dashboard_user'
    }
    
    # Store in both dashboard and user systems
    dashboard_result = dashboard_mode.add_dashboard_anomaly(test_anomaly)
    user_result = add_user_anomaly('dashboard_user', 'live', test_anomaly)
    
    return {
        "success": True,
        "message": "Test anomaly created",
        "dashboard_stored": dashboard_result is not None,
        "user_stored": user_result,
        "monitoring_active": dashboard_mode.session_metadata.get('monitoring_active', False),
        "test_anomaly": test_anomaly
    }

@app.get("/debug/test_websocket")
async def test_websocket_anomaly():
    """DEBUG ENDPOINT: Send a test anomaly via WebSocket to dashboard_user"""
    websocket = session_manager.get_websocket("dashboard_user")
    
    if not websocket:
        return {
            "success": False,
            "message": "No active WebSocket connection for dashboard_user",
            "active_connections": list(session_manager._websocket_connections.keys())
        }
    
    # Create test anomaly message
    test_message = {
        "status": "Suspected Anomaly",
        "details": "TEST ANOMALY: Manually triggered via debug endpoint",
        "frame_id": f"test_{int(time.time())}",
        "timestamp": time.time(),
        "fusion_status": "test",
        "video_file": "test.mp4",
        "tier1_components": {
            "pose_analysis": {
                "anomaly_detected": True,
                "summary": "Test pose anomaly",
                "raw_score": 0.85
            },
            "audio_analysis": {
                "transcripts": [],
                "available": False,
                "summary": "No audio for test",
                "transcript_text": ""
            },
            "scene_analysis": {
                "anomaly_probability": 0.92,
                "summary": "Test scene anomaly with high confidence"
            },
            "fusion_logic": {
                "initial_status": "Suspected Anomaly",
                "final_status": "Suspected Anomaly",
                "smoothing_applied": False,
                "details": "TEST: High-confidence test anomaly"
            }
        }
    }
    
    try:
        await websocket.send_json(test_message)
        return {
            "success": True,
            "message": "Test anomaly sent via WebSocket",
            "test_data": test_message
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to send test anomaly: {e}",
            "error": str(e)
        }

@app.get("/debug/dashboard_status")
async def dashboard_status():
    """DEBUG ENDPOINT: Check dashboard status and data"""
    dashboard_anomalies = dashboard_mode.get_dashboard_anomalies()
    user_anomalies = get_user_anomalies('dashboard_user')
    
    return {
        "dashboard_mode": {
            "monitoring_active": dashboard_mode.session_metadata.get('monitoring_active', False),
            "session_id": dashboard_mode.current_session_id,
            "session_start": dashboard_mode.session_metadata.get('session_start'),
            "anomaly_count": len(dashboard_anomalies),
            "session_metadata": dashboard_mode.session_metadata
        },
        "user_mode": {
            "anomaly_count": len(user_anomalies),
            "last_5_anomalies": user_anomalies[:5] if user_anomalies else []
        },
        "websocket_connections": list(session_manager._websocket_connections.keys()),
        "active_sessions": len(session_manager._sessions)
    }

@app.get("/user_stats/{username}")
async def get_user_stats(username: str):
    """Get user-specific statistics"""
    user_data = get_user_data(username)
    total_anomalies = sum(len(user_data[atype]) for atype in ['live', 'upload', 'cctv'])
    
    return {
        "username": username,
        "total_anomalies": total_anomalies,
        "live_anomalies": len(user_data['live']),
        "upload_anomalies": len(user_data['upload']),
        "cctv_anomalies": len(user_data['cctv']),
        "sessions": len(user_data['sessions'])
    }

@app.get("/download-session-data")
async def download_session_data(username: str = "demo_user"):
    """Create downloadable zip with all session data for specific user"""
    import zipfile
    import io
    import base64
    from datetime import datetime
    
    # Get user's anomalies
    user_anomalies = get_user_anomalies(username)
    
    # Create in-memory zip file
    zip_buffer = io.BytesIO()
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Create session summary
            session_summary = {
                "session_info": {
                    "username": username,
                    "total_anomalies": len(user_anomalies),
                    "generation_time": datetime.now().isoformat(),
                    "performance_stats": session_manager.get_stats()  # Use SessionManager stats
                },
                "anomaly_events": user_anomalies
            }
            
            # Add metadata
            zip_file.writestr("metadata/session_summary.json", 
                            json.dumps(session_summary, indent=2, default=str))
            
            # Add individual anomaly frames if they exist
            for i, anomaly in enumerate(user_anomalies):
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
            if len(user_anomalies) > 0:
                video_files = set()
                for anomaly in user_anomalies:
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
    """CONSOLIDATED uploaded video processing via SessionManager"""
    await websocket.accept()
    
    # Get user authentication from WebSocket headers or query params
    current_username = "demo_user"  # Default for now - should be from session/auth
    
    # Try to get username from query parameters
    query_params = websocket.query_params
    if "username" in query_params:
        current_username = query_params["username"]
    
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
        # CONSOLIDATED: SessionManager handles ALL state initialization
        # No need for manual global variable reset - SessionManager handles this
        
        print(f"📹 Processing uploaded video: {filename}")
        await websocket.send_json({"status": "Processing started", "filename": filename})
        
        # CONSOLIDATED: Use SessionManager's start_session_workers for uploaded video
        upload_session_id = session_manager.create_session(current_username, "uploaded_video")
        
        # SessionManager handles ALL worker creation and management
        workers_started = session_manager.start_session_workers(
            upload_session_id, 
            video_cap=video_cap,
            video_writer=None,  # No recording for uploaded videos
            fps=30,  # Default FPS 
            audio_stream=None  # No audio for uploaded videos
        )
        
        if not workers_started:
            video_cap.release()
            await websocket.send_json({"error": "Failed to start video processing workers"})
            return
        
        print(f"🚀 Upload workers started via SessionManager for session {upload_session_id}")
        
        # Process fusion results (same logic as live stream)
        last_stats_time = time.time()
        
        while True:
            try:
                # Get fused result from SessionManager fusion queue - CONSOLIDATED
                fused_result = session_manager.fusion_results_queue.get(timeout=0.5)
            except queue.Empty:
                # Check if video processing is complete via SessionManager
                session = session_manager.get_session(upload_session_id)
                if session and not any(t.is_alive() for t in session['threads']):
                    print("📹 Video processing completed")
                    user_anomalies = get_user_anomalies(current_username, 'upload')
                    await websocket.send_json({"status": "Processing completed", "total_anomalies": len(user_anomalies)})
                    break
                continue
            
            # Process the fused result (same logic as live stream)
            frame_id = fused_result.get("frame_id", "unknown")
            timestamp = fused_result.get("timestamp", time.time())
            fusion_status = fused_result.get("fusion_status", "unknown")
            frame = fused_result.get("frame")
            frame = fused_result.get("frame")
            audio_chunk_path = fused_result.get("audio_chunk_path")
            
            # Get detection results
            tier1_result = run_tier1_continuous(frame, audio_chunk_path)
            
            # SAFETY CHECK: Handle None result from tier1 (uploaded video)
            if tier1_result is None:
                print("⚠️ Uploaded video Tier1 returned None, using fallback")
                tier1_result = {
                    "status": "Normal",
                    "details": "Monitoring...",
                    "fusion_status": fusion_status
                }
            
            status = tier1_result.get("status", "Normal")
            details = tier1_result.get("details", "Monitoring...")
            
            if status == "Suspected Anomaly":
                # CONSOLIDATED: Use SessionManager for anomaly cooldown tracking (uploaded video)
                stats = session_manager.get_stats()
                last_anomaly_time = stats.get("last_anomaly_time", 0) 
                anomaly_cooldown_period = 1.0  # 1 second cooldown
                
                time_since_last = timestamp - last_anomaly_time
                
                if time_since_last < anomaly_cooldown_period:
                    # This is part of the same incident - update but don't process fully
                    print(f"🔄 Continuing incident (cooldown: {time_since_last:.1f}s)")
                    # Still send to frontend but mark as continuation
                    tier1_result.update({
                        "status": "Normal",
                        "details": "Monitoring...",
                        "incident_continuation": True
                    })
                else:
                    # This is a NEW anomaly incident - process fully (uploaded video)
                    session_manager.update_stats({"last_anomaly_time": timestamp})
                    # CONSOLIDATED: Use SessionManager for stats
                    session_manager.increment_stat("tier1_anomalies_detected")
                    stats = session_manager.get_stats()
                    print(f"\n🚨 NEW ANOMALY INCIDENT #{stats['tier1_anomalies_detected']}")
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
                    # Add to user's upload video anomalies
                    add_user_anomaly(current_username, 'upload', anomaly_event)
                    current_anomaly_event = anomaly_event
                    
                    # TRIGGER TIER 2 ANALYSIS - CONSOLIDATED stats for upload
                    session_manager.increment_stat("tier2_analyses_triggered")
                    tier2_stats = session_manager.get_stats()
                    print(f"🔬 TRIGGERING TIER 2 ANALYSIS #{tier2_stats['tier2_analyses_triggered']}...")
                    
                    try:
                        tier2_result = run_tier2_continuous(frame.copy(), audio_chunk_path, tier1_result.copy())
                        session_manager.increment_stat("tier2_analyses_completed")
                        
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
                        session_manager.increment_stat("tier2_analyses_failed")
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
            
            # Add frame data for frontend display (same as live stream)
            if frame is not None:
                try:
                    # Encode frame as base64 for WebSocket transmission
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    tier1_result["frame_data"] = frame_base64
                except Exception as encode_error:
                    print(f"Frame encoding error: {encode_error}")
            
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
        # CONSOLIDATED CLEANUP - SessionManager handles everything
        print(f"🧹 CONSOLIDATED cleanup for upload session: {upload_session_id}")
        session_manager.cleanup_session(upload_session_id)
        print("✅ Upload session cleanup complete")
        
        # Destroy OpenCV windows
        cv2.destroyAllWindows()
        print("🪟 OpenCV windows destroyed")
        
        # Reset stop signal for next session
        stop_processing.clear()
        print("🔄 Stop signal reset for next session")
        
        # No audio_stream to stop for uploaded videos
        print(f"📹 Video processing session ended: {filename}")

@app.websocket("/connect_cctv")
async def connect_cctv(websocket: WebSocket, ip: str, port: int = 554, username: str = None, password: str = None):
    """Connect to CCTV camera via RTSP and process through the same anomaly detection pipeline"""
    await websocket.accept()
    
    # Clear any previous stop signals
    global stop_processing
    stop_processing.clear()
    print("🔄 Stop signal cleared for CCTV session")
    
    # Get user authentication from WebSocket headers or query params
    current_username = "demo_user"  # Default for now - should be from session/auth
    
    # Try to get username from query parameters
    query_params = websocket.query_params
    if "username" in query_params:
        current_username = query_params["username"]
    
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
        # CONSOLIDATED: SessionManager handles ALL state initialization for CCTV
        # No need for manual global variable reset - SessionManager handles this
        
        print(f"🎥 CCTV connection successful: {ip}:{port}")
        await websocket.send_json({"status": "CCTV connected", "rtsp_url": rtsp_url})
        
        # Use the same processing pipeline as live stream but for CCTV
        # Note: Most CCTV streams don't have audio, so primarily video-only processing
        
        # CONSOLIDATED: Use SessionManager's start_session_workers for CCTV
        cctv_session_id = session_manager.create_session(current_username, "cctv_stream")
        
        # SessionManager handles ALL worker creation and management for CCTV
        workers_started = session_manager.start_session_workers(
            cctv_session_id,
            video_cap=video_cap,
            video_writer=None,  # No recording for CCTV by default
            fps=30,  # Default FPS for CCTV
            audio_stream=None  # Most CCTV streams don't have audio
        )
        
        if not workers_started:
            video_cap.release()
            await websocket.send_json({"error": "Failed to start CCTV processing workers"})
            return
        
        print(f"🚀 CCTV workers started via SessionManager for session {cctv_session_id}")
        
        # Process fusion results via SessionManager - CONSOLIDATED
        last_stats_time = time.time()
        
        while True:
            try:
                # Get fused result from SessionManager fusion queue
                fused_result = session_manager.fusion_results_queue.get(timeout=0.5)
            except queue.Empty:
                # Print stats if no results for a while
                if time.time() - last_stats_time > 30.0:  # Every 30 seconds
                    stats = session_manager.get_stats()
                    pipeline_start = stats.get("pipeline_start_time")
                    if pipeline_start:
                        elapsed = time.time() - pipeline_start
                        if elapsed > 30:  # Only after 30 seconds
                            fps_processed = stats["frames_processed"] / elapsed if elapsed > 0 else 0
                            print(f"\n📊 CCTV PIPELINE (Runtime: {elapsed:.1f}s)")
                            print(f"🎬 Video: {fps_processed:.1f} FPS | 🚨 Anomalies: {stats['tier1_anomalies_detected']}")
                    last_stats_time = time.time()
                continue
            
            # Process the fused result (same logic as live stream)
            frame_id = fused_result.get("frame_id", "unknown")
            timestamp = fused_result.get("timestamp", time.time())
            fusion_status = fused_result.get("fusion_status", "video-only")  # Usually video-only for CCTV
            frame = fused_result.get("frame")
            audio_chunk_path = fused_result.get("audio_chunk_path")  # Usually None for CCTV
            
            # Get detection results
            tier1_result = run_tier1_continuous(frame, audio_chunk_path)
            
            # SAFETY CHECK: Handle None result from tier1 (CCTV)
            if tier1_result is None:
                print("⚠️ CCTV Tier1 returned None, using fallback")
                tier1_result = {
                    "status": "Normal", 
                    "details": "Monitoring...",
                    "fusion_status": fusion_status
                }
            
            status = tier1_result.get("status", "Normal")
            details = tier1_result.get("details", "Monitoring...")
            
            if status == "Suspected Anomaly":
                # CONSOLIDATED: Use SessionManager for anomaly cooldown tracking (CCTV)
                stats = session_manager.get_stats()
                last_anomaly_time = stats.get("last_anomaly_time", 0)
                anomaly_cooldown_period = 1.0  # 1 second cooldown
                
                time_since_last = timestamp - last_anomaly_time
                
                if time_since_last < anomaly_cooldown_period:
                    print(f"🔄 Continuing incident (cooldown: {time_since_last:.1f}s)")
                    tier1_result.update({
                        "status": "Normal",
                        "details": "Monitoring...",
                        "incident_continuation": True
                    })
                else:
                    # NEW anomaly incident (CCTV)
                    session_manager.update_stats({"last_anomaly_time": timestamp})
                    session_manager.increment_stat("tier1_anomalies_detected")
                    stats = session_manager.get_stats()
                    print(f"\n🚨 CCTV ANOMALY #{stats['tier1_anomalies_detected']}")
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
                    # Add to user's CCTV anomalies
                    add_user_anomaly(current_username, 'cctv', anomaly_event)
                    current_anomaly_event = anomaly_event
                    
                    # TRIGGER TIER 2 ANALYSIS
                    session_manager.increment_stat("tier2_analyses_triggered")
                    stats = session_manager.get_stats() 
                    print(f"🔬 TRIGGERING TIER 2 ANALYSIS #{stats['tier2_analyses_triggered']}...")
                    
                    try:
                        tier2_result = run_tier2_continuous(frame.copy(), audio_chunk_path, tier1_result.copy())
                        session_manager.increment_stat("tier2_analyses_completed")
                        
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
                        session_manager.increment_stat("tier2_analyses_failed")
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
        # CONSOLIDATED CLEANUP - SessionManager handles everything
        print(f"🧹 CONSOLIDATED cleanup for CCTV session: {cctv_session_id}")
        session_manager.cleanup_session(cctv_session_id)
        print("✅ CCTV session cleanup complete")
        print("🔄 Stop signal reset for next session")
        
        print(f"🎥 CCTV session ended: {ip}:{port}")

# REMOVED: video_capture_worker_uploaded - SessionManager.start_session_workers() handles this

# REMOVED: video_capture_worker_cctv - SessionManager.start_session_workers() handles this
# REMOVED: All remaining CCTV worker function code - SessionManager handles this
# This removes another ~50 lines of redundant worker code
