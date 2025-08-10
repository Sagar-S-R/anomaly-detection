#!/usr/bin/env python3
"""
Simplified app for testing WebSocket without complex processing
"""
from fastapi import FastAPI, WebSocket
import cv2
import asyncio
import json

app = FastAPI()

@app.websocket("/stream_video")
async def stream_video(websocket: WebSocket):
    await websocket.accept()
    
    # Try to open camera with retry
    video_cap = None
    for attempt in range(3):
        video_cap = cv2.VideoCapture(0)
        if video_cap.isOpened():
            ret, test_frame = video_cap.read()
            if ret:
                print(f"✅ Camera opened successfully on attempt {attempt + 1}")
                break
            else:
                video_cap.release()
                video_cap = None
        
        if attempt < 2:
            await asyncio.sleep(1)
    
    if video_cap is None or not video_cap.isOpened():
        await websocket.send_json({"error": "Could not open video stream after multiple attempts"})
        return

    try:
        frame_count = 0
        while True:
            ret, frame = video_cap.read()
            if not ret:
                await websocket.send_json({"error": "Could not read frame"})
                break
            
            frame_count += 1
            
            # Simple result without complex processing
            result = {
                "status": "Normal" if frame_count % 10 != 0 else "Suspected Anomaly",
                "frame_id": frame_count,
                "frame_size": f"{frame.shape[1]}x{frame.shape[0]}",
                "message": f"Processing frame {frame_count}",
                "pose_summary": "Pose analysis complete",
                "audio_summary": "Audio analysis complete", 
                "scene_summary": "Scene analysis complete"
            }
            
            # Add tier2 result for anomalies
            if frame_count % 10 == 0:
                result["tier2_result"] = {
                    "threat_severity_index": 0.6,
                    "reasoning_summary": "Test anomaly detected",
                    "visual_score": 0.7,
                    "audio_score": 0.5
                }
            
            await websocket.send_json(result)
            
            # 1 FPS
            await asyncio.sleep(1.0)
            
    except Exception as e:
        await websocket.send_json({"error": f"Processing error: {str(e)}"})
        print(f"❌ Error: {e}")
    finally:
        video_cap.release()
        print("Camera released")

if __name__ == "__main__":
    import uvicorn
    print("Starting simplified test server...")
    print("WebSocket endpoint: ws://127.0.0.1:8001/stream_video")
    uvicorn.run(app, host="127.0.0.1", port=8001)
