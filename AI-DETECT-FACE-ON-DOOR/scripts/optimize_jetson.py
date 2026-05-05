# scripts/optimize_jetson.py
import os
import subprocess

def optimize_to_tensorrt():
    print("=== NIN-FACENet: TensorRT Optimization Tool ===")
    print("[*] Detecting models...")
    
    model_path = os.path.expanduser("~/.insightface/models/buffalo_sc/")
    
    if not os.path.exists(model_path):
        print("[!] Model path not found. Please run the AI engine once first.")
        return

    onnx_files = [f for f in os.listdir(model_path) if f.endswith(".onnx")]
    
    for onnx_file in onnx_files:
        full_path = os.path.join(model_path, onnx_file)
        engine_path = full_path.replace(".onnx", ".engine")
        
        cmd = [
            "/usr/src/tensorrt/bin/trtexec",
            f"--onnx={full_path}",
            f"--saveEngine={engine_path}",
            "--fp16"
        ]
        
        print(f"\n[>] Converting {onnx_file}...")
        try:
            if os.path.exists(cmd[0]):
                subprocess.run(cmd, check=True)
                print(f"[V] Done: {onnx_file}")
            else:
                print(f"[!] trtexec missing at {cmd[0]}")
                break
        except Exception as e:
            print(f"[X] Error: {e}")

if __name__ == "__main__":
    optimize_to_tensorrt()
