import cv2
import numpy as np
from typing import Dict, Any, Optional

class PoseDetector:
    """Detect accidents using simple OpenCV methods (no MediaPipe needed)"""
    
    def __init__(self):
        """Initialize simple pose detector"""
        print("✅ Simple Pose Detector initialized (OpenCV-based, no MediaPipe)")
        self.prev_frame = None
        self.motion_threshold = 5000  # Threshold for motion detection
    
    def detect_fall_simple(self, frame: np.ndarray) -> tuple:
        """Simple fall detection using contour analysis"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Find contours
        _, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        accident_detected = False
        accident_type = None
        
        frame_height = frame.shape[0]
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Only check significant contours (likely a person)
            if area > 8000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / float(h) if h > 0 else 0
                
                # Check if contour is very wide (horizontal) - possible fall
                if aspect_ratio > 2.5:
                    accident_detected = True
                    accident_type = "fall_detected"
                    break
                
                # Check if person is in lower part of frame (on ground)
                center_y = y + h/2
                if center_y > frame_height * 0.7 and aspect_ratio > 1.8:
                    accident_detected = True
                    accident_type = "person_on_ground"
                    break
        
        return accident_detected, accident_type
    
    def detect_motion_anomaly(self, frame: np.ndarray) -> bool:
        """Detect sudden motion changes (possible accident)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            return False
        
        # Calculate frame difference
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Count motion pixels
        motion_pixels = cv2.countNonZero(thresh)
        
        self.prev_frame = gray
        
        # Large motion could indicate fall
        return motion_pixels > self.motion_threshold
    
    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Main detection method - simple accident detection
        
        Args:
            frame: Input BGR image
            
        Returns:
            Dictionary with detection results
        """
        try:
            # Method 1: Contour-based fall detection
            accident_detected, accident_type = self.detect_fall_simple(frame)
            
            # Method 2: Motion anomaly (optional additional check)
            motion_anomaly = self.detect_motion_anomaly(frame)
            
            # Combine both methods
            if not accident_detected and motion_anomaly:
                # High motion detected but no obvious fall
                # Could be a sudden movement/accident
                accident_detected = False  # Be conservative
                accident_type = None
            
            return {
                'accident_detected': accident_detected,
                'accident_type': accident_type,
                'confidence': 0.7 if accident_detected else 0.0,
                'pose_detected': True,
                'method': 'opencv_simple'
            }
            
        except Exception as e:
            print(f"Error in pose detection: {e}")
            return {
                'accident_detected': False,
                'accident_type': None,
                'error': str(e),
                'pose_detected': False
            }