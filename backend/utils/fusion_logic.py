from groq import Groq
import json
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file

# Initialize Groq client with error handling
try:
    groq_client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
        # Remove problematic parameters for compatibility
    )
except Exception as e:
    print(f"Warning: Groq client initialization failed: {e}")
    groq_client = None



def tier1_fusion(pose_summary, audio_summary, scene_summary):
    """Enhanced Tier 1 fusion with AUDIO detection for help calls"""
    # Extract scene anomaly probability for threshold check
    scene_prob = 0.0
    if "Scene anomaly probability:" in scene_summary:
        try:
            prob_str = scene_summary.split("Scene anomaly probability:")[1].strip()
            scene_prob = float(prob_str)
        except:
            scene_prob = 0.0
    
    # Parse pose anomaly status
    pose_anomaly_detected = "True" in pose_summary or "anomaly detected: True" in pose_summary
    
    # CHECK AUDIO FOR EMERGENCY KEYWORDS - THIS WAS MISSING!
    audio_emergency_detected = False
    if audio_summary and isinstance(audio_summary, str):
        audio_lower = audio_summary.lower()
        emergency_words = ["help", "emergency", "call", "911", "stop", "hurt", "pain", "can't breathe", "help me"]
        audio_emergency_detected = any(word in audio_lower for word in emergency_words)
        
        # Also check for repeated help calls
        if "help" in audio_lower and audio_lower.count("help") >= 2:
            audio_emergency_detected = True
            
        if audio_emergency_detected:
            print(f"🚨🚨🚨 AUDIO EMERGENCY DETECTED: '{audio_summary}' 🚨🚨🚨")
        else:
            # Only log if there's actual audio content
            if audio_summary and len(audio_summary) > 20 and "no transcripts found" not in audio_lower:
                pass  # Removed debug spam
    
    # IMMEDIATE ANOMALY if audio emergency is detected
    if audio_emergency_detected:
        result = "Suspected Anomaly"
        details = f"AUDIO EMERGENCY: '{audio_summary}' - Pose={pose_anomaly_detected}, Scene={scene_prob:.3f}"
        print(f"🚨🚨🚨 Tier 1 AUDIO EMERGENCY RESULT: {result} 🚨🚨🚨")
        return result, details
    
    # BALANCED thresholds - not too sensitive for startup
    if pose_anomaly_detected:
        scene_threshold = 0.15  # BALANCED from 0.10 - less startup false positives
    else:
        scene_threshold = 0.20  # BALANCED from 0.15 - less startup false positives
    
    moderate_scene_anomaly = scene_prob > scene_threshold
    
    # Enhanced decision logic with better edge case handling
    if pose_anomaly_detected and moderate_scene_anomaly:
        # Both systems agree - highest confidence
        result = "Suspected Anomaly"
        details = f"Multi-modal anomaly: Pose={pose_anomaly_detected}, Scene={scene_prob:.3f} (threshold={scene_threshold})"
        print(f"🚨 Tier 1 STRONG ANOMALY: pose={pose_anomaly_detected}, scene={scene_prob:.3f}")
    elif pose_anomaly_detected and scene_prob > 0.05:
        # Pose anomaly with minimal scene support - still valid for falls/medical emergencies
        result = "Suspected Anomaly"
        details = f"Pose-driven anomaly: Pose={pose_anomaly_detected}, Scene={scene_prob:.3f} (minimal support)"
        print(f"🚨 Tier 1 POSE ANOMALY: pose={pose_anomaly_detected}, scene={scene_prob:.3f}")
    elif pose_anomaly_detected and scene_prob <= 0.05:
        # Strong pose signal with very low scene confidence - could be lighting/camera issue
        # Still trigger but mark as uncertain
        result = "Suspected Anomaly"
        details = f"Pose-only anomaly: Pose={pose_anomaly_detected}, Scene={scene_prob:.3f} (low scene confidence - possible lighting issue)"
        print(f"🚨 Tier 1 POSE-ONLY ANOMALY: pose={pose_anomaly_detected}, scene={scene_prob:.3f}")
    elif not pose_anomaly_detected and scene_prob > 0.30:
        # Very high scene probability without pose
        result = "Suspected Anomaly"
        details = f"Scene-driven anomaly: Scene={scene_prob:.3f} (high confidence), Pose={pose_anomaly_detected}"
        print(f"🚨 Tier 1 SCENE ANOMALY: scene={scene_prob:.3f}, pose={pose_anomaly_detected}")
    else:
        # Normal activity
        result = "Normal"
        details = f"Normal activity: Pose={pose_anomaly_detected}, Scene={scene_prob:.3f} (threshold={scene_threshold})"
        print(f"✅ Tier 1 NORMAL: pose={pose_anomaly_detected}, scene={scene_prob:.3f}")
    
    return result, details

