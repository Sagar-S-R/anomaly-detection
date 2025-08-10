#!/usr/bin/env python3
"""
Test camera access and find available video devices
"""
import cv2

def test_camera_access():
    """Test different camera indices to find working cameras"""
    print("Testing camera access...")
    
    working_cameras = []
    
    # Test camera indices 0-5
    for i in range(6):
        print(f"Testing camera index {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                print(f"✅ Camera {i} works! Resolution: {width}x{height}")
                working_cameras.append(i)
            else:
                print(f"❌ Camera {i} opened but couldn't read frame")
        else:
            print(f"❌ Camera {i} couldn't be opened")
        
        cap.release()
    
    return working_cameras

def test_camera_permissions():
    """Check if we have camera permissions"""
    print("\nTesting camera permissions...")
    
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ Camera permissions OK")
                return True
            else:
                print("❌ Camera opened but can't read frames - may be permission issue")
        else:
            print("❌ Can't open camera - likely permission issue")
        cap.release()
    except Exception as e:
        print(f"❌ Camera access error: {e}")
    
    return False

def main():
    print("Camera Diagnostics")
    print("=" * 30)
    
    # Test camera access
    working_cameras = test_camera_access()
    
    # Test permissions
    has_permissions = test_camera_permissions()
    
    print("\n" + "=" * 30)
    print("Results:")
    
    if working_cameras:
        print(f"✅ Found {len(working_cameras)} working camera(s): {working_cameras}")
        print(f"📝 Recommended: Use camera index {working_cameras[0]}")
    else:
        print("❌ No working cameras found")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check if camera is connected")
        print("2. Close other apps using camera (FaceTime, Zoom, etc.)")
        print("3. Grant camera permissions to Terminal:")
        print("   - System Preferences > Security & Privacy > Camera")
        print("   - Add Terminal or Python to allowed apps")
        print("4. Try running: 'sudo python test_camera.py'")
    
    if not has_permissions:
        print("\n⚠️  Camera permission issue detected!")
        print("Please grant camera access in System Preferences")

if __name__ == "__main__":
    main()
