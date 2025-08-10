from utils.audio_processing import chunk_and_transcribe_tiny, extract_audio
from utils.pose_processing import process_pose_frame, process_pose
from utils.scene_processing import process_scene_frame, process_scene_tier1
from utils.fusion_logic import tier1_fusion
import cv2
import numpy as np
from collections import deque

# Global variables for smoothing/easing
_anomaly_history = deque(maxlen=5)  # Keep last 5 results for smoothing
_scene_prob_history = deque(maxlen=3)  # Scene probability smoothing
_pose_history = deque(maxlen=3)  # Pose anomaly smoothing

def smooth_anomaly_detection(current_status, current_scene_prob, current_pose_anomaly):
    """Minimal smoothing - preserve original detection logic"""
    # Just pass through the original decision - no complex smoothing
    return current_status

def run_tier1_continuous(frame, audio_chunk_path):
    try:
        # Pose processing
        pose_anomaly = process_pose_frame(frame)
        pose_summary = f"Pose anomaly detected: {bool(pose_anomaly)}"

        # Audio processing
        audio_transcripts = []
        try:
            if audio_chunk_path:
                transcripts = chunk_and_transcribe_tiny(audio_chunk_path)
                audio_transcripts = transcripts if transcripts else []
                audio_summary = "Audio transcripts: " + " | ".join(transcripts) if transcripts else "No audio."
            else:
                audio_summary = "No audio available."
        except Exception as e:
            audio_summary = "Audio processing failed."

        # Scene processing
        anomaly_prob = process_scene_frame(frame)
        scene_summary = f"Scene anomaly probability: {anomaly_prob:.2f}"

        # Tier 1 fusion
        initial_status, fusion_details = tier1_fusion(pose_summary, audio_summary, scene_summary)
        
        # Apply smoothing
        smoothed_status = smooth_anomaly_detection(initial_status, anomaly_prob, pose_anomaly)
        
        # Add smoothing info if status changed
        if smoothed_status != initial_status:
            fusion_details += f" [Smoothed from {initial_status} to {smoothed_status}]"
        
        # Return enhanced JSON with component details
        # Construct enhanced response with detailed components
        return {
            "status": smoothed_status,
            "details": fusion_details,
            "tier1_components": {
                "pose_analysis": {
                    "anomaly_detected": bool(pose_anomaly),
                    "summary": pose_summary
                },
                "audio_analysis": {
                    "transcripts": audio_transcripts,
                    "available": bool(audio_chunk_path),
                    "summary": audio_summary,
                    "transcript_text": " | ".join(audio_transcripts) if audio_transcripts else ""
                },
                "scene_analysis": {
                    "anomaly_probability": anomaly_prob,
                    "summary": scene_summary
                },
                "fusion_logic": {
                    "initial_status": initial_status,
                    "final_status": smoothed_status,
                    "smoothing_applied": smoothed_status != initial_status
                }
            }
        }
        
    except Exception as e:
        print(f"Error in run_tier1_continuous: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise e

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