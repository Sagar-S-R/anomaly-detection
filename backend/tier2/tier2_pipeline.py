from utils.audio_processing import transcribe_large
from utils.scene_processing import process_scene_tier2_frame
from utils.fusion_logic import tier2_fusion
from utils.pose_processing import process_pose_frame

def run_tier2_continuous(frame, audio_chunk_path, tier1_result):
    try:
        print(f"Starting Tier 2 analysis...")
        
        # Audio processing
        try:
            full_transcript = transcribe_large(audio_chunk_path) if audio_chunk_path else ""
            print(f"Tier 2 audio transcript: {full_transcript}")
        except Exception as e:
            print(f"Tier 2 audio processing error: {e}")
            full_transcript = ""

        # Visual processing  
        try:
            captions, visual_anomaly_max = process_scene_tier2_frame(frame)
            print(f"Tier 2 visual analysis: captions={captions}, anomaly_max={visual_anomaly_max}")
        except Exception as e:
            print(f"Tier 2 visual processing error: {e}")
            captions = ["Image processing failed"]
            visual_anomaly_max = 0.3

        # Simulate timestamps for frame
        timestamps = [0.0]  # Placeholder for current frame

        # Fusion
        try:
            result = tier2_fusion(full_transcript, captions, visual_anomaly_max, tier1_result["details"])
            result["frame_id"] = "A0F"  # Placeholder for streaming
            result["timestamps"] = timestamps
            print(f"Tier 2 fusion completed successfully")
            return result
        except Exception as e:
            print(f"Tier 2 fusion error: {e}")
            # Return safe fallback
            return {
                "visual_score": 0.4,
                "audio_score": 0.4,
                "text_alignment_score": 0.4,
                "multimodal_agreement": 0.4,
                "reasoning_summary": f"Tier 2 analysis error: {str(e)}",
                "threat_severity_index": 0.4,
                "frame_id": "A0F",
                "timestamps": timestamps
            }
            
    except Exception as e:
        print(f"Critical error in run_tier2_continuous: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Return minimal safe response
        return {
            "visual_score": 0.3,
            "audio_score": 0.3,
            "text_alignment_score": 0.3,
            "multimodal_agreement": 0.3,
            "reasoning_summary": f"Critical Tier 2 error: {str(e)}",
            "threat_severity_index": 0.3,
            "frame_id": "ERR",
            "timestamps": [0.0]
        }