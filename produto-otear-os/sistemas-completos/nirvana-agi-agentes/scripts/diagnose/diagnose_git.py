import subprocess
import os

files = {
    "git_remote.txt": ["git", "remote", "-v"],
    "git_branch.txt": ["git", "branch", "-vv"],
    "git_status.txt": ["git", "status"],
    "git_log.txt": ["git", "log", "-n", "1"]
}

try:
    with open("git_diagnosis.txt", "w") as outfile:
        outfile.write("Diagnosing git environment:\n")
        outfile.write(f"CWD: {os.getcwd()}\n")
        
        for name, cmd in files.items():
            outfile.write(f"\n--- {name} ---\n")
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, check=False)
                outfile.write(f"STDOUT:\n{res.stdout}\n")
                outfile.write(f"STDERR:\n{res.stderr}\n")
                outfile.write(f"EXIT CODE: {res.returncode}\n")
            except Exception as e:
                outfile.write(f"Error running {cmd}: {e}\n")

    print("Diagnosis complete, written to git_diagnosis.txt")

except Exception as e:
    print(f"Failed to write diagnosis file: {e}")
