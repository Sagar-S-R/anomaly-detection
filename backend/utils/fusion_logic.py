from groq import Groq
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client with simple error handling
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        groq_client = Groq(api_key=groq_api_key)
        print("🤖 Groq AI client initialized successfully")
    else:
        print("⚠️ GROQ_API_KEY not found in environment")
        groq_client = None
except Exception as e:
    print(f"⚠️ Groq client failed: {e}")
    groq_client = None



def tier1_fusion(pose_summary, audio_summary, scene_summary):
    """IMPROVED Tier 1 fusion - better accuracy with simple logic"""
    
    # 1. Extract scene probability (cleaner parsing with type handling)
    scene_prob = 0.0
    
    # Handle both string and numeric scene outputs  
    if isinstance(scene_summary, (int, float)):
        # Scene processing returned a confidence score directly
        scene_prob = min(1.0, max(0.0, float(scene_summary)))
    elif scene_summary and isinstance(scene_summary, str) and "Scene anomaly probability:" in scene_summary:
        try:
            prob_str = scene_summary.split("Scene anomaly probability:")[1].strip()
            scene_prob = min(1.0, max(0.0, float(prob_str)))
        except:
            scene_prob = 0.0
    
    # 2. Parse pose anomaly (more reliable)
    pose_detected = False
    pose_confidence = 0.5
    
    if pose_summary and isinstance(pose_summary, str):
        pose_lower = pose_summary.lower()
        if "true" in pose_lower or "anomaly detected: true" in pose_lower:
            pose_detected = True
            
            # Smart confidence based on detection type
            if "fall" in pose_lower:
                pose_confidence = 0.9  # High confidence for falls
            elif "rapid" in pose_lower or "movement" in pose_lower:
                pose_confidence = 0.7  # Medium-high for movement
            elif "instability" in pose_lower or "head" in pose_lower:
                pose_confidence = 0.6  # Medium for other poses
    
    # 3. IMPROVED Audio Analysis - more accurate keyword detection
    audio_detected = False
    audio_confidence = 0.0
    
    if audio_summary and isinstance(audio_summary, str) and len(audio_summary.strip()) > 3:
        audio_lower = audio_summary.lower().strip()
        
        # Skip system messages and non-audio content  
        system_messages = ["no audio", "audio processing", "transcripts", "audio chunk", "no transcripts", "available", "provided", "conversation", "talking", "speaking"]
        if any(msg in audio_lower for msg in system_messages):
            audio_detected = False
            audio_confidence = 0.0
        else:
            # Critical emergency keywords (high precision)
            critical_keywords = ["help me", "emergency", "call 911", "heart attack", "fire", "ambulance"]
            urgent_keywords = ["help", "stop", "hurt", "pain", "no", "911", "police"]
            concern_keywords = ["please", "wait", "scared", "call", "what", "why"]
            
            if any(word in audio_lower for word in critical_keywords):
                audio_detected = True
                audio_confidence = 0.95
            elif any(word in audio_lower for word in urgent_keywords):
                audio_detected = True
                audio_confidence = 0.8
            elif any(word in audio_lower for word in concern_keywords) and len(audio_summary) > 10:
                audio_detected = True
                audio_confidence = 0.6
            elif len(audio_summary) > 30 and any(word in audio_lower for word in ["stressed", "worried", "trouble", "problem"]):
                # Only long speech with distress indicators
                audio_detected = True
                audio_confidence = 0.4
            
        if audio_detected:
            print(f"� AUDIO ALERT (conf={audio_confidence:.2f}): '{audio_summary[:50]}'")
    
    # 4. IMMEDIATE DECISION if audio emergency
    if audio_detected and audio_confidence >= 0.8:
        result = "Suspected Anomaly" 
        details = f"AUDIO EMERGENCY: '{audio_summary[:100]}' | Pose={pose_detected}, Scene={scene_prob:.3f}"
        print(f"🚨 TIER1 AUDIO EMERGENCY: {details}")
        return result, details
    
    # 5. IMPROVED Multi-modal Decision Logic
    # Dynamic thresholds based on confidence levels
    if pose_confidence >= 0.8:
        scene_threshold = 0.05  # High pose confidence = low scene threshold
    elif pose_confidence >= 0.6:
        scene_threshold = 0.15  # Medium pose confidence = medium scene threshold  
    else:
        scene_threshold = 0.3   # Low pose confidence = high scene threshold needed
    
    # SMART FUSION DECISIONS
    if pose_detected and scene_prob > scene_threshold:
        # Strong agreement between pose and scene
        combined_confidence = (pose_confidence + scene_prob) / 2
        result = "Suspected Anomaly"
        details = f"Multi-modal: Pose={pose_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}, Combined={combined_confidence:.2f}"
        print(f"🚨 TIER1 MULTI-MODAL ANOMALY: {details}")
        
    elif pose_detected and pose_confidence >= 0.85:
        # Very high pose confidence alone
        result = "Suspected Anomaly"
        details = f"High-confidence pose: Pose={pose_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}"
        print(f"🚨 TIER1 POSE ANOMALY: {details}")
        
    elif scene_prob >= 0.7:
        # Very high scene confidence alone
        result = "Suspected Anomaly"
        details = f"High-confidence scene: Scene={scene_prob:.3f}, Pose={pose_detected}(conf={pose_confidence:.2f})"
        print(f"🚨 TIER1 SCENE ANOMALY: {details}")
        
    elif audio_detected and (pose_detected or scene_prob > 0.2):
        # Audio with any other support
        result = "Suspected Anomaly"
        details = f"Audio + support: Audio={audio_detected}(conf={audio_confidence:.2f}), Pose={pose_detected}, Scene={scene_prob:.3f}"
        print(f"🚨 TIER1 AUDIO SUPPORTED: {details}")
        
    else:
        # Normal - no strong evidence
        result = "Normal"
        details = f"Normal: Pose={pose_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}(need>{scene_threshold:.2f}), Audio={audio_detected}"
        # Only log significant cases to reduce noise
        if scene_prob > 0.2 or pose_detected or audio_detected:
            print(f"✅ TIER1 NORMAL (notable): {details}")
    
    return result, details

