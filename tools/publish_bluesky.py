#!/usr/bin/env python3
"""Publish a Markdown article as a Bluesky link-card post via AT Protocol.

Usage:
    python3 publish_bluesky.py <article.md> [--dry-run] [--confirm]

Default: --dry-run (prints post text, no API call).
Pass --confirm to actually publish.

Env vars required:
    BLUESKY_HANDLE       — e.g. yourname.bsky.social
    BLUESKY_APP_PASSWORD — app password from bsky.app settings
"""
from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared.env import load as _load_env; _load_env()
from shared.article import ArticleData, parse_article, update_frontmatter

MAX_POST_GRAPHEMES = 300


def build_post_text(article: ArticleData) -> str:
    """Build a Bluesky post text within the 300 grapheme limit."""
    tags = " ".join(f"#{t}" for t in article.tags[:3])
    url = article.canonical_url

    # Full version: title + description + tags + url
    full = f"{article.title}\n\n{article.description}\n\n{tags}\n\n{url}"
    if len(full) <= MAX_POST_GRAPHEMES:
        return full

    # Shorter: title + tags + url (drop description)
    short = f"{article.title}\n\n{tags}\n\n{url}"
    if len(short) <= MAX_POST_GRAPHEMES:
        return short

    # Minimal: truncated title + url
    url_part = f"\n\n{url}"
    available = MAX_POST_GRAPHEMES - len(url_part) - 3
    title = article.title[:available] + "..."
    return f"{title}{url_part}"


def publish(article: ArticleData, handle: str, app_password: str) -> tuple[str, str]:
    """Create a Bluesky post with link card. Returns (uri, url)."""
    from atproto import Client

    client = Client()
    client.login(handle, app_password)

    post_text = build_post_text(article)

    resp = client.send_post(
        text=post_text,
        embed=client.app.bsky.embed.external.Main(
            external=client.app.bsky.embed.external.External(
                uri=article.canonical_url,
                title=article.title,
                description=article.description,
            )
        ),
    )

    uri = resp.uri
    # Convert at:// URI to bsky.app URL
    rkey = uri.split("/")[-1]
    post_url = f"https://bsky.app/profile/{handle}/post/{rkey}"
    return uri, post_url


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Publish article to Bluesky")
    parser.add_argument("article", help="Path to Markdown article")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Print post text without posting (default)",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        default=False,
        help="Actually publish to Bluesky",
    )
    args = parser.parse_args(argv)

    handle = os.environ.get("BLUESKY_HANDLE")
    app_password = os.environ.get("BLUESKY_APP_PASSWORD")
    missing = [v for v, val in [("BLUESKY_HANDLE", handle), ("BLUESKY_APP_PASSWORD", app_password)] if not val]
    if missing:
        print(f"ERROR: Missing env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    article = parse_article(args.article)
    if not article.canonical_url:
        print("ERROR: canonical_url is required in frontmatter for Bluesky", file=sys.stderr)
        sys.exit(1)
    post_text = build_post_text(article)

    if args.confirm:
        uri, post_url = publish(article, handle, app_password)
        rkey = uri.split("/")[-1]
        update_frontmatter(args.article, {"bluesky_post_id": rkey, "bluesky_post_url": post_url})
        print(f"Published: {post_url}")
        print(f"Frontmatter updated: bluesky_post_id={rkey}")
    else:
        print("=== DRY RUN — Bluesky post ===")
        print(f"\n{post_text}")
        print(f"\n({len(post_text)}/{MAX_POST_GRAPHEMES} graphemes)")
        print("\nPass --confirm to publish.")


if __name__ == "__main__":
    main()
