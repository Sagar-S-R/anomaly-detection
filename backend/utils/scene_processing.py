import cv2
from transformers import AutoProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

clip_processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

clip_large_processor = AutoProcessor.from_pretrained("openai/clip-vit-large-patch14")
clip_large_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")

blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def process_scene_tier1(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps) if fps > 0 else 1
    frame_count = 0
    anomaly_probs = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # Comprehensive text prompts including aggressive behaviors
            texts = [
                "person sitting normally in chair or standing upright",
                "person working at desk or normal daily activity", 
                "person walking or moving normally",
                "person fallen on floor unconscious or injured",
                "person crawling on ground in distress",
                "person punching or fighting aggressively",
                "person making threatening gestures or violent movements"
            ]
            inputs = clip_processor(text=texts, images=image, return_tensors="pt", padding=True)
            outputs = clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)[0]
            
            # Normal activities: indices 0, 1, 2
            # Anomaly activities: indices 3, 4, 5, 6
            normal_prob = max(probs[0], probs[1], probs[2])  # Max of normal activities
            anomaly_prob = max(probs[3], probs[4], probs[5], probs[6])  # Max of anomaly activities
            
            # Add to anomaly_probs if anomaly exceeds normal by reasonable margin
            if anomaly_prob > normal_prob * 1.3:  # Original working threshold
                anomaly_probs.append(anomaly_prob.item())
            else:
                anomaly_probs.append(0.0)
        frame_count += 1

    cap.release()
    return max(anomaly_probs) if anomaly_probs else 0.0

def process_scene_tier2(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps) if fps > 0 else 1
    frame_count = 0
    captions = []
    anomaly_probs = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # BLIP Captioning
            inputs = blip_processor(images=image, return_tensors="pt")
            generated_ids = blip_model.generate(**inputs)
            caption = blip_processor.decode(generated_ids[0], skip_special_tokens=True)
            captions.append(caption)
            
            # CLIP ViT-L/14 for anomaly prob with comprehensive prompts
            texts = [
                "person sitting normally in chair or standing upright",
                "person working at desk or normal daily activity", 
                "person walking or moving normally",
                "person fallen on floor unconscious or injured",
                "person crawling on ground in distress",
                "person punching or fighting aggressively",
                "person making threatening gestures or violent movements"
            ]
            inputs = clip_large_processor(text=texts, images=image, return_tensors="pt", padding=True)
            outputs = clip_large_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)[0]
            
            # Normal activities: indices 0, 1, 2
            # Anomaly activities: indices 3, 4, 5, 6
            normal_prob = max(probs[0], probs[1], probs[2])  # Max of normal activities
            anomaly_prob = max(probs[3], probs[4], probs[5], probs[6])  # Max of anomaly activities
            
            # Add to anomaly_probs if anomaly exceeds normal by reasonable margin
            if anomaly_prob > normal_prob * 1.3:  # Original working threshold
                anomaly_probs.append(anomaly_prob.item())
            else:
                anomaly_probs.append(0.0)
        frame_count += 1

    cap.release()
    return captions, max(anomaly_probs) if anomaly_probs else 0.0

# Existing code...
def process_scene_frame(image_array):
    image = Image.fromarray(image_array)
    # Comprehensive text prompts including aggressive behaviors
    texts = [
        "person sitting normally in chair or standing upright",
        "person working at desk or normal daily activity", 
        "person walking or moving normally",
        "person fallen on floor unconscious or injured",
        "person crawling on ground in distress",
        "person punching or fighting aggressively",
        "person making threatening gestures or violent movements"
    ]
    inputs = clip_processor(text=texts, images=image, return_tensors="pt", padding=True)
    outputs = clip_model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)[0]
    
    # Normal activities: indices 0, 1, 2
    # Anomaly activities: indices 3, 4, 5, 6
    normal_prob = max(probs[0], probs[1], probs[2])  # Max of normal activities
    anomaly_prob = max(probs[3], probs[4], probs[5], probs[6])  # Max of anomaly activities
    
    # Return the anomaly probability if it exceeds normal probability by a very small margin
    # Much more sensitive threshold to catch subtle visual anomalies
    result = anomaly_prob.item() if anomaly_prob > normal_prob * 0.8 else 0.0  # Very sensitive: anomaly just needs to be 80% of normal
    
    # Debug logging to see what's happening
    print(f"🎬 Scene Debug: normal_prob={normal_prob:.3f}, anomaly_prob={anomaly_prob:.3f}, threshold=0.8x, result={result:.3f}")
    
    return result

def process_scene_tier2_frame(image_array):
    image = Image.fromarray(image_array)
    inputs = blip_processor(images=image, return_tensors="pt")
    generated_ids = blip_model.generate(**inputs)
    caption = blip_processor.decode(generated_ids[0], skip_special_tokens=True)
    
    # Comprehensive text prompts for tier 2 analysis including aggressive behaviors
    texts = [
        "person sitting normally in chair or standing upright",
        "person working at desk or normal daily activity", 
        "person walking or moving normally",
        "person fallen on floor unconscious or injured",
        "person crawling on ground in distress",
        "person punching or fighting aggressively",
        "person making threatening gestures or violent movements"
    ]
    inputs = clip_large_processor(text=texts, images=image, return_tensors="pt", padding=True)
    outputs = clip_large_model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)[0]
    
    # Normal activities: indices 0, 1, 2
    # Anomaly activities: indices 3, 4, 5, 6
    normal_prob = max(probs[0], probs[1], probs[2])  # Max of normal activities
    anomaly_prob = max(probs[3], probs[4], probs[5], probs[6])  # Max of anomaly activities
    
    # Return anomaly probability if it exceeds normal by reasonable margin
    anomaly_max = anomaly_prob.item() if anomaly_prob > normal_prob * 1.3 else 0.0
    return [caption], anomaly_max