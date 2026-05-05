# src/utils/maintenance.py
import os
import time
import sqlite3
from datetime import datetime, timedelta
from ..core.config import DATA_DIR, DB_DIR

def cleanup_old_data(days=90):
    """ลบข้อมูลที่เก่ากว่าจำนวนวันที่กำหนด"""
    print(f"[*] Starting Maintenance: Purging data older than {days} days...")
    
    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_timestamp = cutoff_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # 1. Clean SQLite Database
    db_path = os.path.join(DB_DIR, "door_access.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM access_logs WHERE timestamp < ?", (cutoff_timestamp,))
            deleted_rows = conn.total_changes
            conn.commit()
            conn.close()
            print(f"[V] Database Cleaned: Removed {deleted_rows} old records.")
        except Exception as e:
            print(f"[X] Database Cleanup Error: {e}")

    # 2. Clean Snapshot Files (if stored in data/snapshots)
    snapshot_dir = os.path.join(DATA_DIR, "snapshots")
    if os.path.exists(snapshot_dir):
        count = 0
        now = time.time()
        for f in os.listdir(snapshot_dir):
            f_path = os.path.join(snapshot_dir, f)
            if os.stat(f_path).st_mtime < (now - (days * 86400)):
                os.remove(f_path)
                count += 1
        print(f"[V] Files Cleaned: Removed {count} old snapshots.")

def start_maintenance_thread(days=90):
    """รันระบบ Cleanup ในเบื้องหลังทุกๆ 24 ชม."""
    def run():
        while True:
            cleanup_old_data(days)
            # Sleep for 24 hours
            time.sleep(86400)
            
    import threading
    threading.Thread(target=run, daemon=True).start()
