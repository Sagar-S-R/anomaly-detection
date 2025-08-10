#!/usr/bin/env python3
"""
Simple test to verify your anomaly detection setup
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe imported successfully")
    except ImportError as e:
        print(f"❌ MediaPipe import failed: {e}")
        return False
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import websockets
        print("✅ WebSockets imported successfully")
    except ImportError as e:
        print(f"❌ WebSockets import failed: {e}")
        return False
    
    return True

def test_app_structure():
    """Test if app structure is correct"""
    print("\nTesting app structure...")
    
    required_files = [
        'app.py',
        'tier1/tier1_pipeline.py',
        'tier2/tier2_pipeline.py',
        'utils/audio_processing.py',
        'utils/pose_processing.py',
        'utils/fusion_logic.py',
        'utils/scene_processing.py'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def test_app_import():
    """Test if the main app can be imported"""
    print("\nTesting app import...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        import app
        print("✅ App imported successfully")
        
        # Check if the FastAPI app exists
        if hasattr(app, 'app'):
            print("✅ FastAPI app instance found")
            return True
        else:
            print("❌ FastAPI app instance not found")
            return False
            
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def main():
    print("Anomaly Detection API Setup Test")
    print("=" * 40)
    
    all_tests_passed = True
    
    # Test 1: Imports
    if not test_imports():
        all_tests_passed = False
    
    # Test 2: File structure
    if not test_app_structure():
        all_tests_passed = False
    
    # Test 3: App import
    if not test_app_import():
        all_tests_passed = False
    
    print("\n" + "=" * 40)
    if all_tests_passed:
        print("🎉 All tests passed! Your setup looks good.")
        print("\nNext steps:")
        print("1. Start the server: venv/bin/python -m uvicorn app:app --reload")
        print("2. Open http://127.0.0.1:8000/docs to see the API docs")
        print("3. Test WebSocket: venv/bin/python test_websocket.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    return all_tests_passed

if __name__ == "__main__":
    exit(0 if main() else 1)
