from utils.audio_processing import chunk_and_transcribe_tiny, extract_audio
from utils.pose_processing import process_pose_frame, process_pose
from utils.scene_processing import process_scene_frame, process_scene_tier1
from utils.fusion_logic import tier1_fusion
import cv2
import numpy as np
import json
import time
from collections import deque

# Global variables for smoothing/easing - simplified approach
_anomaly_history = deque(maxlen=3)  # Reduced from 5 to 3 for faster response
_startup_frame_count = 0  # Track startup frames to prevent initial false positives

def smooth_anomaly_detection(current_status, current_scene_prob, current_pose_anomaly, fusion_details=""):
    """Enhanced smoothing with AUDIO EMERGENCY BYPASS and startup protection"""
    global _startup_frame_count
    _startup_frame_count += 1
    
    # CRITICAL: Bypass smoothing for audio emergencies
    if "AUDIO EMERGENCY" in fusion_details:
        print(f"🚨 AUDIO EMERGENCY - BYPASSING ALL SMOOTHING")
        return "Suspected Anomaly"
    
    # Ignore first 10 frames to prevent startup false positives (unless audio emergency)
    if _startup_frame_count <= 10 and "AUDIO EMERGENCY" not in fusion_details:
        return "Normal"
    
    _anomaly_history.append({
        "status": current_status == "Suspected Anomaly",
        "scene_prob": current_scene_prob,
        "pose": current_pose_anomaly,
        "timestamp": time.time()
    })
    
    # Count recent anomalies
    anomaly_count = sum(1 for h in _anomaly_history if h["status"])
    
    # Check for high-confidence signals that should bypass smoothing
    high_confidence_pose = current_pose_anomaly and current_scene_prob > 0.15
    very_high_scene = current_scene_prob > 0.4
    
    # Immediate trigger for high-confidence anomalies
    if high_confidence_pose or very_high_scene:
        print(f"🚨 High-confidence anomaly detected - bypassing smoothing")
        return "Suspected Anomaly"
    
    # Normal smoothing: require majority agreement
    if anomaly_count >= 2:  # 2 out of 3 frames
        return "Suspected Anomaly"
    else:
        return "Normal"

def run_tier1_continuous(frame, audio_chunk_path):
    """Enhanced Tier 1 processing with structured logging and error handling"""
    try:
        # Initialize components with error handling
        pose_anomaly = 0
        pose_summary = "Pose processing skipped"
        audio_transcripts = []
        audio_summary = "No audio available"
        anomaly_prob = 0.0
        scene_summary = "Scene processing skipped"
        
        # Pose processing with error handling
        try:
            pose_anomaly = process_pose_frame(frame)
            pose_summary = f"Pose anomaly detected: {bool(pose_anomaly)}"
        except Exception as e:
            print(f"⚠️ Pose processing error: {e}")
            pose_anomaly = 0
            pose_summary = f"Pose processing failed: {str(e)}"

        # Audio processing with error handling
        try:
            if audio_chunk_path:
                transcripts = chunk_and_transcribe_tiny(audio_chunk_path)
                audio_transcripts = transcripts if transcripts else []
                audio_summary = "Audio transcripts: " + " | ".join(transcripts) if transcripts else "No transcripts found"
                
                # Debug: Print what we found (only for emergencies)
                if transcripts:
                    for transcript in transcripts:
                        if any(word in transcript.lower() for word in ["help", "emergency", "call", "911"]):
                            print(f"🚨 EMERGENCY AUDIO DETECTED: '{transcript}'")
            else:
                audio_summary = "No audio chunk provided"
        except Exception as e:
            print(f"⚠️ Audio processing error: {e}")
            audio_summary = f"Audio processing failed: {str(e)}"

        # Scene processing with error handling
        try:
            # Convert frame to RGB for scene processing
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                rgb_frame = frame
            anomaly_prob = process_scene_frame(rgb_frame)
            scene_summary = f"Scene anomaly probability: {anomaly_prob:.3f}"
        except Exception as e:
            print(f"⚠️ Scene processing error: {e}")
            anomaly_prob = 0.0
            scene_summary = f"Scene processing failed: {str(e)}"

        # Tier 1 fusion with error handling
        try:
            # Only print fusion debug for emergencies or actual anomalies
            initial_status, fusion_details = tier1_fusion(pose_summary, audio_summary, scene_summary)
            
            if initial_status == "Suspected Anomaly":
                print(f"🚨 ANOMALY DETECTED: {fusion_details}")
        except Exception as e:
            print(f"⚠️ Fusion logic error: {e}")
            initial_status = "Error"
            fusion_details = f"Fusion failed: {str(e)}"
        
        # Apply smoothing WITH fusion details for audio emergency bypass
        smoothed_status = smooth_anomaly_detection(initial_status, anomaly_prob, pose_anomaly, fusion_details)
        
        # Add smoothing info if status changed
        if smoothed_status != initial_status:
            fusion_details += f" [Smoothed from {initial_status} to {smoothed_status}]"
        
        # Construct enhanced response with detailed components
        result = {
            "status": smoothed_status,
            "details": fusion_details,
            "tier1_components": {
                "pose_analysis": {
                    "anomaly_detected": bool(pose_anomaly),
                    "summary": pose_summary,
                    "raw_score": pose_anomaly
                },
                "audio_analysis": {
                    "transcripts": audio_transcripts,
                    "available": bool(audio_chunk_path),
                    "summary": audio_summary,
                    "transcript_text": " | ".join(audio_transcripts) if audio_transcripts else ""
                },
                "scene_analysis": {
                    "anomaly_probability": round(anomaly_prob, 3),
                    "summary": scene_summary
                },
                "fusion_logic": {
                    "initial_status": initial_status,
                    "final_status": smoothed_status,
                    "smoothing_applied": smoothed_status != initial_status,
                    "details": fusion_details
                }
            }
        }
        
        # Log structured output for debugging
        print(f"🔍 Tier1 Result: {json.dumps(result, indent=2)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Critical error in run_tier1_continuous: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # Return error result
        return {
            "status": "Error",
            "details": f"Critical processing error: {str(e)}",
            "tier1_components": {
                "pose_analysis": {"anomaly_detected": False, "summary": "Error", "raw_score": 0},
                "audio_analysis": {"transcripts": [], "available": False, "summary": "Error", "transcript_text": ""},
                "scene_analysis": {"anomaly_probability": 0.0, "summary": "Error"},
                "fusion_logic": {"initial_status": "Error", "final_status": "Error", "smoothing_applied": False, "details": f"Critical error: {str(e)}"}
            }
        }

def run_tier1(video_path):
    # Keep original batch function
    audio_path = extract_audio(video_path)
    transcripts = chunk_and_transcribe_tiny(audio_path)
    num_anomalies, total_frames, _, _ = process_pose(video_path)
    pose_summary = f"Pose anomalies (fall/crawl) detected in {num_anomalies} out of {total_frames} frames."
    audio_summary = "Audio transcripts: " + " | ".join(transcripts) if transcripts else "No audio."
    max_anomaly_prob = process_scene_tier1(video_path)
    scene_summary = f"Highest scene anomaly probability: {max_anomaly_prob:.2f}"
    status, details = tier1_fusion(pose_summary, audio_summary, scene_summary)
    return {"status": status, "details": details}