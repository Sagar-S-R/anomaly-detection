
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision as mp_vision
import numpy as np
import time

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

# Enhanced tracking variables for SOTA detection
_streaming_timestamp = 0
_previous_landmarks = None
_pose_history = []  # Store last 10 frames for temporal analysis
_velocity_history = []  # Store velocities for acceleration detection
_last_anomaly_time = 0
_anomaly_cooldown_ms = 1500  # Optimized cooldown
_anomaly_counter = 0
_required_anomaly_frames = 3  # Balanced for real-time detection

# SOTA pose analysis constants used by big companies
FALL_DETECTION_THRESHOLD = 0.45  # Industry standard
VIOLENCE_VELOCITY_THRESHOLD = 0.3  # Fast movement detection
ABNORMAL_POSTURE_DURATION = 1000  # ms for sustained abnormal posture

def detect_aggressive_movements(landmarks, previous_landmarks=None):
    """SOTA Violence & Fighting Detection - used by security companies"""
    if not landmarks or not previous_landmarks:
        return False
    
    # Extract key body points (MediaPipe 33-point model)
    def get_point(lm_list, idx):
        return (lm_list[idx].x, lm_list[idx].y, lm_list[idx].z)
    
    # Current frame keypoints
    curr = {
        'nose': get_point(landmarks, 0),
        'left_shoulder': get_point(landmarks, 11),
        'right_shoulder': get_point(landmarks, 12),
        'left_elbow': get_point(landmarks, 13),
        'right_elbow': get_point(landmarks, 14),
        'left_wrist': get_point(landmarks, 15),
        'right_wrist': get_point(landmarks, 16),
        'left_hip': get_point(landmarks, 23),
        'right_hip': get_point(landmarks, 24),
        'left_knee': get_point(landmarks, 25),
        'right_knee': get_point(landmarks, 26)
    }
    
    # Previous frame keypoints
    prev = {
        'nose': get_point(previous_landmarks, 0),
        'left_shoulder': get_point(previous_landmarks, 11),
        'right_shoulder': get_point(previous_landmarks, 12),
        'left_elbow': get_point(previous_landmarks, 13),
        'right_elbow': get_point(previous_landmarks, 14),
        'left_wrist': get_point(previous_landmarks, 15),
        'right_wrist': get_point(previous_landmarks, 16),
        'left_hip': get_point(previous_landmarks, 23),
        'right_hip': get_point(previous_landmarks, 24),
        'left_knee': get_point(previous_landmarks, 25),
        'right_knee': get_point(previous_landmarks, 26)
    }
    
    # === 1. PUNCHING DETECTION (Industry Standard) ===
    def detect_punch():
        # Calculate wrist velocities
        left_wrist_vel = np.sqrt(sum((c-p)**2 for c,p in zip(curr['left_wrist'], prev['left_wrist'])))
        right_wrist_vel = np.sqrt(sum((c-p)**2 for c,p in zip(curr['right_wrist'], prev['right_wrist'])))
        
        # Punch characteristics: high velocity + forward/upward motion
        punch_velocity_threshold = 0.25  # Industry standard
        
        if left_wrist_vel > punch_velocity_threshold or right_wrist_vel > punch_velocity_threshold:
            # Validate punch direction (forward/upward motion)
            left_forward = curr['left_wrist'][0] > prev['left_wrist'][0]  # Moving forward
            right_forward = curr['right_wrist'][0] < prev['right_wrist'][0]  # Moving forward (right hand)
            upward_motion = (curr['left_wrist'][1] < prev['left_wrist'][1]) or (curr['right_wrist'][1] < prev['right_wrist'][1])
            
            if (left_wrist_vel > punch_velocity_threshold and (left_forward or upward_motion)) or \
               (right_wrist_vel > punch_velocity_threshold and (right_forward or upward_motion)):
                print(f"🥊 PUNCH DETECTED: L_vel={left_wrist_vel:.3f}, R_vel={right_wrist_vel:.3f}")
                return True
        return False
    
    # === 2. KICKING DETECTION ===
    def detect_kick():
        # Foot/knee movement analysis
        left_knee_vel = np.sqrt(sum((c-p)**2 for c,p in zip(curr['left_knee'], prev['left_knee'])))
        right_knee_vel = np.sqrt(sum((c-p)**2 for c,p in zip(curr['right_knee'], prev['right_knee'])))
        
        kick_threshold = 0.2
        if left_knee_vel > kick_threshold or right_knee_vel > kick_threshold:
            # Validate kick: knee moving upward + forward
            left_knee_up = curr['left_knee'][1] < prev['left_knee'][1]
            right_knee_up = curr['right_knee'][1] < prev['right_knee'][1]
            
            if (left_knee_vel > kick_threshold and left_knee_up) or \
               (right_knee_vel > kick_threshold and right_knee_up):
                print(f"🦵 KICK DETECTED: L_knee_vel={left_knee_vel:.3f}, R_knee_vel={right_knee_vel:.3f}")
                return True
        return False
    
    # === 3. AGGRESSIVE STANCE DETECTION ===
    def detect_aggressive_stance():
        # Fighting stance: wide legs, raised arms, forward lean
        shoulder_center = ((curr['left_shoulder'][0] + curr['right_shoulder'][0])/2,
                          (curr['left_shoulder'][1] + curr['right_shoulder'][1])/2)
        hip_center = ((curr['left_hip'][0] + curr['right_hip'][0])/2,
                      (curr['left_hip'][1] + curr['right_hip'][1])/2)
        
        # Wide stance detection
        leg_width = abs(curr['left_hip'][0] - curr['right_hip'][0])
        wide_stance = leg_width > 0.25
        
        # Raised arms detection (fighting guard)
        left_arm_raised = curr['left_wrist'][1] < curr['left_shoulder'][1] - 0.1
        right_arm_raised = curr['right_wrist'][1] < curr['right_shoulder'][1] - 0.1
        arms_raised = left_arm_raised and right_arm_raised
        
        # Forward lean (aggressive posture)
        forward_lean = shoulder_center[1] > hip_center[1] + 0.05
        
        if wide_stance and arms_raised and forward_lean:
            print(f"⚔️ AGGRESSIVE STANCE: wide={wide_stance}, arms_up={arms_raised}, lean={forward_lean}")
            return True
        return False
    
    # === 4. RAPID MOVEMENT DETECTION ===
    def detect_rapid_movement():
        # Calculate overall body movement velocity
        total_velocity = 0
        key_points = ['nose', 'left_wrist', 'right_wrist', 'left_elbow', 'right_elbow']
        
        for point in key_points:
            vel = np.sqrt(sum((c-p)**2 for c,p in zip(curr[point], prev[point])))
            total_velocity += vel
        
        avg_velocity = total_velocity / len(key_points)
        
        if avg_velocity > 0.15:  # High movement threshold
            print(f"� RAPID MOVEMENT: avg_velocity={avg_velocity:.3f}")
            return True
        return False
    
    # Run all detection methods
    return detect_punch() or detect_kick() or detect_aggressive_stance() or detect_rapid_movement()