def tier2_fusion(audio_transcript, captions, visual_anomaly_max, tier1_details, enhanced_context=None):
    """Enhanced Tier 2 fusion with additional context for better anomaly reasoning"""
    try:
        visual_summary = " | ".join(captions) if captions else "No captions."
        scene_summary = f"Highest visual anomaly probability: {visual_anomaly_max:.2f}"
        
        # Enhanced context processing
        audio_indicators = enhanced_context.get("audio_indicators", []) if enhanced_context else []
        scene_analysis = enhanced_context.get("scene_analysis", {}) if enhanced_context else {}
        anomaly_type = enhanced_context.get("anomaly_type", "unknown") if enhanced_context else "unknown"
        pose_context = enhanced_context.get("pose_context", {}) if enhanced_context else {}
        
        # Build enhanced prompt with structured context
        context_details = ""
        if audio_indicators:
            context_details += f"- Audio Indicators: {', '.join(audio_indicators)}\n"
        if scene_analysis.get("description"):
            context_details += f"- Enhanced Scene Analysis: {scene_analysis['description']} (confidence: {scene_analysis.get('confidence', 0):.2f})\n"
        if anomaly_type != "unknown":
            context_details += f"- Detected Anomaly Type: {anomaly_type}\n"
        if pose_context.get("summary"):
            context_details += f"- Pose Context: {pose_context['summary']}\n"
        
        prompt = (
            f"You are an expert anomaly analyst. Provide detailed analysis and reasoning for this anomaly detection case. "
            f"Return ONLY a valid JSON object with no additional text or formatting.\n\n"
            f"INPUT DATA:\n"
            f"- Tier 1 Simple Detection: {tier1_details}\n"
            f"- Audio Transcript: {audio_transcript or 'No audio detected'}\n"
            f"- Visual Scene Description: {visual_summary}\n"
            f"- Visual Anomaly Probability: {visual_anomaly_max:.2f}\n"
            f"{context_details}"
            f"\nANALYSIS REQUIREMENTS:\n"
            f"Provide detailed reasoning that MUST include:\n"
            f"1. POSE ANALYSIS: What does the pose data suggest? (normal posture, aggressive stance, fall position, etc.)\n"
            f"2. SCENE ANALYSIS: What does the visual scene show? How confident are we in this assessment?\n"
            f"3. AUDIO ANALYSIS: Any verbal indicators of distress, aggression, or normalcy?\n"
            f"4. MULTIMODAL CORRELATION: How do all the indicators align? Do they support each other or contradict?\n"
            f"5. ANOMALY TYPE: What specific type of anomaly is most likely? (fall, aggression, medical emergency, false positive)\n"
            f"6. CONFIDENCE ASSESSMENT: How certain is this detection and why?\n"
            f"7. THREAT LEVEL JUSTIFICATION: Why this specific threat severity score?\n\n"
            f"Return JSON with these exact keys:\n"
            f'{{"visual_score": <0-1 float>, "audio_score": <0-1 float>, "text_alignment_score": <0-1 float>, '
            f'"multimodal_agreement": <0-1 float>, "reasoning_summary": "<comprehensive 4-6 sentence analysis covering ALL points above>", "threat_severity_index": <0-1 float>}}'
        )
        
        print(f"Tier 2 fusion prompt: {prompt}")  # Debug logging
        
        if groq_client is None:
            print("Warning: Groq client not available, using fallback response")
            return {
                "status": "Suspected Anomaly",
                "visual_score": 0.6,
                "audio_score": 0.5,
                "multimodal_agreement": 0.5,
                "reasoning_summary": "AI analysis unavailable - using basic detection",
                "threat_severity_index": 0.6
            }
        
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.1  # Lower temperature for more consistent JSON output
        )
        output = response.choices[0].message.content.strip()
        print(f"Tier 2 fusion raw response: {output}")  # Debug logging
        
        # Clean up the response to extract JSON
        if "```json" in output:
            output = output.split("```json")[1].split("```")[0].strip()
        elif "```" in output:
            output = output.split("```")[1].split("```")[0].strip()
        
        # Try to parse JSON
        result = json.loads(output)
        
        # Validate required keys
        required_keys = ["visual_score", "audio_score", "text_alignment_score", 
                        "multimodal_agreement", "reasoning_summary", "threat_severity_index"]
        
        for key in required_keys:
            if key not in result:
                raise KeyError(f"Missing required key: {key}")
        
        # Validate score ranges
        for score_key in ["visual_score", "audio_score", "text_alignment_score", 
                         "multimodal_agreement", "threat_severity_index"]:
            if not (0 <= result[score_key] <= 1):
                result[score_key] = max(0, min(1, result[score_key]))  # Clamp to 0-1
        
        print(f"Tier 2 fusion successful: {result}")  # Debug logging
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error in tier2_fusion: {e}")
        print(f"Raw output: {output}")
    except Exception as e:
        print(f"Error in tier2_fusion: {e}")
    
    # Enhanced fallback with actual data-based scoring
    fallback_visual_score = min(1.0, visual_anomaly_max * 2)  # Scale up the visual score
    fallback_audio_score = 0.3 if audio_transcript and len(audio_transcript.strip()) > 0 else 0.1
    fallback_threat = (fallback_visual_score + fallback_audio_score) / 2
    
    result = {
        "visual_score": fallback_visual_score,
        "audio_score": fallback_audio_score,
        "text_alignment_score": 0.4,
        "multimodal_agreement": 0.4,
        "reasoning_summary": f"Fallback analysis: Visual anomaly {visual_anomaly_max:.2f}, Audio available: {bool(audio_transcript)}",
        "threat_severity_index": fallback_threat
    }
    print(f"Using fallback tier2 result: {result}")
    return result