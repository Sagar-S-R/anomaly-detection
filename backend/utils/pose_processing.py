
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
_anomaly_counter = 0  # Counter for persistent anomaly detection
_required_anomaly_frames = 3  # Require anomaly to persist for 3 frames

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
    
    # BALANCED THRESHOLDS - Sensitive but not too sensitive for startup
    # Check for rapid arm movements (potential punching) - BALANCED THRESHOLD
    wrist_speed_threshold = 0.22  # BALANCED - between 0.15 and 0.30
    if left_wrist_speed > wrist_speed_threshold or right_wrist_speed > wrist_speed_threshold:
        print(f"🚨 Pose Anomaly: Rapid arm movement (L:{left_wrist_speed:.3f}, R:{right_wrist_speed:.3f} > {wrist_speed_threshold})")
        return True
    
    # Check for significant head movement (bending, falling) - BALANCED THRESHOLD
    head_threshold = 0.15  # BALANCED - between 0.10 and 0.20
    if head_movement > head_threshold:
        print(f"🚨 Pose Anomaly: Significant head movement ({head_movement:.3f} > {head_threshold})")
        return True
    
    # Check for torso bending (significant change in shoulder-hip distance) - BALANCED THRESHOLD
    torso_threshold = 0.08  # BALANCED - between 0.06 and 0.12
    if torso_length_change > torso_threshold:
        print(f"🚨 Pose Anomaly: Torso bending/postural change ({torso_length_change:.3f} > {torso_threshold})")
        return True
    
    # Check for extended arm positions (potential aggressive gestures) - improved logic
    arm_extension_threshold = 0.35  # Increased from 0.2 - less sensitive
    left_arm_extended = (current_arms['left_wrist'][0] < current_arms['left_shoulder'][0] - arm_extension_threshold or 
                        current_arms['left_wrist'][0] > current_arms['left_shoulder'][0] + arm_extension_threshold)
    right_arm_extended = (current_arms['right_wrist'][0] < current_arms['right_shoulder'][0] - arm_extension_threshold or 
                         current_arms['right_wrist'][0] > current_arms['right_shoulder'][0] + arm_extension_threshold)
    
    if left_arm_extended or right_arm_extended:
        # Check if arms are raised (potential fighting stance) - more restrictive
        arm_raise_threshold = 0.20  # Increased from 0.1 - less sensitive
        left_raised = current_arms['left_wrist'][1] < current_arms['left_shoulder'][1] - arm_raise_threshold
        right_raised = current_arms['right_wrist'][1] < current_arms['right_shoulder'][1] - arm_raise_threshold
        
        # Additional check: both arms must be in aggressive position
        if (left_raised and right_raised) or (left_raised and right_arm_extended) or (right_raised and left_arm_extended):
            print(f"🚨 Pose Anomaly: Extended/raised arm position (ext_thresh:{arm_extension_threshold}, raise_thresh:{arm_raise_threshold})")
            return True
    
    return False



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
    global _streaming_timestamp, _previous_landmarks, _last_anomaly_time, _anomaly_counter
    """Process a single frame for pose anomaly detection with temporal smoothing"""
    
    # Convert frame to MediaPipe format
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    _streaming_timestamp += 33  # Increment by ~33ms (30 FPS)
    
    # Cooldown check - don't detect anomalies too frequently
    if _streaming_timestamp - _last_anomaly_time < _anomaly_cooldown_ms:
        return 0  # Still in cooldown period
    
    result = landmarker.detect_for_video(mp_image, _streaming_timestamp)
    
    frame_anomaly_detected = False
    fall_detected = False  # Track fall detection specifically for adaptive smoothing
    
    if result.pose_landmarks:
        landmarks = result.pose_landmarks[0]
        
        # Check for fall/crawl patterns - improved threshold
        xs = [lm.x * mp_image.width for lm in landmarks]
        ys = [lm.y * mp_image.height for lm in landmarks]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = max_x - min_x + 1e-6
        height = max_y - min_y
        ratio = height / width
        
        # Enhanced fall detection - multiple validation methods
        fall_threshold = 0.35  # Less restrictive than 0.25 to catch real falls
        fall_detected = False
        
        if ratio < fall_threshold:
            # Method 1: Traditional horizontal check
            shoulder_y = (landmarks[11].y + landmarks[12].y) / 2
            hip_y = (landmarks[23].y + landmarks[24].y) / 2
            horizontal_alignment = abs(shoulder_y - hip_y) < 0.08  # Slightly more lenient
            
            # Method 2: Check if person is low to ground (Y position of key points)
            avg_torso_y = (shoulder_y + hip_y) / 2
            ground_proximity = avg_torso_y > 0.6  # Lower half of frame
            
            # Method 3: Check head position relative to body
            head_y = landmarks[0].y  # Nose position
            head_below_shoulders = head_y > shoulder_y + 0.05
            
            # Fall detected if ANY of these conditions are met (not ALL)
            if horizontal_alignment or (ground_proximity and head_below_shoulders):
                print(f"🚨 Pose Anomaly: Fall detected (ratio:{ratio:.3f}, horizontal:{horizontal_alignment}, ground:{ground_proximity}, head_low:{head_below_shoulders})")
                fall_detected = True
            
        if fall_detected:
            frame_anomaly_detected = True
        
        # Check for aggressive movements (punching, fighting)
        if _previous_landmarks and detect_aggressive_movements(landmarks, _previous_landmarks):
            frame_anomaly_detected = True
        
        # Store current landmarks for next frame comparison
        _previous_landmarks = landmarks
    
    # Adaptive temporal smoothing: different requirements based on anomaly type
    if frame_anomaly_detected:
        _anomaly_counter += 1
        print(f"🔍 Pose: Anomaly frame count: {_anomaly_counter}/{_required_anomaly_frames}")
    else:
        _anomaly_counter = max(0, _anomaly_counter - 1)  # Decay counter
    
    # Adaptive confirmation based on anomaly strength
    # For falls: require only 2 frames (faster response)
    # For other anomalies: require 3 frames (more filtering)
    if fall_detected and _anomaly_counter >= 2:
        _last_anomaly_time = _streaming_timestamp
        _anomaly_counter = 0
        print("🚨 Pose: CONFIRMED FALL ANOMALY (fast track)")
        return 1
    elif not fall_detected and _anomaly_counter >= _required_anomaly_frames:
        _last_anomaly_time = _streaming_timestamp
        _anomaly_counter = 0
        print("🚨 Pose: CONFIRMED ANOMALY after temporal filtering")
        return 1
    
    return 0  # No confirmed anomaly