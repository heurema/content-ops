#!/usr/bin/env python3
"""Publish a Markdown article to dev.to via REST API.

Usage:
    python3 publish_devto.py <article.md> [--dry-run] [--confirm]

Default: --dry-run (prints payload, no API call).
Pass --confirm to actually publish.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

_HTTP_TIMEOUT = (10, 30)   # (connect_s, read_s)
_MAX_RETRIES = 3


def _http(method, url, *, headers, json):
    """Make HTTP request with retry on 429 Rate Limit."""
    for attempt in range(_MAX_RETRIES):
        resp = method(url, headers=headers, json=json, timeout=_HTTP_TIMEOUT)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 2 ** attempt))
            print(f"Rate limited — waiting {wait}s (attempt {attempt + 1}/{_MAX_RETRIES})", file=sys.stderr)
            time.sleep(wait)
            continue
        return resp
    return resp  # return last response after all retries exhausted

sys.path.insert(0, str(Path(__file__).parent))
from shared.env import load as _load_env; _load_env()
from shared.article import ArticleData, parse_article, update_frontmatter, slugify_tag

DEVTO_API_BASE = "https://dev.to/api"
MAX_TAGS = 4


def build_payload(article: ArticleData) -> dict:
    tags = [slugify_tag(t, allow_hyphens=False) for t in article.tags[:MAX_TAGS]]
    return {
        "article": {
            "title": article.title,
            "body_markdown": article.body,
            "description": article.description,
            "tags": tags,
            "canonical_url": article.canonical_url,
            "published": True,
        }
    }


def publish(article: ArticleData, api_key: str) -> tuple[int, str]:
    """POST (new) or PUT (update existing). Returns (id, url)."""
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    payload = build_payload(article)

    if article.devto_id:
        url = f"{DEVTO_API_BASE}/articles/{article.devto_id}"
        resp = _http(requests.put, url, headers=headers, json=payload)
    else:
        url = f"{DEVTO_API_BASE}/articles"
        resp = _http(requests.post, url, headers=headers, json=payload)

    if resp.status_code not in (200, 201):
        body_preview = resp.text[:200] if resp.text else "(empty body)"
        print(
            f"ERROR: dev.to API returned {resp.status_code}: {body_preview}",
            file=sys.stderr,
        )
        sys.exit(1)

    data = resp.json()
    article_id = data.get("id")
    article_url = data.get("url")
    if not article_id or not article_url:
        print(f"ERROR: Unexpected dev.to response (missing id/url): {str(data)[:200]}", file=sys.stderr)
        sys.exit(1)
    return int(article_id), article_url


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Publish article to dev.to")
    parser.add_argument("article", help="Path to Markdown article")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print payload without posting (default)",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        default=False,
        help="Actually publish to dev.to",
    )
    args = parser.parse_args(argv)

    api_key = os.environ.get("DEVTO_API_KEY")
    if not api_key:
        print("ERROR: DEVTO_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    article = parse_article(args.article)
    payload = build_payload(article)

    if args.confirm:
        dev_id, dev_url = publish(article, api_key)
        update_frontmatter(args.article, {"devto_id": dev_id, "devto_url": dev_url})
        print(f"Published: {dev_url}")
        print(f"Frontmatter updated: devto_id={dev_id}")
    else:
        print("=== DRY RUN — dev.to payload ===")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("\nPass --confirm to publish.")


if __name__ == "__main__":
    main()
