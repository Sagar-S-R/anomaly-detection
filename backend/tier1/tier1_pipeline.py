from utils.audio_processing import chunk_and_transcribe_tiny, extract_audio
from utils.pose_processing import process_pose_frame, process_pose
from utils.scene_processing import process_scene_frame, process_scene_tier1
from utils.fusion_logic import tier1_fusion
import cv2
import numpy as np
import json
import time
import traceback
from collections import deque

# Global variables for smoothing/easing - simplified approach
_anomaly_history = deque(maxlen=3)  # Reduced from 5 to 3 for faster response
_startup_frame_count = 0  # Track startup frames to prevent initial false positives

def apply_temporal_smoothing(current_status, current_scene_prob, current_pose_anomaly, fusion_details):
    """NO SMOOTHING - Immediate anomaly detection for demo"""
    global _anomaly_history, _startup_frame_count
    
    _startup_frame_count += 1
    
    # CRITICAL: Bypass smoothing for audio emergencies
    if "AUDIO EMERGENCY" in fusion_details:
        print(f"🚨 AUDIO EMERGENCY - BYPASSING ALL SMOOTHING")
        return "Suspected Anomaly"
    
    # NO STARTUP PROTECTION - Immediate detection!
    print(f"� NO SMOOTHING MODE: frame {_startup_frame_count}, status={current_status}")
    
    # Return the status immediately without any smoothing
    if current_status == "Suspected Anomaly":
        print(f"🚨 IMMEDIATE ANOMALY: scene={current_scene_prob:.3f}, pose={current_pose_anomaly}")
        return "Suspected Anomaly"
    
    return "Normal"
    
    # Add current frame to history
    _anomaly_history.append({
        "status": current_status == "Suspected Anomaly",
        "scene_prob": current_scene_prob,
        "pose": current_pose_anomaly,
        "timestamp": time.time(),
        "confidence": 0.9 if "High-confidence" in fusion_details else 0.7 if "Multi-modal" in fusion_details else 0.5
    })
    
    # Analyze recent history
    anomaly_count = sum(1 for h in _anomaly_history if h["status"])
    avg_confidence = np.mean([h["confidence"] for h in _anomaly_history if h["status"]]) if anomaly_count > 0 else 0
    
    # MORE SENSITIVE immediate triggers 
    very_high_confidence = (
        ("SMART Fall Detection" in fusion_details and current_scene_prob > 0.15) or  # Reduced from 0.3
        ("High-confidence pose" in fusion_details and current_scene_prob > 0.1) or   # Reduced from 0.2  
        ("High-confidence scene" in fusion_details and current_scene_prob > 0.3) or  # Reduced from 0.5
        ("Rapid arm movement" in fusion_details) or  # Any rapid arm movement
        ("Head movement" in fusion_details) or       # Any head movement
        ("Torso change" in fusion_details)           # Any torso change
    )
    
    if very_high_confidence:
        print(f"🚨 High-confidence immediate trigger: {fusion_details[:80]}...")
        return "Suspected Anomaly"
    
    # MORE LENIENT smoothing requirements
    if avg_confidence > 0.7:  # High average confidence - reduced from 0.8
        required_agreement = 1  # Need only 1 frame! - reduced from 2
    elif avg_confidence > 0.5:  # Medium confidence - reduced from 0.6
        required_agreement = 2  # Need 2 out of 3 frames - reduced from 3
    else:  # Low confidence
        required_agreement = 2  # Need 2 out of 3 frames - reduced from 3
        # Simplified validation
        if anomaly_count >= required_agreement:
            print(f"🟡 Low confidence but sufficient agreement: {anomaly_count}/{len(_anomaly_history)}")
    
    # Decision based on adaptive requirements
    if anomaly_count >= required_agreement:
        print(f"🚨 SENSITIVE anomaly confirmed: {anomaly_count}/{len(_anomaly_history)} frames, avg_conf={avg_confidence:.2f}, req={required_agreement}")
        return "Suspected Anomaly"
    else:
        if anomaly_count > 0:  # Some anomalies detected but not enough
            print(f"🟡 Partial anomaly: {anomaly_count}/{len(_anomaly_history)} frames (need {required_agreement}), avg_conf={avg_confidence:.2f}")
        return "Normal"

