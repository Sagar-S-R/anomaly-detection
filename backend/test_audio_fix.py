#!/usr/bin/env python3
"""
Test script to verify audio processing fixes
"""

import sys
import os
from utils.audio_processing import AudioStream
import time

def test_audio_stream():
    print("Testing AudioStream...")
    
    # Test audio stream creation
    try:
        audio_stream = AudioStream()
        print("✅ AudioStream created successfully")
    except Exception as e:
        print(f"❌ AudioStream creation failed: {e}")
        return False
    
    # Test audio stream start
    try:
        audio_stream.start()
        print("✅ AudioStream started successfully")
        time.sleep(2)  # Let it capture some audio
    except Exception as e:
        print(f"❌ AudioStream start failed: {e}")
        return False
    
    # Test getting audio chunk
    try:
        chunk_path = audio_stream.get_chunk()
        if chunk_path:
            print(f"✅ Audio chunk created: {chunk_path}")
            if os.path.exists(chunk_path):
                size = os.path.getsize(chunk_path)
                print(f"✅ Audio file exists with size: {size} bytes")
                # Clean up test file
                os.remove(chunk_path)
            else:
                print("❌ Audio file path returned but file doesn't exist")
        else:
            print("⚠️  No audio chunk available yet (might need more capture time)")
    except Exception as e:
        print(f"❌ Audio chunk creation failed: {e}")
    
    # Test audio stream stop
    try:
        audio_stream.stop()
        print("✅ AudioStream stopped successfully")
    except Exception as e:
        print(f"❌ AudioStream stop failed: {e}")
    
    return True

if __name__ == "__main__":
    print("🎤 Testing Audio Processing Fixes")
    print("=" * 40)
    
    success = test_audio_stream()
    
    if success:
        print("\n🎉 Audio testing completed!")
        print("Your audio processing should now work better.")
    else:
        print("\n❌ Audio testing failed.")
        print("There may still be issues with audio processing.")
