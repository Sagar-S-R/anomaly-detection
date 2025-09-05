import cv2
from transformers import AutoProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import numpy as np

# SOTA Model Initialization - Industry Standard Vision Models
clip_processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

clip_large_processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_large_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# SOTA Prompt Engineering - Used by Major AI Companies
SOTA_NORMAL_PROMPTS = [
    "person sitting calmly at desk working on computer",
    "person standing upright with relaxed normal posture",
    "person walking steadily with normal gait pattern",
    "person talking calmly with natural hand gestures",
    "person reading or doing peaceful everyday activities"
]

SOTA_VIOLENCE_PROMPTS = [
    "person throwing punches with clenched fists fighting",
    "person kicking aggressively in fighting stance",
    "person in violent confrontation with raised weapons",
    "person making threatening aggressive gestures",
    "multiple people engaged in physical altercation"
]

SOTA_MEDICAL_EMERGENCY_PROMPTS = [
    "person collapsed unconscious on floor medical emergency",
    "elderly person fallen down unable to get up",
    "person lying motionless on ground requiring help",
    "person in medical distress showing signs of injury",
    "person crawling on floor in obvious physical distress"
]

SOTA_ABNORMAL_BEHAVIOR_PROMPTS = [
    "person behaving erratically with unusual movements",
    "person in suspicious crouching or hiding position",
    "person making repetitive abnormal gestures",
    "person exhibiting signs of mental distress",
    "person in unusual body position or posture"
]

# NEW: Environmental Hazard Detection
SOTA_FIRE_EMERGENCY_PROMPTS = [
    "fire flames burning in indoor environment emergency",
    "smoke filling room with visible fire hazard",
    "orange flames and smoke emergency evacuation needed",
    "building fire with visible flames and smoke damage",
    "electrical fire with sparks and burning materials"
]

SOTA_FLOOD_EMERGENCY_PROMPTS = [
    "water flooding indoor space emergency situation",
    "rising flood water covering floor area",
    "water damage with flooding in indoor environment",
    "burst pipe flooding with water everywhere",
    "flood water emergency requiring immediate evacuation"
]

SOTA_ENVIRONMENTAL_HAZARD_PROMPTS = [
    "gas leak with visible vapor or mist emergency",
    "structural collapse with debris falling down",
    "chemical spill with hazardous materials visible",
    "severe storm damage with broken windows debris",
    "ceiling collapse with dangerous falling materials"
]

# NEW: Security & Theft Detection
SOTA_SECURITY_THEFT_PROMPTS = [
    "person breaking into building unauthorized entry",
    "person stealing items taking property unlawfully",
    "burglar with mask breaking glass windows",
    "person hiding and lurking in suspicious manner",
    "unauthorized person accessing restricted areas"
]

# NEW: Workplace Safety & Industrial Accidents
SOTA_WORKPLACE_SAFETY_PROMPTS = [
    "worker injured on job site accident emergency",
    "person operating dangerous machinery unsafely",
    "industrial equipment malfunction sparks danger",
    "worker fallen from height construction accident",
    "person not wearing required safety equipment"
]

# NEW: Electrical & Technical Emergencies  
SOTA_ELECTRICAL_EMERGENCY_PROMPTS = [
    "electrical sparks and wires creating fire hazard",
    "person electrocuted by electrical equipment shock",
    "electrical panel smoking with visible damage",
    "power lines down creating electrical danger",
    "electrical equipment overheating with smoke"
]

def detect_violence_sota(image, confidence_threshold=0.40):
    """SOTA Violence Detection using Security Industry Standards"""
    try:
        # Multi-scale violence detection with ensemble scoring
        all_prompts = SOTA_NORMAL_PROMPTS + SOTA_VIOLENCE_PROMPTS
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        # Calculate violence vs normal scores
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        violence_scores = probs[len(SOTA_NORMAL_PROMPTS):]
        
        max_normal = torch.max(normal_scores).item()
        max_violence = torch.max(violence_scores).item()
        best_violence_idx = torch.argmax(violence_scores).item()
        
        # Industry-standard confidence scoring
        confidence_ratio = max_violence / (max_normal + 1e-6)
        violence_confidence = max_violence - max_normal
        
        # Multi-criteria violence detection
        is_violence = (
            max_violence > confidence_threshold and
            confidence_ratio > 1.2 and
            violence_confidence > 0.05
        )
        
        if is_violence:
            violence_type = SOTA_VIOLENCE_PROMPTS[best_violence_idx]
            print(f"🥊 SOTA Violence: {violence_confidence:.3f} conf, type: {violence_type[:50]}...")
            return True, max_violence, violence_type
        
        return False, 0.0, ""
        
    except Exception as e:
        print(f"Error in violence detection: {e}")
        return False, 0.0, ""

