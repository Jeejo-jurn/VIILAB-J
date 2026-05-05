# scripts/view_logs.py
import sqlite3
import os
from datetime import datetime

# Path to database (from clean structure)
DB_PATH = "d:/AI-DETECT-FACE-ON-DOOR/data/database/access_log.db"

def view_logs():
    if not os.path.exists(DB_PATH):
        print(f"[!] No database found at {DB_PATH}")
        return

    print("\n" + "="*60)
    print(f"{'ID':<5} | {'NAME':<15} | {'TIMESTAMP':<20} | {'STATUS':<10}")
    print("-" * 60)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Query last 20 access events
        cursor.execute("SELECT id, name, timestamp FROM access_logs ORDER BY timestamp DESC LIMIT 20")
        rows = cursor.fetchall()

        for row in rows:
            # Format timestamp
            ts = datetime.fromisoformat(row[2].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{row[0]:<5} | {row[1]:<15} | {ts:<20} | {'SUCCESS':<10}")
            
        conn.close()
    except Exception as e:
        print(f"[X] Database Error: {e}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    view_logs()
