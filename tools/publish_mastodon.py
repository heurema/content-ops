#!/usr/bin/env python3
"""Publish a Markdown article as a Mastodon status post via REST API.

Usage:
    python3 publish_mastodon.py <article.md> [--dry-run] [--confirm]

Default: --dry-run (prints status text, no API call).
Pass --confirm to actually post.

Env vars required:
    MASTODON_ACCESS_TOKEN  — access token from your Mastodon instance
    MASTODON_INSTANCE_URL  — e.g. https://mastodon.social
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from shared.env import load as _load_env; _load_env()
from shared.article import ArticleData, parse_article, update_frontmatter

MAX_STATUS_CHARS = 500
_HTTP_TIMEOUT = (10, 30)
_MAX_RETRIES = 3


def build_status(article: ArticleData) -> str:
    """Build Mastodon status text within the 500 character limit."""
    tags = " ".join(f"#{t}" for t in article.tags[:4])
    url = article.canonical_url

    # Full: title + description + tags + url
    full = f"{article.title}\n\n{article.description}\n\n{tags}\n\n{url}"
    if len(full) <= MAX_STATUS_CHARS:
        return full

    # Drop description
    short = f"{article.title}\n\n{tags}\n\n{url}"
    if len(short) <= MAX_STATUS_CHARS:
        return short

    # Minimal: truncated title + url
    url_part = f"\n\n{url}"
    available = MAX_STATUS_CHARS - len(url_part) - 3
    title = article.title[:available] + "..."
    return f"{title}{url_part}"


def _http_post(url: str, headers: dict, data: dict) -> requests.Response:
    """POST with retry on 429."""
    for attempt in range(_MAX_RETRIES):
        resp = requests.post(url, headers=headers, json=data, timeout=_HTTP_TIMEOUT)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 2 ** attempt))
            print(f"Rate limited — waiting {wait}s (attempt {attempt + 1}/{_MAX_RETRIES})", file=sys.stderr)
            time.sleep(wait)
            continue
        return resp
    return resp


def publish(article: ArticleData, token: str, instance_url: str) -> tuple[str, str]:
    """Post a status to Mastodon. Returns (status_id, status_url)."""
    instance_url = instance_url.rstrip("/")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    status_text = build_status(article)
    payload = {"status": status_text}

    resp = _http_post(f"{instance_url}/api/v1/statuses", headers, payload)

    if resp.status_code not in (200, 201):
        body_preview = resp.text[:200] if resp.text else "(empty body)"
        print(f"ERROR: Mastodon API returned {resp.status_code}: {body_preview}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    status_id = data.get("id")
    status_url = data.get("url")
    if not status_id or not status_url:
        print(f"ERROR: Unexpected Mastodon response (missing id/url): {str(data)[:200]}", file=sys.stderr)
        sys.exit(1)

    return str(status_id), status_url


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Publish article to Mastodon")
    parser.add_argument("article", help="Path to Markdown article")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print status text without posting (default)",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        default=False,
        help="Actually post to Mastodon",
    )
    args = parser.parse_args(argv)

    token = os.environ.get("MASTODON_ACCESS_TOKEN")
    instance_url = os.environ.get("MASTODON_INSTANCE_URL")
    missing = [v for v, val in [("MASTODON_ACCESS_TOKEN", token), ("MASTODON_INSTANCE_URL", instance_url)] if not val]
    if missing:
        print(f"ERROR: Missing env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)
    if not instance_url.startswith("https://"):
        print("ERROR: MASTODON_INSTANCE_URL must start with https://", file=sys.stderr)
        sys.exit(1)

    article = parse_article(args.article)
    if not article.canonical_url:
        print("ERROR: canonical_url is required in frontmatter for Mastodon", file=sys.stderr)
        sys.exit(1)
    status_text = build_status(article)

    if args.confirm:
        status_id, status_url = publish(article, token, instance_url)
        update_frontmatter(args.article, {"mastodon_post_id": status_id, "mastodon_post_url": status_url})
        print(f"Published: {status_url}")
        print(f"Frontmatter updated: mastodon_post_id={status_id}")
    else:
        print("=== DRY RUN — Mastodon status ===")
        print(f"\n{status_text}")
        print(f"\n({len(status_text)}/{MAX_STATUS_CHARS} chars)")
        print("\nPass --confirm to publish.")


if __name__ == "__main__":
    main()
