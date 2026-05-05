# src/core/reporter.py
import requests
import threading
from .config import API_URL, STATUS_REPORT_URL, API_KEY

class SystemReporter:
    def __init__(self):
        self.headers = {"X-API-KEY": API_KEY}

    def _post_async(self, url, data):
        """ส่งข้อมูลแบบ Async ไม่ให้รบกวน AI Thread"""
        def run():
            try:
                requests.post(url, json=data, headers=self.headers, timeout=0.8)
            except: pass
        threading.Thread(target=run, daemon=True).start()

    def report_access(self, name, similarity, is_live):
        data = {"name": name, "similarity": float(similarity), "is_live": is_live}
        self._post_async(API_URL, data)

    def report_status(self, engine_active, camera_active, fps):
        data = {
            "engine_active": engine_active,
            "camera_active": camera_active,
            "fps": round(fps, 2),
            "device": "JETSON_NANO_01"
        }
        self._post_async(STATUS_REPORT_URL, data)
