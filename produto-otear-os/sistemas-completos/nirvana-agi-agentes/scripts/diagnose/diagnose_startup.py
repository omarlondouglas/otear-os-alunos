import sys
import os
import traceback

print("=== DIAGNOSIS START ===")
print(f"Python: {sys.version}")

def check_import(module_name):
    print(f"Checking {module_name}...", end=" ")
    try:
        __import__(module_name)
        print("OK")
        return True
    except ImportError as e:
        print(f"FAIL: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

# 1. Basic Imports
check_import("fastapi")
check_import("uvicorn")
check_import("dotenv")

# 2. Agno Imports (Critical)
check_import("agno")
check_import("agno.agent")
check_import("agno.models.openai")
check_import("agno.models.google")

# 3. Google GenAI
check_import("google.genai")

# 4. App Imports
print("\n--- Checking App Logic ---")
try:
    print("Importing app.agents.agno_agents...", end=" ")
    from app.agents import agno_agents
    print("OK")
except Exception as e:
    print(f"FAIL: {e}")
    traceback.print_exc()

print("\n--- Checking API Gateway ---")
try:
    print("Importing api_gateway...", end=" ")
    import api_gateway
    print("OK")
except Exception as e:
    print(f"FAIL: {e}")
    traceback.print_exc()

print("=== DIAGNOSIS END ===")
