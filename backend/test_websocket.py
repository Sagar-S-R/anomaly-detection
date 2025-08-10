#!/usr/bin/env python3
"""
WebSocket test client for real-time anomaly detection
"""
import asyncio
import websockets
import json
import cv2
import base64

async def test_websocket_streaming():
    """Test the WebSocket streaming endpoint"""
    uri = "ws://127.0.0.1:8000/stream_video"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket streaming endpoint...")
            
            # Listen for messages from the server
            async for message in websocket:
                try:
                    data = json.loads(message)
                    print(f"Received: {data}")
                    
                    # Check if it's an error
                    if "error" in data:
                        print(f"Error from server: {data['error']}")
                        break
                        
                    # Check if anomaly detected
                    if data.get("status") == "Suspected Anomaly":
                        print("🚨 ANOMALY DETECTED!")
                        
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {message}")
                    
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed")
    except Exception as e:
        print(f"Error connecting to WebSocket: {e}")

if __name__ == "__main__":
    print("Starting WebSocket test...")
    print("Make sure your webcam is connected and the server is running!")
    print("Press Ctrl+C to stop")
    
    try:
        asyncio.run(test_websocket_streaming())
    except KeyboardInterrupt:
        print("\nTest stopped by user")