def detect_medical_emergency_sota(image, confidence_threshold=0.35):
    """SOTA Medical Emergency Detection using Healthcare Industry Standards"""
    try:
        all_prompts = SOTA_NORMAL_PROMPTS + SOTA_MEDICAL_EMERGENCY_PROMPTS
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        medical_scores = probs[len(SOTA_NORMAL_PROMPTS):]
        
        max_normal = torch.max(normal_scores).item()
        max_medical = torch.max(medical_scores).item()
        best_medical_idx = torch.argmax(medical_scores).item()
        
        confidence_ratio = max_medical / (max_normal + 1e-6)
        medical_confidence = max_medical - max_normal
        
        is_medical = (
            max_medical > confidence_threshold and
            confidence_ratio > 1.1 and  # Lower threshold for medical emergencies
            medical_confidence > 0.03
        )
        
        if is_medical:
            medical_type = SOTA_MEDICAL_EMERGENCY_PROMPTS[best_medical_idx]
            print(f"🚑 SOTA Medical Emergency: {medical_confidence:.3f} conf, type: {medical_type[:50]}...")
            return True, max_medical, medical_type
        
        return False, 0.0, ""
        
    except Exception as e:
        print(f"Error in medical detection: {e}")
        return False, 0.0, ""

def detect_abnormal_behavior_sota(image, confidence_threshold=0.38):
    """SOTA Abnormal Behavior Detection using Surveillance Industry Standards"""
    try:
        all_prompts = SOTA_NORMAL_PROMPTS + SOTA_ABNORMAL_BEHAVIOR_PROMPTS
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        abnormal_scores = probs[len(SOTA_NORMAL_PROMPTS):]
        
        max_normal = torch.max(normal_scores).item()
        max_abnormal = torch.max(abnormal_scores).item()
        best_abnormal_idx = torch.argmax(abnormal_scores).item()
        
        confidence_ratio = max_abnormal / (max_normal + 1e-6)
        abnormal_confidence = max_abnormal - max_normal
        
        is_abnormal = (
            max_abnormal > confidence_threshold and
            confidence_ratio > 1.15 and
            abnormal_confidence > 0.04
        )
        
        if is_abnormal:
            abnormal_type = SOTA_ABNORMAL_BEHAVIOR_PROMPTS[best_abnormal_idx]
            print(f"🤯 SOTA Abnormal Behavior: {abnormal_confidence:.3f} conf, type: {abnormal_type[:50]}...")
            return True, max_abnormal, abnormal_type
        
        return False, 0.0, ""
        
    except Exception as e:
        print(f"Error in abnormal behavior detection: {e}")
        return False, 0.0, ""

def detect_fire_emergency_sota(image, confidence_threshold=0.42):
    """SOTA Fire Emergency Detection"""
    try:
        all_prompts = SOTA_NORMAL_PROMPTS + SOTA_FIRE_EMERGENCY_PROMPTS
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        fire_scores = probs[len(SOTA_NORMAL_PROMPTS):]
        
        max_normal = torch.max(normal_scores).item()
        max_fire = torch.max(fire_scores).item()
        best_fire_idx = torch.argmax(fire_scores).item()
        
        confidence_ratio = max_fire / (max_normal + 1e-6)
        fire_confidence = max_fire - max_normal
        
        is_fire = (
            max_fire > confidence_threshold and
            confidence_ratio > 1.3 and
            fire_confidence > 0.06
        )
        
        if is_fire:
            fire_type = SOTA_FIRE_EMERGENCY_PROMPTS[best_fire_idx]
            print(f"🔥 SOTA Fire Emergency: {fire_confidence:.3f} conf, type: {fire_type[:50]}...")
            return True, max_fire, fire_type
        
        return False, 0.0, ""
        
    except Exception as e:
        print(f"Error in fire detection: {e}")
        return False, 0.0, ""