def run_tier1_continuous(frame, audio_chunk_path):
    """Enhanced Tier 1 processing with FIXED audio handling"""
    try:
        # Initialize components with error handling
        pose_anomaly = 0
        pose_summary = "Pose processing skipped"
        audio_transcripts = []
        audio_summary = None  # KEY CHANGE: Start with None to distinguish states
        anomaly_prob = 0.0
        scene_summary = "Scene processing skipped"
        
        # Pose processing with error handling
        try:
            pose_anomaly = process_pose_frame(frame)
            pose_summary = f"Pose anomaly detected: {bool(pose_anomaly)}"
        except Exception as e:
            print(f"⚠ Pose processing error: {e}")
            pose_anomaly = 0
            pose_summary = f"Pose processing failed: {str(e)}"

        # FIXED Audio processing with proper state tracking
        audio_processing_attempted = False
        try:
            # Check if audio is available
            if audio_chunk_path and isinstance(audio_chunk_path, str) and len(audio_chunk_path.strip()) > 0:
                print(f"🎤 Processing audio from: {audio_chunk_path}")
                audio_processing_attempted = True
                
                transcripts = chunk_and_transcribe_tiny(audio_chunk_path)
                audio_transcripts = transcripts if transcripts else []
                
                if transcripts and len(transcripts) > 0:
                    # Audio successfully processed with content
                    audio_summary = " | ".join(transcripts)
                    print(f"🎤 Audio transcripts found: {len(transcripts)} segments")
                    
                    # Debug: Print emergency audio immediately
                    for transcript in transcripts:
                        if any(word in transcript.lower() for word in ["help", "emergency", "call", "911", "fire"]):
                            print(f"🚨 EMERGENCY AUDIO DETECTED: '{transcript}'")
                else:
                    # Audio processed but no transcripts (silence or unclear audio)
                    audio_summary = "no transcripts"  # This will be recognized by fusion logic
                    print(f"🎤 Audio processed but no clear transcripts")
            else:
                # No audio source provided
                print(f"🎤 No audio source available (audio_chunk_path={audio_chunk_path})")
                audio_summary = None  # Truly no audio available
                
        except Exception as e:
            print(f"⚠ Audio processing error: {e}")
            if audio_processing_attempted:
                # Audio was available but failed to process
                audio_summary = "audio processing failed"
                print(f"🎤 Audio processing failed: {str(e)}")
            else:
                # No audio was available to begin with
                audio_summary = None
                print(f"🎤 No audio available due to error: {str(e)}")

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
            print(f"⚠ Scene processing error: {e}")
            anomaly_prob = 0.0
            scene_summary = f"Scene processing failed: {str(e)}"

        # FIXED Tier 1 fusion with proper audio state handling
        try:
            print(f"🔧 Fusion inputs: pose='{pose_summary}', audio='{audio_summary}', scene='{scene_summary}'")
            
            initial_status, fusion_details = tier1_fusion(pose_summary, audio_summary, scene_summary)
            
            if initial_status == "Suspected Anomaly":
                print(f"🚨 ANOMALY DETECTED: {fusion_details}")
            elif anomaly_prob > 0.5 or pose_anomaly > 0:
                print(f"🟡 Notable activity: {fusion_details}")
                
        except Exception as e:
            print(f"⚠ Fusion logic error: {e}")
            print(f"📋 Fusion error traceback: {traceback.format_exc()}")
            initial_status = "Error"
            fusion_details = f"Fusion failed: {str(e)}"
        
        # Apply smoothing WITH fusion details for audio emergency bypass
        smoothed_status = apply_temporal_smoothing(initial_status, anomaly_prob, pose_anomaly, fusion_details)
        
        # Add smoothing info if status changed
        if smoothed_status != initial_status:
            fusion_details += f" [Smoothed from {initial_status} to {smoothed_status}]"
        
        # ENHANCED result with better audio state tracking
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
                    "available": audio_summary is not None,  # True availability check
                    "transcripts": audio_transcripts,
                    "processing_attempted": audio_processing_attempted,
                    "summary": audio_summary if audio_summary else "No audio available",
                    "transcript_text": " | ".join(audio_transcripts) if audio_transcripts else "",
                    "audio_source_provided": bool(audio_chunk_path)
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
        
        # CONDITIONAL logging - only log anomalies or significant events
        if smoothed_status == "Suspected Anomaly" or anomaly_prob > 0.3 or pose_anomaly > 0:
            print(f"🔍 Tier1 Result: {json.dumps(result, indent=2)}")
        else:
            # Minimal logging for normal frames
            print(f"✅ Tier1 Normal: scene={anomaly_prob:.2f}, pose={pose_anomaly}, audio={'Yes' if audio_summary else 'No'}")
        
        return result
        
    except Exception as e:
        print(f"❌ Critical error in run_tier1_continuous: {e}")
        print(f"📋 Critical error traceback: {traceback.format_exc()}")
        
        # Return error result
        return {
            "status": "Error",
            "details": f"Critical processing error: {str(e)}",
            "tier1_components": {
                "pose_analysis": {"anomaly_detected": False, "summary": "Error", "raw_score": 0},
                "audio_analysis": {
                    "available": False, 
                    "transcripts": [], 
                    "processing_attempted": False,
                    "summary": "Error", 
                    "transcript_text": "",
                    "audio_source_provided": bool(audio_chunk_path) if 'audio_chunk_path' in locals() else False
                },
                "scene_analysis": {"anomaly_probability": 0.0, "summary": "Error"},
                "fusion_logic": {
                    "initial_status": "Error", 
                    "final_status": "Error", 
                    "smoothing_applied": False, 
                    "details": f"Critical error: {str(e)}"
                }
            }
        }

