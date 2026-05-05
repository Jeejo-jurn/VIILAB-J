# src/utils/notifier.py
import requests
import os
from ..core.config import *

class LineNotifier:
    def __init__(self, token=None):
        self.token = token or os.getenv("LINE_TOKEN")
        self.url = "https://notify-api.line.me/api/notify"

    def send_text(self, message):
        if not self.token: return
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"message": message}
        try:
            requests.post(self.url, headers=headers, data=payload, timeout=5)
        except Exception as e:
            print(f"[Notifier] Error: {e}")

    def send_with_image(self, message, image_path):
        if not self.token: return
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"message": message}
        try:
            with open(image_path, 'rb') as f:
                files = {"imageFile": f}
                requests.post(self.url, headers=headers, data=payload, files=files, timeout=10)
        except Exception as e:
            print(f"[Notifier] Image Error: {e}")
