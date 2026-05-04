import time
import threading
import os
from datetime import datetime
from ..core.config import UNLOCK_DURATION, UNLOCK_COOLDOWN, JETSON_PIN, LOG_FILE

class BaseController:
    def __init__(self):
        self._is_busy = False
        self._lock = threading.Lock()

    def trigger_access(self, name: str):
        threading.Thread(target=self._execution_flow, args=(name,), daemon=True).start()

    def _execution_flow(self, name: str):
        with self._lock:
            # ตรวจสอบ _is_busy ภายใน lock เพื่อป้องกัน race condition
            if self._is_busy:
                return
            self._is_busy = True
        try:
            self.unlock()
            self._log_csv(name)
            time.sleep(UNLOCK_COOLDOWN)
        finally:
            with self._lock:
                self._is_busy = False

    def unlock(self):
        raise NotImplementedError

    def _log_csv(self, name: str, status: str = "Authorized"):
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