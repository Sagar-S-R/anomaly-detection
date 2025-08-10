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
            texts = ["normal activity in a room", "person fallen on the floor", "person crawling on the ground"]
            inputs = clip_processor(text=texts, images=image, return_tensors="pt", padding=True)
            outputs = clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)[0]
            anomaly_prob = max(probs[1], probs[2])
            anomaly_probs.append(anomaly_prob.item())
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
            # CLIP ViT-L/14 for anomaly prob
            texts = ["normal activity in a room", "person fallen on the floor", "person crawling on the ground"]
            inputs = clip_large_processor(text=texts, images=image, return_tensors="pt", padding=True)
            outputs = clip_large_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)[0]
            anomaly_prob = max(probs[1], probs[2])
            anomaly_probs.append(anomaly_prob.item())
        frame_count += 1

    cap.release()
    return captions, max(anomaly_probs) if anomaly_probs else 0.0

# Existing code...
def process_scene_frame(image_array):
    image = Image.fromarray(image_array)
    texts = ["normal activity in a room", "person fallen on the floor", "person crawling on the ground"]
    inputs = clip_processor(text=texts, images=image, return_tensors="pt", padding=True)
    outputs = clip_model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)[0]
    return max(probs[1], probs[2]).item()

def process_scene_tier2_frame(image_array):
    image = Image.fromarray(image_array)
    inputs = blip_processor(images=image, return_tensors="pt")
    generated_ids = blip_model.generate(**inputs)
    caption = blip_processor.decode(generated_ids[0], skip_special_tokens=True)
    texts = ["normal activity in a room", "person fallen on the floor", "person crawling on the ground"]
    inputs = clip_large_processor(text=texts, images=image, return_tensors="pt", padding=True)
    outputs = clip_large_model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)[0]
    anomaly_max = max(probs[1], probs[2]).item()
    return [caption], anomaly_max