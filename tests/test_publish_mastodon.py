"""Tests for tools/publish_mastodon.py"""
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
    monkeypatch.delenv("MASTODON_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("MASTODON_INSTANCE_URL", raising=False)
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nBody.\n")
    with pytest.raises(SystemExit) as exc:
        mod = load_script("publish_mastodon")
        mod.main([str(md), "--confirm"])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "MASTODON" in captured.err or "MASTODON" in captured.out


def test_dry_run_prints_status_text(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("MASTODON_ACCESS_TOKEN", "fake-token")
    monkeypatch.setenv("MASTODON_INSTANCE_URL", "https://mastodon.social")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: My Post\ndescription: A description\ndate: 2026-01-01\ntags: [python]\nlang: en\n---\nBody.\n")
    mod = load_script("publish_mastodon")
    mod.main([str(md), "--dry-run"])
    out = capsys.readouterr().out
    assert "DRY RUN" in out.upper() or "dry" in out.lower()
    assert "My Post" in out


def test_status_within_500_chars(tmp_path, monkeypatch):
    monkeypatch.setenv("MASTODON_ACCESS_TOKEN", "fake-token")
    monkeypatch.setenv("MASTODON_INSTANCE_URL", "https://mastodon.social")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: My Post\ndescription: A short description\ndate: 2026-01-01\ntags: [python]\nlang: en\n---\nBody.\n")
    mod = load_script("publish_mastodon")
    from shared.article import parse_article
    article = parse_article(str(md))
    text = mod.build_status(article)
    assert len(text) <= mod.MAX_STATUS_CHARS


def test_long_content_truncated(tmp_path, monkeypatch):
    monkeypatch.setenv("MASTODON_ACCESS_TOKEN", "fake-token")
    monkeypatch.setenv("MASTODON_INSTANCE_URL", "https://mastodon.social")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    long_title = "A" * 490
    md = tmp_path / "test.md"
    md.write_text(
        f"---\ntitle: {long_title}\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\ncanonical_url: https://example.com/article\n---\nBody.\n"
    )
    mod = load_script("publish_mastodon")
    from shared.article import parse_article
    article = parse_article(str(md))
    text = mod.build_status(article)
    assert len(text) <= mod.MAX_STATUS_CHARS


def test_confirm_calls_publish_and_writes_frontmatter(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("MASTODON_ACCESS_TOKEN", "fake-token")
    monkeypatch.setenv("MASTODON_INSTANCE_URL", "https://mastodon.social")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\ncanonical_url: https://example.com/t\n---\nBody.\n")

    mod = load_script("publish_mastodon")
    with patch.object(mod, "publish", return_value=("123456", "https://mastodon.social/@user/123456")):
        mod.main([str(md), "--confirm"])

    out = capsys.readouterr().out
    assert "Published" in out
    content = md.read_text()
    assert "mastodon_post_id" in content