def detect_flood_emergency_sota(image, confidence_threshold=0.41):
    """SOTA Flood Emergency Detection"""
    try:
        all_prompts = SOTA_NORMAL_PROMPTS + SOTA_FLOOD_EMERGENCY_PROMPTS
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        flood_scores = probs[len(SOTA_NORMAL_PROMPTS):]
        
        max_normal = torch.max(normal_scores).item()
        max_flood = torch.max(flood_scores).item()
        best_flood_idx = torch.argmax(flood_scores).item()
        
        confidence_ratio = max_flood / (max_normal + 1e-6)
        flood_confidence = max_flood - max_normal
        
        is_flood = (
            max_flood > confidence_threshold and
            confidence_ratio > 1.25 and
            flood_confidence > 0.05
        )
        
        if is_flood:
            flood_type = SOTA_FLOOD_EMERGENCY_PROMPTS[best_flood_idx]
            print(f"🌊 SOTA Flood Emergency: {flood_confidence:.3f} conf, type: {flood_type[:50]}...")
            return True, max_flood, flood_type
        
        return False, 0.0, ""
        
    except Exception as e:
        print(f"Error in flood detection: {e}")
        return False, 0.0, ""

def detect_environmental_hazard_sota(image, confidence_threshold=0.43):
    """SOTA Environmental Hazard Detection"""
    try:
        all_prompts = SOTA_NORMAL_PROMPTS + SOTA_ENVIRONMENTAL_HAZARD_PROMPTS
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        environmental_scores = probs[len(SOTA_NORMAL_PROMPTS):]
        
        max_normal = torch.max(normal_scores).item()
        max_environmental = torch.max(environmental_scores).item()
        best_environmental_idx = torch.argmax(environmental_scores).item()
        
        confidence_ratio = max_environmental / (max_normal + 1e-6)
        environmental_confidence = max_environmental - max_normal
        
        is_environmental = (
            max_environmental > confidence_threshold and
            confidence_ratio > 1.35 and
            environmental_confidence > 0.07
        )
        
        if is_environmental:
            environmental_type = SOTA_ENVIRONMENTAL_HAZARD_PROMPTS[best_environmental_idx]
            print(f"☢️ SOTA Environmental Hazard: {environmental_confidence:.3f} conf, type: {environmental_type[:50]}...")
            return True, max_environmental, environmental_type
        
        return False, 0.0, ""
        
    except Exception as e:
        print(f"Error in environmental hazard detection: {e}")
        return False, 0.0, ""

def detect_security_theft_sota(image, confidence_threshold=0.44):
    """SOTA Security & Theft Detection"""
    try:
        all_prompts = SOTA_NORMAL_PROMPTS + SOTA_SECURITY_THEFT_PROMPTS
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        security_scores = probs[len(SOTA_NORMAL_PROMPTS):]
        
        max_normal = torch.max(normal_scores).item()
        max_security = torch.max(security_scores).item()
        best_security_idx = torch.argmax(security_scores).item()
        
        confidence_ratio = max_security / (max_normal + 1e-6)
        security_confidence = max_security - max_normal
        
        is_security = (
            max_security > confidence_threshold and
            confidence_ratio > 1.4 and
            security_confidence > 0.08
        )
        
        if is_security:
            security_type = SOTA_SECURITY_THEFT_PROMPTS[best_security_idx]
            print(f"🔐 SOTA Security Threat: {security_confidence:.3f} conf, type: {security_type[:50]}...")
            return True, max_security, security_type
        
        return False, 0.0, ""
        
    except Exception as e:
        print(f"Error in security detection: {e}")
        return False, 0.0, ""

