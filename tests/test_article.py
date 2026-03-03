"""Tests for tools/shared/article.py"""
import sys, os, tempfile, pathlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import pytest
from shared.article import (
    ArticleData, parse_article, update_frontmatter,
    content_hash, slugify_tag
)

SAMPLE_MD = """\
---
title: "Hello World"
description: "A test post"
date: 2026-03-03
tags:
  - python
  - claude-code
lang: en
---

# Hello World

This is the body.
"""

def test_parse_article_fields(tmp_path):
    f = tmp_path / "hello-world.md"
    f.write_text(SAMPLE_MD)
    a = parse_article(str(f))
    assert a.title == "Hello World"
    assert a.description == "A test post"
    assert a.date == "2026-03-03"
    assert a.tags == ["python", "claude-code"]
    assert a.lang == "en"
    assert a.slug == "hello-world"
    assert "This is the body." in a.body
    assert a.devto_id is None

def test_parse_article_canonical_url(tmp_path):
    f = tmp_path / "my-article.md"
    f.write_text(SAMPLE_MD.replace("lang: en", "lang: en\ncanonical_url: https://example.com/custom"))
    a = parse_article(str(f))
    assert a.canonical_url == "https://example.com/custom"

def test_parse_article_default_canonical_url(tmp_path, monkeypatch):
    f = tmp_path / "hello-world.md"
    f.write_text(SAMPLE_MD)
    monkeypatch.delenv("CONTENT_OPS_CANONICAL_BASE", raising=False)
    a = parse_article(str(f))
    # default canonical: no base URL configured, just slug-based
    assert "hello-world" in a.canonical_url

def test_content_hash_deterministic(tmp_path):
    f = tmp_path / "hello-world.md"
    f.write_text(SAMPLE_MD)
    a = parse_article(str(f))
    h1 = content_hash(a.body)
    h2 = content_hash(a.body)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex

def test_content_hash_different_bodies():
    h1 = content_hash("body one")
    h2 = content_hash("body two")
    assert h1 != h2

def test_slugify_tag_basic():
    assert slugify_tag("Context Engineering") == "context-engineering"
    assert slugify_tag("LLM") == "llm"
    assert slugify_tag("claude-code") == "claude-code"
    assert slugify_tag("  spaces  ") == "spaces"

def test_update_frontmatter_atomic(tmp_path):
    f = tmp_path / "hello-world.md"
    f.write_text(SAMPLE_MD)
    body_before = parse_article(str(f)).body

    update_frontmatter(str(f), {"devto_id": 12345, "devto_url": "https://dev.to/p/12345"})

    a = parse_article(str(f))
    assert a.devto_id == 12345
    assert a.devto_url == "https://dev.to/p/12345"
    # body must be preserved exactly
    assert a.body.strip() == body_before.strip()

def test_update_frontmatter_preserves_unknown_fields(tmp_path):
    md = SAMPLE_MD.replace("lang: en", "lang: en\ncustom_field: keep-me")
    f = tmp_path / "hello-world.md"
    f.write_text(md)
    update_frontmatter(str(f), {"devto_id": 1})
    text = f.read_text()
    assert "custom_field: keep-me" in text

def test_update_frontmatter_is_atomic(tmp_path, monkeypatch):
    """os.replace must be called (atomic write pattern)."""
    import shared.article as art
    calls = []
    real_replace = os.replace
    def fake_replace(src, dst):
        calls.append((src, dst))
        real_replace(src, dst)
    monkeypatch.setattr(os, "replace", fake_replace)
    f = tmp_path / "hello-world.md"
    f.write_text(SAMPLE_MD)
    update_frontmatter(str(f), {"devto_id": 99})
    assert len(calls) == 1, "os.replace must be called exactly once"
