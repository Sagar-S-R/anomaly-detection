from groq import Groq
import json
import os
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client with simple error handling
def initialize_groq_client():
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        print(f"🔑 GROQ_API_KEY found: {groq_api_key[:20]}..." if groq_api_key else "❌ GROQ_API_KEY not found")
        
        if not groq_api_key:
            print("⚠️ GROQ_API_KEY not found in environment")
            return None
            
        # Simple initialization
        client = Groq(api_key=groq_api_key)
        print("🤖 Groq AI client initialized successfully")
        return client
                
    except Exception as e:
        print(f"⚠️ Groq client failed to initialize: {e}")
        print(f"📋 Full error: {traceback.format_exc()}")
        return None

groq_client = initialize_groq_client()



def tier1_fusion(pose_summary, audio_summary, scene_summary):
    """IMPROVED Tier 1 fusion - handles missing audio gracefully"""
    
    # 1. Extract scene probability
    scene_prob = 0.0
    if isinstance(scene_summary, (int, float)):
        scene_prob = min(1.0, max(0.0, float(scene_summary)))
    elif scene_summary and isinstance(scene_summary, str) and "Scene anomaly probability:" in scene_summary:
        try:
            prob_str = scene_summary.split("Scene anomaly probability:")[1].strip()
            scene_prob = min(1.0, max(0.0, float(prob_str)))
        except:
            scene_prob = 0.0
    
    # 2. Parse pose anomaly
    pose_detected = False
    pose_confidence = 0.5
    if pose_summary and isinstance(pose_summary, str):
        pose_lower = pose_summary.lower()
        if "true" in pose_lower or "anomaly detected: true" in pose_lower:
            pose_detected = True
            if "fall" in pose_lower:
                pose_confidence = 0.9
            elif "rapid" in pose_lower or "movement" in pose_lower:
                pose_confidence = 0.7
            elif "instability" in pose_lower or "head" in pose_lower:
                pose_confidence = 0.6
    
    # 3. Audio Analysis - but track if audio is available
    audio_detected = False
    audio_confidence = 0.0
    audio_available = False
    
    if audio_summary and isinstance(audio_summary, str) and len(audio_summary.strip()) > 3:
        audio_available = True
        audio_lower = audio_summary.lower().strip()
        
        # Skip system messages
        system_messages = ["no audio", "audio processing", "transcripts", "audio chunk", "no transcripts"]
        if not any(msg in audio_lower for msg in system_messages):
            # Analyze audio content
            critical_keywords = ["help me", "emergency", "call 911", "heart attack", "fire", "ambulance"]
            environmental_keywords = ["fire", "flood", "flooding", "gas leak", "smoke", "burning"]
            urgent_keywords = ["help", "stop", "hurt", "pain", "no", "911", "police"]
            
            if any(word in audio_lower for word in critical_keywords):
                audio_detected = True
                audio_confidence = 0.95
            elif any(word in audio_lower for word in environmental_keywords):
                audio_detected = True
                audio_confidence = 0.90
            elif any(word in audio_lower for word in urgent_keywords):
                audio_detected = True
                audio_confidence = 0.8
    
    # 4. IMMEDIATE AUDIO EMERGENCY (if audio available and critical)
    if audio_detected and audio_confidence >= 0.8:
        result = "Suspected Anomaly"
        details = f"AUDIO EMERGENCY: '{audio_summary[:100]}' | Pose={pose_detected}, Scene={scene_prob:.3f}"
        print(f"🚨 TIER1 AUDIO EMERGENCY: {details}")
        return result, details
    
    # 5. VISUAL-FIRST DETECTION (works with or without audio)
    # HIGH VISUAL CONFIDENCE - trigger regardless of audio
    if scene_prob >= 0.80:  # Very high scene confidence
        result = "Suspected Anomaly"
        details = f"HIGH SCENE CONFIDENCE: Scene={scene_prob:.3f}, Pose={pose_detected}(conf={pose_confidence:.2f}), Audio={'Available' if audio_available else 'N/A'}"
        print(f"🚨 TIER1 HIGH SCENE: {details}")
        return result, details
        
    if pose_detected and pose_confidence >= 0.85:  # Very high pose confidence
        result = "Suspected Anomaly"
        details = f"HIGH POSE CONFIDENCE: Pose={pose_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}, Audio={'Available' if audio_available else 'N/A'}"
        print(f"🚨 TIER1 HIGH POSE: {details}")
        return result, details
    
    # MEDIUM VISUAL CONFIDENCE - with adaptive thresholds
    if pose_detected and scene_prob > 0.65:  # Strong agreement
        result = "Suspected Anomaly"
        details = f"STRONG VISUAL AGREEMENT: Pose={pose_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}"
        print(f"🚨 TIER1 VISUAL AGREEMENT: {details}")
        return result, details
        
    if scene_prob >= 0.70:  # Good scene evidence alone
        result = "Suspected Anomaly"
        details = f"GOOD SCENE EVIDENCE: Scene={scene_prob:.3f}, Pose={pose_detected}"
        print(f"🚨 TIER1 SCENE EVIDENCE: {details}")
        return result, details
    
    # AUDIO-SUPPORTED DETECTION (only if audio is available)
    if audio_available and audio_detected:
        if pose_detected or scene_prob > 0.45:  # Lower threshold when audio supports
            result = "Suspected Anomaly"
            details = f"AUDIO SUPPORTED: Audio={audio_detected}(conf={audio_confidence:.2f}), Pose={pose_detected}, Scene={scene_prob:.3f}"
            print(f"🚨 TIER1 AUDIO SUPPORTED: {details}")
            return result, details
    
    # Normal case
    result = "Normal"
    audio_status = f"Audio={audio_detected}" if audio_available else "Audio=N/A"
    details = f"Normal: Pose={pose_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}, {audio_status}"
    
    return result, details