def run_tier1(video_path):
    """Keep original batch function - ENHANCED with better audio handling"""
    try:
        # Audio processing with better error handling
        audio_transcripts = []
        try:
            audio_path = extract_audio(video_path)
            if audio_path:
                transcripts = chunk_and_transcribe_tiny(audio_path)
                audio_transcripts = transcripts if transcripts else []
                
                if audio_transcripts:
                    audio_summary = " | ".join(audio_transcripts)
                else:
                    audio_summary = "no transcripts"  # Processed but silent
            else:
                audio_summary = None  # No audio available
        except Exception as e:
            print(f"⚠ Batch audio processing error: {e}")
            audio_summary = "audio processing failed"
        
        # Pose processing
        try:
            num_anomalies, total_frames, _, _ = process_pose(video_path)
            pose_summary = f"Pose anomalies (fall/crawl) detected in {num_anomalies} out of {total_frames} frames."
        except Exception as e:
            print(f"⚠ Batch pose processing error: {e}")
            pose_summary = f"Pose processing failed: {str(e)}"
        
        # Scene processing
        try:
            max_anomaly_prob = process_scene_tier1(video_path)
            scene_summary = f"Highest scene anomaly probability: {max_anomaly_prob:.2f}"
        except Exception as e:
            print(f"⚠ Batch scene processing error: {e}")
            scene_summary = f"Scene processing failed: {str(e)}"
        
        # Fusion
        status, details = tier1_fusion(pose_summary, audio_summary, scene_summary)
        
        return {
            "status": status, 
            "details": details,
            "batch_info": {
                "audio_transcripts": audio_transcripts,
                "audio_available": audio_summary is not None
            }
        }
        
    except Exception as e:
        print(f"❌ Critical error in run_tier1: {e}")
        return {
            "status": "Error",
            "details": f"Batch processing error: {str(e)}",
            "batch_info": {"audio_transcripts": [], "audio_available": False}
        }