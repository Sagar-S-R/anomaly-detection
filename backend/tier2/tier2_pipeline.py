from utils.audio_processing import extract_audio, transcribe_large
from utils.scene_processing import process_scene_tier2
from utils.pose_processing import process_pose
from utils.fusion_logic import tier2_fusion

def run_tier2(video_path, tier1_result):
    audio_path = extract_audio(video_path)
    full_transcript = transcribe_large(audio_path)

    captions, visual_anomaly_max = process_scene_tier2(video_path)

    num_anomalies, total_frames, timestamps, fps = process_pose(video_path)

    # Compute frame_id from first anomaly timestamp
    if timestamps:
        first_ts = timestamps[0]  # seconds
        frame_num = int(first_ts * fps) if fps > 0 else 0
    else:
        frame_num = 0
    frame_id = f"A{frame_num}F"

    result = tier2_fusion(full_transcript, captions, visual_anomaly_max, tier1_result["details"])
    result["frame_id"] = frame_id
    result["timestamps"] = timestamps  # For log

    return result