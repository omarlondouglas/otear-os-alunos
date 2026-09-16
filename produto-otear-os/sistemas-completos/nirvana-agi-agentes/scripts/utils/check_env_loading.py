import os
from dotenv import load_dotenv

# Try loading
load_dotenv()

print("--- ENV DEBUG START ---")
print(f"GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')}")
print(f"VIDEO_EDITOR_API_KEY: {os.getenv('VIDEO_EDITOR_API_KEY')}")
print(f"CAROUSEL_API_KEY: {os.getenv('CAROUSEL_API_KEY')}")
print(f"VIDEO_EDITOR_API_URL: {os.getenv('VIDEO_EDITOR_API_URL')}")
print("--- ENV DEBUG END ---")

# Check file encoding/content raw
try:
    with open('.env', 'rb') as f:
        raw = f.read(20)
        print(f"Raw bytes start: {raw}")
except Exception as e:
    print(f"Error reading .env: {e}")
