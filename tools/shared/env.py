"""Load .env into os.environ (stdlib only, no overwrite).

Search order (first found wins):
  1. ./.env              (current working directory — project-specific)
  2. ~/.config/content-ops/.env  (global fallback)
"""
from __future__ import annotations

import os
from pathlib import Path


_GLOBAL_ENV_PATH = Path.home() / ".config" / "content-ops" / ".env"


def _load_file(path: Path) -> None:
    """Parse key=value lines from path into os.environ (no overwrite)."""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def load() -> None:
    """Load env vars from .env files (CWD first, then global).

    - Skips blank lines and comments (#)
    - Does NOT overwrite existing env vars (explicit env takes precedence)
    - Strips surrounding quotes from values
    - Disabled when CONTENT_OPS_NO_DOTENV=1 (used in tests)
    """
    if os.environ.get("CONTENT_OPS_NO_DOTENV") == "1":
        return
    # CWD .env takes precedence over global
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        _load_file(cwd_env)
    if _GLOBAL_ENV_PATH.exists():
        _load_file(_GLOBAL_ENV_PATH)
