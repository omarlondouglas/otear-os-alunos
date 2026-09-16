
import os
import json
import sys
from dotenv import load_dotenv

# Add app to path
sys.path.append(os.getcwd())

load_dotenv()

from app.agents.agno_tools import generate_carousel_tool

def test():
    print("Testing generate_carousel_tool...")
    slides = [
        {"type": "cover", "title": "TESTE AGENTE", "subtitle": "Verificando orquestração", "bgColor": "#0a0a0a"},
        {"type": "text-only", "title": "Slide 2", "bgColor": "#1a1a1a"}
    ]
    
    result = generate_carousel_tool(slides)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test()
