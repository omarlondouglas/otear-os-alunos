import sys
import os
from unittest.mock import MagicMock, patch

# Mock environment variables
os.environ["API_BASE_URL"] = "http://localhost:8000"
os.environ["VIDEO_EDITOR_API_URL"] = "http://localhost:8001"

# Mock agno.utils.log to avoid import errors
sys.modules["agno.utils.log"] = MagicMock()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.agno_tools import check_video_status_tool

def test_check_video_status_rewrite():
    print("Testing check_video_status_tool URL rewriting...")
    
    # Mock response from Video Service
    mock_response = {
        "status": "completed",
        "download_url": "http://localhost:8001/static/job_123_final.mp4"
    }
    
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200
        
        result = check_video_status_tool("job_123")
        
        expected_url = "http://localhost:8000/static/job_123_final.mp4"
        actual_url = result.get("download_url")
        
        if actual_url == expected_url:
            print(f"PASS: URL rewritten correctly to {actual_url}")
        else:
            print(f"FAIL: Expected {expected_url}, got {actual_url}")

def check_api_gateway_mount():
    print("\nChecking api_gateway.py for static mount...")
    try:
        with open("api_gateway.py", "r") as f:
            content = f.read()
            if 'app.mount("/static", StaticFiles(directory=STORAGE_PATH)' in content:
                print("PASS: Static mount found in api_gateway.py")
            else:
                print("FAIL: Static mount NOT found in api_gateway.py")
    except Exception as e:
        print(f"FAIL: Could not read api_gateway.py: {e}")

if __name__ == "__main__":
    test_check_video_status_rewrite()
    check_api_gateway_mount()
