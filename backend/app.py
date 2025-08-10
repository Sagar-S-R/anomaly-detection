from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from tier1.tier1_pipeline import run_tier1_continuous
from tier2.tier2_pipeline import run_tier2_continuous
from utils.audio_processing import AudioStream
import cv2
import asyncio
import queue
from threading import Thread

app = FastAPI()

@app.websocket("/stream_video")
async def stream_video(websocket: WebSocket):
    await websocket.accept()
    
    # Try multiple times to open camera
    video_cap = None
    for attempt in range(3):
        video_cap = cv2.VideoCapture(0)
        if video_cap.isOpened():
            # Test if we can actually read a frame
            ret, test_frame = video_cap.read()
            if ret:
                print(f"✅ Camera opened successfully on attempt {attempt + 1}")
                break
            else:
                video_cap.release()
                video_cap = None
        else:
            video_cap = None
        
        if attempt < 2:  # Don't sleep on last attempt
            await asyncio.sleep(1)
    
    if video_cap is None or not video_cap.isOpened():
        await websocket.send_json({"error": "Could not open video stream after multiple attempts"})
        return

    audio_stream = AudioStream()  # Start audio capture
    audio_stream.start()

    frame_queue = queue.Queue(maxsize=10)  # Buffer for frames
    anomaly_detected = False

    def capture_frames():
        while True:
            ret, frame = video_cap.read()
            if not ret:
                break
            if not frame_queue.full():
                frame_queue.put(frame)

    frame_thread = Thread(target=capture_frames)
    frame_thread.start()

    try:
        fps = video_cap.get(cv2.CAP_PROP_FPS) or 30
        frame_interval = int(fps)  # For 1 FPS
        frame_count = 0
        while True:
            try:
                if frame_queue.empty():
                    await asyncio.sleep(0.01)
                    continue

                frame = frame_queue.get()
                frame_count += 1
                if frame_count % frame_interval != 0:
                    continue

                # Get audio chunk (2-sec window)
                audio_chunk = audio_stream.get_chunk()  # Get latest 2-sec audio

                # Run Tier 1 on current frame and audio
                tier1_result = run_tier1_continuous(frame, audio_chunk)
                await websocket.send_json(tier1_result)

                if tier1_result["status"] == "Suspected Anomaly":
                    anomaly_detected = True
                    # Run Tier 2 on current frame/audio for reasoning
                    tier2_result = run_tier2_continuous(frame, audio_chunk, tier1_result)
                    await websocket.send_json(tier2_result)

                await asyncio.sleep(1 / fps)  # Control rate
                
            except Exception as e:
                # Log error but continue processing
                print(f"Error processing frame: {e}")
                error_msg = {"error": str(e), "status": "Error - continuing"}
                try:
                    await websocket.send_json(error_msg)
                except:
                    pass  # If we can't send error, client probably disconnected
                await asyncio.sleep(1)  # Brief pause before continuing
                continue
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Fatal WebSocket error: {e}")
        try:
            await websocket.send_json({"error": f"Fatal error: {str(e)}"})
        except:
            pass
    finally:
        video_cap.release()
        audio_stream.stop()
        frame_thread.join()