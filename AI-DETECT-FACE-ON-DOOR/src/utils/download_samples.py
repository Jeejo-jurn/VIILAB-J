# download_samples.py
import os
import shutil
import tarfile
import kagglehub

def extract_lfw_from_cache():
    handle = "atulanandjha/lfwpeople"
    target_dir = "data/authorized_users"
    
    print(f"Resolving cache for '{handle}'...")
    try:
        path = kagglehub.dataset_download(handle)
        print(f"Cache path: {path}")
        
        # Look for the .tgz file
        tgz_path = os.path.join(path, "lfw-funneled.tgz")
        if os.path.exists(tgz_path):
            print(f"Extracting faces from {tgz_path}...")
            with tarfile.open(tgz_path, "r:gz") as tar:
                # Group by person folder
                extracted_people = set()
                max_people = 10
                
                for member in tar.getmembers():
                    if member.isdir(): continue
                    
                    # Expected path: lfw_funneled/Person_Name/image.jpg
                    parts = member.name.split('/')
                    if len(parts) >= 3:
                        person_name = parts[1]
                        
                        if person_name not in extracted_people:
                            if len(extracted_people) >= max_people:
                                continue
                            extracted_people.add(person_name)
                            print(f"  [+] Extracting: {person_name}")
                        
                        # Set extract path
                        member.name = os.path.join(person_name, parts[2])
                        tar.extract(member, target_dir)
            
            print(f"\n[V] Successfully imported {len(extracted_people)} people into {target_dir}")
            print("Next step: Run 'python enroll.py' to process these faces.")
        else:
            print(f"[!] Could not find lfw-funneled.tgz in {path}")
            print(f"Contents: {os.listdir(path)}")
            
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    extract_lfw_from_cache()
