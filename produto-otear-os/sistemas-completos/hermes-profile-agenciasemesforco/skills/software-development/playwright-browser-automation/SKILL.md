---
name: playwright-browser-automation
description: "Use when automating websites with Playwright."
version: 1.0.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [playwright, browser, screenshots, scraping, qa, windows]
---

# Playwright Browser Automation

Use this skill when a task needs Playwright-driven browser automation: capturing screenshots, scraping public pages, testing flows outside the built-in browser tools, or wiring Playwright into an app/service.

## Workflow

1. **Confirm the runtime and storage constraints first.** On Windows or low-space hosts, check where browser binaries/cache will land before installing.
2. **Install browsers into a project-controlled cache.** Prefer a path under the repo or app storage that is already ignored by git, not the OS user profile.
3. **Set environment before importing/launching Playwright.** `PLAYWRIGHT_BROWSERS_PATH` is read by Playwright internals; set it before `async_playwright()` or before importing the module that launches browsers.
4. **Use persistent context for sites that show cookie/login/signup interstitials.** Keep `user_data_dir` in app storage so cookies/session survive repeated captures.
5. **Handle public-site modals explicitly.** Look for localized close affordances (`Fechar`, `Close`, `Agora não`, `Not Now`) and SVG/icon-only controls with `aria-label`.
6. **Verify with a real launch and screenshot.** Syntax checks are not enough; run a minimal capture and inspect that the modal is gone and target content is visible.
7. **Do not commit caches or captured artifacts.** Ensure browser caches, screenshots, temp files, and profile folders are under ignored paths such as `storage/`, `.cache/`, or `tmp/`.

## Windows / MSYS path pitfall

When running from Git Bash/MSYS on Windows, a POSIX-looking path like `/d/SSD 2/...` may be accepted by shell tools but not by the Windows Python/Playwright process. For `PLAYWRIGHT_BROWSERS_PATH`, use a native Windows path (`D:\\...`) or let application code derive it from `Path`/environment consistently.

See `references/playwright-windows-storage.md` for a compact tested recipe.

## Verification checklist

- `python -m py_compile <changed_file>.py` passes for changed automation modules.
- `python -m playwright install chromium` was run with the intended `PLAYWRIGHT_BROWSERS_PATH`.
- A real `launch_persistent_context()` run succeeds without “Executable doesn't exist”.
- A screenshot path is produced under ignored project storage.
- Visual inspection confirms the screenshot contains target page content, not a login/signup overlay.
