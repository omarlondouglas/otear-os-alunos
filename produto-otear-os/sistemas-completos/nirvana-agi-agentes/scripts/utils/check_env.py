import sys

def check_import(module_name):
    try:
        __import__(module_name)
        return "OK"
    except ImportError as e:
        return f"MISSING ({e})"
    except Exception as e:
        return f"ERROR ({e})"

with open("env_check.txt", "w") as f:
    f.write(f"Python: {sys.version}\n")
    f.write(f"redis: {check_import('redis')}\n")
    f.write(f"httpx: {check_import('httpx')}\n")
    f.write(f"dotenv: {check_import('dotenv')}\n") # python-dotenv
    f.write(f"agno: {check_import('agno')}\n")
