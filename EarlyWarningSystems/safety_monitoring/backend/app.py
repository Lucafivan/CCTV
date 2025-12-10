import asyncio
import json
from datetime import datetime
from typing import Set
import threading

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from camera_worker import CameraWorker
from audio_worker import AudioWorker
from logger import EventLogger
from utils import get_timestamp

app = FastAPI(title="Safety Monitoring API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Queue for worker communication
event_queue = asyncio.Queue()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"✅ Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"❌ Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        self.active_connections -= disconnected

manager = ConnectionManager()

# Initialize Logger
logger = EventLogger()

# Initialize Workers (will start in background)
camera_worker = None
audio_worker = None

@app.on_event("startup")
async def startup_event():
    """Start background workers when server starts"""
    global camera_worker, audio_worker
    
    print("🚀 Starting Safety Monitoring System...")
    
    # Start Camera Worker in thread
    camera_worker = CameraWorker(event_queue)
    camera_thread = threading.Thread(target=camera_worker.run, daemon=True)
    camera_thread.start()
    print("📹 Camera worker started")
    
    # Start Audio Worker in thread
    audio_worker = AudioWorker(event_queue)
    audio_thread = threading.Thread(target=audio_worker.run, daemon=True)
    audio_thread.start()
    print("🎧 Audio worker started")
    
    # Start event processor
    asyncio.create_task(process_events())
    print("⚙️ Event processor started")
    
    print("✅ All systems operational!")

async def process_events():
    """Process events from queue and broadcast to clients"""
    while True:
        try:
            # Get event from queue
            event_data = await event_queue.get()
            
            # Add timestamp if not present
            if 'timestamp' not in event_data:
                event_data['timestamp'] = get_timestamp()
            
            # Log event
            logger.log_event(event_data)
            
            # Broadcast to all connected clients
            await manager.broadcast(event_data)
            
        except Exception as e:
            print(f"Error processing event: {e}")
            await asyncio.sleep(0.1)

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "operational",
        "service": "Safety Monitoring System",
        "timestamp": get_timestamp(),
        "connected_clients": len(manager.active_connections)
    }

@app.get("/stats")
async def get_stats():
    """Get current system statistics"""
    return {
        "connected_clients": len(manager.active_connections),
        "camera_worker_active": camera_worker.is_running if camera_worker else False,
        "audio_worker_active": audio_worker.is_running if audio_worker else False,
        "timestamp": get_timestamp()
    }

@app.get("/logs")
async def get_logs(limit: int = 50):
    """Fetch recent logs from database"""
    logs = logger.get_recent_logs(limit)
    return {
        "total": len(logs),
        "logs": logs
    }

@app.get("/logs/summary")
async def get_log_summary():
    """Get aggregated statistics from logs"""
    summary = logger.get_summary()
    return summary

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial status
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "timestamp": get_timestamp()
        })
        
        # Keep connection alive
        while True:
            # Wait for any message from client (ping/pong)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Echo back if client sends ping
                if data == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": get_timestamp()
                    })
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({
                    "type": "keepalive",
                    "timestamp": get_timestamp()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.post("/control/camera/{camera_id}/{action}")
async def control_camera(camera_id: str, action: str):
    """Control camera operations (start/stop/restart)"""
    if action not in ["start", "stop", "restart"]:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid action. Use: start, stop, or restart"}
        )
    
    # Implement camera control logic here
    return {
        "camera_id": camera_id,
        "action": action,
        "status": "executed",
        "timestamp": get_timestamp()
    }

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when server shuts down"""
    print("🛑 Shutting down Safety Monitoring System...")
    
    if camera_worker:
        camera_worker.stop()
    
    if audio_worker:
        audio_worker.stop()
    
    logger.close()
    print("✅ Cleanup complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )