#!/usr/bin/env python3
"""Generate a Hacker News submitlink URL for an article (no auth required).

Also checks Algolia HN search for potential duplicates.

Usage:
    python3 publish_hn.py <article.md>

No credentials needed. Opens submitlink in browser or prints URL to copy.
"""
from __future__ import annotations

import sys
import urllib.parse
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from shared.article import parse_article

ALGOLIA_SEARCH = "https://hn.algolia.com/api/v1/search"
HN_SUBMITLINK = "https://news.ycombinator.com/submitlink"


def check_duplicates(canonical_url: str, title: str) -> list[dict]:
    """Search Algolia for existing HN submissions of this URL."""
    try:
        resp = requests.get(
            ALGOLIA_SEARCH,
            params={"query": canonical_url, "restrictSearchableAttributes": "url"},
            timeout=5,
        )
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        return [h for h in hits if canonical_url in h.get("url", "")]
    except requests.exceptions.Timeout:
        print("WARNING: Algolia duplicate check timed out — skipping.", file=sys.stderr)
        return []
    except Exception as e:
        print(f"WARNING: Algolia check failed: {e}", file=sys.stderr)
        return []


def submitlink_url(title: str, url: str) -> str:
    params = urllib.parse.urlencode({"u": url, "t": title})
    return f"{HN_SUBMITLINK}?{params}"


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate HN submitlink for an article")
    parser.add_argument("article", help="Path to Markdown article")
    args = parser.parse_args(argv)

    article = parse_article(args.article)

    # Duplicate check (graceful — never blocks submitlink output)
    dupes = check_duplicates(article.canonical_url, article.title)
    if dupes:
        print(f"WARNING: Article may already be on HN ({len(dupes)} match(es) found):")
        for d in dupes[:3]:
            hn_id = d.get("objectID")
            print(
                f"  - https://news.ycombinator.com/item?id={hn_id} — {d.get('title', '')}"
            )
        print()

    link = submitlink_url(article.title, article.canonical_url)
    print("=== Hacker News submitlink ===")
    print(link)
    print("\nOpen this URL in your browser to submit (human-in-loop).")
    print("Tip: Add 'Show HN: ' prefix if it's a project you built.")


if __name__ == "__main__":
    main()
