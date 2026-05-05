# src/core/enrollment.py
import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from .config import MODEL_NAME, DET_SIZE, USERS_DIR, EMBED_CACHE, NAMES_CACHE, DB_DIR

def enroll_users():
    print("[*] Starting Enrollment Process...")

    app = FaceAnalysis(name=MODEL_NAME, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=DET_SIZE)

    all_embeddings = []
    all_names = []

    if not os.path.exists(USERS_DIR):
        print(f"[X] Users directory not found: {USERS_DIR}")
        return

    for user_name in sorted(os.listdir(USERS_DIR)):
        user_dir = os.path.join(USERS_DIR, user_name)
        if not os.path.isdir(user_dir):
            continue

        count = 0
        for img_file in os.listdir(user_dir):
            if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            img_path = os.path.join(user_dir, img_file)
            img = cv2.imread(img_path)
            if img is None:
                print(f"  [!] Cannot read: {img_file}")
                continue

            faces = app.get(img)
            if not faces:
                print(f"  [!] No face found in {img_file}")
                continue

            all_embeddings.append(faces[0].normed_embedding)
            all_names.append(user_name)
            count += 1

        if count > 0:
            print(f"  [V] {user_name}: {count} embedding(s) enrolled.")
        else:
            print(f"  [!] {user_name}: no valid images found.")

    if not all_embeddings:
        print("[X] No embeddings generated. Check images in data/authorized_users/")
        return

    os.makedirs(DB_DIR, exist_ok=True)
    np.save(EMBED_CACHE, np.array(all_embeddings))
    np.save(NAMES_CACHE, np.array(all_names))
    print(f"[V] Enrollment Complete! {len(all_names)} total embedding(s) saved.")
