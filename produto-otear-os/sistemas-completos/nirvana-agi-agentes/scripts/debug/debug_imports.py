print("Start debug script")
import os
print("Imported os")
import sys
print("Imported sys")
try:
    from app.agents.agno_tools import edit_video_tool
    print("Imported edit_video_tool")
except Exception as e:
    print(f"Import failed: {e}")
print("Done debug script")
