import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.ass_generator import generate_ass

# Mock Whisper Result
mock_segments = [
    {
        "start": 0.0,
        "end": 2.0,
        "text": "Hello world this is a test"
    },
    {
        "start": 2.5,
        "end": 4.0,
        "text": "Second segment here"
    }
]

mock_words = [
    {"word": "Hello", "start": 0.0, "end": 0.5},
    {"word": "world", "start": 0.5, "end": 1.0},
    {"word": "this", "start": 1.0, "end": 1.2},
    {"word": "is", "start": 1.2, "end": 1.4},
    {"word": "a", "start": 1.4, "end": 1.5},
    {"word": "test", "start": 1.5, "end": 2.0},
    
    {"word": "Second", "start": 2.5, "end": 3.0},
    {"word": "segment", "start": 3.0, "end": 3.5},
    {"word": "here", "start": 3.5, "end": 4.0},
]

def test_animation(animation_name):
    print(f"\n--- Testing Animation: {animation_name} ---")
    config = {
        "animation": animation_name,
        "font": "Arial",
        "font_size": 20,
        "color": "&H00FFFFFF",
        "highlight_color": "&H0000FFFF",
        "alignment": 2,
        "margin_v": 50,
        "typewriter_speed": 10
    }
    
    try:
        ass_content = generate_ass(mock_segments, mock_words, config)
        print("Generated ASS Content Preview (First 20 lines):")
        print("\n".join(ass_content.split('\n')[:20]))
        
        # Save to file for manual inspection if needed
        filename = f"test_output_{animation_name}.ass"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(ass_content)
        print(f"Full output saved to {filename}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_animation("highlight-word")
    test_animation("typewriter")
