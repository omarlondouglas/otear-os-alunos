import os
import sys
from dotenv import load_dotenv

# Add app directory to path
sys.path.append(os.getcwd())

load_dotenv()

from app.agents.agno_tools import edit_video_tool

def test_tool_polling():
    print("Testing edit_video_tool polling...")
    video_url = "https://teste-minio.qc7qit.easypanel.host/stories/teste_jump.mp4"
    
    # Use simple operations to speed up testing if possible, or just the same payload
    operations = [
        {
            "type": "add_text_overlay",
            "params": {
                "text": "TESTE DE POLLING",
                "position": "top",
                "padding_top": 60,
                "font_size": 40,
                "color": "#FFFFFF",
                "background_color": "#00000080"
            }
        }
    ]
    
    with open("verification_result.txt", "w") as f:
        try:
            result = edit_video_tool(video_url=video_url, operations=operations)
            f.write(f"Function returned: {result}\n")
            
            if result.get("status") == "completed" or ("url" in result and result["url"].startswith("http")):
                 f.write("\n✅ SUCCESS: Tool waited for completion and returned result.")
            elif "message" in result and "taking longer" in result["message"]:
                 f.write("\n⚠️ PARTIAL SUCCESS: Tool timed out but started polling. Check logs for polling attempts.")
            else:
                 f.write("\n❌ FAILED: Tool did not wait or returned error.")
                 
        except Exception as e:
            f.write(f"\n❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_tool_polling()
