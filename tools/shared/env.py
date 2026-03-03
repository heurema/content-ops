"""Load ~/.config/content-ops/.env into os.environ (stdlib only, no overwrite)."""
from __future__ import annotations

import os
from pathlib import Path


_ENV_PATH = Path.home() / ".config" / "content-ops" / ".env"


def load() -> None:
    """Load key=value pairs from ~/.config/content-ops/.env.

    - Skips blank lines and comments (#)
    - Does NOT overwrite existing env vars (explicit env takes precedence)
    - Strips surrounding quotes from values
    - Disabled when CONTENT_OPS_NO_DOTENV=1 (used in tests)
    """
    if os.environ.get("CONTENT_OPS_NO_DOTENV") == "1":
        return
    if not _ENV_PATH.exists():
        return
    for line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value
