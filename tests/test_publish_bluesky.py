"""Tests for tools/publish_bluesky.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import pytest
from unittest.mock import patch, MagicMock
import importlib.util
import pathlib


def load_script(name):
    spec = importlib.util.spec_from_file_location(
        name,
        pathlib.Path(__file__).parent.parent / "tools" / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_missing_credentials_exits(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("BLUESKY_HANDLE", raising=False)
    monkeypatch.delenv("BLUESKY_APP_PASSWORD", raising=False)
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nBody.\n")
    with pytest.raises(SystemExit) as exc:
        mod = load_script("publish_bluesky")
        mod.main([str(md), "--confirm"])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "BLUESKY_HANDLE" in captured.err or "BLUESKY_HANDLE" in captured.out


def test_dry_run_prints_post_text(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("BLUESKY_HANDLE", "test.bsky.social")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "fake-password")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: My Post\ndescription: A description\ndate: 2026-01-01\ntags: [python]\nlang: en\n---\nBody.\n")
    mod = load_script("publish_bluesky")
    mod.main([str(md), "--dry-run"])
    out = capsys.readouterr().out
    assert "DRY RUN" in out.upper() or "dry" in out.lower()
    assert "My Post" in out


def test_post_text_within_300_graphemes(tmp_path, monkeypatch):
    monkeypatch.setenv("BLUESKY_HANDLE", "test.bsky.social")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "fake-password")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: My Post\ndescription: A short description\ndate: 2026-01-01\ntags: [python]\nlang: en\n---\nBody.\n")
    mod = load_script("publish_bluesky")
    from shared.article import parse_article
    article = parse_article(str(md))
    text = mod.build_post_text(article)
    assert len(text) <= mod.MAX_POST_GRAPHEMES


def test_long_title_truncated(tmp_path, monkeypatch):
    monkeypatch.setenv("BLUESKY_HANDLE", "test.bsky.social")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "fake-password")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    long_title = "A" * 290
    md = tmp_path / "test.md"
    md.write_text(
        f"---\ntitle: {long_title}\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\ncanonical_url: https://example.com/article\n---\nBody.\n"
    )
    mod = load_script("publish_bluesky")
    from shared.article import parse_article
    article = parse_article(str(md))
    text = mod.build_post_text(article)
    assert len(text) <= mod.MAX_POST_GRAPHEMES


def test_confirm_calls_publish_and_writes_frontmatter(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("BLUESKY_HANDLE", "test.bsky.social")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "fake-password")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\ncanonical_url: https://example.com/t\n---\nBody.\n")

    mock_resp = MagicMock()
    mock_resp.uri = "at://did:plc:abc123/app.bsky.feed.post/3jtest"

    mod = load_script("publish_bluesky")
    with patch.object(mod, "publish", return_value=("3jtest", "https://bsky.app/profile/test.bsky.social/post/3jtest")):
        mod.main([str(md), "--confirm"])

    out = capsys.readouterr().out
    assert "Published" in out
    content = md.read_text()
    assert "bluesky_post_id" in content
