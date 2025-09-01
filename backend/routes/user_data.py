"""
User Data Management Routes
Handles per-user anomaly data, frames, audio transcriptions, and Tier 2 analysis
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional, List
import base64
import os
from bson import ObjectId

# Import the database connection from main app
import sys
sys.path.append('..')

router = APIRouter(prefix="/api/user", tags=["User Data"])

# MongoDB Collections Schema:
# users: {username, password, email, full_name, role, created_at, status}
# user_anomalies: {user_id, username, anomaly_data, frames, audio_transcriptions, tier2_reasoning}
# user_sessions: {user_id, username, session_id, login_time, last_activity}

@router.get("/dashboard/{username}")
async def get_user_dashboard(username: str):
    """Get user dashboard with recent anomalies and statistics"""
    from app import database, user_anomaly_data, get_user_data
    
    if database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get user info
        user = await database.users.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get in-memory user data (current session anomalies)
        user_data = get_user_data(username)
        current_session_anomalies = []
        current_session_anomalies.extend(user_data['live'])
        current_session_anomalies.extend(user_data['upload'])
        current_session_anomalies.extend(user_data['cctv'])
        
        # Get recent persisted anomalies (last 24 hours)
        recent_time = datetime.now() - timedelta(hours=24)
        recent_persisted_anomalies = await database.anomalies.find({
            "username": username,
            "session_time": {"$gte": recent_time.isoformat()}
        }).sort("session_time", -1).limit(10).to_list(10)
        
        # Get total statistics (include current session)
        total_persisted_anomalies = await database.anomalies.count_documents({"username": username})
        total_current_anomalies = len(current_session_anomalies)
        total_anomalies = total_persisted_anomalies + total_current_anomalies
        
        total_sessions = await database.user_sessions.count_documents({"username": username})
        if user_data['sessions']:  # Add current session if active
            total_sessions += len(user_data['sessions'])
        
        # Format current session anomalies for dashboard
        dashboard_anomalies = []
        for anomaly in current_session_anomalies[-5:]:  # Latest 5 from current session
            dashboard_anomalies.append({
                "id": f"current_{anomaly.get('frame_id', 'unknown')}",
                "timestamp": anomaly.get("timestamp", 0),
                "details": anomaly.get("details", "Current session anomaly"),
                "fusion_status": anomaly.get("fusion_status", "active"),
                "session_time": anomaly.get("session_time", datetime.now().isoformat()),
                "tier2_reasoning": anomaly.get("tier2_analysis", {}).get("reasoning_summary", "Real-time detection"),
                "source": "current_session"
            })
        
        # Add persisted anomalies
        for anomaly in recent_persisted_anomalies[:5]:  # Latest 5 from database
            dashboard_anomalies.append({
                "id": str(anomaly["_id"]),
                "timestamp": anomaly.get("timestamp", 0),
                "details": anomaly.get("details", ""),
                "fusion_status": anomaly.get("fusion_status", ""),
                "session_time": anomaly.get("session_time", ""),
                "tier2_reasoning": anomaly.get("tier2_analysis", {}).get("reasoning_summary", "Pending analysis..."),
                "source": "database"
            })
        
        return {
            "user": {
                "username": user["username"],
                "email": user.get("email", ""),
                "full_name": user.get("full_name", ""),
                "role": user.get("role", "operator")
            },
            "statistics": {
                "total_anomalies": total_anomalies,
                "recent_anomalies": len(recent_persisted_anomalies) + len(current_session_anomalies[-5:]),
                "total_sessions": total_sessions
            },
            "recent_anomalies": dashboard_anomalies
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

@router.get("/anomalies/{username}")
async def get_user_anomalies(
    username: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_current: bool = Query(True, description="Include current session anomalies")
):
    """Get paginated list of user's anomalies with filtering"""
    from app import database, get_user_data
    
    if database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get current session anomalies if requested
        current_session_anomalies = []
        if include_current:
            user_data = get_user_data(username)
            current_session_anomalies.extend(user_data['live'])
            current_session_anomalies.extend(user_data['upload'])
            current_session_anomalies.extend(user_data['cctv'])
        
        # Build filter query for database
        query = {"username": username}
        
        if start_date or end_date:
            time_filter = {}
            if start_date:
                time_filter["$gte"] = start_date
            if end_date:
                time_filter["$lte"] = end_date
            query["session_time"] = time_filter
        
        # Get total count from database
        total_persisted = await database.anomalies.count_documents(query)
        total_current = len(current_session_anomalies)
        total = total_persisted + total_current
        
        # Calculate pagination for combined data
        skip = (page - 1) * limit
        
        # Get database anomalies
        db_anomalies = await database.anomalies.find(query)\
            .sort("session_time", -1)\
            .skip(max(0, skip - total_current))\
            .limit(limit)\
            .to_list(limit)
        
        # Combine current session and database anomalies
        result_anomalies = []
        
        # Add current session anomalies first (most recent)
        current_start = max(0, skip)
        current_end = min(len(current_session_anomalies), skip + limit)
        if current_start < len(current_session_anomalies):
            for i, anomaly in enumerate(current_session_anomalies[current_start:current_end]):
                result_anomalies.append({
                    "id": f"current_{anomaly.get('frame_id', i)}",
                    "frame_id": anomaly.get("frame_id", i),
                    "timestamp": anomaly.get("timestamp", 0),
                    "session_id": f"current_{username}",
                    "details": anomaly.get("details", "Current session anomaly"),
                    "fusion_status": anomaly.get("fusion_status", "active"),
                    "session_time": anomaly.get("session_time", datetime.now().isoformat()),
                    "duration": anomaly.get("duration", 0),
                    "frame_count": anomaly.get("frame_count", 1),
                    "tier1_confidence": anomaly.get("tier1_result", {}).get("confidence", 0),
                    "tier2_status": "real_time",
                    "tier2_reasoning": anomaly.get("tier2_analysis", {}).get("reasoning_summary", "Real-time detection"),
                    "source": "current_session"
                })
        
        # Add database anomalies
        remaining_limit = limit - len(result_anomalies)
        for anomaly in db_anomalies[:remaining_limit]:
            result_anomalies.append({
                "id": str(anomaly["_id"]),
                "frame_id": anomaly.get("frame_id", 0),
                "timestamp": anomaly.get("timestamp", 0),
                "session_id": anomaly.get("session_id", ""),
                "details": anomaly.get("details", ""),
                "fusion_status": anomaly.get("fusion_status", ""),
                "session_time": anomaly.get("session_time", ""),
                "duration": anomaly.get("duration", 0),
                "frame_count": anomaly.get("frame_count", 1),
                "tier1_confidence": anomaly.get("tier1_result", {}).get("confidence", 0),
                "tier2_status": "completed" if anomaly.get("tier2_analysis") else "pending",
                "tier2_reasoning": anomaly.get("tier2_analysis", {}).get("reasoning_summary", "Pending analysis..."),
                "source": "database"
            })
        
        return {
            "anomalies": result_anomalies,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
                "current_session_count": total_current,
                "database_count": total_persisted
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomalies fetch error: {str(e)}")

@router.get("/current_session/{username}")
async def get_current_session_anomalies(username: str):
    """Get all current session anomalies for a user"""
    from app import get_user_data
    
    try:
        user_data = get_user_data(username)
        
        # Combine all current session anomalies
        current_anomalies = []
        
        # Live feed anomalies
        for anomaly in user_data['live']:
            anomaly_copy = anomaly.copy()
            anomaly_copy['detection_type'] = 'live'
            current_anomalies.append(anomaly_copy)
        
        # Upload anomalies
        for anomaly in user_data['upload']:
            anomaly_copy = anomaly.copy()
            anomaly_copy['detection_type'] = 'upload'
            current_anomalies.append(anomaly_copy)
        
        # CCTV anomalies
        for anomaly in user_data['cctv']:
            anomaly_copy = anomaly.copy()
            anomaly_copy['detection_type'] = 'cctv'
            current_anomalies.append(anomaly_copy)
        
        # Sort by timestamp (most recent first)
        current_anomalies.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        return {
            "username": username,
            "session_anomalies": current_anomalies,
            "total_count": len(current_anomalies),
            "breakdown": {
                "live": len(user_data['live']),
                "upload": len(user_data['upload']),
                "cctv": len(user_data['cctv'])
            },
            "active_sessions": user_data['sessions']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Current session fetch error: {str(e)}")

@router.post("/clear_session/{username}")
async def clear_user_session_data(username: str, data_type: str = Query("all", regex="^(all|live|upload|cctv)$")):
    """Clear current session data for a user"""
    from app import user_anomaly_data, get_user_data
    
    try:
        user_data = get_user_data(username)
        
        cleared_count = 0
        if data_type == "all":
            cleared_count += len(user_data['live'])
            cleared_count += len(user_data['upload'])
            cleared_count += len(user_data['cctv'])
            user_data['live'].clear()
            user_data['upload'].clear()
            user_data['cctv'].clear()
            user_data['sessions'].clear()
        elif data_type == "live":
            cleared_count = len(user_data['live'])
            user_data['live'].clear()
        elif data_type == "upload":
            cleared_count = len(user_data['upload'])
            user_data['upload'].clear()
        elif data_type == "cctv":
            cleared_count = len(user_data['cctv'])
            user_data['cctv'].clear()
        
        return {
            "success": True,
            "message": f"Cleared {cleared_count} {data_type} anomalies for user {username}",
            "cleared_count": cleared_count,
            "data_type": data_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear session error: {str(e)}")

@router.post("/save_session/{username}")
async def save_current_session_to_database(username: str):
    """Save current session anomalies to database for persistence"""
    from app import database, get_user_data
    
    if database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        user_data = get_user_data(username)
        
        # Collect all current session anomalies
        all_anomalies = []
        all_anomalies.extend(user_data['live'])
        all_anomalies.extend(user_data['upload'])
        all_anomalies.extend(user_data['cctv'])
        
        if not all_anomalies:
            return {
                "success": True,
                "message": "No current session anomalies to save",
                "saved_count": 0
            }
        
        # Prepare documents for insertion
        documents = []
        for anomaly in all_anomalies:
            doc = anomaly.copy()
            doc["username"] = username
            doc["saved_at"] = datetime.now().isoformat()
            # Remove any existing _id to prevent conflicts
            if "_id" in doc:
                del doc["_id"]
            documents.append(doc)
        
        # Insert into database
        result = await database.anomalies.insert_many(documents)
        
        # Clear current session after successful save
        user_data['live'].clear()
        user_data['upload'].clear()
        user_data['cctv'].clear()
        
        return {
            "success": True,
            "message": f"Saved {len(result.inserted_ids)} anomalies to database",
            "saved_count": len(result.inserted_ids),
            "inserted_ids": [str(id) for id in result.inserted_ids]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save session error: {str(e)}")

@router.get("/anomaly/{anomaly_id}/frames")
async def get_anomaly_frames(anomaly_id: str):
    """Get frames associated with a specific anomaly"""
    from app import database
    
    if database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get anomaly record
        anomaly = await database.anomalies.find_one({"_id": ObjectId(anomaly_id)})
        if not anomaly:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        frames_data = []
        
        # Get main frame
        if anomaly.get("frame_file") and os.path.exists(anomaly["frame_file"]):
            with open(anomaly["frame_file"], "rb") as f:
                frame_data = base64.b64encode(f.read()).decode()
                frames_data.append({
                    "type": "main_frame",
                    "timestamp": anomaly.get("timestamp", 0),
                    "data": f"data:image/jpeg;base64,{frame_data}",
                    "filename": os.path.basename(anomaly["frame_file"])
                })
        
        # Get additional frames if stored
        if anomaly.get("additional_frames"):
            for frame_info in anomaly["additional_frames"]:
                if os.path.exists(frame_info["path"]):
                    with open(frame_info["path"], "rb") as f:
                        frame_data = base64.b64encode(f.read()).decode()
                        frames_data.append({
                            "type": "additional_frame",
                            "timestamp": frame_info.get("timestamp", 0),
                            "data": f"data:image/jpeg;base64,{frame_data}",
                            "filename": os.path.basename(frame_info["path"])
                        })
        
        return {
            "anomaly_id": anomaly_id,
            "frames": frames_data,
            "total_frames": len(frames_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Frames fetch error: {str(e)}")

@router.get("/anomaly/{anomaly_id}/audio")
async def get_anomaly_audio_transcription(anomaly_id: str):
    """Get audio transcription for a specific anomaly"""
    from app import database
    
    if database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get anomaly record
        anomaly = await database.anomalies.find_one({"_id": ObjectId(anomaly_id)})
        if not anomaly:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        # Extract audio transcription from tier1_result
        tier1_result = anomaly.get("tier1_result", {})
        audio_data = {
            "anomaly_id": anomaly_id,
            "timestamp": anomaly.get("timestamp", 0),
            "audio_transcription": tier1_result.get("audio_transcription", "No audio transcription available"),
            "audio_confidence": tier1_result.get("audio_confidence", 0),
            "audio_detected": tier1_result.get("audio_detected", False),
            "language": tier1_result.get("audio_language", "unknown")
        }
        
        return audio_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio transcription fetch error: {str(e)}")

@router.get("/anomaly/{anomaly_id}/tier2")
async def get_anomaly_tier2_analysis(anomaly_id: str):
    """Get detailed Tier 2 analysis for a specific anomaly"""
    from app import database
    
    if database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get anomaly record
        anomaly = await database.anomalies.find_one({"_id": ObjectId(anomaly_id)})
        if not anomaly:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        tier2_analysis = anomaly.get("tier2_analysis", {})
        
        if not tier2_analysis:
            return {
                "anomaly_id": anomaly_id,
                "status": "pending",
                "message": "Tier 2 analysis not yet completed"
            }
        
        return {
            "anomaly_id": anomaly_id,
            "status": tier2_analysis.get("status", "completed"),
            "reasoning_summary": tier2_analysis.get("reasoning_summary", ""),
            "threat_level": tier2_analysis.get("threat_level", "unknown"),
            "confidence_score": tier2_analysis.get("confidence_score", 0),
            "detected_behaviors": tier2_analysis.get("detected_behaviors", []),
            "recommended_actions": tier2_analysis.get("recommended_actions", []),
            "scene_analysis": tier2_analysis.get("scene_analysis", {}),
            "pose_analysis": tier2_analysis.get("pose_analysis", {}),
            "audio_analysis": tier2_analysis.get("audio_analysis", {}),
            "full_reasoning": tier2_analysis.get("full_reasoning", "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tier 2 analysis fetch error: {str(e)}")

@router.get("/sessions/{username}")
async def get_user_sessions(
    username: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Get user's monitoring sessions"""
    from app import database
    
    if database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get total count
        total = await database.user_sessions.count_documents({"username": username})
        
        # Get paginated results
        skip = (page - 1) * limit
        sessions = await database.user_sessions.find({"username": username})\
            .sort("login_time", -1)\
            .skip(skip)\
            .limit(limit)\
            .to_list(limit)
        
        # Process sessions
        result_sessions = []
        for session in sessions:
            # Count anomalies in this session
            session_anomalies = await database.anomalies.count_documents({
                "session_id": session.get("session_id", "")
            })
            
            result_sessions.append({
                "session_id": session.get("session_id", ""),
                "login_time": session.get("login_time", ""),
                "last_activity": session.get("last_activity", session.get("login_time", "")),
                "role": session.get("role", "operator"),
                "anomalies_detected": session_anomalies
            })
        
        return {
            "sessions": result_sessions,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sessions fetch error: {str(e)}")

@router.delete("/anomaly/{anomaly_id}")
async def delete_user_anomaly(anomaly_id: str):
    """Delete a specific anomaly record (admin/user owner only)"""
    from app import database
    
    if database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get anomaly to check ownership and cleanup files
        anomaly = await database.anomalies.find_one({"_id": ObjectId(anomaly_id)})
        if not anomaly:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        # Delete associated files
        files_deleted = 0
        if anomaly.get("frame_file") and os.path.exists(anomaly["frame_file"]):
            os.remove(anomaly["frame_file"])
            files_deleted += 1
        
        if anomaly.get("video_file") and os.path.exists(anomaly["video_file"]):
            os.remove(anomaly["video_file"])
            files_deleted += 1
        
        # Delete from database
        result = await database.anomalies.delete_one({"_id": ObjectId(anomaly_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        return {
            "success": True,
            "message": "Anomaly deleted successfully",
            "files_deleted": files_deleted
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")
