from groq import Groq
import json
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))



def tier1_fusion(pose_summary, audio_summary, scene_summary):
    # Extract scene anomaly probability for threshold check
    scene_prob = 0.0
    if "Scene anomaly probability:" in scene_summary:
        try:
            prob_str = scene_summary.split("Scene anomaly probability:")[1].strip()
            scene_prob = float(prob_str)
        except:
            scene_prob = 0.0
    
    # Debug logging for scene probability parsing
    print(f"🔍 Tier 1 Debug: scene_summary='{scene_summary}', parsed_prob={scene_prob}")
    
    # Simple thresholds - no AI reasoning in Tier 1
    pose_anomaly_detected = "True" in pose_summary
    
    # Very sensitive thresholds to catch visual anomalies better
    if pose_anomaly_detected:
        scene_threshold = 0.15  # Lower threshold when pose anomaly is detected
    else:
        scene_threshold = 0.20  # Much lower threshold for scene-only anomalies (22% should now trigger)
    
    moderate_scene_anomaly = scene_prob > scene_threshold
    
    # Quick decisions without AI reasoning - but be more lenient
    if not pose_anomaly_detected and scene_prob < 0.10:  # Only skip if very low scene probability
        return "Normal", f"Scene probability ({scene_prob:.2f}) and pose analysis indicate normal activity"
    
    # Simple threshold-based detection for Tier 1
    if pose_anomaly_detected or moderate_scene_anomaly:
        result = "Suspected Anomaly"
        details = f"Pose anomaly: {pose_anomaly_detected}, Scene probability: {scene_prob:.2f}"
        print(f"🚨 Tier 1 ANOMALY: pose={pose_anomaly_detected}, scene={scene_prob:.2f}, threshold={scene_threshold}")
        return result, details
    else:
        result = "Normal"
        details = f"Pose anomaly: {pose_anomaly_detected}, Scene probability: {scene_prob:.2f}"
        print(f"✅ Tier 1 NORMAL: pose={pose_anomaly_detected}, scene={scene_prob:.2f}, threshold={scene_threshold}")
        return result, details

def tier2_fusion(audio_transcript, captions, visual_anomaly_max, tier1_details):
    try:
        visual_summary = " | ".join(captions) if captions else "No captions."
        scene_summary = f"Highest visual anomaly probability: {visual_anomaly_max:.2f}"
        prompt = (
            f"You are an expert anomaly analyst. Provide detailed analysis and reasoning for this anomaly detection case. "
            f"Return ONLY a valid JSON object with no additional text or formatting.\n\n"
            f"INPUT DATA:\n"
            f"- Tier 1 Simple Detection: {tier1_details}\n"
            f"- Audio Transcript: {audio_transcript or 'No audio detected'}\n"
            f"- Visual Scene Description: {visual_summary}\n"
            f"- Visual Anomaly Probability: {visual_anomaly_max:.2f}\n\n"
            f"ANALYSIS REQUIREMENTS:\n"
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