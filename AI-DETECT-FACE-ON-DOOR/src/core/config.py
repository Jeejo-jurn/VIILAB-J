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

USERS_DIR = DATA_DIR / "authorized_users"
EMBED_CACHE = DB_DIR / "embeddings.npy"
NAMES_CACHE = DB_DIR / "names.npy"

# --- REMOTE SERVER SETTINGS ---
REMOTE_SERVER_IP = os.getenv("REMOTE_SERVER_IP", "100.104.10.46")
API_KEY = os.getenv("API_KEY", "NIN_FACENET_SECRET_DEFAULT")
API_URL = f"http://{REMOTE_SERVER_IP}/api/log_access"
STATUS_REPORT_URL = f"http://{REMOTE_SERVER_IP}/api/update_status"

JETSON_PIN = 18
UNLOCK_DURATION = 3
UNLOCK_COOLDOWN = 5

LOG_FILE = DATA_DIR / "reports" / "access_log.csv"
