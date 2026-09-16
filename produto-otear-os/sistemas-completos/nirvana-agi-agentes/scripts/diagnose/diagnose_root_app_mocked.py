import sys
import os
import traceback
from unittest.mock import MagicMock

# 1. Mock sqlalchemy BEFORE importing app modules
sys.modules["sqlalchemy"] = MagicMock()
sys.modules["sqlalchemy.orm"] = MagicMock()
sys.modules["sqlalchemy.ext.declarative"] = MagicMock()

# Also mock app.core.database to avoid it doing anything
database_mock = MagicMock()
sys.modules["app.core.database"] = database_mock
# We need Base and engine to be available on the mock
database_mock.Base = MagicMock()
database_mock.engine = MagicMock()
database_mock.SessionLocal = MagicMock()

# Mock fast-whisper and other heavy libs if needed
# sys.modules["faster_whisper"] = MagicMock()

# Add root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"Added {current_dir} to sys.path")
print("Mocks installed for sqlalchemy and app.core.database")

print("\n--- Checking Root App Imports ---")

try:
    print("Importing app.main...", end=" ")
    # app.main imports app.core.database, which is mocked.
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
