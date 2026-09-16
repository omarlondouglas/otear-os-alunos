import httpx
import time
import sys

def verify_job_status():
    job_id = "edcffb7c-7a30-4534-be53-d70178846e86"
    url = f"http://localhost:8001/api/v1/videos/status/{job_id}"
    print(f"Testing connectivity to: {url}")
    
    try:
        response = httpx.get(url, timeout=10.0)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            print(f"Job Status: {status}")
            if status == "completed":
                print("SUCCESS: Job is completed.")
            elif status == "failed":
                print(f"FAILURE: Job failed with error: {data.get('error_message')}")
            else:
                print(f"PENDING: Job is still in state: {status}")
        else:
            print("ERROR: Non-200 response")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    verify_job_status()