def tier2_fusion(audio_transcript, captions, visual_anomaly_max, tier1_details, enhanced_context=None):
    """IMPROVED Tier 2 fusion - better accuracy with cleaner AI integration"""
    
    # 1. Smart Fallback Scoring (more accurate)
    visual_score = min(0.95, max(0.1, visual_anomaly_max * 1.5))  # Better scaling
    
    # Improved audio scoring
    audio_score = 0.1  # Default low
    if audio_transcript and len(audio_transcript.strip()) > 5:
        audio_lower = audio_transcript.lower()
        critical_words = ["help", "emergency", "stop", "hurt", "pain", "911", "fire"]
        urgent_words = ["no", "please", "wait", "call", "scared", "what", "why"]
        
        if any(word in audio_lower for word in critical_words):
            audio_score = 0.9
        elif any(word in audio_lower for word in urgent_words):
            audio_score = 0.7
        elif len(audio_transcript) > 15:
            audio_score = 0.5
    
    # Calculate threat level (simplified)
    threat_level = (visual_score + audio_score) / 2
    multimodal_agreement = min(0.9, 1.0 - abs(visual_score - audio_score))  # Better agreement calculation
    
    # 2. Smart fallback result
    fallback_result = {
        "visual_score": visual_score,
        "audio_score": audio_score,
        "text_alignment_score": 0.6 if audio_transcript else 0.3,
        "multimodal_agreement": multimodal_agreement,
        "reasoning_summary": f"Analysis: Visual={visual_score:.2f}, Audio={audio_score:.2f}, Threat={threat_level:.2f}",
        "threat_severity_index": threat_level
    }
    
    # 3. Try AI analysis if available (simplified)
    if groq_client is None:
        print("⚠️ Using intelligent fallback (no AI)")
        return fallback_result
    
    try:
        # Build effective but simple prompt
        visual_summary = " | ".join(captions[:3]) if captions else "No visual description"  # Limit to 3 captions
        audio_text = audio_transcript[:200] if audio_transcript else "No audio"  # Limit audio length
        
        prompt = f"""Analyze this emergency situation. Return ONLY valid JSON.

DATA:
- Tier 1: {tier1_details}
- Visual: {visual_summary}
- Audio: {audio_text}
- Visual Score: {visual_anomaly_max:.2f}

Return JSON with exactly these keys:
{{"visual_score": 0.0-1.0, "audio_score": 0.0-1.0, "text_alignment_score": 0.0-1.0, "multimodal_agreement": 0.0-1.0, "reasoning_summary": "brief analysis", "threat_severity_index": 0.0-1.0}}"""

        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",  # Updated to currently supported model
            temperature=0.1,  # Very low for consistency
            max_tokens=250    # Shorter for faster response
        )
        
        ai_output = response.choices[0].message.content.strip()
        
        # Robust JSON extraction
        json_start = ai_output.find('{')
        json_end = ai_output.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = ai_output[json_start:json_end]
            ai_result = json.loads(json_str)
            
            # Quick validation and sanitization
            required_keys = ["visual_score", "audio_score", "text_alignment_score", 
                           "multimodal_agreement", "reasoning_summary", "threat_severity_index"]
            
            if all(key in ai_result for key in required_keys):
                # Clamp numeric values to valid range
                for key in ["visual_score", "audio_score", "text_alignment_score", 
                           "multimodal_agreement", "threat_severity_index"]:
                    if isinstance(ai_result[key], (int, float)):
                        ai_result[key] = min(1.0, max(0.0, float(ai_result[key])))
                    else:
                        ai_result[key] = fallback_result[key]
                
                # Ensure reasoning is valid
                if not isinstance(ai_result["reasoning_summary"], str) or len(ai_result["reasoning_summary"]) < 5:
                    ai_result["reasoning_summary"] = fallback_result["reasoning_summary"]
                
                print(f"✅ AI analysis complete: threat={ai_result['threat_severity_index']:.2f}")
                return ai_result
        
        print(f"⚠️ Invalid AI response format, using fallback")
        return fallback_result
            
    except Exception as ai_error:
        print(f"🤖 AI error: {ai_error}, using fallback")
        return fallback_result