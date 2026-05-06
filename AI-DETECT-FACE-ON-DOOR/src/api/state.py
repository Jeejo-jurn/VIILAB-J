# src/api/state.py
from pydantic import BaseModel
from typing import Optional
import time
import threading

class SystemStatus(BaseModel):
    engine_active: bool = False
    camera_active: bool = False
    fps: float = 0.0
    last_heartbeat: float = 0.0
    uptime: float = 0.0
    last_user_detected: Optional[str] = None
    last_similarity: float = 0.0

# Global State Instance
global_status = SystemStatus(last_heartbeat=time.time(), uptime=time.time())

def get_uptime():
    return time.time() - global_status.uptime

# --- Live Frame Buffer for MJPEG streaming ---
latest_frame_jpg: Optional[bytes] = None
frame_lock = threading.Lock()
