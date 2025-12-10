import sqlite3
import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any
from threading import Lock

from utils import get_timestamp, get_date_string, ensure_dir, safe_json_serialize

class EventLogger:
    """Central logging system with SQLite and CSV fallback"""
    
    def __init__(self, db_path: str = "safety_logs.db", log_dir: str = "logs"):
        self.db_path = db_path
        self.log_dir = log_dir
        self.lock = Lock()
        
        # Ensure log directory exists
        ensure_dir(log_dir)
        
        # Initialize database
        self.init_database()
        
        # Event buffer for batching
        self.event_buffer = []
        self.last_flush_time = datetime.now()
        self.flush_interval = 60  # Flush every 60 seconds
        
        print(f"📝 EventLogger initialized (DB: {db_path})")
    
    def init_database(self):
        """Initialize SQLite database and create tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON events(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_source 
                ON events(source)
            """)
            
            conn.commit()
            conn.close()
            
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            print("⚠️ Will use CSV fallback for logging")
    
    def log_event(self, event_data: Dict[str, Any]):
        """Log an event to buffer"""
        with self.lock:
            self.event_buffer.append(event_data)
            
            # Check if it's time to flush
            elapsed = (datetime.now() - self.last_flush_time).total_seconds()
            if elapsed >= self.flush_interval or len(self.event_buffer) >= 100:
                self._flush_buffer()
    
    def _flush_buffer(self):
        """Flush event buffer to database"""
        if not self.event_buffer:
            return
        
        try:
            # Try SQLite first
            self._flush_to_sqlite()
            print(f"💾 Flushed {len(self.event_buffer)} events to database")
            
        except Exception as e:
            print(f"⚠️ SQLite flush failed: {e}")
            try:
                # Fallback to CSV
                self._flush_to_csv()
                print(f"💾 Flushed {len(self.event_buffer)} events to CSV")
            except Exception as csv_error:
                print(f"❌ CSV flush also failed: {csv_error}")
        
        # Clear buffer and update timestamp
        self.event_buffer.clear()
        self.last_flush_time = datetime.now()
    
    def _flush_to_sqlite(self):
        """Flush events to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for event in self.event_buffer:
            timestamp = event.get('timestamp', get_timestamp())
            source = event.get('source', 'unknown')
            event_type = event.get('type', 'unknown')
            
            # Convert entire event to JSON for payload
            payload = safe_json_serialize(event)
            
            cursor.execute("""
                INSERT INTO events (timestamp, source, event_type, payload)
                VALUES (?, ?, ?, ?)
            """, (timestamp, source, event_type, payload))
        
        conn.commit()
        conn.close()
    
    def _flush_to_csv(self):
        """Flush events to CSV file (fallback)"""
        csv_filename = f"events_{get_date_string()}.csv"
        csv_path = os.path.join(self.log_dir, csv_filename)
        
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'source', 'event_type', 'payload']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for event in self.event_buffer:
                writer.writerow({
                    'timestamp': event.get('timestamp', get_timestamp()),
                    'source': event.get('source', 'unknown'),
                    'event_type': event.get('type', 'unknown'),
                    'payload': safe_json_serialize(event)
                })
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent logs from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, source, event_type, payload, created_at
                FROM events
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to list of dicts
            logs = []
            for row in rows:
                try:
                    payload = json.loads(row[4])
                except:
                    payload = {"raw": row[4]}
                
                logs.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'source': row[2],
                    'event_type': row[3],
                    'payload': payload,
                    'created_at': row[5]
                })
            
            return logs
            
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return []
    
    def get_summary(self) -> Dict[str, Any]:
        """Get aggregated statistics from logs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total events
            cursor.execute("SELECT COUNT(*) FROM events")
            total_events = cursor.fetchone()[0]
            
            # Events by source
            cursor.execute("""
                SELECT source, COUNT(*) as count
                FROM events
                GROUP BY source
            """)
            by_source = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Events by type
            cursor.execute("""
                SELECT event_type, COUNT(*) as count
                FROM events
                GROUP BY event_type
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Recent accident count (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM events
                WHERE event_type = 'camera_detection'
                AND payload LIKE '%"accident_detected": true%'
                AND datetime(timestamp) > datetime('now', '-1 day')
            """)
            recent_accidents = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_events': total_events,
                'by_source': by_source,
                'by_type': by_type,
                'recent_accidents': recent_accidents,
                'timestamp': get_timestamp()
            }
            
        except Exception as e:
            print(f"Error getting summary: {e}")
            return {
                'error': str(e),
                'timestamp': get_timestamp()
            }
    
    def close(self):
        """Flush remaining events and close logger"""
        with self.lock:
            if self.event_buffer:
                print("💾 Flushing remaining events before shutdown...")
                self._flush_buffer()
        
        print("✅ Logger closed")