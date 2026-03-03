"""Shared article model and utilities for content-ops publishing tools."""
from __future__ import annotations

import hashlib
import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ArticleData:
    title: str
    description: str
    date: str           # YYYY-MM-DD
    tags: list[str]
    lang: str
    slug: str
    body: str
    canonical_url: str
    content_hash: str   # SHA-256 of normalized body
    # Platform IDs — written back after publish
    devto_id: int | None = None
    devto_url: str | None = None
    hashnode_id: str | None = None
    hashnode_url: str | None = None
    twitter_thread_id: str | None = None
    frontmatter: dict[str, Any] = field(default_factory=dict)


def parse_article(path: str) -> ArticleData:
    """Parse a Markdown file with YAML frontmatter. Returns ArticleData."""
    text = Path(path).read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)
    data = yaml.safe_load(fm) or {}

    slug = Path(path).stem
    base = os.environ.get("CONTENT_OPS_CANONICAL_BASE", "").rstrip("/")
    canonical_url = data.get("canonical_url") or (f"{base}/{slug}" if base else slug)

    tags = data.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    return ArticleData(
        title=data.get("title") or "",
        description=data.get("description") or "",
        date=str(data.get("date") or ""),
        tags=tags,
        lang=data.get("lang") or "en",
        slug=slug,
        body=body,
        canonical_url=canonical_url,
        content_hash=content_hash(body),
        devto_id=data.get("devto_id"),
        devto_url=data.get("devto_url"),
        hashnode_id=data.get("hashnode_id"),
        hashnode_url=data.get("hashnode_url"),
        twitter_thread_id=data.get("twitter_thread_id"),
        frontmatter=data,
    )


def update_frontmatter(path: str, updates: dict[str, Any]) -> None:
    """Atomically update YAML frontmatter fields in a Markdown file.

    Preserves: field order, unknown fields, body, encoding.
    Uses NamedTemporaryFile + os.replace() for atomicity.
    """
    text = Path(path).read_text(encoding="utf-8")
    fm_text, body = _split_frontmatter(text)
    data = yaml.safe_load(fm_text) or {}
    data.update(updates)

    new_fm = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    new_text = f"---\n{new_fm}---\n{body}"

    dir_ = os.path.dirname(os.path.abspath(path))
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=dir_, delete=False, suffix=".tmp"
    ) as tmp:
        tmp.write(new_text)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = tmp.name

    try:
        os.replace(tmp_path, path)
    except Exception:
        os.unlink(tmp_path)
        raise


def content_hash(body: str) -> str:
    """Return SHA-256 hex digest of normalized body text."""
    normalized = body.strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def slugify_tag(tag: str) -> str:
    """Convert tag string to lowercase-hyphenated slug."""
    tag = tag.strip().lower()
    tag = re.sub(r"[^a-z0-9]+", "-", tag)
    tag = tag.strip("-")
    return tag


_OPEN_RE = re.compile(r"\A(?:\ufeff)?---[ \t]*\r?\n")
_CLOSE_RE = re.compile(r"(?m)^---[ \t]*\r?$")


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split '---\\nYAML\\n---\\nbody' into (yaml_text, body_text).

    Closing delimiter must be '---' at column 0 (no leading whitespace),
    so '---' inside indented YAML block scalars is never misidentified.
    """
    open_match = _OPEN_RE.match(text)
    if not open_match:
        return "", text
    yaml_start = open_match.end()
    close_match = _CLOSE_RE.search(text, yaml_start)
    if not close_match:
        return "", text
    fm = text[yaml_start:close_match.start()].strip()
    body_start = close_match.end()
    if text.startswith("\n", body_start):
        body_start += 1
    return fm, text[body_start:]