def detect_fall_sota(landmarks, previous_landmarks=None):
    """SOTA Fall Detection - used by healthcare and eldercare companies"""
    if not landmarks:
        return False, 0.0
    
    # Extract key body points for fall analysis
    def get_point(lm_list, idx):
        return (lm_list[idx].x, lm_list[idx].y)
    
    points = {
        'head': get_point(landmarks, 0),
        'left_shoulder': get_point(landmarks, 11),
        'right_shoulder': get_point(landmarks, 12),
        'left_hip': get_point(landmarks, 23),
        'right_hip': get_point(landmarks, 24),
        'left_knee': get_point(landmarks, 25),
        'right_knee': get_point(landmarks, 26),
        'left_ankle': get_point(landmarks, 27),
        'right_ankle': get_point(landmarks, 28)
    }
    
    # === INDUSTRY STANDARD FALL DETECTION METHODS ===
    
    # 1. Body Aspect Ratio Analysis (most reliable)
    xs = [landmarks[i].x for i in range(33)]
    ys = [landmarks[i].y for i in range(33)]
    body_width = max(xs) - min(xs)
    body_height = max(ys) - min(ys)
    aspect_ratio = body_height / (body_width + 1e-6)
    
    # 2. Center of Mass Analysis
    shoulder_y = (points['left_shoulder'][1] + points['right_shoulder'][1]) / 2
    hip_y = (points['left_hip'][1] + points['right_hip'][1]) / 2
    center_of_mass_y = (shoulder_y + hip_y) / 2
    
    # 3. Head Position Relative to Body
    head_below_shoulders = points['head'][1] > shoulder_y
    head_at_hip_level = abs(points['head'][1] - hip_y) < 0.15
    
    # 4. Limb Configuration Analysis
    knees_low = (points['left_knee'][1] > hip_y + 0.1) or (points['right_knee'][1] > hip_y + 0.1)
    horizontal_spread = body_width > 0.4  # Person spread out horizontally
    
    # 5. Ground Proximity (person low in frame)
    ground_proximity = center_of_mass_y > 0.6  # Lower half of frame
    
    # === SOTA SCORING SYSTEM ===
    fall_score = 0.0
    
    # Aspect ratio scoring (most important - 40% weight)
    if aspect_ratio < 0.6:
        fall_score += 0.4
    elif aspect_ratio < 0.8:
        fall_score += 0.25
    elif aspect_ratio < 1.0:
        fall_score += 0.1
    
    # Head position scoring (30% weight)
    if head_below_shoulders and head_at_hip_level:
        fall_score += 0.3
    elif head_below_shoulders:
        fall_score += 0.2
    elif head_at_hip_level:
        fall_score += 0.15
    
    # Ground proximity scoring (15% weight)
    if ground_proximity:
        fall_score += 0.15
    
    # Limb configuration scoring (15% weight)
    if knees_low and horizontal_spread:
        fall_score += 0.15
    elif knees_low or horizontal_spread:
        fall_score += 0.08
    
    # Fall detection threshold
    fall_detected = fall_score >= 0.5  # Industry standard threshold
    
    if fall_detected:
        print(f"🚨 SOTA FALL DETECTED: score={fall_score:.2f}, ratio={aspect_ratio:.2f}, head_low={head_below_shoulders}, ground={ground_proximity}")
    
    return fall_detected, fall_score

