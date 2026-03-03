#!/usr/bin/env python3
"""Publish a Markdown article as a Twitter/X thread via Tweepy.

Usage:
    python3 publish_twitter.py <article.md> [--dry-run] [--confirm]

Default: --dry-run (prints thread, no API call).
Pass --confirm to actually post.

Env vars required:
    X_API_KEY, X_API_KEY_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
"""
from __future__ import annotations

import os
import sys
import time
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared.env import load as _load_env; _load_env()
from shared.article import parse_article, update_frontmatter

MAX_TWEET_LEN = 280


def validate_thread(tweets: list[str]) -> None:
    """Exit non-zero if any tweet exceeds 280 characters."""
    errors = []
    for i, tweet in enumerate(tweets, 1):
        if len(tweet) > MAX_TWEET_LEN:
            errors.append(
                f"Tweet {i} is {len(tweet)} chars (max {MAX_TWEET_LEN}): {tweet[:50]}..."
            )
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def build_thread(article) -> list[str]:
    """Convert article into a list of tweet strings."""
    tweets = []

    # Tweet 1: hook — title + description
    hook = f"{article.title}\n\n{article.description}"
    if len(hook) > MAX_TWEET_LEN:
        hook = hook[:MAX_TWEET_LEN - 3] + "..."
    tweets.append(hook)

    # Tweets 2-N: key paragraphs from body (one per tweet)
    paragraphs = [p.strip() for p in article.body.split("\n\n") if p.strip()]
    # Strip markdown headings; skip code blocks
    paragraphs = [p.lstrip("#").strip() for p in paragraphs if not p.startswith("```")]
    for para in paragraphs[1:6]:  # max 5 body tweets
        if len(para) <= MAX_TWEET_LEN:
            tweets.append(para)
        else:
            chunks = textwrap.wrap(para, MAX_TWEET_LEN - 4)
            for chunk in chunks[:2]:
                tweets.append(chunk)

    # Last tweet: CTA with link
    cta = f"Full article: {article.canonical_url}"
    if len(cta) > MAX_TWEET_LEN:
        cta = cta[:MAX_TWEET_LEN]
    tweets.append(cta)

    return tweets


def post_thread(
    tweets: list[str],
    api_key: str,
    api_secret: str,
    access_token: str,
    access_secret: str,
) -> list[str]:
    """Post thread via Tweepy OAuth 1.0a. Returns list of tweet IDs."""
    import tweepy

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )
    ids = []
    prev_id = None
    for tweet_text in tweets:
        kwargs: dict = {"text": tweet_text}
        if prev_id:
            kwargs["in_reply_to_tweet_id"] = prev_id
        resp = client.create_tweet(**kwargs)
        prev_id = resp.data["id"]
        ids.append(str(prev_id))
        time.sleep(1)  # avoid rate limits between tweets
    return ids


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Publish article as Twitter/X thread")
    parser.add_argument("article", help="Path to Markdown article")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--confirm", action="store_true", default=False)
    args = parser.parse_args(argv)

    required = ["X_API_KEY", "X_API_KEY_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    article = parse_article(args.article)
    tweets = build_thread(article)

    # Validate BEFORE any API call
    validate_thread(tweets)

    if args.confirm:
        ids = post_thread(
            tweets,
            os.environ["X_API_KEY"],
            os.environ["X_API_KEY_SECRET"],
            os.environ["X_ACCESS_TOKEN"],
            os.environ["X_ACCESS_TOKEN_SECRET"],
        )
        thread_url = f"https://x.com/i/web/status/{ids[0]}"
        update_frontmatter(args.article, {"twitter_thread_id": ids[0]})
        print(f"Thread posted: {thread_url}")
        print(f"Tweet IDs: {', '.join(ids)}")
    else:
        print("=== DRY RUN — Twitter thread ===")
        for i, tweet in enumerate(tweets, 1):
            print(f"\nTweet {i}/{len(tweets)} ({len(tweet)} chars):")
            print(tweet)
            print("-" * 40)
        print("\nPass --confirm to post.")


if __name__ == "__main__":
    main()
