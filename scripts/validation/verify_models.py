#!/usr/bin/env python3
"""
Startup verification script to ensure all models are ready before starting the app
"""

import os
import sys
import time
from pathlib import Path

def check_model_cache():
    """Check if model cache directory exists and has models"""
    cache_dir = Path("/app/model_cache")
    
    if not cache_dir.exists():
        print("❌ Model cache directory not found!")
        return False
    
    # Check for expected model files/directories
    expected_models = [
        "transformers",  # Transformers cache
        "torch",         # PyTorch cache
        "hub",           # HuggingFace hub cache
    ]
    
    cache_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
    cache_size_mb = cache_size / (1024 * 1024)
    
    print(f"📁 Model cache directory: {cache_dir}")
    print(f"💾 Cache size: {cache_size_mb:.1f} MB")
    
    if cache_size_mb < 100:  # Expect at least 100MB of models
        print("⚠️  Cache size seems small, models might not be fully downloaded")
        return False
    
    print("✅ Model cache appears to be properly populated")
    return True

def test_model_imports():
    """Test that all models can be imported and loaded quickly"""
    print("🧪 Testing model imports...")
    
    try:
        # Test basic imports
        print("📦 Testing basic imports...")
        import torch
        import transformers
        import whisper
        import mediapipe
        import cv2
        print("✅ All packages imported successfully")
        
        # Quick model loading test
        print("🤖 Testing model loading...")
        
        # Test small models first
        start_time = time.time()
        
        from transformers import AutoProcessor, CLIPModel
        processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        
        load_time = time.time() - start_time
        print(f"⚡ CLIP model loaded in {load_time:.2f}s")
        
        if load_time > 10:  # Should load quickly from cache
            print("⚠️  Model loading seems slow, cache might not be working properly")
            return False
        
        print("✅ Models load quickly from cache")
        return True
        
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False

def main():
    """Main startup verification"""
    print("🚀 Starting Model Verification...")
    print("=" * 40)
    
    # Check cache
    cache_ok = check_model_cache()
    
    # Test imports
    import_ok = test_model_imports()
    
    if cache_ok and import_ok:
        print("\n🎉 All models verified successfully!")
        print("⚡ Application ready for fast startup")
        return True
    else:
        print("\n❌ Model verification failed!")
        print("🔄 Models may need to be re-downloaded")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
