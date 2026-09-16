import os
import sys
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from app.agents.agno_tools import generate_carousel_tool, check_carousel_health_tool

def test_carousel_tool():
    print("🔹 Testing Carousel Service Health...")
    health = check_carousel_health_tool()
    print(f"Health Status: {health}")
    
    if "error" in health:
        print("❌ Service is likely down or unreachable.")
        return

    print("\n🔹 Testing Generate Carousel Tool...")
    
    # Payload similar to what ReviewerAgent generates
    slides = [
        {
            "type": "cover", 
            "title": "TESTE DE CARROSSEL", 
            "subtitle": "Verificação de Fluxo", 
            "bgColor": "#000000", 
            "titleColor": "#00FF00",
            # Assuming the service handles missing images for cover by using a default or solid color if we provide bgColor
            # or we provide a dummy URL
            "images": {"bg": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1080&auto=format&fit=crop"} 
        },
        {
            "type": "text-only", 
            "title": "Slide de Texto", 
            "bgColor": "#111111", 
            "titleColor": "#FFFFFF"
        },
        {
            "type": "cta", # or text-only
            "title": "Gostou?", 
            "bgColor": "#000000", 
            "titleColor": "#FFFFFF"
        }
    ]
    
    print(f"Sending {len(slides)} slides...")
    result = generate_carousel_tool(slides)
    
    print("\n🔹 Tool Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("success"):
        print("\n✅ Verification PASSED: Carousel generated successfully.")
    else:
        print("\n❌ Verification FAILED: Tool returned error.")

if __name__ == "__main__":
    test_carousel_tool()
