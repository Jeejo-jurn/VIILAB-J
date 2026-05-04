# src/core/engine.py
import cv2
import os
import time
import threading
import pyttsx3
import logging
import signal
import sys
from queue import Queue, Empty
from insightface.app import FaceAnalysis
from .config import MODEL_NAME, DET_SIZE, FRAME_SCALE, EMBED_CACHE
from .vector_db import VectorDB
from .reporter import SystemReporter
from ..hardware.controller import JetsonController, MockController

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

class NINFaceEngine:
    def __init__(self, use_jetson=False):
        self.app = FaceAnalysis(name=MODEL_NAME, providers=['TensorrtExecutionProvider', 'CUDAExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=DET_SIZE)
        self.db = VectorDB()
        self.hw = JetsonController() if use_jetson else MockController()
        self.reporter = SystemReporter()

        self.voice_queue = Queue()
        self.is_running = False

        # แยก queue: inference_queue สำหรับ AI, display_queue สำหรับแสดงผล
        self.inference_queue = Queue(maxsize=1)
        self.display_queue = Queue(maxsize=1)
        self.result_queue = Queue(maxsize=1)

        self.live_history = {}
        self.current_fps = 0.0
        self.camera_ok = False
        self.db_mtime = os.path.getmtime(EMBED_CACHE) if os.path.exists(EMBED_CACHE) else 0

        signal.signal(signal.SIGINT, self.shutdown)

    def shutdown(self, _signum=None, _frame=None):
        logging.info("Shutting down NIN-FACENet...")
        self.is_running = False
        sys.exit(0)

    def voice_worker(self):
        engine = pyttsx3.init()
        engine.setProperty('rate', 155)
        while self.is_running:
            try:
                name = self.voice_queue.get(timeout=1)
                engine.say(f"Welcome {name}")
                engine.runAndWait()
            except Empty:
                continue
            except Exception as e:
                logging.warning(f"Voice error: {e}")

    def capture_loop(self):
        while self.is_running:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self.camera_ok = cap.isOpened()
            while self.is_running and self.camera_ok:
                ret, frame = cap.read()
                if not ret:
                    break
                # ส่ง frame ไปทั้ง inference และ display แยกกัน
                if self.inference_queue.full():
                    self.inference_queue.get()
                self.inference_queue.put(frame)

                if self.display_queue.full():
                    self.display_queue.get()
                self.display_queue.put(frame.copy())
            cap.release()
            time.sleep(2)

    def inference_loop(self):
        while self.is_running:
            if not self.inference_queue.empty():
                try:
                    frame = self.inference_queue.get()
                    faces = self.app.get(cv2.resize(frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE))
                    results = []
                    scale = 1.0 / FRAME_SCALE
                    for face in faces:
                        bbox = (face.bbox * scale).astype(int)
                        roi = frame[max(0, bbox[1]):bbox[3], max(0, bbox[0]):bbox[2]]
                        if roi.size == 0:
                            continue
                        var = cv2.Laplacian(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
                        is_live = 50 < var < 450
                        name, sim = self.db.search(face.normed_embedding) if is_live else ("SPOOF", 0.0)
                        results.append({"bbox": bbox, "name": name, "sim": sim, "live": is_live})
                    if not self.result_queue.full():
                        self.result_queue.put(results)
                except Exception as e:
                    logging.error(f"Inference error: {e}")

    def run(self):
        self.is_running = True
        threads = [
            threading.Thread(target=self.capture_loop, daemon=True),
            threading.Thread(target=self.inference_loop, daemon=True),
            threading.Thread(target=self.voice_worker, daemon=True),
            threading.Thread(target=self.maintenance_loop, daemon=True),
        ]
        for t in threads:
            t.start()

        t_prev = time.time()
        results = []
        while self.is_running:
            if not self.display_queue.empty():
                frame = cv2.flip(self.display_queue.get(), 1)
                if not self.result_queue.empty():
                    results = self.result_queue.get()

                # รวบรวมชื่อที่ detect ได้ใน frame นี้เพื่อ reset คนที่หายไป
                detected_names = set()
                W = frame.shape[1]
                for r in results:
                    bbox, name, sim, live = r['bbox'], r['name'], r['sim'], r['live']
                    if live and name != "Unknown":
                        detected_names.add(name)
                        self.live_history[name] = self.live_history.get(name, 0) + 1
                        if self.live_history[name] == 2:
                            self.hw.trigger_access(name)
                            self.reporter.report_access(name, sim, True)
                            self.voice_queue.put(name)
                    else:
                        self.live_history[name] = 0

                    color = (0, 255, 0) if self.live_history.get(name, 0) >= 2 else (0, 0, 255)
                    x1, x2 = W - bbox[2], W - bbox[0]
                    cv2.rectangle(frame, (x1, bbox[1]), (x2, bbox[3]), color, 2)
                    cv2.putText(frame, name, (x1, bbox[1] - 10), 0, 0.6, color, 2)

                # Reset counter สำหรับคนที่ไม่อยู่ใน frame นี้แล้ว
                for name in list(self.live_history.keys()):
                    if name not in detected_names:
                        self.live_history[name] = 0

                self.current_fps = 0.9 * self.current_fps + 0.1 * (1.0 / max(time.time() - t_prev, 1e-6))
                t_prev = time.time()
                cv2.imshow("NIN-FACENet PRO V4", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.shutdown()

    def maintenance_loop(self):
        while self.is_running:
            self.reporter.report_status(True, self.camera_ok, self.current_fps)
            if os.path.exists(EMBED_CACHE):
                mtime = os.path.getmtime(EMBED_CACHE)
                if mtime > self.db_mtime:
                    self.db.reload()
                    self.db_mtime = mtime
            time.sleep(10)