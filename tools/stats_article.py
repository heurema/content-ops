#!/usr/bin/env python3
"""Fetch engagement stats for a published article from all platforms.

Usage:
    python3 stats_article.py <article.md> [--json]

Reads platform IDs from article frontmatter and queries each platform's API.
Platforms with no stored ID are silently skipped.
Platforms with missing env vars are skipped with a warning.
API errors print a warning and continue — partial results are shown.

Env vars (all optional — platforms without credentials are skipped):
    DEVTO_API_KEY           — dev.to API key
    X_BEARER_TOKEN          — Twitter/X Bearer token (read-only)
    MASTODON_INSTANCE_URL   — e.g. https://mastodon.social
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

_HTTP_TIMEOUT = (10, 30)

sys.path.insert(0, str(Path(__file__).parent))
from shared.env import load as _load_env; _load_env()
from shared.article import parse_article, ArticleData


# ---------------------------------------------------------------------------
# Per-platform stat fetchers
# Each returns a dict of metric_name -> int, or None on skip/error.
# Warnings are printed to stderr; the caller continues regardless.
# ---------------------------------------------------------------------------

def _fetch_devto(article: ArticleData) -> dict[str, int] | None:
    if not article.devto_id:
        return None
    api_key = os.environ.get("DEVTO_API_KEY")
    if not api_key:
        print("WARNING: DEVTO_API_KEY not set — skipping dev.to stats", file=sys.stderr)
        return None
    url = f"https://dev.to/api/articles/{article.devto_id}"
    try:
        resp = requests.get(url, headers={"api-key": api_key}, timeout=_HTTP_TIMEOUT)
    except requests.RequestException as exc:
        print(f"WARNING: dev.to request failed: {exc}", file=sys.stderr)
        return None
    if resp.status_code != 200:
        print(f"WARNING: dev.to returned {resp.status_code} — skipping", file=sys.stderr)
        return None
    data = resp.json()
    return {
        "views": data.get("page_views_count", 0),
        "reactions": data.get("public_reactions_count", 0),
        "comments": data.get("comments_count", 0),
    }


def _fetch_hashnode(article: ArticleData) -> dict[str, int] | None:
    if not article.hashnode_id:
        return None
    query = """
    query($id: ObjectId!) {
        post(id: $id) {
            views
            reactionCount
            replyCount
        }
    }
    """
    payload = {"query": query, "variables": {"id": article.hashnode_id}}
    try:
        resp = requests.post(
            "https://gql.hashnode.com",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=_HTTP_TIMEOUT,
        )
    except requests.RequestException as exc:
        print(f"WARNING: Hashnode request failed: {exc}", file=sys.stderr)
        return None
    if resp.status_code != 200:
        print(f"WARNING: Hashnode returned {resp.status_code} — skipping", file=sys.stderr)
        return None
    body = resp.json()
    if body.get("errors"):
        msg = body["errors"][0].get("message", "unknown error")
        print(f"WARNING: Hashnode GraphQL error: {msg} — skipping", file=sys.stderr)
        return None
    post = (body.get("data") or {}).get("post") or {}
    return {
        "views": post.get("views", 0),
        "reactions": post.get("reactionCount", 0),
        "replies": post.get("replyCount", 0),
    }


def _fetch_twitter(article: ArticleData) -> dict[str, int] | None:
    if not article.twitter_thread_id:
        return None
    bearer = os.environ.get("X_BEARER_TOKEN")
    if not bearer:
        print("WARNING: X_BEARER_TOKEN not set — skipping Twitter/X stats", file=sys.stderr)
        return None
    url = (
        f"https://api.x.com/2/tweets/{article.twitter_thread_id}"
        "?tweet.fields=public_metrics"
    )
    try:
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {bearer}"},
            timeout=_HTTP_TIMEOUT,
        )
    except requests.RequestException as exc:
        print(f"WARNING: Twitter/X request failed: {exc}", file=sys.stderr)
        return None
    if resp.status_code != 200:
        print(f"WARNING: Twitter/X returned {resp.status_code} — skipping", file=sys.stderr)
        return None
    metrics = (resp.json().get("data") or {}).get("public_metrics") or {}
    return {
        "impressions": metrics.get("impression_count", 0),
        "likes": metrics.get("like_count", 0),
        "retweets": metrics.get("retweet_count", 0),
        "replies": metrics.get("reply_count", 0),
    }


def _fetch_hn(article: ArticleData) -> dict[str, int] | None:
    hn_id = article.frontmatter.get("hn_story_id")
    if not hn_id:
        return None
    url = f"https://hacker-news.firebaseio.com/v0/item/{hn_id}.json"
    try:
        resp = requests.get(url, timeout=_HTTP_TIMEOUT)
    except requests.RequestException as exc:
        print(f"WARNING: HN request failed: {exc}", file=sys.stderr)
        return None
    if resp.status_code != 200:
        print(f"WARNING: HN returned {resp.status_code} — skipping", file=sys.stderr)
        return None
    data = resp.json() or {}
    return {
        "score": data.get("score", 0),
        "comments": data.get("descendants", 0),
    }


def _fetch_bluesky(_article: ArticleData) -> dict[str, int] | None:
    # AT Protocol metrics not straightforward — skip
    return None


def _fetch_mastodon(article: ArticleData) -> dict[str, int] | None:
    if not article.mastodon_post_id:
        return None
    instance_url = os.environ.get("MASTODON_INSTANCE_URL", "").rstrip("/")
    if not instance_url:
        print("WARNING: MASTODON_INSTANCE_URL not set — skipping Mastodon stats", file=sys.stderr)
        return None
    url = f"{instance_url}/api/v1/statuses/{article.mastodon_post_id}"
    try:
        resp = requests.get(url, timeout=_HTTP_TIMEOUT)
    except requests.RequestException as exc:
        print(f"WARNING: Mastodon request failed: {exc}", file=sys.stderr)
        return None
    if resp.status_code != 200:
        print(f"WARNING: Mastodon returned {resp.status_code} — skipping", file=sys.stderr)
        return None
    data = resp.json()
    return {
        "reblogs": data.get("reblogs_count", 0),
        "favourites": data.get("favourites_count", 0),
        "replies": data.get("replies_count", 0),
    }


def _fetch_linkedin(_article: ArticleData) -> dict[str, int] | None:
    # Requires Marketing API approval — skip
    return None


# ---------------------------------------------------------------------------
# Platform registry: (name, id_field, fetcher, skipped_note)
# ---------------------------------------------------------------------------

_PLATFORMS: list[tuple[str, str | None, Any, str | None]] = [
    ("dev.to",    "devto_id",          _fetch_devto,    None),
    ("Hashnode",  "hashnode_id",        _fetch_hashnode, None),
    ("Twitter/X", "twitter_thread_id", _fetch_twitter,  None),
    ("HN",        "hn_story_id",       _fetch_hn,       None),
    ("Bluesky",   "bluesky_post_id",   _fetch_bluesky,  "stats not available"),
    ("Mastodon",  "mastodon_post_id",  _fetch_mastodon, None),
    ("LinkedIn",  "linkedin_post_id",  _fetch_linkedin, "stats not available"),
]


def collect_stats(article: ArticleData) -> list[dict]:
    """Return list of {platform, metrics, note} dicts for all platforms."""
    results = []
    for name, id_field, fetcher, skip_note in _PLATFORMS:
        # Resolve the ID — some are on frontmatter directly (hn_story_id)
        if id_field == "hn_story_id":
            has_id = bool(article.frontmatter.get("hn_story_id"))
        else:
            has_id = bool(getattr(article, id_field, None))

        if not has_id:
            continue  # no ID stored — platform not published there yet

        if skip_note:
            results.append({"platform": name, "metrics": None, "note": skip_note})
            continue

        metrics = fetcher(article)
        results.append({"platform": name, "metrics": metrics, "note": None})

    return results


def _fmt_metrics(metrics: dict[str, int] | None) -> str:
    if metrics is None:
        return "(error)"
    return "  ".join(f"{k}: {v}" for k, v in metrics.items())


def print_table(results: list[dict]) -> None:
    if not results:
        print("No platform IDs found in frontmatter — nothing to fetch.")
        return

    col_w = max(len(r["platform"]) for r in results) + 2
    header = f"{'Platform':<{col_w}}  Stats"
    print(header)
    print("-" * (col_w + 40))
    for r in results:
        platform = r["platform"]
        if r["note"]:
            detail = r["note"]
        else:
            detail = _fmt_metrics(r["metrics"])
        print(f"{platform:<{col_w}}  {detail}")


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch engagement stats for a published article"
    )
    parser.add_argument("article", help="Path to Markdown article")
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output machine-readable JSON instead of a table",
    )
    args = parser.parse_args(argv)

    article = parse_article(args.article)
    results = collect_stats(article)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_table(results)


if __name__ == "__main__":
    main()
