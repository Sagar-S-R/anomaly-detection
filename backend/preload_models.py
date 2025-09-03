#!/usr/bin/env python3
"""
OPTIMIZED Pre-load and cache all AI models for the Anomaly Detection System
This script downloads and initializes all required models during container build
"""

import os
import sys
import time
import torch
from transformers import AutoProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
import whisper
import mediapipe as mp
import cv2
import numpy as np

def setup_model_cache_dir():
    """Setup model cache directory"""
    cache_dir = "/app/model_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    # Set environment variables for model caching
    os.environ['TRANSFORMERS_CACHE'] = cache_dir
    os.environ['TORCH_HOME'] = cache_dir
    os.environ['HF_HOME'] = cache_dir
    os.environ['WHISPER_CACHE_DIR'] = cache_dir
    
    print(f"📁 Model cache directory: {cache_dir}")
    return cache_dir

def download_transformers_models():
    """Download all Transformers models with progress"""
    print("🤖 [1/4] Downloading Transformers models...")
    start_time = time.time()
    
    models_to_download = [
        # CLIP Models for scene analysis
        ("openai/clip-vit-base-patch32", CLIPModel, AutoProcessor),
        ("openai/clip-vit-large-patch14", CLIPModel, AutoProcessor),
        
        # BLIP Model for image captioning
        ("Salesforce/blip-image-captioning-base", BlipForConditionalGeneration, BlipProcessor),
    ]
    
    for model_name, model_class, processor_class in models_to_download:
        try:
            print(f"📥 Downloading {model_name}...")
            
            # Download and cache model
            model = model_class.from_pretrained(model_name)
            processor = processor_class.from_pretrained(model_name)
            
            print(f"✅ {model_name} downloaded and cached successfully")
            
            # Clean up memory
            del model
            del processor
            
        except Exception as e:
            print(f"❌ Error downloading {model_name}: {e}")
            sys.exit(1)

def download_whisper_models():
    """Download Whisper models"""
    print("🎵 Downloading Whisper models...")
    
    whisper_models = ["tiny", "base", "small", "medium", "large"]
    
    for model_name in whisper_models:
        try:
            print(f"📥 Downloading Whisper {model_name}...")
            model = whisper.load_model(model_name)
            print(f"✅ Whisper {model_name} downloaded successfully")
            
            # Clean up memory
            del model
            
        except Exception as e:
            print(f"❌ Error downloading Whisper {model_name}: {e}")
            # Don't exit for whisper errors, continue with other models

def download_mediapipe_models():
    """Initialize MediaPipe models to trigger download"""
    print("🏃 Initializing MediaPipe models...")
    
    try:
        # Pose detection model
        print("📥 Downloading MediaPipe Pose model...")
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        
        # Create a dummy image to trigger model download
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        pose.process(cv2.cvtColor(dummy_image, cv2.COLOR_BGR2RGB))
        
        print("✅ MediaPipe Pose model initialized successfully")
        pose.close()
        
    except Exception as e:
        print(f"❌ Error initializing MediaPipe models: {e}")
        sys.exit(1)

def test_model_loading():
    """Test that all models can be loaded successfully"""
    print("🧪 Testing model loading...")
    
    try:
        # Test CLIP
        print("🔍 Testing CLIP model...")
        clip_processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        print("✅ CLIP model loads successfully")
        
        # Test BLIP
        print("🖼️ Testing BLIP model...")
        blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        print("✅ BLIP model loads successfully")
        
        # Test Whisper
        print("🎵 Testing Whisper model...")
        whisper_model = whisper.load_model("tiny")
        print("✅ Whisper model loads successfully")
        
        # Test MediaPipe
        print("🏃 Testing MediaPipe model...")
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(model_complexity=1)
        pose.close()
        print("✅ MediaPipe model loads successfully")
        
        print("🎉 All models tested successfully!")
        
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        sys.exit(1)

def main():
    """Main function to download all models"""
    print("🚀 Starting AI Model Pre-loading Process")
    print("=" * 50)
    
    # Setup cache directory
    cache_dir = setup_model_cache_dir()
    print(f"📁 Model cache directory: {cache_dir}")
    
    # Download all models
    download_transformers_models()
    download_whisper_models()
    download_mediapipe_models()
    
    # Test model loading
    test_model_loading()
    
    print("\n🎉 All AI models have been pre-loaded successfully!")
    print("📦 Models are cached and ready for immediate use")
    print("⚡ Container startup will be much faster now")
    
    # Display cache size
    try:
        import subprocess
        result = subprocess.run(['du', '-sh', cache_dir], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"💾 Total cache size: {result.stdout.strip().split()[0]}")
    except:
        pass

if __name__ == "__main__":
    main()
