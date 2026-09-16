import sys

try:
    from google import genai
    from google.genai import types
    with open("install_status.txt", "w") as f:
        f.write("SUCCESS: google.genai imported")
    print("Import successful")
except Exception as e:
    with open("install_status.txt", "w") as f:
        f.write(f"FAILURE: {e}")
    print(f"Import failed: {e}")
