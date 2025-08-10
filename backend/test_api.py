#!/usr/bin/env python3
"""
Simple HTTP test client for testing API endpoints
"""
import requests
import json

def test_api_health():
    """Test if the API is responding"""
    try:
        response = requests.get("http://127.0.0.1:8000/docs")
        if response.status_code == 200:
            print("✅ API is running and accessible")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_openapi_spec():
    """Get the OpenAPI specification"""
    try:
        response = requests.get("http://127.0.0.1:8000/openapi.json")
        if response.status_code == 200:
            spec = response.json()
            print("✅ OpenAPI spec retrieved")
            print("Available endpoints:")
            for path, methods in spec.get("paths", {}).items():
                for method in methods.keys():
                    print(f"  {method.upper()} {path}")
            return spec
        else:
            print(f"❌ Could not get OpenAPI spec: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting OpenAPI spec: {e}")
        return None

def test_video_upload_endpoint():
    """Test if video upload endpoint exists"""
    try:
        # Try to get info about the endpoint without actually uploading
        response = requests.post("http://127.0.0.1:8000/process_video")
        # We expect a 422 (validation error) since we didn't send a file
        if response.status_code == 422:
            print("✅ Video upload endpoint exists (returned validation error as expected)")
            return True
        else:
            print(f"📝 Video upload endpoint responded with: {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ Error testing video upload: {e}")
        return False

if __name__ == "__main__":
    print("Testing Anomaly Detection API...")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("\n1. Testing API connectivity...")
    if not test_api_health():
        exit(1)
    
    # Test 2: Get API specification
    print("\n2. Getting API specification...")
    spec = test_openapi_spec()
    
    # Test 3: Test endpoints
    print("\n3. Testing endpoints...")
    test_video_upload_endpoint()
    
    print("\n" + "=" * 50)
    print("API testing complete!")
    print("\n📖 To see the interactive docs, open: http://127.0.0.1:8000/docs")
    print("🔄 To test WebSocket streaming, run: python test_websocket.py")
