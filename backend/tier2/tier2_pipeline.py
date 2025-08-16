from utils.audio_processing import transcribe_large
from utils.scene_processing import process_scene_tier2_frame
from utils.fusion_logic import tier2_fusion
from utils.pose_processing import process_pose_frame
import json

def run_tier2_continuous(frame, audio_chunk_path, tier1_result):
    """Enhanced Tier 2 analysis with anomaly type detection and better reasoning"""
    try:
        # Structured logging for Tier 2 start
        tier2_log = {
            "component": "tier2_pipeline",
            "phase": "start",
            "audio_available": bool(audio_chunk_path),
            "frame_available": frame is not None,
            "tier1_anomaly": tier1_result.get("result", "unknown")
        }
        print(f"🔍 TIER2_START: {json.dumps(tier2_log)}")
        
        # Extract pose information from Tier 1 for context
        pose_info = {}
        if tier1_result.get("tier1_components"):
            pose_comp = tier1_result["tier1_components"].get("pose_analysis", {})
            pose_info = {
                "anomaly_detected": pose_comp.get("anomaly_detected", False),
                "raw_score": pose_comp.get("raw_score", 0),
                "summary": pose_comp.get("summary", "")
            }
        
        # Determine likely anomaly type from Tier 1 data
        anomaly_type = "unknown"
        if "Fall" in pose_info.get("summary", ""):
            anomaly_type = "fall"
        elif "arm movement" in pose_info.get("summary", "") or "Extended/raised arm" in pose_info.get("summary", ""):
            anomaly_type = "aggressive"
        elif "Torso bending" in pose_info.get("summary", ""):
            anomaly_type = "medical"
        
        # Extract audio transcript from Tier 1 result with enhanced processing
        full_transcript = ""
        audio_indicators = []
        try:
            # Get transcript from tier1_components
            if tier1_result.get("tier1_components"):
                audio_comp = tier1_result["tier1_components"].get("audio_analysis", {})
                full_transcript = audio_comp.get("transcript_text", "")
                
            # Analyze audio for specific indicators
            if full_transcript:
                transcript_lower = full_transcript.lower()
                if any(word in transcript_lower for word in ["help", "emergency", "call", "911"]):
                    audio_indicators.append("distress_call")
                if any(word in transcript_lower for word in ["fight", "stop", "get away", "leave me alone"]):
                    audio_indicators.append("conflict")
                if any(word in transcript_lower for word in ["hurt", "pain", "can't breathe", "chest"]):
                    audio_indicators.append("medical")
                
        except Exception as e:
            print(f"🎤 Tier 2 audio processing error: {e}")
            full_transcript = ""
            audio_indicators = []
            
        # Structured logging for audio analysis
        audio_log = {
            "component": "tier2_audio",
            "transcript_length": len(full_transcript) if full_transcript else 0,
            "indicators_found": len(audio_indicators),
            "indicators": audio_indicators
        }
        print(f"🎤 TIER2_AUDIO: {json.dumps(audio_log)}")

        # Visual processing with advanced scene analysis  
        captions = ["Scene analysis failed"]
        visual_anomaly_max = 0.3
        scene_description = ""
        scene_anomaly_detected = False
        scene_confidence = 0.0
        
        try:
            # Standard scene captioning
            captions, visual_anomaly_max = process_scene_tier2_frame(frame)
            
            # Use captions for scene analysis
            if frame is not None and captions:
                scene_description = " | ".join(captions)
                
                # Determine anomaly based on scene content and anomaly type
                scene_text = scene_description.lower()
                if anomaly_type == "fall":
                    scene_anomaly_detected = any(word in scene_text for word in 
                        ["lying", "collapsed", "ground", "floor", "fallen"])
                elif anomaly_type == "aggressive":
                    scene_anomaly_detected = any(word in scene_text for word in 
                        ["raised", "fighting", "aggressive", "confrontation"])
                elif anomaly_type == "medical":
                    scene_anomaly_detected = any(word in scene_text for word in 
                        ["distress", "emergency", "bent", "pain"])
                
                # Set confidence based on visual anomaly score
                scene_confidence = min(0.9, visual_anomaly_max * 1.5)
                
        except Exception as e:
            print(f"🖼️ Tier 2 visual processing error: {e}")
            scene_description = "Scene analysis unavailable"
            
        # Structured logging for visual analysis
        visual_log = {
            "component": "tier2_visual",
            "captions_count": len(captions),
            "visual_anomaly_score": visual_anomaly_max,
            "scene_anomaly_detected": scene_anomaly_detected,
            "scene_confidence": scene_confidence,
            "anomaly_type": anomaly_type
        }
        print(f"🖼️ TIER2_VISUAL: {json.dumps(visual_log)}")

        # Tier 2 fusion with AI reasoning
        timestamps = [0.0]
        try:
            # Enhanced fusion with additional context
            fusion_result = tier2_fusion(
                full_transcript, 
                captions, 
                visual_anomaly_max, 
                tier1_result["details"],
                {
                    "audio_indicators": audio_indicators,
                    "scene_analysis": {
                        "description": scene_description,
                        "anomaly_detected": scene_anomaly_detected,
                        "confidence": scene_confidence
                    },
                    "anomaly_type": anomaly_type,
                    "pose_context": pose_info
                }
            )
            fusion_result["frame_id"] = "A0F"
            fusion_result["timestamps"] = timestamps
            
            # Structured logging for fusion result
            fusion_log = {
                "component": "tier2_fusion",
                "visual_score": fusion_result.get("visual_score", 0),
                "audio_score": fusion_result.get("audio_score", 0),
                "multimodal_agreement": fusion_result.get("multimodal_agreement", 0),
                "threat_severity": fusion_result.get("threat_severity_index", 0),
                "anomaly_type": anomaly_type
            }
            print(f"🧠 TIER2_FUSION: {json.dumps(fusion_log)}")
            
            # Add enhanced component breakdown to result
            fusion_result["tier2_components"] = {
                "audio_analysis": {
                    "full_transcript": full_transcript,
                    "audio_indicators": audio_indicators,
                    "available": bool(audio_chunk_path),
                    "length": len(full_transcript) if full_transcript else 0
                },
                "visual_analysis": {
                    "captions": captions,
                    "visual_anomaly_score": visual_anomaly_max,
                    "description": " | ".join(captions) if captions else "No description",
                    "scene_analysis": {
                        "description": scene_description,
                        "anomaly_detected": scene_anomaly_detected,
                        "confidence": scene_confidence,
                        "anomaly_type": anomaly_type
                    }
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
            
            # Final success logging
            success_log = {
                "component": "tier2_pipeline",
                "phase": "complete",
                "status": "success",
                "final_threat_severity": fusion_result.get("threat_severity_index", 0),
                "reasoning_available": bool(fusion_result.get("reasoning_summary"))
            }
            print(f"✅ TIER2_SUCCESS: {json.dumps(success_log)}")
            
            return fusion_result
            
        except Exception as e:
            # Structured error logging
            error_log = {
                "component": "tier2_fusion",
                "phase": "error",
                "error": str(e),
                "fallback_applied": True
            }
            print(f"❌ TIER2_FUSION_ERROR: {json.dumps(error_log)}")
            
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
                        "audio_indicators": audio_indicators,
                        "available": bool(audio_chunk_path),
                        "length": len(full_transcript) if full_transcript else 0
                    },
                    "visual_analysis": {
                        "captions": captions,
                        "visual_anomaly_score": visual_anomaly_max,
                        "description": " | ".join(captions) if captions else "No description",
                        "scene_analysis": {
                            "description": scene_description,
                            "anomaly_detected": scene_anomaly_detected,
                            "confidence": scene_confidence,
                            "anomaly_type": anomaly_type
                        }
                    },
                    "ai_reasoning": {
                        "error": str(e)
                    }
                }
            }
            
    except Exception as e:
        # Critical error logging
        critical_log = {
            "component": "tier2_pipeline",
            "phase": "critical_error",
            "error": str(e),
            "safe_fallback_applied": True
        }
        print(f"💥 TIER2_CRITICAL_ERROR: {json.dumps(critical_log)}")
        
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
            "timestamps": [0.0],
            "tier2_components": {
                "error": str(e),
                "status": "critical_failure"
            }
        }