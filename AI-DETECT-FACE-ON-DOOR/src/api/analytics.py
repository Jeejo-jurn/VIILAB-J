# src/api/analytics.py
import os
import numpy as np
import cv2
from pathlib import Path


IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _brightness_label(mean_val: float) -> str:
    if mean_val < 60:
        return "dark"
    if mean_val > 180:
        return "bright"
    return "normal"


def _analyze_image(path: Path) -> dict | None:
    img = cv2.imread(str(path))
    if img is None:
        return None
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    brightness = float(gray.mean())
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    size_kb = path.stat().st_size / 1024
    return {
        "file": path.name,
        "width": w,
        "height": h,
        "size_kb": round(size_kb, 1),
        "brightness": round(brightness, 1),
        "lighting": _brightness_label(brightness),
        "sharpness": round(sharpness, 1),
        "quality": "good" if sharpness > 100 else "blurry",
    }


def analyze_photos(users_dir: Path) -> list[dict]:
    """Per-user photo analysis: count, resolution, brightness, sharpness."""
    result = []
    if not users_dir.exists():
        return result

    for user_dir in sorted(users_dir.iterdir()):
        if not user_dir.is_dir():
            continue

        photos = [f for f in user_dir.iterdir() if f.suffix.lower() in IMG_EXTS]
        if not photos:
            result.append({
                "name": user_dir.name,
                "photo_count": 0,
                "photos": [],
                "avg_brightness": 0,
                "avg_sharpness": 0,
                "lighting_dist": {},
                "quality_dist": {},
            })
            continue

        analyzed = [r for r in (_analyze_image(p) for p in photos) if r is not None]

        lighting_dist: dict[str, int] = {}
        quality_dist: dict[str, int] = {}
        for a in analyzed:
            lighting_dist[a["lighting"]] = lighting_dist.get(a["lighting"], 0) + 1
            quality_dist[a["quality"]] = quality_dist.get(a["quality"], 0) + 1

        avg_brightness = round(sum(a["brightness"] for a in analyzed) / len(analyzed), 1) if analyzed else 0
        avg_sharpness = round(sum(a["sharpness"] for a in analyzed) / len(analyzed), 1) if analyzed else 0

        result.append({
            "name": user_dir.name,
            "photo_count": len(analyzed),
            "photos": analyzed,
            "avg_brightness": avg_brightness,
            "avg_sharpness": avg_sharpness,
            "lighting_dist": lighting_dist,
            "quality_dist": quality_dist,
        })

    return result


def analyze_embeddings(embed_cache: Path, names_cache: Path) -> list[dict]:
    """Per-class intra-similarity: average cosine sim between embeddings of same person."""
    if not embed_cache.exists() or not names_cache.exists():
        return []

    try:
        embeddings = np.load(str(embed_cache))
        names = np.load(str(names_cache), allow_pickle=True)
    except Exception:
        return []

    unique_names = list(dict.fromkeys(names))
    result = []

    for name in unique_names:
        idxs = [i for i, n in enumerate(names) if n == name]
        vecs = embeddings[idxs]  # shape (k, D)

        if len(vecs) < 2:
            result.append({"name": name, "sample_count": len(vecs), "intra_sim": None})
            continue

        # Normalise (should already be normed, but just in case)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        vecs_n = vecs / np.maximum(norms, 1e-8)

        # Average pairwise cosine similarity (upper triangle)
        sim_matrix = vecs_n @ vecs_n.T
        k = len(vecs)
        upper = [sim_matrix[i, j] for i in range(k) for j in range(i + 1, k)]
        avg_sim = float(np.mean(upper)) if upper else None

        result.append({
            "name": name,
            "sample_count": len(vecs),
            "intra_sim": round(avg_sim, 4) if avg_sim is not None else None,
        })

    return result


def build_report(users_dir: Path, embed_cache: Path, names_cache: Path) -> dict:
    photo_data = analyze_photos(users_dir)
    embed_data = analyze_embeddings(embed_cache, names_cache)

    embed_by_name = {e["name"]: e for e in embed_data}

    users_summary = []
    for u in photo_data:
        emb = embed_by_name.get(u["name"], {})
        users_summary.append({
            **u,
            "sample_count": emb.get("sample_count"),
            "intra_sim": emb.get("intra_sim"),
        })

    total_photos = sum(u["photo_count"] for u in photo_data)
    total_users = len(photo_data)

    # Dataset class distribution (photos per class)
    class_dist = [{"name": u["name"], "count": u["photo_count"]} for u in photo_data]

    return {
        "total_users": total_users,
        "total_photos": total_photos,
        "class_distribution": class_dist,
        "users": users_summary,
    }
