# src/api/main.py
import asyncio
import base64
import os
import time
import datetime
import shutil
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Security, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import state as api_state
from .state import global_status, get_uptime
from .database import engine, Base, SessionLocal, AccessLog
from .auth import login as auth_login, is_valid as auth_is_valid, logout as auth_logout
from ..core.config import API_KEY, USERS_DIR, EMBED_CACHE, NAMES_CACHE
from ..core.enrollment import enroll_users
from .analytics import build_report

# ---------------------------------------------------------------------------
# App & Middleware
# ---------------------------------------------------------------------------
app = FastAPI(title="NIN-FACENet Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to the web/ directory (three levels up from this file: src/api/ -> src/ -> project root)
WEB_DIR = Path(__file__).resolve().parent.parent.parent / "web"

# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)


def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return key


def _get_web_token(request: Request) -> str | None:
    """Extract web session token from X-TOKEN header or ?token= query param."""
    token = request.headers.get("X-TOKEN") or request.query_params.get("token")
    return token


def require_web_token(request: Request):
    token = _get_web_token(request)
    if not token or not auth_is_valid(token):
        raise HTTPException(status_code=401, detail="Unauthorized – please log in")
    return token


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------
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


class LoginRequest(BaseModel):
    password: str


# ---------------------------------------------------------------------------
# WebSocket Manager
# ---------------------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for c in dead:
            self.disconnect(c)


manager = ConnectionManager()

# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------


@app.get("/")
async def serve_dashboard():
    """Serve the single-page web dashboard."""
    index = WEB_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return FileResponse(index)


@app.get("/app.js")
async def serve_app_js():
    """Serve the frontend JavaScript (separated from HTML)."""
    js = WEB_DIR / "app.js"
    if not js.exists():
        raise HTTPException(status_code=404, detail="app.js not found")
    return FileResponse(js, media_type="application/javascript")


@app.post("/api/login")
async def api_login(data: LoginRequest):
    token = auth_login(data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"token": token}


@app.post("/api/logout")
async def api_logout(request: Request):
    token = _get_web_token(request)
    if token:
        auth_logout(token)
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Engine endpoints (X-API-KEY protected – called by the local face engine)
# ---------------------------------------------------------------------------


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

    db = SessionLocal()
    try:
        event_type = "access_granted" if data.is_live else "spoof_attempt"
        new_log = AccessLog(
            name=data.name,
            status=event_type,
            similarity=round(data.similarity, 4),
            is_live=data.is_live,
            timestamp=datetime.datetime.utcnow(),
        )
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
        "time": time.strftime("%H:%M:%S"),
    }
    await manager.broadcast(event)
    return {"status": "ok"}



# ---------------------------------------------------------------------------
# Web dashboard API endpoints (X-TOKEN protected)
# ---------------------------------------------------------------------------


@app.get("/api/status")
async def get_system_status(request: Request):
    return {
        "status": "online" if (time.time() - global_status.last_heartbeat) < 20 else "offline",
        "engine": global_status.engine_active,
        "camera": global_status.camera_active,
        "fps": round(global_status.fps, 1),
        "uptime_seconds": int(get_uptime()),
        "last_detection": {
            "user": global_status.last_user_detected,
            "sim": round(global_status.last_similarity, 3),
        },
    }


@app.get("/api/history")
async def get_access_history(request: Request):
    require_web_token(request)
    db = SessionLocal()
    try:
        logs = db.query(AccessLog).order_by(AccessLog.id.desc()).limit(100).all()
        return [
            {
                "id": l.id,
                "name": l.name,
                "status": l.status or "access_granted",
                "timestamp": (l.timestamp.isoformat() + "Z") if l.timestamp else None,
            }
            for l in logs
        ]
    finally:
        db.close()


@app.get("/api/users")
async def list_users(request: Request):
    """List enrolled users with photo counts. Requires X-TOKEN."""
    require_web_token(request)

    users_dir = Path(USERS_DIR)
    if not users_dir.exists():
        return []

    result = []
    for entry in sorted(users_dir.iterdir()):
        if entry.is_dir():
            photos = [
                f for f in entry.iterdir()
                if f.suffix.lower() in {".jpg", ".jpeg", ".png"}
            ]
            result.append({"name": entry.name, "photo_count": len(photos)})
    return result


@app.delete("/api/users/{name}")
async def delete_user(name: str, request: Request):
    """Delete a user folder and re-run enrollment. Requires X-TOKEN."""
    require_web_token(request)

    safe_name = os.path.basename(name)
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid username")

    user_path = Path(USERS_DIR) / safe_name
    if not str(user_path.resolve()).startswith(str(Path(USERS_DIR).resolve())):
        raise HTTPException(status_code=400, detail="Invalid username")

    if not user_path.exists():
        raise HTTPException(status_code=404, detail=f"User '{safe_name}' not found")

    shutil.rmtree(user_path)

    # Re-run enrollment in background thread to update embeddings
    await asyncio.to_thread(enroll_users)

    return {"status": "deleted", "name": safe_name}


@app.post("/api/enroll")
async def web_enroll(data: EnrollRequest, request: Request):
    """Enroll a new user via web dashboard. Requires X-TOKEN."""
    require_web_token(request)

    safe_name = os.path.basename(data.username.strip())
    if not safe_name or safe_name.startswith("."):
        raise HTTPException(status_code=400, detail="Invalid username")

    user_path = Path(USERS_DIR) / safe_name
    if not str(user_path.resolve()).startswith(str(Path(USERS_DIR).resolve())):
        raise HTTPException(status_code=400, detail="Invalid username")

    os.makedirs(user_path, exist_ok=True)

    saved = 0
    for i, b64_str in enumerate(data.images_b64):
        try:
            img_data = base64.b64decode(b64_str)
            with open(user_path / f"photo_{i:02d}.jpg", "wb") as f:
                f.write(img_data)
            saved += 1
        except Exception:
            continue

    if saved == 0:
        raise HTTPException(status_code=400, detail="No valid images provided")

    await asyncio.to_thread(enroll_users)
    return {"status": "enrolled", "name": safe_name, "photos_saved": saved}


@app.get("/api/stream")
async def mjpeg_stream(request: Request):
    """MJPEG live camera stream. Token passed as ?token= query parameter."""
    token = request.query_params.get("token")
    if not token or not auth_is_valid(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    async def frame_generator():
        while True:
            with api_state.frame_lock:
                jpg = api_state.latest_frame_jpg

            if jpg:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
                )
            await asyncio.sleep(0.033)  # ~30 fps cap

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/api/admin/report")
async def admin_report(request: Request):
    """Full dataset quality report for admin. Requires X-TOKEN."""
    require_web_token(request)
    import logging as _log
    try:
        report = await asyncio.to_thread(
            build_report, Path(USERS_DIR), Path(EMBED_CACHE), Path(NAMES_CACHE)
        )
        return report
    except Exception as exc:
        _log.error(f"[admin_report] {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------


@app.websocket("/ws/admin")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token or not auth_is_valid(token):
        await websocket.close(code=1008)
        return
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
