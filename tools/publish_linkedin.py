#!/usr/bin/env python3
"""Publish a Markdown article as a LinkedIn ugcPost via REST API.

Usage:
    python3 publish_linkedin.py <article.md> [--dry-run] [--confirm]

Default: --dry-run (prints post payload, no API call).
Pass --confirm to actually publish.

Env vars required:
    LINKEDIN_ACCESS_TOKEN  — OAuth 2.0 access token
    LINKEDIN_PERSON_URN    — e.g. urn:li:person:AbCdEfGhIj
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

LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
MAX_COMMENTARY_CHARS = 3000
_HTTP_TIMEOUT = (10, 30)
_MAX_RETRIES = 3


def build_payload(article: ArticleData, person_urn: str) -> dict:
    """Build LinkedIn ugcPost payload for a link share."""
    return {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": f"{article.title}\n\n{article.description}\n\n{article.canonical_url}"[:MAX_COMMENTARY_CHARS]
                },
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "description": {"text": article.description},
                        "originalUrl": article.canonical_url,
                        "title": {"text": article.title},
                    }
                ],
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }


def _http_post(url: str, headers: dict, payload: dict) -> requests.Response:
    """POST with retry on 429."""
    for attempt in range(_MAX_RETRIES):
        resp = requests.post(url, headers=headers, json=payload, timeout=_HTTP_TIMEOUT)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 2 ** attempt))
            print(f"Rate limited — waiting {wait}s (attempt {attempt + 1}/{_MAX_RETRIES})", file=sys.stderr)
            time.sleep(wait)
            continue
        return resp
    return resp


def publish(article: ArticleData, token: str, person_urn: str) -> tuple[str, str]:
    """Create ugcPost on LinkedIn. Returns (post_id, post_url)."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = build_payload(article, person_urn)

    resp = _http_post(f"{LINKEDIN_API_BASE}/ugcPosts", headers, payload)

    if resp.status_code not in (200, 201):
        body_preview = resp.text[:200] if resp.text else "(empty body)"
        print(f"ERROR: LinkedIn API returned {resp.status_code}: {body_preview}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    # LinkedIn returns the post ID in the 'id' field (URN format)
    post_id = data.get("id")
    if not post_id:
        print(f"ERROR: Unexpected LinkedIn response (missing id): {str(data)[:200]}", file=sys.stderr)
        sys.exit(1)

    post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
    return str(post_id), post_url


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Publish article to LinkedIn")
    parser.add_argument("article", help="Path to Markdown article")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print post payload without publishing (default)",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        default=False,
        help="Actually publish to LinkedIn",
    )
    args = parser.parse_args(argv)

    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    person_urn = os.environ.get("LINKEDIN_PERSON_URN")
    missing = [v for v, val in [("LINKEDIN_ACCESS_TOKEN", token), ("LINKEDIN_PERSON_URN", person_urn)] if not val]
    if missing:
        print(f"ERROR: Missing env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    article = parse_article(args.article)
    if not article.canonical_url:
        print("ERROR: canonical_url is required in frontmatter for LinkedIn", file=sys.stderr)
        sys.exit(1)
    payload = build_payload(article, person_urn)

    if args.confirm:
        post_id, post_url = publish(article, token, person_urn)
        update_frontmatter(args.article, {"linkedin_post_id": post_id, "linkedin_post_url": post_url})
        print(f"Published: {post_url}")
        print(f"Frontmatter updated: linkedin_post_id={post_id}")
    else:
        print("=== DRY RUN — LinkedIn ugcPost payload ===")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("\nPass --confirm to publish.")


if __name__ == "__main__":
    main()
