import cv2
import numpy as np
from typing import Dict, Any, List

class PeopleDetector:
    """Detect people in video frames using HOG + SVM or DNN"""
    
    def __init__(self, method: str = "hog"):
        """
        Initialize people detector
        
        Args:
            method: Detection method ('hog' or 'dnn')
        """
        self.method = method
        
        if method == "hog":
            # Initialize HOG descriptor with default people detector
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            print("✅ HOG People Detector initialized")
            
        elif method == "dnn":
            # Try to load DNN model (MobileNet-SSD)
            try:
                model_path = "models/MobileNetSSD_deploy.caffemodel"
                config_path = "models/MobileNetSSD_deploy.prototxt"
                
                self.net = cv2.dnn.readNetFromCaffe(config_path, model_path)
                self.confidence_threshold = 0.5
                print("✅ DNN People Detector initialized")
            except:
                print("⚠️ DNN model not found, falling back to HOG")
                self.method = "hog"
                self.hog = cv2.HOGDescriptor()
                self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
    def detect_hog(self, frame: np.ndarray) -> Dict[str, Any]:
        """Detect people using HOG descriptor"""
        # Resize for faster processing
        height, width = frame.shape[:2]
        scale = min(1.0, 640 / width)
        
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame_resized = cv2.resize(frame, (new_width, new_height))
        else:
            frame_resized = frame
        
        # Detect people
        boxes, weights = self.hog.detectMultiScale(
            frame_resized,
            winStride=(8, 8),
            padding=(4, 4),
            scale=1.05
        )
        
        people_count = len(boxes)
        
        # Convert boxes to original scale
        detections = []
        for i, (x, y, w, h) in enumerate(boxes):
            if scale < 1.0:
                x, y, w, h = int(x/scale), int(y/scale), int(w/scale), int(h/scale)
            
            detections.append({
                'bbox': [x, y, x+w, y+h],
                'confidence': float(weights[i][0]) if len(weights) > i else 1.0
            })
        
        return {
            'people_count': people_count,
            'detections': detections,
            'method': 'hog'
        }
    
    def detect_dnn(self, frame: np.ndarray) -> Dict[str, Any]:
        """Detect people using DNN model"""
        height, width = frame.shape[:2]
        
        # Prepare blob for DNN
        blob = cv2.dnn.blobFromImage(
            frame,
            scalefactor=0.007843,
            size=(300, 300),
            mean=(127.5, 127.5, 127.5),
            swapRB=True,
            crop=False
        )
        
        # Run detection
        self.net.setInput(blob)
        detections_raw = self.net.forward()
        
        # Filter detections
        people_count = 0
        detections = []
        
        for i in range(detections_raw.shape[2]):
            confidence = detections_raw[0, 0, i, 2]
            class_id = int(detections_raw[0, 0, i, 1])
            
            # Class 15 is 'person' in MobileNet-SSD
            if class_id == 15 and confidence > self.confidence_threshold:
                people_count += 1
                
                # Get bounding box
                box = detections_raw[0, 0, i, 3:7] * np.array([width, height, width, height])
                x1, y1, x2, y2 = box.astype(int)
                
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': float(confidence)
                })
        
        return {
            'people_count': people_count,
            'detections': detections,
            'method': 'dnn'
        }
    
    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Main detection method
        
        Args:
            frame: Input BGR image
            
        Returns:
            Dictionary with detection results
        """
        try:
            if self.method == "dnn":
                return self.detect_dnn(frame)
            else:
                return self.detect_hog(frame)
                
        except Exception as e:
            print(f"Error in people detection: {e}")
            return {
                'people_count': 0,
                'detections': [],
                'error': str(e)
            }