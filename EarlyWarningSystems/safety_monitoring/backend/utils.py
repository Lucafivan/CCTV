import json
import time
from datetime import datetime
from typing import Any, Dict
import os

def get_timestamp() -> str:
    """Generate ISO format timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_timestamp_filename() -> str:
    """Generate timestamp for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_date_string() -> str:
    """Get current date as string"""
    return datetime.now().strftime("%Y%m%d")

class FPSCounter:
    """Calculate FPS for video streams"""
    def __init__(self):
        self.start_time = time.time()
        self.frame_count = 0
        self.fps = 0.0
        
    def update(self):
        """Update frame count and calculate FPS"""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        
        if elapsed > 1.0:  # Update every second
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
        
        return self.fps
    
    def get_fps(self) -> float:
        """Get current FPS"""
        return round(self.fps, 2)

class Config:
    """Configuration manager"""
    DEFAULT_CONFIG = {
        "cam0_device": 0,
        "cam10_device": 1,  # Usually device 10 is not available, use 1 as fallback
        "noise_threshold": 85,
        "ppe_detection_enabled": True,
        "accident_detection_enabled": True,
        "log_interval_seconds": 60,
        "camera_fps": 10,
        "audio_sample_rate": 44100,
        "audio_chunk_size": 2048,
        "detection_confidence": 0.5
    }
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded)
                    return config
            except Exception as e:
                print(f"⚠️ Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get config value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set config value and save"""
        self.config[key] = value
        self.save_config(self.config)

def safe_json_serialize(obj: Any) -> str:
    """Safely serialize object to JSON"""
    try:
        return json.dumps(obj, default=str)
    except Exception as e:
        return json.dumps({"error": f"Serialization failed: {str(e)}"})

def ensure_dir(directory: str):
    """Ensure directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created directory: {directory}")

def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))

def calculate_iou(box1, box2):
    """Calculate Intersection over Union for bounding boxes"""
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    
    # Calculate intersection area
    x_left = max(x1_min, x2_min)
    y_top = max(y1_min, y2_min)
    x_right = min(x1_max, x2_max)
    y_bottom = min(y1_max, y2_max)
    
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    
    # Calculate union area
    box1_area = (x1_max - x1_min) * (y1_max - y1_min)
    box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = box1_area + box2_area - intersection_area
    
    return intersection_area / union_area if union_area > 0 else 0.0

# Global config instance
config = Config()