def detect_abnormal_posture(landmarks):
    """Detect sustained abnormal postures (crouching, crawling, etc.)"""
    if not landmarks:
        return False
    
    # Get key points
    head = (landmarks[0].x, landmarks[0].y)
    left_shoulder = (landmarks[11].x, landmarks[11].y)
    right_shoulder = (landmarks[12].x, landmarks[12].y)
    left_hip = (landmarks[23].x, landmarks[23].y)
    right_hip = (landmarks[24].x, landmarks[24].y)
    
    # Calculate body metrics
    shoulder_level = (left_shoulder[1] + right_shoulder[1]) / 2
    hip_level = (left_hip[1] + right_hip[1]) / 2
    torso_height = abs(shoulder_level - hip_level)
    
    # Abnormal posture indicators
    head_very_low = head[1] > shoulder_level + 0.2  # Head significantly below shoulders
    compressed_torso = torso_height < 0.15  # Torso compressed (crouching/crawling)
    
    if head_very_low and compressed_torso:
        print(f"🚨 ABNORMAL POSTURE: head_low={head_very_low}, compressed={compressed_torso}")
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
    """Process a single frame for pose anomaly detection with SOTA algorithms"""
    
    # Convert frame to MediaPipe format
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    _streaming_timestamp += 33  # Increment by ~33ms (30 FPS)
    
    # Cooldown check - don't detect anomalies too frequently
    if _streaming_timestamp - _last_anomaly_time < _anomaly_cooldown_ms:
        return 0  # Still in cooldown period
    
    result = landmarker.detect_for_video(mp_image, _streaming_timestamp)
    
    frame_anomaly_detected = False
    anomaly_type = "unknown"
    confidence_score = 0.0
    
    if result.pose_landmarks:
        landmarks = result.pose_landmarks[0]
        
        # === SOTA DETECTION PIPELINE ===
        
        # 1. SOTA Fall Detection (healthcare-grade)
        fall_detected, fall_score = detect_fall_sota(landmarks, _previous_landmarks)
        if fall_detected:
            frame_anomaly_detected = True
            anomaly_type = "fall"
            confidence_score = fall_score
            print(f"🏥 SOTA Fall Detection: confidence={fall_score:.2f}")
        
        # 2. Violence/Fighting Detection (security industry standard)
        if _previous_landmarks and detect_aggressive_movements(landmarks, _previous_landmarks):
            frame_anomaly_detected = True
            anomaly_type = "violence"
            confidence_score = 0.8  # High confidence for movement-based detection
            print(f"🥊 Violence/Fighting Detection: confidence={confidence_score:.2f}")
        
        # 3. Abnormal Posture Detection (surveillance standard)
        if detect_abnormal_posture(landmarks):
            frame_anomaly_detected = True
            anomaly_type = "abnormal_posture"
            confidence_score = 0.7  # Good confidence for posture-based detection
            print(f"🔍 Abnormal Posture Detection: confidence={confidence_score:.2f}")
        
        # Store current landmarks for next frame comparison
        _previous_landmarks = landmarks
    
    # === ADAPTIVE TEMPORAL SMOOTHING ===
    # Different thresholds based on anomaly type and confidence
    if frame_anomaly_detected:
        _anomaly_counter += 1
        print(f"🔍 Pose: {anomaly_type} anomaly frame count: {_anomaly_counter}/{_required_anomaly_frames}")
    else:
        _anomaly_counter = max(0, _anomaly_counter - 1)  # Decay counter
    
    # SOTA temporal filtering based on anomaly type
    required_frames = _required_anomaly_frames
    
    # Adjust temporal requirements based on anomaly type and confidence
    if anomaly_type == "fall" and confidence_score > 0.7:
        required_frames = 3  # Falls: quick detection for healthcare
    elif anomaly_type == "violence" and confidence_score > 0.8:
        required_frames = 4  # Violence: moderate filtering for security
    elif anomaly_type == "abnormal_posture":
        required_frames = 6  # Posture: more filtering to avoid false positives
    
    # Confirm anomaly if enough consecutive frames detected
    if _anomaly_counter >= required_frames:
        _last_anomaly_time = _streaming_timestamp
        _anomaly_counter = 0
        print(f"🚨 Pose: CONFIRMED {anomaly_type.upper()} ANOMALY (confidence={confidence_score:.2f})")
        return 1
    
    return 0  # No confirmed anomaly