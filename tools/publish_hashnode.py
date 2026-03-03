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
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
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
    """Execute GraphQL publishPost mutation. Returns (post_id, url)."""
    headers = {"Authorization": token, "Content-Type": "application/json"}
    variables = build_variables(article, publication_id)
    payload = {"query": PUBLISH_MUTATION, "variables": variables}

    resp = requests.post(HASHNODE_API, headers=headers, json=payload)
    if resp.status_code != 200:
        token_hint = token[:4] + "***"
        print(
            f"ERROR: Hashnode API {resp.status_code} (token={token_hint})",
            file=sys.stderr,
        )
        sys.exit(1)

    body = resp.json()
    if "errors" in body:
        print(f"ERROR: GraphQL errors: {body['errors']}", file=sys.stderr)
        sys.exit(1)

    post = body["data"]["publishPost"]["post"]
    return post["id"], post["url"]


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
