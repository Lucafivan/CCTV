import sounddevice as sd
import numpy as np
import time
import queue
from threading import Event

from utils import config, get_timestamp

class AudioWorker:
    """Worker class to monitor audio levels"""
    
    def __init__(self, event_queue):
        self.event_queue = event_queue
        self.is_running = False
        self.stop_event = Event()
        
        # Audio configuration
        self.sample_rate = config.get('audio_sample_rate', 44100)
        self.chunk_size = config.get('audio_chunk_size', 2048)
        self.noise_threshold = config.get('noise_threshold', 85)
        
        # Audio stream
        self.stream = None
        
        print("🎧 AudioWorker initialized")
    
    def calculate_db(self, audio_data: np.ndarray) -> float:
        """Calculate decibel level from audio data"""
        try:
            # Calculate RMS (Root Mean Square)
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Avoid log of zero
            if rms < 1e-10:
                return 0.0
            
            # Convert to decibels (reference: 1.0)
            # This gives relative dB, calibrate based on your mic
            db = 20 * np.log10(rms)
            
            # Scale to reasonable range (0-120 dB)
            # Adjust these values based on your microphone calibration
            db_scaled = db + 100  # Shift to positive range
            db_scaled = max(0, min(120, db_scaled))  # Clamp to 0-120
            
            return round(db_scaled, 1)
            
        except Exception as e:
            print(f"Error calculating dB: {e}")
            return 0.0
    
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            print(f"Audio status: {status}")
        
        try:
            # Convert to mono if stereo
            if len(indata.shape) > 1:
                audio_mono = np.mean(indata, axis=1)
            else:
                audio_mono = indata.flatten()
            
            # Calculate dB level
            db_level = self.calculate_db(audio_mono)
            
            # Check if exceeds threshold
            alert = db_level > self.noise_threshold
            
            # Prepare event data
            event_data = {
                'source': 'audio',
                'type': 'noise_level',
                'noise_level': db_level,
                'threshold': self.noise_threshold,
                'alert': alert,
                'timestamp': get_timestamp()
            }
            
            # Put in queue
            try:
                self.event_queue.put_nowait(event_data)
            except queue.Full:
                pass  # Queue full, skip
                
        except Exception as e:
            print(f"Error in audio callback: {e}")
    
    def run(self):
        """Main worker loop"""
        self.is_running = True
        
        try:
            # List available audio devices
            devices = sd.query_devices()
            print(f"📢 Available audio devices: {len(devices)}")
            
            # Find default input device
            default_input = sd.query_devices(kind='input')
            print(f"🎤 Using audio device: {default_input['name']}")
            
            # Open audio stream
            self.stream = sd.InputStream(
                callback=self.audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size
            )
            
            print("🎬 Audio worker loop started")
            self.stream.start()
            
            # Keep running until stop signal
            while not self.stop_event.is_set():
                time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Audio worker error: {e}")
            print("⚠️ Audio monitoring disabled. System will continue without audio.")
        finally:
            self.cleanup()
            print("🛑 Audio worker stopped")
    
    def stop(self):
        """Stop the worker"""
        print("🛑 Stopping audio worker...")
        self.stop_event.set()
        self.is_running = False
    
    def cleanup(self):
        """Release audio resources"""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
                print("🎧 Audio stream closed")
            except Exception as e:
                print(f"Error closing audio stream: {e}")