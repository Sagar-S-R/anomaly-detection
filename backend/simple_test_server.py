#!/usr/bin/env python3
"""
Simple WebSocket test server without audio processing
"""
from fastapi import FastAPI, WebSocket
import cv2
import asyncio
import json

app = FastAPI()

@app.websocket("/test_video")
async def test_video_stream(websocket: WebSocket):
    """Simple video streaming test without audio"""
    await websocket.accept()
    
    print("WebSocket connected, testing camera...")
    
    # Test camera access
    video_cap = cv2.VideoCapture(0)
    if not video_cap.isOpened():
        error_msg = {"error": "Could not open video stream", "camera_index": 0}
        await websocket.send_json(error_msg)
        print("❌ Camera access failed")
        return
    
    print("✅ Camera opened successfully")
    
    try:
        frame_count = 0
        while True:
            ret, frame = video_cap.read()
            if not ret:
                await websocket.send_json({"error": "Could not read frame"})
                break
            
            frame_count += 1
            
            # Send basic frame info (without actual frame data)
            result = {
                "status": "Normal",
                "frame_id": frame_count,
                "frame_size": f"{frame.shape[1]}x{frame.shape[0]}",
                "message": f"Processing frame {frame_count}"
            }
            
            await websocket.send_json(result)
            
            # Simulate some processing time
            await asyncio.sleep(1.0)  # 1 FPS
            
    except Exception as e:
        await websocket.send_json({"error": f"Processing error: {str(e)}"})
        print(f"❌ Error: {e}")
    finally:
        video_cap.release()
        print("Camera released")

if __name__ == "__main__":
    import uvicorn
    print("Starting simple test server...")
    print("WebSocket endpoint: ws://127.0.0.1:8001/test_video")
    uvicorn.run(app, host="127.0.0.1", port=8001)
