# test_setup.py
import os
import sys
import cv2
import shutil

def setup():
    print("=== NIN-FACENet Local Test Setup ===")
    
    # 1. Create necessary folders
    folders = [
        "data/authorized_users",
        "data/logs",
        "models",
        "data/authorized_users/MOCK_USER"
    ]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[+] Created: {folder}")
        else:
            print(f"[-] Exists: {folder}")

    # 2. Check Camera
    print("\n--- Camera Check ---")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[!] ERROR: Cannot open webcam. Please check your connection.")
    else:
        ret, frame = cap.read()
        if ret:
            print("[V] Webcam is working correctly.")
            # Save a sample photo for mock enrollment if folder is empty
            mock_path = "data/authorized_users/MOCK_USER/sample.jpg"
            if not os.listdir("data/authorized_users/MOCK_USER"):
                cv2.imwrite(mock_path, frame)
                print(f"[+] Saved sample photo to {mock_path} for testing.")
        cap.release()

    print("\n=== Instructions ===")
    print("1. Put your photos in 'data/authorized_users/YourName/'")
    print("2. Run enrollment: python enroll.py")
    print("3. Run Backend API: python src/api/main.py (Open a new terminal)")
    print("4. Run AI Engine: python main.py")
    print("====================================")

if __name__ == "__main__":
    setup()
