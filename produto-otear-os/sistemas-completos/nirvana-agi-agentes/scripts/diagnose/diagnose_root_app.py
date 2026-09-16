import sys
import os
import traceback

# Add root directory to sys.path to simulate docker environment
current_dir = os.path.dirname(os.path.abspath(__file__))
# root_path = os.path.join(current_dir, "") # current_dir is root in this context
sys.path.insert(0, current_dir)

print(f"Added {current_dir} to sys.path")
print(f"Current sys.path: {sys.path}")

print("\n--- Checking Root App Imports ---")

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
