
import os
import json
import sys
from dotenv import load_dotenv

# Add app to path
sys.path.append(os.getcwd())

load_dotenv()

from app.agents.agno_tools import check_carousel_health_tool

def test():
    print("Testing check_carousel_health_tool...")
    result = check_carousel_health_tool()
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test()
