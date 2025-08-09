from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from tier1.tier1_pipeline import run_tier1_continuous
import os
from tempfile import NamedTemporaryFile
import cv2

app = FastAPI()

@app.websocket("/stream_video")
async def stream_video(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)  # Use 0 for default camera; replace with RTSP/HTTP URL for stream
    if not cap.isOpened():
        await websocket.send_json({"error": "Could not open video stream"})
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Simulate continuous Tier 1 (replace with actual streaming logic)
            result = run_tier1_continuous(frame)  # Placeholder; update tier1_pipeline.py
            await websocket.send_json(result)
    except WebSocketDisconnect:
        cap.release()
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        cap.release()

@app.post("/process_video")
async def process_video(file: UploadFile = File(...)):
    # Keep batch processing for compatibility
    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        contents = await file.read()
        temp_video.write(contents)
        video_path = temp_video.name

    tier1_result = run_tier1(video_path)  # Original batch function

    if tier1_result["status"] == "Normal":
        os.remove(video_path)
        return {
            "frame_id": "N/A",
            "visual_score": 0.0,
            "audio_score": 0.0,
            "text_alignment_score": 0.0,
            "multimodal_agreement": 0.0,
            "reasoning_summary": "No anomaly detected. Normal activity.",
            "threat_severity_index": 0.0
        }

    tier2_result = run_tier2(video_path, tier1_result)
    if tier2_result["threat_severity_index"] > 0.5:
        tier2_result["log"] = {
            "snapshot": "path/to/anomaly_snapshot.jpg",
            "reasoning": tier2_result["reasoning_summary"],
            "timestamps": tier2_result.get("timestamps", [])
        }
        print("Alert: Anomaly Detected!")

    os.remove(video_path)
    return tier2_result