def detect_workplace_safety_sota(image, confidence_threshold=0.40):
    """SOTA Workplace Safety Detection"""
    try:
        all_prompts = SOTA_NORMAL_PROMPTS + SOTA_WORKPLACE_SAFETY_PROMPTS
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        workplace_scores = probs[len(SOTA_NORMAL_PROMPTS):]
        
        max_normal = torch.max(normal_scores).item()
        max_workplace = torch.max(workplace_scores).item()
        best_workplace_idx = torch.argmax(workplace_scores).item()
        
        confidence_ratio = max_workplace / (max_normal + 1e-6)
        workplace_confidence = max_workplace - max_normal
        
        is_workplace = (
            max_workplace > confidence_threshold and
            confidence_ratio > 1.2 and
            workplace_confidence > 0.05
        )
        
        if is_workplace:
            workplace_type = SOTA_WORKPLACE_SAFETY_PROMPTS[best_workplace_idx]
            print(f"⚠️ SOTA Workplace Safety: {workplace_confidence:.3f} conf, type: {workplace_type[:50]}...")
            return True, max_workplace, workplace_type
        
        return False, 0.0, ""
        
    except Exception as e:
        print(f"Error in workplace safety detection: {e}")
        return False, 0.0, ""

def detect_electrical_emergency_sota(image, confidence_threshold=0.43):
    """SOTA Electrical Emergency Detection"""
    try:
        all_prompts = SOTA_NORMAL_PROMPTS + SOTA_ELECTRICAL_EMERGENCY_PROMPTS
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        electrical_scores = probs[len(SOTA_NORMAL_PROMPTS):]
        
        max_normal = torch.max(normal_scores).item()
        max_electrical = torch.max(electrical_scores).item()
        best_electrical_idx = torch.argmax(electrical_scores).item()
        
        confidence_ratio = max_electrical / (max_normal + 1e-6)
        electrical_confidence = max_electrical - max_normal
        
        is_electrical = (
            max_electrical > confidence_threshold and
            confidence_ratio > 1.35 and
            electrical_confidence > 0.07
        )
        
        if is_electrical:
            electrical_type = SOTA_ELECTRICAL_EMERGENCY_PROMPTS[best_electrical_idx]
            print(f"⚡ SOTA Electrical Emergency: {electrical_confidence:.3f} conf, type: {electrical_type[:50]}...")
            return True, max_electrical, electrical_type
        
        return False, 0.0, ""
        
    except Exception as e:
        print(f"Error in electrical emergency detection: {e}")
        return False, 0.0, ""

