#!/usr/bin/env python3
"""Quick import test to validate all dependencies work before Docker build"""

import sys

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing critical imports...")
    
    # Test basic imports
    try:
        import fastapi
        print("✅ FastAPI")
    except ImportError as e:
        print(f"❌ FastAPI: {e}")
        return False
    
    # Test AI/ML imports
    try:
        import torch
        print("✅ PyTorch")
    except ImportError as e:
        print(f"❌ PyTorch: {e}")
        return False
    
    try:
        from transformers import CLIPModel
        print("✅ Transformers/CLIP")
    except ImportError as e:
        print(f"❌ Transformers: {e}")
        return False
    
    try:
        import whisper
        print("✅ Whisper")
    except ImportError as e:
        print(f"❌ Whisper: {e}")
        return False
    
    # Test computer vision
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe")
    except ImportError as e:
        print(f"❌ MediaPipe: {e}")
        return False
    
    # Test video processing
    try:
        from moviepy.editor import VideoFileClip
        print("✅ MoviePy")
    except ImportError as e:
        print(f"⚠️  MoviePy: {e} (fallback available)")
    
    # Test audio processing
    try:
        import pyaudio
        print("✅ PyAudio")
    except ImportError as e:
        print(f"❌ PyAudio: {e}")
        return False
    
    try:
        from pydub import AudioSegment
        print("✅ Pydub")
    except ImportError as e:
        print(f"❌ Pydub: {e}")
        return False
    
    # Test the actual application imports
    try:
        from tier1.tier1_pipeline import run_tier1_continuous
        print("✅ Tier1 Pipeline")
    except ImportError as e:
        print(f"❌ Tier1 Pipeline: {e}")
        return False
    
    try:
        from utils.audio_processing import chunk_and_transcribe_tiny, extract_audio
        print("✅ Audio Processing Utils")
    except ImportError as e:
        print(f"❌ Audio Processing: {e}")
        return False
    
    print("\n🎉 All critical imports successful!")
    return True

if __name__ == "__main__":
    success = test_imports()
    if not success:
        print("\n❌ Import test failed! Fix issues before building Docker image.")
        sys.exit(1)
    else:
        print("\n✅ Import test passed! Ready for Docker build.")
        sys.exit(0)
