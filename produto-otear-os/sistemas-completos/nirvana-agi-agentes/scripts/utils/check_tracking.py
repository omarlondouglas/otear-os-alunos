import subprocess
import os

try:
    res = subprocess.run(["git", "ls-tree", "-r", "HEAD", "--name-only"], capture_output=True, text=True, check=True)
    all_files = res.stdout.splitlines()

    targets = ["chat.py", "settings.py", "storage.py", "force_deploy.bat"]
    
    with open("git_tracking_check.txt", "w", encoding="utf-8") as f:
        f.write("Checking tracked files in HEAD:\n")
        for t in targets:
            found = [x for x in all_files if t in x]
            f.write(f"\nScanning for {t}:\n")
            if found:
                for item in found:
                    f.write(f"  FOUND: {item}\n")
            else:
                f.write(f"  NOT FOUND\n")

except Exception as e:
    with open("git_tracking_check.txt", "w") as f:
        f.write(f"Error: {e}")

print("Done")
