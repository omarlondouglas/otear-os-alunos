from __future__ import annotations

import os
import platform
import shutil


_IS_WINDOWS = platform.system() == "Windows"


def find_git_bash() -> str | None:
    """Find the Git Bash executable required by Claude Code CLI on Windows."""
    if not _IS_WINDOWS:
        return None

    candidates = [
        os.environ.get("CLAUDE_CODE_GIT_BASH_PATH", "").strip(),
        shutil.which("bash") or "",
        r"{GIT_ROOT}\usr\bin\bash.exe",
        r"{GIT_ROOT}\bin\bash.exe",
        r"D:\Git\usr\bin\bash.exe",
        r"D:\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def build_claude_cli_env() -> dict:
    """Return an environment suitable for non-interactive Claude CLI calls."""
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)

    node_opts = env.get("NODE_OPTIONS", "")
    if "--max-old-space-size" not in node_opts:
        env["NODE_OPTIONS"] = f"{node_opts} --max-old-space-size=4096".strip()

    git_bash = find_git_bash()
    if _IS_WINDOWS and git_bash:
        env["CLAUDE_CODE_GIT_BASH_PATH"] = git_bash

    return env
