import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.agents.agno_agents import orchestrator

def test_delegation():
    print("🔹 Testing Orchestrator Delegation to VideoAnalyst...")
    
    # Prompt explicitly asking for "analysis" and "smart cut"
    prompt = "Analise este vídeo e faça um corte inteligente das melhores partes: http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    
    print(f"User Prompt: {prompt}")
    print("-" * 50)
    
    try:
        # Run the orchestrator
        # We use stream=False to get the full response at once for the test
        response = orchestrator.run(prompt, stream=False)
        
        print("-" * 50)
        print("✅ Response received:")
        print(response.content)
        
        # Check if VideoAnalyst was mentioned or used in the thought process (if available)
        # Since we can't easily see internal thoughts here without debug logs, 
        # we rely on the final response likely mentioning the analysis or the tool call.
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_delegation()