def tier2_fusion(audio_transcript, captions, visual_anomaly_max, tier1_details, enhanced_context=None):
    """IMPROVED Tier 2 fusion - audio-agnostic approach"""
    
    # 1. Visual scoring (unchanged)
    visual_score = min(0.95, max(0.1, visual_anomaly_max * 1.5))
    
    # 2. IMPROVED Audio handling - don't penalize missing audio
    audio_available = bool(audio_transcript and len(audio_transcript.strip()) > 5)
    audio_score = 0.0  # Neutral default
    
    if audio_available:
        audio_lower = audio_transcript.lower()
        critical_words = ["help", "emergency", "stop", "hurt", "pain", "911", "fire"]
        urgent_words = ["no", "please", "wait", "call", "scared", "what", "why"]
        
        if any(word in audio_lower for word in critical_words):
            audio_score = 0.9
        elif any(word in audio_lower for word in urgent_words):
            audio_score = 0.7
        elif len(audio_transcript) > 15:
            audio_score = 0.5
        else:
            audio_score = 0.3  # Neutral for normal speech
    
    # 3. ADAPTIVE threat calculation based on available modalities
    if audio_available:
        # Multi-modal: consider both visual and audio
        threat_level = (visual_score * 0.7 + audio_score * 0.3)  # Weight visual higher
        multimodal_agreement = min(0.9, 1.0 - abs(visual_score - audio_score))
        text_alignment_score = 0.8 if abs(visual_score - audio_score) < 0.3 else 0.5
    else:
        # Visual-only: use visual score directly
        threat_level = visual_score
        multimodal_agreement = 0.8  # High agreement for single modality
        text_alignment_score = 0.9   # High alignment when no conflicting audio
    
    # 4. Build result with appropriate reasoning
    result = {
        "visual_score": visual_score,
        "audio_score": audio_score,
        "text_alignment_score": text_alignment_score,
        "multimodal_agreement": multimodal_agreement,
        "threat_severity_index": threat_level
    }
    
    # 5. Reasoning summary based on available data
    if audio_available:
        result["reasoning_summary"] = f"Multi-modal analysis: Visual={visual_score:.2f}, Audio={audio_score:.2f}, Threat={threat_level:.2f}"
    else:
        result["reasoning_summary"] = f"Visual-only analysis: Visual={visual_score:.2f}, Threat={threat_level:.2f} (no audio available - not penalized)"
    
    # 6. Try AI analysis with audio-aware prompting
    if groq_client:
        try:
            visual_summary = " | ".join(captions[:3]) if captions else "No visual description"
            audio_text = audio_transcript[:200] if audio_available else "No audio available"
            
            prompt = f"""You are analyzing surveillance footage for security threats.

SITUATION:
- Tier 1 Detection: {tier1_details}
- Visual Description: {visual_summary}
- Audio Status: {'Available: ' + audio_text if audio_available else 'No audio available (do not penalize this)'}
- Visual Anomaly Score: {visual_anomaly_max:.2f}

IMPORTANT: If no audio is available, focus entirely on visual analysis. Missing audio should NOT reduce threat assessment.

Provide analysis as valid JSON:
{{
  "visual_score": [0.0-1.0],
  "audio_score": [0.0-1.0, use 0.5 if no audio available],
  "text_alignment_score": [0.0-1.0, use 0.8-0.9 if no audio to conflict with visuals],
  "multimodal_agreement": [0.0-1.0, use 0.8+ for single modality],
  "reasoning_summary": "[Explain what you observe and why, note if audio unavailable]",
  "threat_severity_index": [0.0-1.0, based on available evidence only]
}}"""

            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.3,
                max_tokens=400
            )
            
            ai_output = response.choices[0].message.content.strip()
            json_start = ai_output.find('{')
            json_end = ai_output.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = ai_output[json_start:json_end]
                ai_result = json.loads(json_str)
                
                # Validate and sanitize
                required_keys = ["visual_score", "audio_score", "text_alignment_score", 
                               "multimodal_agreement", "reasoning_summary", "threat_severity_index"]
                
                if all(key in ai_result for key in required_keys):
                    for key in required_keys[:-1]:  # All except reasoning_summary
                        if key != "reasoning_summary":
                            ai_result[key] = min(1.0, max(0.0, float(ai_result[key])))
                    
                    ai_result["reasoning_summary"] = "🤖 AI Analysis: " + str(ai_result["reasoning_summary"])
                    print(f"✅ AI analysis complete: threat={ai_result['threat_severity_index']:.2f}")
                    return ai_result
            
            print("⚠ AI analysis failed, using fallback")
            
        except Exception as ai_error:
            print(f"🤖 AI error: {ai_error}")
    
    # Return fallback result
    result["reasoning_summary"] = "⚠ Fallback analysis: " + result["reasoning_summary"]
    return result


# Example usage demonstration
if __name__ == "__main__":
    # Test case: High visual score, no audio
    print("=== TEST: High Visual Score (0.87), No Audio ===")
    
    # Simulate high visual detection
    pose_summary = "Anomaly detected: true - rapid movement detected"
    audio_summary = None  # No audio available
    scene_summary = "Scene anomaly probability: 0.73"
    
    # Tier 1
    tier1_result, tier1_details = tier1_fusion(pose_summary, audio_summary, scene_summary)
    print(f"Tier 1 Result: {tier1_result}")
    print(f"Tier 1 Details: {tier1_details}")
    
    # Tier 2
    tier2_result = tier2_fusion(
        audio_transcript=None,
        captions=["Person making aggressive gestures", "Rapid movement detected"],
        visual_anomaly_max=0.87,
        tier1_details=tier1_details
    )
    
    print(f"Tier 2 Threat Level: {tier2_result['threat_severity_index']:.2f}")
    print(f"Tier 2 Reasoning: {tier2_result['reasoning_summary']}")