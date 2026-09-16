
import sys
import os
from dotenv import load_dotenv

load_dotenv()

print(f"Python Executable: {sys.executable}")
print("Attempting to import google.genai...")
try:
    import google.genai
    print(f"SUCCESS: google.genai imported. Version: {getattr(google.genai, '__version__', 'unknown')}")
except ImportError as e:
    print(f"ERROR: Failed to import google.genai: {e}")
    sys.exit(1)

print("Attempting to import agno...")
try:
    import agno
    print(f"SUCCESS: agno imported.")
except ImportError as e:
    print(f"ERROR: Failed to import agno: {e}")
    sys.exit(1)

print("Attempting to import orchestrator from app.agents.agno_agents...")
try:
    # Add current directory to sys.path
    sys.path.append(os.getcwd())
    from app.agents.agno_agents import orchestrator
    print("SUCCESS: Orchestrator imported successfully.")
except Exception as e:
    print(f"ERROR: Failed to import orchestrator: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
