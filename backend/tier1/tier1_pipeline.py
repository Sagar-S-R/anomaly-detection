from utils.audio_processing import chunk_and_transcribe_tiny, extract_audio
from utils.pose_processing import process_pose_frame, process_pose
from utils.scene_processing import process_scene_frame, process_scene_tier1
from utils.fusion_logic import tier1_fusion
import cv2
import numpy as np

def run_tier1_continuous(frame, audio_chunk_path):
    try:
        pose_anomaly = process_pose_frame(frame)  # 0 or 1 (anomaly or not)
        pose_summary = f"Pose anomaly detected: {bool(pose_anomaly)}"
        print(f"Pose processing completed: {pose_summary}")

        # Handle audio processing with fallback
        try:
            if audio_chunk_path:
                print(f"Processing audio chunk: {audio_chunk_path}")
                transcripts = chunk_and_transcribe_tiny(audio_chunk_path)
                audio_summary = "Audio transcripts: " + " | ".join(transcripts) if transcripts else "No audio."
            else:
                audio_summary = "No audio available."
            print(f"Audio processing completed: {audio_summary}")
        except Exception as e:
            print(f"Audio processing error in tier1: {e}")
            audio_summary = "Audio processing failed."

        anomaly_prob = process_scene_frame(frame)
        scene_summary = f"Scene anomaly probability: {anomaly_prob:.2f}"
        print(f"Scene processing completed: {scene_summary}")

        status, details = tier1_fusion(pose_summary, audio_summary, scene_summary)
        print(f"Fusion completed: {status}")
        return {
            "status": status,
            "details": details
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