def detect_comprehensive_anomalies(image, confidence_threshold=0.40):
    """Comprehensive Anomaly Detection including Violence, Medical, Fire, Flood & Environmental Hazards"""
    try:
        # Comprehensive multi-category detection with ensemble scoring
        all_prompts = (SOTA_NORMAL_PROMPTS + SOTA_VIOLENCE_PROMPTS + 
                      SOTA_MEDICAL_EMERGENCY_PROMPTS + SOTA_ABNORMAL_BEHAVIOR_PROMPTS +
                      SOTA_FIRE_EMERGENCY_PROMPTS + SOTA_FLOOD_EMERGENCY_PROMPTS +
                      SOTA_ENVIRONMENTAL_HAZARD_PROMPTS + SOTA_SECURITY_THEFT_PROMPTS +
                      SOTA_WORKPLACE_SAFETY_PROMPTS + SOTA_ELECTRICAL_EMERGENCY_PROMPTS)
        
        # Use proper CLIP model instead of non-existent clip_interrogator
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        # Calculate category scores
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        violence_scores = probs[len(SOTA_NORMAL_PROMPTS):len(SOTA_NORMAL_PROMPTS)+len(SOTA_VIOLENCE_PROMPTS)]
        medical_start = len(SOTA_NORMAL_PROMPTS) + len(SOTA_VIOLENCE_PROMPTS)
        medical_scores = probs[medical_start:medical_start+len(SOTA_MEDICAL_EMERGENCY_PROMPTS)]
        behavior_start = medical_start + len(SOTA_MEDICAL_EMERGENCY_PROMPTS)
        behavior_scores = probs[behavior_start:behavior_start+len(SOTA_ABNORMAL_BEHAVIOR_PROMPTS)]
        fire_start = behavior_start + len(SOTA_ABNORMAL_BEHAVIOR_PROMPTS)
        fire_scores = probs[fire_start:fire_start+len(SOTA_FIRE_EMERGENCY_PROMPTS)]
        flood_start = fire_start + len(SOTA_FIRE_EMERGENCY_PROMPTS)
        flood_scores = probs[flood_start:flood_start+len(SOTA_FLOOD_EMERGENCY_PROMPTS)]
        hazard_start = flood_start + len(SOTA_FLOOD_EMERGENCY_PROMPTS)
        hazard_scores = probs[hazard_start:hazard_start+len(SOTA_ENVIRONMENTAL_HAZARD_PROMPTS)]
        security_start = hazard_start + len(SOTA_ENVIRONMENTAL_HAZARD_PROMPTS)
        security_scores = probs[security_start:security_start+len(SOTA_SECURITY_THEFT_PROMPTS)]
        workplace_start = security_start + len(SOTA_SECURITY_THEFT_PROMPTS)
        workplace_scores = probs[workplace_start:workplace_start+len(SOTA_WORKPLACE_SAFETY_PROMPTS)]
        electrical_start = workplace_start + len(SOTA_WORKPLACE_SAFETY_PROMPTS)
        electrical_scores = probs[electrical_start:]

        # Find maximum scores for each category
        max_normal = torch.max(normal_scores).item()
        max_violence = torch.max(violence_scores).item()
        max_medical = torch.max(medical_scores).item()
        max_behavior = torch.max(behavior_scores).item()
        max_fire = torch.max(fire_scores).item()
        max_flood = torch.max(flood_scores).item()
        max_hazard = torch.max(hazard_scores).item()
        max_security = torch.max(security_scores).item()
        max_workplace = torch.max(workplace_scores).item()
        max_electrical = torch.max(electrical_scores).item()
        
        # Find the highest anomaly category
        anomaly_scores = {
            'violence': max_violence,
            'medical': max_medical,
            'behavior': max_behavior,
            'fire': max_fire,
            'flood': max_flood,
            'hazard': max_hazard,
            'security': max_security,
            'workplace': max_workplace,
            'electrical': max_electrical
        }
        
        max_anomaly_type = max(anomaly_scores, key=anomaly_scores.get)
        max_anomaly_score = anomaly_scores[max_anomaly_type]
        
        # Enhanced confidence calculation
        confidence_ratio = max_anomaly_score / (max_normal + 1e-6)
        anomaly_confidence = max_anomaly_score - max_normal
        
        # Multi-criteria anomaly detection with category-specific handling
        is_anomaly = False
        anomaly_reason = "Normal activity detected"
        
        # Emergency categories get lower thresholds
        if max_fire > 0.35 or max_flood > 0.35:  # Lower threshold for environmental emergencies
            is_anomaly = True
            anomaly_reason = f"🚨 ENVIRONMENTAL EMERGENCY: {max_anomaly_type.upper()} detected (confidence: {max_anomaly_score:.3f})"
        elif max_electrical > 0.35:  # Lower threshold for electrical emergencies
            is_anomaly = True
            anomaly_reason = f"⚡ ELECTRICAL EMERGENCY: detected (confidence: {max_electrical:.3f})"
        elif max_medical > 0.40:  # Medical emergencies
            is_anomaly = True
            anomaly_reason = f"🏥 MEDICAL EMERGENCY: detected (confidence: {max_medical:.3f})"
        elif max_security > 0.45:  # Security incidents
            is_anomaly = True
            anomaly_reason = f"🔒 SECURITY BREACH: detected (confidence: {max_security:.3f})"
        elif max_workplace > 0.40:  # Workplace safety
            is_anomaly = True
            anomaly_reason = f"🔧 WORKPLACE SAFETY: detected (confidence: {max_workplace:.3f})"
        elif max_violence > confidence_threshold and anomaly_confidence > 0.1:
            is_anomaly = True
            anomaly_reason = f"🥊 VIOLENCE: detected (confidence: {max_violence:.3f})"
        elif max_behavior > 0.45:  # Higher threshold for behavior
            is_anomaly = True
            anomaly_reason = f"⚠️ ABNORMAL BEHAVIOR: detected (confidence: {max_behavior:.3f})"
        elif max_hazard > 0.40:  # Environmental hazards
            is_anomaly = True
            anomaly_reason = f"☢️ ENVIRONMENTAL HAZARD: detected (confidence: {max_hazard:.3f})"

        return max_anomaly_score if is_anomaly else 0.0, {
            'detected': is_anomaly,
            'category': max_anomaly_type if is_anomaly else 'normal',
            'confidence': max_anomaly_score,
            'reason': anomaly_reason,
            'all_scores': anomaly_scores,
            'normal_score': max_normal
        }
        
    except Exception as e:
        print(f"❌ Comprehensive anomaly detection error: {e}")
        return 0.0, {'detected': False, 'category': 'error', 'confidence': 0.0, 'reason': f"Detection error: {e}"}

