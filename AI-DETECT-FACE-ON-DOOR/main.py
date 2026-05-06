import sys
import argparse
import threading
import uvicorn
from src.core.engine import NINFaceEngine
from src.core.config import WEB_PORT
from src.utils.maintenance import start_maintenance_thread


def run_api():
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=WEB_PORT,
        log_level="warning",
        ws="websockets",
    )


def main():
    parser = argparse.ArgumentParser(description="NIN-FACENet Edge AI Entry Point")
    parser.add_argument("--jetson", action="store_true", help="Use Jetson GPIO hardware")
    parser.add_argument(
        "--mode",
        choices=["all", "edge", "server"],
        default="all",
        help=(
            "all    = engine + web (default, dev)\n"
            "edge   = engine only (Jetson, ไม่มี web)\n"
            "server = web only (PC/server ข้างนอก)"
        ),
    )
    args = parser.parse_args()

    print("=== NIN-FACENet Edge AI Entry Point ===")
    print(f"[*] Mode: {args.mode}")

    if args.mode in ("all", "server"):
        start_maintenance_thread(days=90)
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        print(f"[*] Web dashboard: http://0.0.0.0:{WEB_PORT}")

    if args.mode in ("all", "edge"):
        engine = NINFaceEngine(use_jetson=args.jetson)
        engine.run()
    else:
        # server-only mode: block main thread
        import time
        print("[*] Running in server-only mode. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("[*] Shutting down server...")
            sys.exit(0)


if __name__ == "__main__":
    main()
