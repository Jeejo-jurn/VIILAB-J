# src/core/vector_db.py
import numpy as np
import os
import threading
from .config import EMBED_CACHE, NAMES_CACHE, SIMILARITY_THRESHOLD

class VectorDB:
    def __init__(self):
        self._lock = threading.RLock()
        self.embeddings = None
        self.names = None
        self.reload()

    def reload(self):
        if os.path.exists(EMBED_CACHE) and os.path.exists(NAMES_CACHE):
            embeddings = np.load(EMBED_CACHE)
            names = np.load(NAMES_CACHE)
            with self._lock:
                self.embeddings = embeddings
                self.names = names
            print(f"[*] VectorDB Reloaded: {len(self.names)} users found.")
        else:
            with self._lock:
                self.embeddings = np.array([])
                self.names = np.array([])
            print("[!] VectorDB is empty or files missing.")

    def search(self, target_embed):
        with self._lock:
            if len(self.embeddings) == 0:
                return "Unknown", 0.0
            similarities = np.dot(self.embeddings, target_embed)
            best_idx = np.argmax(similarities)
            score = similarities[best_idx]

        if score > SIMILARITY_THRESHOLD:
            return self.names[best_idx], score
        return "Unknown", score