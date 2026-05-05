# src/core/vector_db.py
import numpy as np
import os
from .config import EMBED_CACHE, NAMES_CACHE, SIMILARITY_THRESHOLD

class VectorDB:
    def __init__(self):
        self.embeddings = None
        self.names = None
        self.reload() # Initial load

    def reload(self):
        """โหลดฐานข้อมูลจากไฟล์ล่าสุด"""
        if os.path.exists(EMBED_CACHE) and os.path.exists(NAMES_CACHE):
            self.embeddings = np.load(EMBED_CACHE)
            self.names = np.load(NAMES_CACHE)
            print(f"[*] VectorDB Reloaded: {len(self.names)} users found.")
        else:
            self.embeddings = np.array([])
            self.names = np.array([])
            print("[!] VectorDB is empty or files missing.")

    def search(self, target_embed):
        if len(self.embeddings) == 0:
            return "Unknown", 0.0
            
        # Cosine Similarity calculation
        similarities = np.dot(self.embeddings, target_embed)
        best_idx = np.argmax(similarities)
        score = similarities[best_idx]
        
        if score > SIMILARITY_THRESHOLD:
            return self.names[best_idx], score
        return "Unknown", score
