"""
Camera module for capturing video frames using OpenCV.
"""
import cv2
from typing import Optional
import numpy as np


class Camera:
    """Handles camera initialization and frame capture."""
    
    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        """
        Initialize camera.
        
        Args:
            camera_id: Camera device ID
            width: Frame width
            height: Frame height
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the camera capture."""
        try:
            print(f"Attempting to open camera {self.camera_id}...", flush=True)
            self.cap = cv2.VideoCapture(self.camera_id)
            print(f"VideoCapture object created for ID {self.camera_id}", flush=True)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Failed to open camera {self.camera_id}")
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            print(f"Camera initialized successfully: {self.width}x{self.height}", flush=True)
        except Exception as e:
            print(f"Error initializing camera: {e}")
            self.cap = None
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Capture and return a frame from the camera.
        
        Returns:
            Frame as numpy array (BGR format, horizontally flipped) or None if capture fails
        """
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        return frame
    
    def release(self) -> None:
        """Release the camera resource."""
        if self.cap is not None:
            self.cap.release()
            print("Camera released successfully")
            self.cap = None
    
    def __del__(self):
        """Ensure camera is released on object destruction."""
        self.release()
