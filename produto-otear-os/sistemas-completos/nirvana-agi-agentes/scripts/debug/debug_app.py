import sys
import os

print("--- DEBUG START ---")
print(f"Current Working Directory: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not Set')}")
print("sys.path:")
for p in sys.path:
    print(f"  - {p}")

print("\nDirectory Listing of CWD:")
try:
    for item in os.listdir(os.getcwd()):
        print(f"  - {item}")
except Exception as e:
    print(f"Error listing CWD: {e}")

print("\nDirectory Listing of /app:")
try:
    for item in os.listdir("/app"):
        print(f"  - {item}")
except Exception as e:
    print(f"Error listing /app: {e}")

print("\nAttempting to import app...")
try:
    import app
    print(f"Successfully imported app from {app.__file__}")
except ImportError as e:
    print(f"Failed to import app: {e}")
except Exception as e:
    print(f"An error occurred during import: {e}")

print("--- DEBUG END ---")
import time
time.sleep(60) # Keep process alive briefly to ensure logs are captured
