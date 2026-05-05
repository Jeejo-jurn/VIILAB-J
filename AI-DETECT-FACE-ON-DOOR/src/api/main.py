# src/api/main.py
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import time
import datetime
from .state import global_status, get_uptime
from .database import engine, Base, SessionLocal, AccessLog
from pydantic import BaseModel

app = FastAPI(title="NIN-FACENet Admin API")

# Enable CORS for Web Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AccessData(BaseModel):
    name: str
    similarity: float
    is_live: bool

class HeartbeatData(BaseModel):
    engine_active: bool
    camera_active: bool
    fps: float

class EnrollRequest(BaseModel):
    username: str
    images_b64: list[str] # List of base64 image strings

# WebSocket Manager for Real-time Admin Updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.get("/status")
def get_system_status():
    """API Check Status Project"""
    return {
        "status": "online" if (time.time() - global_status.last_heartbeat) < 10 else "warning",
        "engine": global_status.engine_active,
        "camera": global_status.camera_active,
        "fps": round(global_status.fps, 1),
        "uptime_seconds": int(get_uptime()),
        "last_detection": {
            "user": global_status.last_user_detected,
            "sim": global_status.last_similarity
        }
    }

@app.post("/update_status")
def update_system_status(data: HeartbeatData):
    """AI Engine รายงานสุขภาพมาที่นี่"""
    global_status.engine_active = data.engine_active
    global_status.camera_active = data.camera_active
    global_status.fps = data.fps
    global_status.last_heartbeat = time.time()
    return {"status": "updated"}

@app.post("/log_access")
async def log_access(data: AccessData):
    """API ส่งผลให้ WEB ADMIN และบันทึก DB"""
    # 1. Update Global State
    global_status.last_user_detected = data.name
    global_status.last_similarity = data.similarity
    
    # 2. Save to Database
    db = SessionLocal()
    new_log = AccessLog(name=data.name, timestamp=datetime.datetime.utcnow())
    db.add(new_log)
    db.commit()
    db.close()
    
    # 3. Broadcast to Web Admin via WebSocket
    event = {
        "event": "access_granted" if data.is_live else "spoof_attempt",
        "name": data.name,
        "similarity": data.similarity,
        "time": time.strftime('%H:%M:%S')
    }
    await manager.broadcast(event)
    return {"status": "ok"}

@app.get("/history")
def get_access_history():
    """ดึงประวัติการเข้าแลปล่าสุด"""
    db = SessionLocal()
    logs = db.query(AccessLog).order_by(AccessLog.id.desc()).limit(20).all()
    db.close()
    return [{"id": l.id, "name": l.name, "timestamp": l.timestamp} for l in logs]

@app.post("/enroll_remote")
async def enroll_remote(data: EnrollRequest):
    """รับรูปจากเว็บหลักมาลงทะเบียนใหม่"""
    import base64
    from ..core.config import USERS_DIR
    from ..core.enrollment import enroll_users
    
    # 1. Create User Directory
    user_path = os.path.join(USERS_DIR, data.username)
    os.makedirs(user_path, exist_ok=True)
    
    # 2. Save Images
    for i, b64_str in enumerate(data.images_b64):
        try:
            img_data = base64.b64decode(b64_str)
            with open(os.path.join(user_path, f"remote_{i}.jpg"), "wb") as f:
                f.write(img_data)
        except: continue
        
    # 3. Trigger Enrollment
    enroll_users()
    
    # 4. Notify AI Engine to reload (we'll do this via a signal or the engine will check)
    global_status.engine_active = True # Temporary flag to trigger reload if we implement it
    
    return {"status": "success", "message": f"User {data.username} enrolled remotely."}

@app.websocket("/ws/admin")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)
