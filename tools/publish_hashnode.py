#!/usr/bin/env python3
"""Publish a Markdown article to Hashnode via GraphQL API.

Usage:
    python3 publish_hashnode.py <article.md> [--dry-run] [--confirm]

Env vars required:
    HASHNODE_TOKEN            — personal access token
    HASHNODE_PUBLICATION_ID   — publication ID from Hashnode dashboard
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

_HTTP_TIMEOUT = (10, 30)
_MAX_RETRIES = 3


def _gql(headers, payload):
    """Execute GraphQL request with retry on 429."""
    for attempt in range(_MAX_RETRIES):
        resp = requests.post(HASHNODE_API, headers=headers, json=payload, timeout=_HTTP_TIMEOUT)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 2 ** attempt))
            print(f"Rate limited — waiting {wait}s (attempt {attempt + 1}/{_MAX_RETRIES})", file=sys.stderr)
            time.sleep(wait)
            continue
        return resp
    return resp

sys.path.insert(0, str(Path(__file__).parent))
from shared.env import load as _load_env; _load_env()
from shared.article import ArticleData, parse_article, update_frontmatter, slugify_tag

HASHNODE_API = "https://gql.hashnode.com"

PUBLISH_MUTATION = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post {
      id
      url
    }
  }
}
"""

UPDATE_MUTATION = """
mutation UpdatePost($input: UpdatePostInput!) {
  updatePost(input: $input) {
    post {
      id
      url
    }
  }
}
"""


def build_variables(article: ArticleData, publication_id: str) -> dict:
    tags = [{"name": t, "slug": slugify_tag(t)} for t in article.tags[:5]]
    return {
        "input": {
            "title": article.title,
            "contentMarkdown": article.body,
            "subtitle": article.description,
            "tags": tags,
            "originalArticleURL": article.canonical_url,
            "publicationId": publication_id,
        }
    }


def publish(article: ArticleData, token: str, publication_id: str) -> tuple[str, str]:
    """Create or update post via GraphQL. Returns (post_id, url)."""
    headers = {"Authorization": token, "Content-Type": "application/json"}

    if article.hashnode_id:
        # Update existing post
        variables = {"input": {"id": article.hashnode_id, **build_variables(article, publication_id)["input"]}}
        payload = {"query": UPDATE_MUTATION, "variables": variables}
        op_key = "updatePost"
    else:
        variables = build_variables(article, publication_id)
        payload = {"query": PUBLISH_MUTATION, "variables": variables}
        op_key = "publishPost"

    resp = _gql(headers, payload)
    if resp.status_code != 200:
        body_preview = resp.text[:200] if resp.text else "(empty body)"
        print(f"ERROR: Hashnode API {resp.status_code}: {body_preview}", file=sys.stderr)
        sys.exit(1)

    body = resp.json()
    if "errors" in body:
        # Sanitize: don't dump raw GraphQL errors (may echo content fragments)
        error_msgs = [e.get("message", "unknown error") for e in body["errors"]]
        print(f"ERROR: GraphQL errors: {'; '.join(error_msgs)}", file=sys.stderr)
        sys.exit(1)

    try:
        post = body["data"][op_key]["post"]
        return post["id"], post["url"]
    except (KeyError, TypeError) as exc:
        print(f"ERROR: Unexpected Hashnode response shape ({exc}): {str(body)[:200]}", file=sys.stderr)
        sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Publish article to Hashnode")
    parser.add_argument("article", help="Path to Markdown article")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--confirm", action="store_true", default=False)
    args = parser.parse_args(argv)

    token = os.environ.get("HASHNODE_TOKEN")
    publication_id = os.environ.get("HASHNODE_PUBLICATION_ID")
    if not token or not publication_id:
        missing = ", ".join(
            v for v in ["HASHNODE_TOKEN", "HASHNODE_PUBLICATION_ID"]
            if not os.environ.get(v)
        )
        print(f"ERROR: Missing env vars: {missing}", file=sys.stderr)
        sys.exit(1)

    article = parse_article(args.article)
    variables = build_variables(article, publication_id)

    if args.confirm:
        post_id, post_url = publish(article, token, publication_id)
        update_frontmatter(args.article, {"hashnode_id": post_id, "hashnode_url": post_url})
        print(f"Published: {post_url}")
        print(f"Frontmatter updated: hashnode_id={post_id}")
    else:
        print("=== DRY RUN — Hashnode GraphQL variables ===")
        print(json.dumps(variables, indent=2, ensure_ascii=False))
        print("\nPass --confirm to publish.")


if __name__ == "__main__":
    main()