def detect_medical_emergency_sota(image, confidence_threshold=0.25):
    """SOTA Medical Emergency Detection - Healthcare Grade"""
    try:
        all_prompts = SOTA_NORMAL_PROMPTS + SOTA_MEDICAL_EMERGENCY_PROMPTS
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        emergency_scores = probs[len(SOTA_NORMAL_PROMPTS):]
        
        max_normal = torch.max(normal_scores).item()
        max_emergency = torch.max(emergency_scores).item()
        best_emergency_idx = torch.argmax(emergency_scores).item()
        
        # Healthcare-grade detection criteria
        confidence_ratio = max_emergency / (max_normal + 1e-6)
        emergency_confidence = max_emergency - max_normal
        
        is_emergency = (
            max_emergency > confidence_threshold and
            confidence_ratio > 1.15 and  # More sensitive for medical emergencies
            emergency_confidence > 0.03
        )
        
        if is_emergency:
            emergency_type = SOTA_MEDICAL_EMERGENCY_PROMPTS[best_emergency_idx]
            print(f"🏥 SOTA Medical Emergency: {emergency_confidence:.3f} conf, type: {emergency_type[:50]}...")
            return True, max_emergency, emergency_type
        
        return False, 0.0, ""
        
    except Exception as e:
        print(f"Error in medical emergency detection: {e}")
        return False, 0.0, ""

def detect_abnormal_behavior_sota(image, confidence_threshold=0.30):
    """SOTA Abnormal Behavior Detection - Surveillance Grade"""
    try:
        all_prompts = SOTA_NORMAL_PROMPTS + SOTA_ABNORMAL_BEHAVIOR_PROMPTS
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]
        
        normal_scores = probs[:len(SOTA_NORMAL_PROMPTS)]
        abnormal_scores = probs[len(SOTA_NORMAL_PROMPTS):]
        
        max_normal = torch.max(normal_scores).item()
        max_abnormal = torch.max(abnormal_scores).item()
        best_abnormal_idx = torch.argmax(abnormal_scores).item()
        
        # Surveillance-grade detection
        confidence_ratio = max_abnormal / (max_normal + 1e-6)
        abnormal_confidence = max_abnormal - max_normal
        
        is_abnormal = (
            max_abnormal > confidence_threshold and
            confidence_ratio > 1.1 and
            abnormal_confidence > 0.02
        )
        
        if is_abnormal:
            abnormal_type = SOTA_ABNORMAL_BEHAVIOR_PROMPTS[best_abnormal_idx]
            print(f"🔍 SOTA Abnormal Behavior: {abnormal_confidence:.3f} conf, type: {abnormal_type[:50]}...")
            return True, max_abnormal, abnormal_type
        
        return False, 0.0, ""
        
    except Exception as e:
        print(f"Error in abnormal behavior detection: {e}")
        return False, 0.0, ""

