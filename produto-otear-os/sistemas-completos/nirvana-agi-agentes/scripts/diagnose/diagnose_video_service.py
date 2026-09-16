import sys
import os
import traceback

# Add agi-videos-temp to sys.path to simulate docker environment
current_dir = os.path.dirname(os.path.abspath(__file__))
video_service_path = os.path.join(current_dir, "agi-videos-temp")
sys.path.insert(0, video_service_path)

print(f"Added {video_service_path} to sys.path")
print(f"Current sys.path: {sys.path}")

print("\n--- Checking Video Service Imports ---")

try:
    print("Importing app.main...", end=" ")
    import app.main
    print("OK")
except Exception:
    print("FAIL")
    traceback.print_exc()

try:
    print("Importing app.workers.video_tasks...", end=" ")
    import app.workers.video_tasks
    print("OK")
except Exception:
    print("FAIL")
    traceback.print_exc()

print("\n--- Checking Operations ---")
try:
    from app.workers.operations import get_operation_handler
    print("get_operation_handler imported OK")
except Exception:
    print("FAIL to import get_operation_handler")
    traceback.print_exc()
