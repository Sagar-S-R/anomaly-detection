from utils.audio_processing import transcribe_large
from utils.scene_processing import process_scene_tier2_frame
from utils.fusion_logic import tier2_fusion
from utils.pose_processing import process_pose_frame

def run_tier2_continuous(frame, audio_chunk_path, tier1_result):
    try:
        # Extract audio transcript from Tier 1 result instead of re-processing
        full_transcript = ""
        try:
            # First try to get from tier1_components (structured data)
            if tier1_result.get("tier1_components"):
                audio_comp = tier1_result["tier1_components"].get("audio_analysis", {})
                full_transcript = audio_comp.get("transcript_text", "")
                
            # If no structured data, extract from details string
            if not full_transcript:
                tier1_details = tier1_result.get("details", "")
                if "Audio transcripts:" in tier1_details:
                    # Extract the audio part
                    audio_part = tier1_details.split("Audio transcripts:")[1]
                    if "|" in audio_part:
                        # Take everything between "Audio transcripts:" and next section
                        next_section = audio_part.find("Scene anomaly")
                        if next_section != -1:
                            audio_part = audio_part[:next_section]
                    full_transcript = audio_part.strip()
                
            # If still no transcript and we have audio chunk, try direct processing as fallback
            if not full_transcript and audio_chunk_path:
                full_transcript = transcribe_large(audio_chunk_path)
                
        except Exception as e:
            print(f"Tier 2 audio processing error: {e}")
            full_transcript = ""
            
        # Debug: Print what we found for audio transcript
        print(f"🎤 Tier 2 Audio Debug: transcript='{full_transcript}', chunk_available={bool(audio_chunk_path)}")

        # Visual processing with advanced scene analysis
        captions = ["Scene analysis failed"]
        visual_anomaly_max = 0.3
        try:
            captions, visual_anomaly_max = process_scene_tier2_frame(frame)
        except Exception as e:
            print(f"Tier 2 visual processing error: {e}")

        # Tier 2 fusion with AI reasoning
        timestamps = [0.0]
        try:
            fusion_result = tier2_fusion(full_transcript, captions, visual_anomaly_max, tier1_result["details"])
            fusion_result["frame_id"] = "A0F"
            fusion_result["timestamps"] = timestamps
            
            # Add component breakdown to result
            fusion_result["tier2_components"] = {
                "audio_analysis": {
                    "full_transcript": full_transcript,
                    "available": bool(audio_chunk_path),
                    "length": len(full_transcript) if full_transcript else 0
                },
                "visual_analysis": {
                    "captions": captions,
                    "visual_anomaly_score": visual_anomaly_max,
                    "description": " | ".join(captions) if captions else "No description"
                },
                "ai_reasoning": {
                    "visual_score": fusion_result.get("visual_score", 0),
                    "audio_score": fusion_result.get("audio_score", 0),
                    "text_alignment_score": fusion_result.get("text_alignment_score", 0),
                    "multimodal_agreement": fusion_result.get("multimodal_agreement", 0),
                    "threat_severity": fusion_result.get("threat_severity_index", 0),
                    "reasoning": fusion_result.get("reasoning_summary", "No reasoning available")
                }
            }
            
            return fusion_result
            
        except Exception as e:
            print(f"Tier 2 fusion error: {e}")
            # Return fallback with component details
            return {
                "visual_score": 0.4,
                "audio_score": 0.4,
                "text_alignment_score": 0.4,
                "multimodal_agreement": 0.4,
                "reasoning_summary": f"Tier 2 analysis error: {str(e)}",
                "threat_severity_index": 0.4,
                "frame_id": "A0F",
                "timestamps": timestamps,
                "tier2_components": {
                    "audio_analysis": {
                        "full_transcript": full_transcript,
                        "available": bool(audio_chunk_path),
                        "length": len(full_transcript) if full_transcript else 0
                    },
                    "visual_analysis": {
                        "captions": captions,
                        "visual_anomaly_score": visual_anomaly_max,
                        "description": " | ".join(captions) if captions else "No description"
                    },
                    "ai_reasoning": {
                        "error": str(e)
                    }
                }
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