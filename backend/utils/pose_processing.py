
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision as mp_vision
import numpy as np

MODEL_PATH = "pose_landmarker_heavy.task"
BaseOptions = mp_tasks.BaseOptions
PoseLandmarker = mp_vision.PoseLandmarker
PoseLandmarkerOptions = mp_vision.PoseLandmarkerOptions
VisionRunningMode = mp_vision.RunningMode
options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO
)
landmarker = PoseLandmarker.create_from_options(options)

# Global timestamp counter for streaming
_streaming_timestamp = 0



def process_pose_frame(frame):
    # Process a single frame (simplified)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    # Placeholder: Integrate with landmarker logic
    return 0  # Update with actual anomaly count

def process_pose(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps) if fps > 0 else 1
    frame_count = 0
    sampled_frames = 0
    pose_anomalies = []
    timestamps = []  # in seconds

    BaseOptions = mp_tasks.BaseOptions
    PoseLandmarker = mp_vision.PoseLandmarker
    PoseLandmarkerOptions = mp_vision.PoseLandmarkerOptions
    VisionRunningMode = mp_vision.RunningMode
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.VIDEO
    )

    with PoseLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % frame_interval == 0:
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                timestamp_ms = int(1000 * frame_count / fps) if fps > 0 else frame_count
                result = landmarker.detect_for_video(mp_image, timestamp_ms)

                if result.pose_landmarks:
                    landmarks = result.pose_landmarks[0]
                    xs = [lm.x * mp_image.width for lm in landmarks]
                    ys = [lm.y * mp_image.height for lm in landmarks]
                    min_x, max_x = min(xs), max(xs)
                    min_y, max_y = min(ys), max(ys)
                    width = max_x - min_x + 1e-6
                    height = max_y - min_y
                    ratio = height / width
                    if ratio < 0.5:  # Threshold for fall/crawl
                        pose_anomalies.append(sampled_frames)
                        timestamps.append(timestamp_ms / 1000.0)

                sampled_frames += 1
            frame_count += 1

    cap.release()
    return len(pose_anomalies), sampled_frames, timestamps, fps

def process_pose_frame(frame):
    global _streaming_timestamp
    # Process a single frame (simplified)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    _streaming_timestamp += 33  # Increment by ~33ms (30 FPS)
    result = landmarker.detect_for_video(mp_image, _streaming_timestamp)  # Use incremental timestamp
    if result.pose_landmarks:
        landmarks = result.pose_landmarks[0]
        xs = [lm.x * mp_image.width for lm in landmarks]
        ys = [lm.y * mp_image.height for lm in landmarks]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = max_x - min_x + 1e-6
        height = max_y - min_y
        ratio = height / width
        if ratio < 0.5:
            return 1  # Anomaly
    return 0  # Normal