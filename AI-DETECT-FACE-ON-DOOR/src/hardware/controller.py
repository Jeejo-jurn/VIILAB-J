import time
import threading
import requests
import os
from datetime import datetime
from ..core.config import *

class BaseController:
    def __init__(self):
        self._is_busy = False
        self._lock = threading.Lock()

    def trigger_access(self, name: str):
        if self._is_busy: return
        threading.Thread(target=self._execution_flow, args=(name,), daemon=True).start()

    def _execution_flow(self, name: str):
        with self._lock:
            self._is_busy = True
            self.unlock()
            self.log(name)
            time.sleep(UNLOCK_COOLDOWN)
            self._is_busy = False

    def unlock(self): raise NotImplementedError

    def log(self, name: str, status: str = "Authorized"):
        try:
            requests.post(API_URL, json={"name": name, "status": status}, timeout=1)
        except Exception: pass

        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{ts}, {name}, {status}\n")

class JetsonController(BaseController):
    def __init__(self):
        super().__init__()
        import Jetson.GPIO as GPIO
        self.GPIO = GPIO
        self.GPIO.setmode(GPIO.BOARD)
        self.GPIO.setup(JETSON_PIN, GPIO.OUT, initial=GPIO.LOW)

    def unlock(self):
        self.GPIO.output(JETSON_PIN, self.GPIO.HIGH)
        time.sleep(UNLOCK_DURATION)
        self.GPIO.output(JETSON_PIN, self.GPIO.LOW)

class MockController(BaseController):
    def unlock(self):
        print(f"[HAL] [SIMULATION] DOOR UNLOCKED ({UNLOCK_DURATION}s)")
        time.sleep(UNLOCK_DURATION)
