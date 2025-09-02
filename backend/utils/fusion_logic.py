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
    """ENHANCED Tier 1 fusion with INTELLIGENT decision making and context awareness"""
    # Extract scene anomaly probability for threshold check
    scene_prob = 0.0
    if "Scene anomaly probability:" in scene_summary:
        try:
            prob_str = scene_summary.split("Scene anomaly probability:")[1].strip()
            scene_prob = float(prob_str)
        except:
            scene_prob = 0.0
    
    # Parse pose anomaly status with context
    pose_anomaly_detected = "True" in pose_summary or "anomaly detected: True" in pose_summary
    pose_confidence = 0.5  # Default
    
    # Extract pose confidence from summary if available
    if "SMART Fall Detection" in pose_summary:
        pose_confidence = 0.9  # High confidence for smart fall detection
    elif "Rapid arm movement" in pose_summary:
        pose_confidence = 0.7  # Medium-high for arm movement
    elif "head movement" in pose_summary or "Torso instability" in pose_summary:
        pose_confidence = 0.6  # Medium for other movements
    
    # ENHANCED AUDIO ANALYSIS
    audio_emergency_detected = False
    audio_confidence = 0.0
    if audio_summary and isinstance(audio_summary, str):
        audio_lower = audio_summary.lower()
        
        # Critical emergency words (highest priority)
        # MUCH MORE SENSITIVE critical word lists
        critical_words = ["help me", "emergency", "call 911", "can't breathe", "heart attack", "fire", "police", "ambulance"]
        high_priority_words = ["help", "stop", "hurt", "pain", "911", "no", "ow", "ouch", "what", "why"]
        medium_words = ["call", "please", "scared", "wait", "ah", "oh", "excuse", "hey"]
        
        # MUCH MORE SENSITIVE audio confidence calculation
        if any(word in audio_lower for word in critical_words):
            audio_emergency_detected = True
            audio_confidence = 0.95
        elif any(word in audio_lower for word in high_priority_words):
            audio_emergency_detected = True
            audio_confidence = 0.8
        elif any(word in audio_lower for word in medium_words) and len(audio_summary) > 15:  # Reduced from 30
            audio_emergency_detected = True
            audio_confidence = 0.55  # Reduced from 0.6
        elif len(audio_summary) > 25:  # New: Any long speech might be distress
            audio_emergency_detected = True
            audio_confidence = 0.4
            
        # ENHANCED repeated word detection - more sensitive
        if "help" in audio_lower and audio_lower.count("help") >= 2:
            audio_emergency_detected = True
            audio_confidence = max(audio_confidence, 0.9)
        elif any(word in audio_lower for word in ["no", "stop", "wait"]) and len(audio_summary) > 10:  # New detection
            audio_emergency_detected = True
            audio_confidence = max(audio_confidence, 0.65)
        elif any(char in audio_summary for char in '!?') and len(audio_summary) > 8:  # Punctuation intensity
            audio_emergency_detected = True
            audio_confidence = max(audio_confidence, 0.5)
            
        if audio_emergency_detected:
            print(f"🚨🚨🚨 AUDIO EMERGENCY (confidence={audio_confidence:.2f}): '{audio_summary}' 🚨🚨🚨")
    
    # IMMEDIATE ANOMALY if audio emergency is detected
    if audio_emergency_detected:
        result = "Suspected Anomaly"
        details = f"AUDIO EMERGENCY (conf={audio_confidence:.2f}): '{audio_summary}' - Pose={pose_anomaly_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}"
        print(f"🚨🚨🚨 Tier 1 AUDIO EMERGENCY RESULT: {result} 🚨🚨🚨")
        return result, details
    
    # MUCH MORE SENSITIVE thresholds based on multi-modal confidence
    confidence_boost = 0
    
    # Boost confidence if multiple indicators align
    if pose_anomaly_detected and scene_prob > 0.05:  # Reduced from 0.1
        confidence_boost += 0.1  # Reduced boost to be more balanced
    
    # Much more sensitive adaptive thresholds based on pose confidence
    if pose_confidence > 0.7:  # Reduced from 0.8
        scene_threshold = 0.02  # EXTREMELY low - reduced from 0.05
    elif pose_confidence > 0.5:  # Reduced from 0.6
        scene_threshold = 0.05  # Very low - reduced from 0.10
    else:  # Low confidence pose
        scene_threshold = 0.15  # Lower - reduced from 0.20
    
    # Apply confidence boost
    effective_scene_prob = scene_prob + confidence_boost
    
    # MUCH MORE SENSITIVE DECISION LOGIC
    if pose_anomaly_detected and effective_scene_prob > scene_threshold:
        # Strong multi-modal agreement
        result = "Suspected Anomaly"
        details = f"Multi-modal anomaly: Pose={pose_anomaly_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}+{confidence_boost:.2f}={effective_scene_prob:.3f} > {scene_threshold:.2f}"
        print(f"🚨 Tier 1 STRONG ANOMALY: {details}")
        
    elif pose_anomaly_detected and pose_confidence > 0.6 and scene_prob > 0.02:  # Much more sensitive
        # Medium-confidence pose with minimal scene support
        result = "Suspected Anomaly"
        details = f"Medium-confidence pose: Pose={pose_anomaly_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f} (minimal support)"
        print(f"🚨 Tier 1 POSE ANOMALY (medium conf): {details}")
        
    elif pose_anomaly_detected and pose_confidence > 0.8:  # High confidence pose alone
        result = "Suspected Anomaly"
        details = f"High-confidence pose alone: Pose={pose_anomaly_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}"
        print(f"🚨 Tier 1 POSE ANOMALY (high conf alone): {details}")
        
    elif not pose_anomaly_detected and scene_prob > 0.4:  # Reduced from 0.6
        # High scene confidence without pose
        result = "Suspected Anomaly"
        details = f"High-confidence scene: Scene={scene_prob:.3f} (high), Pose={pose_anomaly_detected}"
        print(f"🚨 Tier 1 SCENE ANOMALY (high conf): {details}")
        
    elif pose_anomaly_detected and scene_prob > 0.05:  # Much more sensitive
        # Any pose with any scene support
        combined_confidence = (pose_confidence + scene_prob) / 2
        if combined_confidence > 0.25:  # Much lower threshold - reduced from 0.45
            result = "Suspected Anomaly"
            details = f"Combined confidence: Pose={pose_anomaly_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}, Combined={combined_confidence:.2f}"
            print(f"🚨 Tier 1 COMBINED ANOMALY: {details}")
        else:
            result = "Normal"
            details = f"Low combined confidence: Pose={pose_anomaly_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}, Combined={combined_confidence:.2f} < 0.25"
    else:
        # Normal activity
        result = "Normal"
        details = f"Normal activity: Pose={pose_anomaly_detected}(conf={pose_confidence:.2f}), Scene={scene_prob:.3f}(thresh={scene_threshold:.2f})"
        # Only log occasionally to reduce spam
        if scene_prob > 0.10 or pose_anomaly_detected:  # Reduced logging threshold
            print(f"✅ Tier 1 NORMAL: {details}")
    
    return result, details

