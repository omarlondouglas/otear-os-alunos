# Playwright Windows storage recipe

Use this when Playwright automation runs on Windows and the C: drive is tight or the project lives on another drive.

## Goal

Keep browser binaries, temp/cache, persistent profiles, and screenshots under the project/app storage drive instead of `C:\Users\<user>\AppData\Local\ms-playwright`.

## Install browsers on the project drive

From Git Bash/MSYS, convert the repo path to a native Windows path before exporting it to Windows Python/Playwright:

```bash
BPATH="$(cygpath -w "$PWD/storage/.playwright_browsers")"
PLAYWRIGHT_BROWSERS_PATH="$BPATH" .venv/Scripts/python.exe -m playwright install chromium
```

Avoid POSIX-style `/d/...` values for `PLAYWRIGHT_BROWSERS_PATH`; Playwright's Windows Python process may later look for executables at a mismatched native path and fail with:

```text
BrowserType.launch_persistent_context: Executable doesn't exist at ...chrome-headless-shell.exe
Looks like Playwright was just installed or updated.
```

## App code pattern

Set the env var before launching Playwright, preferably at module import in the automation service:

```python
from pathlib import Path
import os

STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "/app/storage"))
PLAYWRIGHT_BROWSERS_PATH = Path(
    os.getenv("PLAYWRIGHT_BROWSERS_PATH", str(STORAGE_PATH / ".playwright_browsers"))
)
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS_PATH))
```

Keep the persistent browser profile and output screenshots under storage too:

```python
PROFILE_DIR = STORAGE_PATH / ".playwright_profile"
SCREENSHOTS_DIR = STORAGE_PATH / "instagram_screenshots"
```

## Public-site modal handling

For sites like Instagram, public profiles can load and then show signup/login overlays after a short delay. Wait briefly, then try several close strategies:

- JS click on `[aria-label='Fechar'], [aria-label='Close']` and its closest button.
- `Escape` key.
- Role buttons named `Fechar`, `Close`, `Agora não`, `Not Now`.
- A dialog-local button fallback, not a global first button (to avoid clicking unrelated login/signup buttons).

For Instagram grid links, selectors may need absolute-href matching:

```css
main a[href*='/p/'], main a[href*='/reel/']
```

rather than only `main article a[href^='/p/']`, because rendered hrefs may be absolute.

## Verification

Run a minimal capture after install/config changes:

```bash
STORAGE_PATH='storage' .venv/Scripts/python.exe - <<'PY'
import asyncio, json, os
from app.services.instagram_playwright import capture_profile_screenshots, PLAYWRIGHT_BROWSERS_PATH

async def main():
    r = await capture_profile_screenshots('@example', count=0, headless=True)
    print(json.dumps({
        'browsers_path': str(PLAYWRIGHT_BROWSERS_PATH),
        'env': os.environ.get('PLAYWRIGHT_BROWSERS_PATH'),
        'profile': r['profile'],
        'grid_path': r['grid_path'],
    }, ensure_ascii=False))

asyncio.run(main())
PY
```

Then inspect the screenshot visually: it should show target content, not a darkened login/signup overlay.
