import sys
import argparse
from src.core.engine import NINFaceEngine
from src.utils.maintenance import start_maintenance_thread

def main():
    parser = argparse.ArgumentParser(description="NIN-FACENet Unified Entry Point")
    parser.add_argument("--jetson", action="store_true", help="Run in Jetson Nano mode")
    args = parser.parse_args()

    print("=== NIN-FACENet Edge AI Entry Point ===")
    
    # Start 90-day Auto-Cleanup in background
    start_maintenance_thread(days=90)

    engine = NINFaceEngine(use_jetson=args.jetson)
    engine.run()

if __name__ == "__main__":
    main()