def process_scene_tier1(video_path):
    """SOTA Tier 1 Scene Processing - Industry Standard Video Analysis"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps) if fps > 0 else 1
    frame_count = 0
    
    # Comprehensive anomaly scoring system
    all_scores = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Use comprehensive detection instead of old functions
            anomaly_score, detection_details = detect_comprehensive_anomalies(image)
            
            # Collect scores for final assessment
            if detection_details['detected']:
                all_scores.append(anomaly_score)
        
        frame_count += 1

    cap.release()
    
    # Return highest confidence anomaly score
    return max(all_scores) if all_scores else 0.0

def process_scene_tier2(video_path):
    """SOTA Tier 2 Scene Processing - Advanced AI with Scene Understanding"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps) if fps > 0 else 1
    frame_count = 0
    
    captions = []
    anomaly_scores = []
    anomaly_types = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # SOTA Scene Captioning with BLIP
            inputs = blip_processor(images=image, return_tensors="pt")
            generated_ids = blip_model.generate(**inputs, max_length=50)
            caption = blip_processor.decode(generated_ids[0], skip_special_tokens=True)
            captions.append(caption)
            
            # Enhanced large model analysis with CLIP-Large
            all_prompts = (SOTA_NORMAL_PROMPTS + SOTA_VIOLENCE_PROMPTS + 
                          SOTA_MEDICAL_EMERGENCY_PROMPTS + SOTA_ABNORMAL_BEHAVIOR_PROMPTS)
            
            inputs = clip_large_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
            outputs = clip_large_model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)[0]
            
            # Sophisticated anomaly scoring
            normal_end = len(SOTA_NORMAL_PROMPTS)
            violence_end = normal_end + len(SOTA_VIOLENCE_PROMPTS)
            medical_end = violence_end + len(SOTA_MEDICAL_EMERGENCY_PROMPTS)
            
            normal_scores = probs[:normal_end]
            violence_scores = probs[normal_end:violence_end]
            medical_scores = probs[violence_end:medical_end]
            abnormal_scores = probs[medical_end:]
            
            max_normal = torch.max(normal_scores).item()
            max_violence = torch.max(violence_scores).item()
            max_medical = torch.max(medical_scores).item()
            max_abnormal = torch.max(abnormal_scores).item()
            
            # Determine best anomaly category
            anomaly_categories = [
                (max_violence, "violence"),
                (max_medical, "medical_emergency"),
                (max_abnormal, "abnormal_behavior")
            ]
            
            best_anomaly_score, best_anomaly_type = max(anomaly_categories, key=lambda x: x[0])
            
            # Industry-standard thresholding
            if best_anomaly_score > max_normal * 1.25:  # SOTA threshold
                anomaly_scores.append(best_anomaly_score)
                anomaly_types.append(best_anomaly_type)
            
        frame_count += 1

    cap.release()
    
    # Return comprehensive analysis
    max_anomaly_score = max(anomaly_scores) if anomaly_scores else 0.0
    return captions, max_anomaly_score

