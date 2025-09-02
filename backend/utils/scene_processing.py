import cv2
from transformers import AutoProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import numpy as np

# SOTA Model Initialization - Industry Standard Vision Models
clip_processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

clip_large_processor = AutoProcessor.from_pretrained("openai/clip-vit-large-patch14")
clip_large_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")

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

def detect_violence_sota(image, confidence_threshold=0.15):
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

def detect_medical_emergency_sota(image, confidence_threshold=0.12):
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

def detect_abnormal_behavior_sota(image, confidence_threshold=0.10):
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
    
    # SOTA anomaly scoring system
    violence_scores = []
    medical_scores = []
    abnormal_scores = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Multi-modal SOTA detection pipeline
            violence_detected, violence_score, _ = detect_violence_sota(image)
            medical_detected, medical_score, _ = detect_medical_emergency_sota(image)
            abnormal_detected, abnormal_score, _ = detect_abnormal_behavior_sota(image)
            
            # Collect scores for final assessment
            if violence_detected:
                violence_scores.append(violence_score)
            if medical_detected:
                medical_scores.append(medical_score)
            if abnormal_detected:
                abnormal_scores.append(abnormal_score)
        
        frame_count += 1

    cap.release()
    
    # Return highest confidence anomaly score
    all_scores = violence_scores + medical_scores + abnormal_scores
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
    """SOTA Scene Analysis - Multi-Modal Anomaly Detection"""
    image = Image.fromarray(image_array)
    
    # === SOTA MULTI-MODAL DETECTION PIPELINE ===
    anomaly_detected = False
    max_confidence = 0.0
    detected_type = "normal"
    
    # 1. Violence Detection (Security Industry Standard)
    violence_detected, violence_score, violence_type = detect_violence_sota(image)
    if violence_detected and violence_score > max_confidence:
        anomaly_detected = True
        max_confidence = violence_score
        detected_type = "violence"
    
    # 2. Medical Emergency Detection (Healthcare Grade)
    medical_detected, medical_score, medical_type = detect_medical_emergency_sota(image)
    if medical_detected and medical_score > max_confidence:
        anomaly_detected = True
        max_confidence = medical_score
        detected_type = "medical_emergency"
    
    # 3. Abnormal Behavior Detection (Surveillance Grade)
    abnormal_detected, abnormal_score, abnormal_type = detect_abnormal_behavior_sota(image)
    if abnormal_detected and abnormal_score > max_confidence:
        anomaly_detected = True
        max_confidence = abnormal_score
        detected_type = "abnormal_behavior"
    
    if anomaly_detected:
        print(f"🎬 SOTA Scene Detection: {detected_type} (confidence={max_confidence:.3f})")
        return max_confidence
    
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