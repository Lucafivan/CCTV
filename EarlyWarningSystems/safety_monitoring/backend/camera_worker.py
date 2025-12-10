import cv2
import time
import queue
from threading import Thread, Event
from typing import Optional

from detectors.people_detector import PeopleDetector
from detectors.pose_detector import PoseDetector
from detectors.ppe_detector import PPEDetector
from utils import FPSCounter, config, get_timestamp

class CameraWorker:
    """Worker class to handle camera streams and detection"""
    
    def __init__(self, event_queue):
        self.event_queue = event_queue
        self.is_running = False
        self.stop_event = Event()
        
        # Camera devices
        self.cam0_device = config.get('cam0_device', 0)
        self.cam10_device = config.get('cam10_device', 1)
        
        # Initialize detectors
        self.people_detector = PeopleDetector()
        self.pose_detector = PoseDetector()
        self.ppe_detector = PPEDetector()
        
        # FPS counters
        self.fps_cam0 = FPSCounter()
        self.fps_cam10 = FPSCounter()
        
        # Camera captures
        self.cap0: Optional[cv2.VideoCapture] = None
        self.cap10: Optional[cv2.VideoCapture] = None
        
        print("📹 CameraWorker initialized")
    
    def initialize_cameras(self):
        """Initialize camera captures"""
        try:
            # Try to open cam0
            self.cap0 = cv2.VideoCapture(self.cam0_device)
            if not self.cap0.isOpened():
                print(f"⚠️ Cannot open cam0 (device {self.cam0_device})")
                self.cap0 = None
            else:
                # Set camera properties for better performance
                self.cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap0.set(cv2.CAP_PROP_FPS, 30)
                print(f"✅ cam0 opened (device {self.cam0_device})")
            
            # Try to open cam10
            self.cap10 = cv2.VideoCapture(self.cam10_device)
            if not self.cap10.isOpened():
                print(f"⚠️ Cannot open cam10 (device {self.cam10_device})")
                self.cap10 = None
            else:
                self.cap10.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap10.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap10.set(cv2.CAP_PROP_FPS, 30)
                print(f"✅ cam10 opened (device {self.cam10_device})")
                
        except Exception as e:
            print(f"❌ Error initializing cameras: {e}")
    
    def process_cam0(self, frame):
        """Process frame from cam0: people detection + accident detection"""
        try:
            # Detect people
            people_result = self.people_detector.detect(frame)
            people_count = people_result.get('people_count', 0)
            
            # Detect accidents via pose estimation
            accident_result = self.pose_detector.detect(frame)
            accident_detected = accident_result.get('accident_detected', False)
            accident_type = accident_result.get('accident_type', None)
            
            # Prepare event data
            event_data = {
                'source': 'cam0',
                'type': 'camera_detection',
                'camera': 'cam0',
                'people_count': people_count,
                'accident_detected': accident_detected,
                'accident_type': accident_type,
                'fps': self.fps_cam0.get_fps(),
                'timestamp': get_timestamp()
            }
            
            # Put in queue (non-blocking)
            try:
                self.event_queue.put_nowait(event_data)
            except queue.Full:
                pass  # Queue full, skip this frame
                
        except Exception as e:
            print(f"Error processing cam0: {e}")
    
    def process_cam10(self, frame):
        """Process frame from cam10: PPE detection"""
        try:
            # Detect PPE compliance
            ppe_result = self.ppe_detector.detect(frame)
            
            # Prepare event data
            event_data = {
                'source': 'cam10',
                'type': 'camera_detection',
                'camera': 'cam10',
                'ppe_compliant': ppe_result.get('ppe_pass', 0),
                'ppe_non_compliant': ppe_result.get('ppe_fail', 0),
                'total_detected': ppe_result.get('total_people', 0),
                'missing_items': ppe_result.get('missing_items', []),
                'fps': self.fps_cam10.get_fps(),
                'timestamp': get_timestamp()
            }
            
            # Put in queue
            try:
                self.event_queue.put_nowait(event_data)
            except queue.Full:
                pass  # Queue full, skip this frame
                
        except Exception as e:
            print(f"Error processing cam10: {e}")
    
    def run(self):
        """Main worker loop"""
        self.is_running = True
        self.initialize_cameras()
        
        if not self.cap0 and not self.cap10:
            print("❌ No cameras available. Worker stopping.")
            self.is_running = False
            return
        
        print("🎬 Camera worker loop started")
        
        target_fps = config.get('camera_fps', 10)
        frame_delay = 1.0 / target_fps
        
        while not self.stop_event.is_set():
            loop_start = time.time()
            
            # Process cam0
            if self.cap0 and self.cap0.isOpened():
                ret0, frame0 = self.cap0.read()
                if ret0:
                    self.fps_cam0.update()
                    self.process_cam0(frame0)
                else:
                    print("⚠️ Failed to read from cam0")
                    time.sleep(1)
                    # Try to reconnect
                    self.cap0.release()
                    self.cap0 = cv2.VideoCapture(self.cam0_device)
            
            # Process cam10
            if self.cap10 and self.cap10.isOpened():
                ret10, frame10 = self.cap10.read()
                if ret10:
                    self.fps_cam10.update()
                    self.process_cam10(frame10)
                else:
                    print("⚠️ Failed to read from cam10")
                    time.sleep(1)
                    # Try to reconnect
                    self.cap10.release()
                    self.cap10 = cv2.VideoCapture(self.cam10_device)
            
            # Maintain target FPS
            elapsed = time.time() - loop_start
            sleep_time = max(0, frame_delay - elapsed)
            time.sleep(sleep_time)
        
        self.cleanup()
        print("🛑 Camera worker stopped")
    
    def stop(self):
        """Stop the worker"""
        print("🛑 Stopping camera worker...")
        self.stop_event.set()
        self.is_running = False
    
    def cleanup(self):
        """Release camera resources"""
        if self.cap0:
            self.cap0.release()
            print("📹 cam0 released")
        
        if self.cap10:
            self.cap10.release()
            print("📹 cam10 released")
        
        cv2.destroyAllWindows()