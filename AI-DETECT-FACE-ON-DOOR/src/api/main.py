# src/api/main.py
import asyncio
import base64
import os
import time
import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .state import global_status, get_uptime
from .database import engine, Base, SessionLocal, AccessLog
from ..core.config import API_KEY, USERS_DIR
from ..core.enrollment import enroll_users

app = FastAPI(title="NIN-FACENet Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication ---
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return key

# --- Pydantic Models ---
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
    images_b64: list[str]

# --- WebSocket Manager ---
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

# --- Endpoints ---

@app.get("/status")
def get_system_status():
    return {
        "status": "online" if (time.time() - global_status.last_heartbeat) < 10 else "warning",
        "engine": global_status.engine_active,
        "camera": global_status.camera_active,
        "fps": round(global_status.fps, 1),
        "uptime_seconds": int(get_uptime()),
        "last_detection": {
            "user": global_status.last_user_detected,
            "sim": global_status.last_similarity,
        },
    }

@app.post("/update_status", dependencies=[Security(verify_api_key)])
def update_system_status(data: HeartbeatData):
    global_status.engine_active = data.engine_active
    global_status.camera_active = data.camera_active
    global_status.fps = data.fps
    global_status.last_heartbeat = time.time()
    return {"status": "updated"}

@app.post("/log_access", dependencies=[Security(verify_api_key)])
async def log_access(data: AccessData):
    global_status.last_user_detected = data.name
    global_status.last_similarity = data.similarity

    # บันทึก DB พร้อม try/finally ป้องกัน session รั่ว
    db = SessionLocal()
    try:
        new_log = AccessLog(name=data.name, timestamp=datetime.datetime.utcnow())
        db.add(new_log)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    event = {
        "event": "access_granted" if data.is_live else "spoof_attempt",
        "name": data.name,
        "similarity": data.similarity,
        "time": time.strftime('%H:%M:%S'),
    }
    await manager.broadcast(event)
    return {"status": "ok"}

@app.get("/history")
def get_access_history():
    db = SessionLocal()
    try:
        logs = db.query(AccessLog).order_by(AccessLog.id.desc()).limit(20).all()
        return [{"id": l.id, "name": l.name, "timestamp": l.timestamp} for l in logs]
    finally:
        db.close()

@app.post("/enroll_remote", dependencies=[Security(verify_api_key)])
async def enroll_remote(data: EnrollRequest):
    # ป้องกัน Path Traversal
    safe_name = os.path.basename(data.username)
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid username")
    user_path = os.path.join(USERS_DIR, safe_name)
    if not str(os.path.abspath(user_path)).startswith(str(os.path.abspath(USERS_DIR))):
        raise HTTPException(status_code=400, detail="Invalid username")

    os.makedirs(user_path, exist_ok=True)

    for i, b64_str in enumerate(data.images_b64):
        try:
            img_data = base64.b64decode(b64_str)
            with open(os.path.join(user_path, f"remote_{i}.jpg"), "wb") as f:
                f.write(img_data)
        except Exception:
            continue

    # รัน enrollment ใน thread แยก ไม่ block event loop
    await asyncio.to_thread(enroll_users)

    return {"status": "success", "message": f"User {safe_name} enrolled remotely."}

@app.websocket("/ws/admin")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)