"""Tests for tools/publish_linkedin.py"""
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
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("LINKEDIN_PERSON_URN", raising=False)
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nBody.\n")
    with pytest.raises(SystemExit) as exc:
        mod = load_script("publish_linkedin")
        mod.main([str(md), "--confirm"])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "LINKEDIN" in captured.err or "LINKEDIN" in captured.out


def test_dry_run_prints_payload(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "fake-token")
    monkeypatch.setenv("LINKEDIN_PERSON_URN", "urn:li:person:abc123")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: My Post\ndescription: A description\ndate: 2026-01-01\ntags: [python]\nlang: en\n---\nBody.\n")
    mod = load_script("publish_linkedin")
    mod.main([str(md), "--dry-run"])
    out = capsys.readouterr().out
    assert "DRY RUN" in out.upper() or "dry" in out.lower()
    assert "My Post" in out


def test_payload_structure(tmp_path, monkeypatch):
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "fake-token")
    monkeypatch.setenv("LINKEDIN_PERSON_URN", "urn:li:person:abc123")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: My Post\ndescription: A description\ndate: 2026-01-01\ntags: [python]\nlang: en\ncanonical_url: https://example.com/post\n---\nBody.\n")
    mod = load_script("publish_linkedin")
    from shared.article import parse_article
    article = parse_article(str(md))
    payload = mod.build_payload(article, "urn:li:person:abc123")
    assert payload["author"] == "urn:li:person:abc123"
    assert payload["lifecycleState"] == "PUBLISHED"
    content = payload["specificContent"]["com.linkedin.ugc.ShareContent"]
    assert "shareCommentary" in content
    assert "media" in content


def test_confirm_calls_publish_and_writes_frontmatter(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "fake-token")
    monkeypatch.setenv("LINKEDIN_PERSON_URN", "urn:li:person:abc123")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\ncanonical_url: https://example.com/t\n---\nBody.\n")

    mod = load_script("publish_linkedin")
    post_id = "urn:li:ugcPost:99887766"
    with patch.object(mod, "publish", return_value=(post_id, f"https://www.linkedin.com/feed/update/{post_id}/")):
        mod.main([str(md), "--confirm"])

    out = capsys.readouterr().out
    assert "Published" in out
    content = md.read_text()
    assert "linkedin_post_id" in content
