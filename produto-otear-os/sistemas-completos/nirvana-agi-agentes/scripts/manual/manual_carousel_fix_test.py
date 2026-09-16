import requests
import json
import os
import time

# Configuration
CAROUSEL_URL = "http://localhost:8002/api/generate-multi"
API_KEY = "your_secret_key_here"

def test_carousel_generation():
    print(f"🚀 Testing Carousel Generation...")
    print(f"URL: {CAROUSEL_URL}")
    print(f"API Key: {API_KEY}")

    # Payload matching the tool's structure
    payload = {
        "slides": [
            {
                "type": "cover",
                "title": "Test Carousel",
                "subtitle": "Generated via API Test",
                "titleColor": "#ffffff",
                "bgColor": "#000000",
                "images": {
                    "bg": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1080&q=80"
                }
            },
            {
                "type": "text-only",
                "title": "It Works!",
                "highlight": "Works",
                "highlightColor": "#00ff00",
                "bgColor": "#1a1a1a",
                "fontFamily": "urbanist"
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    try:
        response = requests.post(CAROUSEL_URL, json=payload, headers=headers, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(json.dumps(result, indent=2))
            
            # Verify images exist/are accessible
            if result.get("success"):
                slides = result.get("slides", [])
                print(f"Generated {len(slides)} slides.")
                for slide in slides:
                    print(f" - Slide {slide['order']}: {slide['url']}")
        else:
            print("❌ Failed!")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_carousel_generation()