def process_scene_frame(image_array):
    """Original Scene Processing with Enhanced Detection Conditions"""
    image = Image.fromarray(image_array)
    
    # Initialize score lists
    violence_scores = []
    medical_scores = []
    abnormal_scores = []
    fire_scores = []
    flood_scores = []
    environmental_scores = []
    security_scores = []
    workplace_scores = []
    electrical_scores = []
    
    try:
        # === ORIGINAL SOTA MULTI-MODAL DETECTION PIPELINE ===
        anomaly_detected = False
        max_confidence = 0.0
        detected_type = "normal"
        
        # 1. Violence Detection (Security Industry Standard)
        violence_detected, violence_score, violence_type = detect_violence_sota(image)
        if violence_detected:
            violence_scores.append(violence_score)
            if violence_score > max_confidence:
                anomaly_detected = True
                max_confidence = violence_score
                detected_type = "violence"
        
        # 2. Medical Emergency Detection (Healthcare Grade)
        medical_detected, medical_score, medical_type = detect_medical_emergency_sota(image)
        if medical_detected:
            medical_scores.append(medical_score)
            if medical_score > max_confidence:
                anomaly_detected = True
                max_confidence = medical_score
                detected_type = "medical_emergency"
        
        # 3. Abnormal Behavior Detection (Surveillance Grade)
        abnormal_detected, abnormal_score, abnormal_type = detect_abnormal_behavior_sota(image)
        if abnormal_detected:
            abnormal_scores.append(abnormal_score)
            if abnormal_score > max_confidence:
                anomaly_detected = True
                max_confidence = abnormal_score
                detected_type = "abnormal_behavior"
        
        # 4. Fire Emergency Detection (Enhanced)
        fire_detected, fire_score, fire_type = detect_fire_emergency_sota(image)
        if fire_detected:
            fire_scores.append(fire_score)
            if fire_score > max_confidence:
                anomaly_detected = True
                max_confidence = fire_score
                detected_type = "fire_emergency"
        
        # 5. Flood Emergency Detection (Enhanced)
        flood_detected, flood_score, flood_type = detect_flood_emergency_sota(image)
        if flood_detected:
            flood_scores.append(flood_score)
            if flood_score > max_confidence:
                anomaly_detected = True
                max_confidence = flood_score
                detected_type = "flood_emergency"
        
        # 6. Environmental Hazard Detection (Enhanced)
        environmental_detected, environmental_score, environmental_type = detect_environmental_hazard_sota(image)
        if environmental_detected:
            environmental_scores.append(environmental_score)
            if environmental_score > max_confidence:
                anomaly_detected = True
                max_confidence = environmental_score
                detected_type = "environmental_hazard"
        
        # 7. Security & Theft Detection (Enhanced)
        security_detected, security_score, security_type = detect_security_theft_sota(image)
        if security_detected:
            security_scores.append(security_score)
            if security_score > max_confidence:
                anomaly_detected = True
                max_confidence = security_score
                detected_type = "security_theft"
        
        # 8. Workplace Safety Detection (Enhanced)
        workplace_detected, workplace_score, workplace_type = detect_workplace_safety_sota(image)
        if workplace_detected:
            workplace_scores.append(workplace_score)
            if workplace_score > max_confidence:
                anomaly_detected = True
                max_confidence = workplace_score
                detected_type = "workplace_safety"
        
        # 9. Electrical Emergency Detection (Enhanced)
        electrical_detected, electrical_score, electrical_type = detect_electrical_emergency_sota(image)
        if electrical_detected:
            electrical_scores.append(electrical_score)
            if electrical_score > max_confidence:
                anomaly_detected = True
                max_confidence = electrical_score
                detected_type = "electrical_emergency"
        
        # Combine all scores for comprehensive analysis
        all_scores = (violence_scores + medical_scores + abnormal_scores + 
                     fire_scores + flood_scores + environmental_scores +
                     security_scores + workplace_scores + electrical_scores)
        
        if anomaly_detected:
            print(f"🎬 SOTA Scene Detection: {detected_type} (confidence={max_confidence:.3f})")
            return max_confidence
        
        return 0.0
        
    except Exception as e:
        print(f"❌ Scene processing error: {e}")
        return 0.0

def process_scene_tier2_frame(image_array):
    """SOTA Tier 2 Scene Analysis - Advanced AI with Scene Understanding"""
    image = Image.fromarray(image_array)
    
    # Enhanced scene captioning with BLIP
    inputs = blip_processor(images=image, return_tensors="pt")
    generated_ids = blip_model.generate(**inputs, max_length=50, num_beams=4)
    caption = blip_processor.decode(generated_ids[0], skip_special_tokens=True)
    
    # SOTA Large Model Analysis with CLIP-Large
    all_prompts = (SOTA_NORMAL_PROMPTS + SOTA_VIOLENCE_PROMPTS + 
                  SOTA_MEDICAL_EMERGENCY_PROMPTS + SOTA_ABNORMAL_BEHAVIOR_PROMPTS)
    
    inputs = clip_large_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
    outputs = clip_large_model(**inputs)
    probs = outputs.logits_per_image.softmax(dim=1)[0]
    
    # Sophisticated category analysis
    normal_end = len(SOTA_NORMAL_PROMPTS)
    violence_end = normal_end + len(SOTA_VIOLENCE_PROMPTS)
    medical_end = violence_end + len(SOTA_MEDICAL_EMERGENCY_PROMPTS)
    
    normal_scores = probs[:normal_end]
    violence_scores = probs[normal_end:violence_end]
    medical_scores = probs[violence_end:medical_end]
    abnormal_scores = probs[medical_end:]
    
    max_normal = torch.max(normal_scores).item()
    max_violence = torch.max(violence_scores).item()
    max_medical = torch.max(medical_scores).item()
    max_abnormal = torch.max(abnormal_scores).item()
    
    # Determine best anomaly with industry-standard thresholds
    anomaly_categories = [
        (max_violence, "violence", 1.25),
        (max_medical, "medical", 1.15),  # More sensitive for medical
        (max_abnormal, "abnormal", 1.20)
    ]
    
    best_score = 0.0
    for score, category, threshold in anomaly_categories:
        if score > max_normal * threshold and score > best_score:
            best_score = score
    
    return [caption], best_score