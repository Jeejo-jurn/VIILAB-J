# src/core/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() # โหลดจากไฟล์ .env

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "database"

MODEL_NAME = "buffalo_sc"
DET_SIZE = (640, 640)
SIMILARITY_THRESHOLD = 0.35
FRAME_SCALE = 0.5

# จำนวน frame ติดต่อกันที่ต้องการก่อน grant access
# ~30 FPS → 30 frames = ~1 วินาที (ต้องตั้งใจมอง)
ACCESS_CONFIRM_FRAMES = int(os.getenv("ACCESS_CONFIRM_FRAMES", "30"))

# ขนาดหน้าขั้นต่ำเทียบกับความกว้างของ frame (0.0-1.0)
# 0.18 = หน้าต้องกว้างอย่างน้อย 18% ของ frame → บังคับยืนใกล้กล้อง
MIN_FACE_RATIO = float(os.getenv("MIN_FACE_RATIO", "0.18"))

USERS_DIR = DATA_DIR / "authorized_users"
EMBED_CACHE = DB_DIR / "embeddings.npy"
NAMES_CACHE = DB_DIR / "names.npy"

# --- API SETTINGS ---
API_KEY = os.getenv("API_KEY", "NIN_FACENET_SECRET_DEFAULT")
_local_port = int(os.getenv("WEB_PORT", "8000"))
API_URL = os.getenv("API_URL", f"http://127.0.0.1:{_local_port}/log_access")
STATUS_REPORT_URL = os.getenv("STATUS_REPORT_URL", f"http://127.0.0.1:{_local_port}/update_status")

JETSON_PIN = 18
UNLOCK_DURATION = 3
UNLOCK_COOLDOWN = 5

LOG_FILE = DATA_DIR / "reports" / "access_log.csv"

# --- WEB DASHBOARD SETTINGS ---
WEB_PASSWORD = os.getenv("WEB_PASSWORD", "nin1234")
WEB_PORT = int(os.getenv("WEB_PORT", "8000"))
