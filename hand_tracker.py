import os
import warnings

# Suppress MediaPipe/Protobuf warnings before importing mediapipe
warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf.symbol_database')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'
os.environ['GLOG_logtostderr'] = '0'
os.environ['GLOG_stderrthreshold'] = '3'
os.environ['XNNPACK_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import cv2
import mediapipe as mp
try:
    from mediapipe.python.solutions import hands as mp_hands
except ImportError:
    import mediapipe.solutions.hands as mp_hands
from typing import List, Optional
import numpy as np


class HandTracker:
    """Handles hand detection and landmark tracking using MediaPipe."""
    
    def __init__(self, min_detection_confidence: float = 0.7, min_tracking_confidence: float = 0.7):
        """
        Initialize hand tracker.
        
        Args:
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
        """
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        print("Hand tracker initialized successfully", flush=True)
    
    def process_frame(self, frame: np.ndarray) -> List[tuple]:
        """
        Process a frame and extract hand landmarks.
        
        Args:
            frame: BGR image from camera
        
        Returns:
            List of (x, y, z) normalized landmark coordinates (0-1 range)
            Returns empty list if no hand detected
        """
        if frame is None:
            return []
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        # Extract landmarks
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]  # Get first hand
            landmarks = []
            for landmark in hand_landmarks.landmark:
                landmarks.append((landmark.x, landmark.y, landmark.z))
            return landmarks
        
        return []
    
    def release(self) -> None:
        """Release MediaPipe resources."""
        if hasattr(self, 'hands') and self.hands:
            try:
                self.hands.close()
                print("Hand tracker released successfully")
            except Exception as e:
                print(f"Note: Hand tracker cleanup partially failed: {e}")
            finally:
                self.hands = None
    
    def __del__(self):
        """Ensure resources are released on object destruction."""
        self.release()
