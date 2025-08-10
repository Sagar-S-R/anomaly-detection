
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
_previous_landmarks = None
_previous_arm_positions = None
_last_anomaly_time = 0  # Cooldown mechanism
_anomaly_cooldown_ms = 1000  # Original working cooldown

def detect_aggressive_movements(landmarks, previous_landmarks=None):
    """Detect movements including aggressive actions, falls, and significant postural changes like bending"""
    if not landmarks or not previous_landmarks:
        return False
    
    # Key landmarks for arms (MediaPipe pose landmarks)
    # 11: Left shoulder, 12: Right shoulder
    # 13: Left elbow, 14: Right elbow  
    # 15: Left wrist, 16: Right wrist
    # 23: Left hip, 24: Right hip
    # 0: Nose (head position)
    
    current_arms = {
        'left_shoulder': (landmarks[11].x, landmarks[11].y),
        'right_shoulder': (landmarks[12].x, landmarks[12].y),
        'left_elbow': (landmarks[13].x, landmarks[13].y),
        'right_elbow': (landmarks[14].x, landmarks[14].y),
        'left_wrist': (landmarks[15].x, landmarks[15].y),
        'right_wrist': (landmarks[16].x, landmarks[16].y),
        'left_hip': (landmarks[23].x, landmarks[23].y),
        'right_hip': (landmarks[24].x, landmarks[24].y),
        'nose': (landmarks[0].x, landmarks[0].y)
    }
    
    prev_arms = {
        'left_shoulder': (previous_landmarks[11].x, previous_landmarks[11].y),
        'right_shoulder': (previous_landmarks[12].x, previous_landmarks[12].y),
        'left_elbow': (previous_landmarks[13].x, previous_landmarks[13].y),
        'right_elbow': (previous_landmarks[14].x, previous_landmarks[14].y),
        'left_wrist': (previous_landmarks[15].x, previous_landmarks[15].y),
        'right_wrist': (previous_landmarks[16].x, previous_landmarks[16].y),
        'left_hip': (previous_landmarks[23].x, previous_landmarks[23].y),
        'right_hip': (previous_landmarks[24].x, previous_landmarks[24].y),
        'nose': (previous_landmarks[0].x, previous_landmarks[0].y)
    }
    
    # Calculate movement speeds for arms
    left_wrist_speed = np.sqrt((current_arms['left_wrist'][0] - prev_arms['left_wrist'][0])**2 + 
                              (current_arms['left_wrist'][1] - prev_arms['left_wrist'][1])**2)
    right_wrist_speed = np.sqrt((current_arms['right_wrist'][0] - prev_arms['right_wrist'][0])**2 + 
                               (current_arms['right_wrist'][1] - prev_arms['right_wrist'][1])**2)
    
    # Calculate postural changes (head and torso movement)
    head_movement = np.sqrt((current_arms['nose'][0] - prev_arms['nose'][0])**2 + 
                           (current_arms['nose'][1] - prev_arms['nose'][1])**2)
    
    # Calculate torso bending (shoulder to hip distance change)
    current_torso_length = np.sqrt((current_arms['left_shoulder'][0] - current_arms['left_hip'][0])**2 + 
                                  (current_arms['left_shoulder'][1] - current_arms['left_hip'][1])**2)
    prev_torso_length = np.sqrt((prev_arms['left_shoulder'][0] - prev_arms['left_hip'][0])**2 + 
                               (prev_arms['left_shoulder'][1] - prev_arms['left_hip'][1])**2)
    torso_length_change = abs(current_torso_length - prev_torso_length)
    
    print(f"🏃 Pose Debug: wrist_speed=L{left_wrist_speed:.3f}/R{right_wrist_speed:.3f}, head_mv={head_movement:.3f}, torso_change={torso_length_change:.3f}")
    
    # Check for rapid arm movements (potential punching) - original working threshold
    if left_wrist_speed > 0.15 or right_wrist_speed > 0.15:  # Original working threshold
        print("🚨 Pose anomaly: Rapid arm movement detected")
        return True
    
    # Check for significant head movement (bending, falling)
    if head_movement > 0.08:  # Sensitive to head position changes
        print("🚨 Pose anomaly: Significant head movement detected")
        return True
    
    # Check for torso bending (significant change in shoulder-hip distance)
    if torso_length_change > 0.05:  # Detect bending/straightening
        print("🚨 Pose anomaly: Torso bending/postural change detected")
        return True
    
    # Check for extended arm positions (potential aggressive gestures)
    left_arm_extended = (current_arms['left_wrist'][0] < current_arms['left_shoulder'][0] - 0.2 or 
                        current_arms['left_wrist'][0] > current_arms['left_shoulder'][0] + 0.2)
    right_arm_extended = (current_arms['right_wrist'][0] < current_arms['right_shoulder'][0] - 0.2 or 
                         current_arms['right_wrist'][0] > current_arms['right_shoulder'][0] + 0.2)
    
    if left_arm_extended or right_arm_extended:
        # Check if arms are raised (potential fighting stance)
        left_raised = current_arms['left_wrist'][1] < current_arms['left_shoulder'][1] - 0.1
        right_raised = current_arms['right_wrist'][1] < current_arms['right_shoulder'][1] - 0.1
        
        if left_raised or right_raised:
            print("🚨 Pose anomaly: Extended/raised arm position detected")
            return True
    
    return False



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
    global _streaming_timestamp, _previous_landmarks, _last_anomaly_time
    # Process a single frame (simplified)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    _streaming_timestamp += 33  # Increment by ~33ms (30 FPS)
    
    # Cooldown check - don't detect anomalies too frequently
    if _streaming_timestamp - _last_anomaly_time < _anomaly_cooldown_ms:
        return 0  # Still in cooldown period
    
    result = landmarker.detect_for_video(mp_image, _streaming_timestamp)  # Use incremental timestamp
    
    anomaly_detected = 0
    
    if result.pose_landmarks:
        landmarks = result.pose_landmarks[0]
        
        # Check for fall/crawl patterns
        xs = [lm.x * mp_image.width for lm in landmarks]
        ys = [lm.y * mp_image.height for lm in landmarks]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = max_x - min_x + 1e-6
        height = max_y - min_y
        ratio = height / width
        
        if ratio < 0.4:  # Slightly more restrictive threshold for fall/crawl detection
            anomaly_detected = 1
        
        # Check for aggressive movements (punching, fighting)
        if _previous_landmarks and detect_aggressive_movements(landmarks, _previous_landmarks):
            anomaly_detected = 1
        
        # If anomaly detected, update the last anomaly time
        if anomaly_detected:
            _last_anomaly_time = _streaming_timestamp
        
        # Store current landmarks for next frame comparison
        _previous_landmarks = landmarks
    
    return anomaly_detected  # Return 1 for anomaly, 0 for normal