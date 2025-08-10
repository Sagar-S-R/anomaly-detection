from utils.audio_processing import chunk_and_transcribe_tiny
from utils.pose_processing import process_pose_frame
from utils.scene_processing import process_scene_frame
from utils.fusion_logic import tier1_fusion
import cv2
import numpy as np

def run_tier1_continuous(frame, audio_chunk_path):
    pose_anomaly = process_pose_frame(frame)  # 0 or 1 (anomaly or not)
    pose_summary = f"Pose anomaly detected: {bool(pose_anomaly)}"

    transcripts = chunk_and_transcribe_tiny(audio_chunk_path)
    audio_summary = "Audio transcripts: " + " | ".join(transcripts) if transcripts else "No audio."

    anomaly_prob = process_scene_frame(frame)
    scene_summary = f"Scene anomaly probability: {anomaly_prob:.2f}"

    status, details = tier1_fusion(pose_summary, audio_summary, scene_summary)
    return {
        "status": status,
        "details": details
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