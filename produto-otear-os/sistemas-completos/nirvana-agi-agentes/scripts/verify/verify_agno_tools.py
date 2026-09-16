try:
    from agno.tools.duckduckgo import DuckDuckGo
    print("DuckDuckGo tool found!")
except ImportError:
    print("DuckDuckGo tool NOT found.")

try:
    from agno.tools.googlesearch import GoogleSearch
    print("GoogleSearch tool found!")
except ImportError:
    print("GoogleSearch tool NOT found.")
