import os
import sys
from unittest.mock import MagicMock

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# MOCK THE TOOL BEFORE IMPORTING ORCHESTRATOR
import app.agents.agno_tools as agno_tools

def mock_generate_carousel_tool(slides_data):
    print(f"\n[MOCK] generate_carousel_tool called with {len(slides_data)} slides.")
    return {
        "success": True,
        "carouselId": "mock-carousel-id",
        "slides": [
            {"order": i+1, "type": slide.get("type"), "url": f"https://mock-service.com/slide-{i+1}.png"}
            for i, slide in enumerate(slides_data)
        ]
    }

# Apply mock
agno_tools.generate_carousel_tool = mock_generate_carousel_tool

from app.agents.agno_agents import orchestrator

def test_carousel_delegation():
    print("🔹 Testing Orchestrator Delegation (with Mocked Tool)...")
    
    # Prompt explicitly asking for a carousel
    prompt = "Crie um carrossel educativo sobre 'Os 3 Pilares de Testes de Software' para o Instagram. Use um estilo técnico e direto."
    
    print(f"User Prompt: {prompt}")
    print("-" * 50)
    
    try:
        # Run the orchestrator
        response = orchestrator.run(prompt, stream=False)
        
        print("-" * 50)
        print("✅ Response received:")
        print(response.content)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_carousel_delegation()
