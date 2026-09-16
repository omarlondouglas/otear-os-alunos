import os

def fix_env():
    encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1']
    content = ""
    success = False
    
    for enc in encodings:
        try:
            print(f"Trying encoding: {enc}...")
            with open('.env', 'r', encoding=enc) as f:
                content = f.read()
            # If we read it, check if it looks like env file (has =)
            if '=' in content:
                print(f"Success reading with {enc}!")
                success = True
                break
        except Exception as e:
            print(f"Failed with {enc}: {e}")

    if not success:
        print("Could not read .env with any common encoding.")
        return

    # Clean content (remove BOM if any, fix newlines)
    if content.startswith('\ufeff'):
        content = content[1:]
    
    # Check if google api key is there
    if 'GOOGLE_API_KEY' in content:
        print("GOOGLE_API_KEY found in content.")
    else:
        print("GOOGLE_API_KEY NOT found in content.")

    # Rewrite as UTF-8
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Rewritten .env to UTF-8.")

if __name__ == "__main__":
    fix_env()