def tier2_fusion(audio_transcript, captions, visual_anomaly_max, tier1_details, enhanced_context=None):
    """ENHANCED Tier 2 fusion with better error handling and fallback logic"""
    try:
        print(f"🧠 Starting Tier 2 fusion with enhanced context: {enhanced_context is not None}")
        
        visual_summary = " | ".join(captions) if captions else "No visual captions available."
        scene_summary = f"Highest visual anomaly probability: {visual_anomaly_max:.2f}"
        
        # Enhanced context processing with error handling
        audio_indicators = enhanced_context.get("audio_indicators", []) if enhanced_context else []
        scene_analysis = enhanced_context.get("scene_analysis", {}) if enhanced_context else {}
        anomaly_type = enhanced_context.get("anomaly_type", "unknown") if enhanced_context else "unknown"
        pose_context = enhanced_context.get("pose_context", {}) if enhanced_context else {}
        
        # INTELLIGENT fallback scoring before trying AI
        fallback_visual_score = min(0.9, max(0.1, visual_anomaly_max * 1.8))
        fallback_audio_score = 0.8 if audio_indicators else (0.4 if audio_transcript and len(audio_transcript.strip()) > 10 else 0.1)
        fallback_threat = min(0.9, (fallback_visual_score + fallback_audio_score) / 2)
        
        # Enhanced fallback result
        fallback_result = {
            "visual_score": fallback_visual_score,
            "audio_score": fallback_audio_score,
            "text_alignment_score": 0.5,
            "multimodal_agreement": min(0.8, (fallback_visual_score + fallback_audio_score) / 2),
            "reasoning_summary": f"Analysis based on {anomaly_type} type detection with visual confidence {visual_anomaly_max:.2f} and {len(audio_indicators)} audio indicators.",
            "threat_severity_index": fallback_threat
        }
        
        # Check if Groq is available
        if groq_client is None:
            print("⚠️ Groq client not available, using intelligent fallback")
            return fallback_result
        
        # Build enhanced prompt with better structure
        context_details = []
        if audio_indicators:
            context_details.append(f"Audio Indicators: {', '.join(audio_indicators)}")
        if scene_analysis.get("description"):
            context_details.append(f"Scene Analysis: {scene_analysis['description']} (confidence: {scene_analysis.get('confidence', 0):.2f})")
        if anomaly_type != "unknown":
            context_details.append(f"Detected Anomaly Type: {anomaly_type}")
        if pose_context.get("summary"):
            context_details.append(f"Pose Context: {pose_context['summary']}")
            
        context_str = "\n- ".join(context_details) if context_details else "Limited context available"
        
        # Simplified, more reliable prompt
        prompt = f"""Analyze this anomaly detection case and return ONLY valid JSON.

INPUT DATA:
- Tier 1 Detection: {tier1_details}
- Audio: {audio_transcript or 'No audio'}
- Visual: {visual_summary}
- Visual Anomaly Score: {visual_anomaly_max:.2f}
- {context_str}

Return JSON with exactly these keys:
{{"visual_score": <0-1>, "audio_score": <0-1>, "text_alignment_score": <0-1>, "multimodal_agreement": <0-1>, "reasoning_summary": "<analysis>", "threat_severity_index": <0-1>}}"""

        print(f"🤖 Sending request to Groq API...")
        
        # Try AI analysis with timeout and error handling
        try:
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.1,
                max_tokens=500  # Limit response size
            )
            
            output = response.choices[0].message.content.strip()
            print(f"🤖 Raw AI response length: {len(output)} chars")
            
            # Clean JSON extraction
            json_start = output.find('{')
            json_end = output.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
                
            json_str = output[json_start:json_end]
            result = json.loads(json_str)
            
            # Validate and sanitize result
            required_keys = ["visual_score", "audio_score", "text_alignment_score", 
                           "multimodal_agreement", "reasoning_summary", "threat_severity_index"]
            
            for key in required_keys:
                if key not in result:
                    print(f"⚠️ Missing key {key}, using fallback")
                    return fallback_result
                    
            # Sanitize numeric values
            for score_key in ["visual_score", "audio_score", "text_alignment_score", 
                             "multimodal_agreement", "threat_severity_index"]:
                if not isinstance(result[score_key], (int, float)) or not (0 <= result[score_key] <= 1):
                    result[score_key] = fallback_result[score_key]
            
            # Ensure reasoning is a string
            if not isinstance(result["reasoning_summary"], str) or len(result["reasoning_summary"]) < 10:
                result["reasoning_summary"] = fallback_result["reasoning_summary"]
            
            print(f"✅ AI analysis successful: threat={result['threat_severity_index']:.2f}")
            return result
            
        except Exception as ai_error:
            print(f"🤖 AI analysis failed: {ai_error}")
            return fallback_result
            
    except Exception as e:
        print(f"❌ Tier 2 fusion error: {e}")
        # Final emergency fallback
        return {
            "visual_score": 0.5,
            "audio_score": 0.3,
            "text_alignment_score": 0.4,
            "multimodal_agreement": 0.4,
            "reasoning_summary": "Emergency fallback due to processing error",
            "threat_severity_index": 0.5
        }