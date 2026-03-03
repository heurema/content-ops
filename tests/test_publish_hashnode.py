"""Tests for tools/publish_hashnode.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import pytest
from unittest.mock import patch, MagicMock
import importlib.util
import pathlib


def load_script(name):
    spec = importlib.util.spec_from_file_location(
        name, pathlib.Path(__file__).parent.parent / "tools" / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_missing_token_exits(tmp_path, monkeypatch, capsys):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nBody.\n")
    monkeypatch.delenv("HASHNODE_TOKEN", raising=False)
    monkeypatch.delenv("HASHNODE_PUBLICATION_ID", raising=False)
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    with pytest.raises(SystemExit) as exc:
        mod = load_script("publish_hashnode")
        mod.main([str(md)])
    assert exc.value.code == 1
    out = capsys.readouterr()
    assert "HASHNODE_TOKEN" in (out.out + out.err)


def test_dry_run_prints_mutation(tmp_path, monkeypatch, capsys):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: Test Post\ndescription: D\ndate: 2026-01-01\ntags: [python]\nlang: en\n---\nBody.\n")
    monkeypatch.setenv("HASHNODE_TOKEN", "fake")
    monkeypatch.setenv("HASHNODE_PUBLICATION_ID", "pub123")
    mod = load_script("publish_hashnode")
    mod.main([str(md), "--dry-run"])
    out = capsys.readouterr().out
    assert "DRY RUN" in out.upper() or "dry" in out.lower()
    assert "Test Post" in out


def test_graphql_mutation_sent(tmp_path, monkeypatch):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [python]\nlang: en\n---\nBody.\n")
    monkeypatch.setenv("HASHNODE_TOKEN", "fake")
    monkeypatch.setenv("HASHNODE_PUBLICATION_ID", "pub123")
    mod = load_script("publish_hashnode")
    calls = []

    def fake_post(url, *, headers, json, **kwargs):
        calls.append(json)
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = {
            "data": {"publishPost": {"post": {"id": "abc", "url": "https://hn.hashnode.dev/t"}}}
        }
        return r

    with patch("requests.post", side_effect=fake_post):
        mod.main([str(md), "--confirm"])
    assert len(calls) == 1
    assert "publishPost" in calls[0]["query"] or "mutation" in calls[0]["query"].lower()


def test_only_token_missing_exits(tmp_path, monkeypatch, capsys):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nBody.\n")
    monkeypatch.delenv("HASHNODE_TOKEN", raising=False)
    monkeypatch.setenv("HASHNODE_PUBLICATION_ID", "pub123")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    with pytest.raises(SystemExit) as exc:
        mod = load_script("publish_hashnode")
        mod.main([str(md)])
    assert exc.value.code == 1
    assert "HASHNODE_TOKEN" in capsys.readouterr().err


def test_graphql_errors_in_body_exits(tmp_path, monkeypatch):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nBody.\n")
    monkeypatch.setenv("HASHNODE_TOKEN", "fake")
    monkeypatch.setenv("HASHNODE_PUBLICATION_ID", "pub123")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    mod = load_script("publish_hashnode")

    def fake_post(url, *, headers, json, **kwargs):
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = {"errors": [{"message": "Unauthorized"}]}
        return r

    with patch("requests.post", side_effect=fake_post):
        with pytest.raises(SystemExit) as exc:
            mod.main([str(md), "--confirm"])
    assert exc.value.code == 1


def test_http_error_exits(tmp_path, monkeypatch):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nBody.\n")
    monkeypatch.setenv("HASHNODE_TOKEN", "fake")
    monkeypatch.setenv("HASHNODE_PUBLICATION_ID", "pub123")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    mod = load_script("publish_hashnode")

    def fake_post(url, *, headers, json, **kwargs):
        r = MagicMock()
        r.status_code = 401
        r.text = "Unauthorized"
        return r

    with patch("requests.post", side_effect=fake_post):
        with pytest.raises(SystemExit) as exc:
            mod.main([str(md), "--confirm"])
    assert exc.value.code == 1


def test_tag_truncation_to_five(tmp_path, monkeypatch):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a,b,c,d,e,f,g]\nlang: en\n---\nBody.\n")
    monkeypatch.setenv("HASHNODE_TOKEN", "fake")
    monkeypatch.setenv("HASHNODE_PUBLICATION_ID", "pub123")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    mod = load_script("publish_hashnode")
    calls = []

    def fake_post(url, *, headers, json, **kwargs):
        calls.append(json)
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = {
            "data": {"publishPost": {"post": {"id": "x", "url": "https://hn.hashnode.dev/x"}}}
        }
        return r

    with patch("requests.post", side_effect=fake_post):
        mod.main([str(md), "--confirm"])
    assert len(calls) == 1
    tags = calls[0]["variables"]["input"]["tags"]
    assert len(tags) <= 5, f"Expected ≤5 tags, got {len(tags)}"


def test_update_uses_existing_hashnode_id(tmp_path, monkeypatch):
    """When hashnode_id is set in frontmatter, updatePost mutation should be used."""
    md = tmp_path / "test.md"
    md.write_text(
        "---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n"
        "hashnode_id: post123\nhashnode_url: https://hn.hashnode.dev/t\n---\nBody.\n"
    )
    monkeypatch.setenv("HASHNODE_TOKEN", "fake")
    monkeypatch.setenv("HASHNODE_PUBLICATION_ID", "pub123")
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    mod = load_script("publish_hashnode")
    calls = []

    def fake_post(url, *, headers, json, **kwargs):
        calls.append(json)
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = {
            "data": {"updatePost": {"post": {"id": "post123", "url": "https://hn.hashnode.dev/t"}}}
        }
        return r

    with patch("requests.post", side_effect=fake_post):
        mod.main([str(md), "--confirm"])
    assert len(calls) == 1
    assert "updatePost" in calls[0]["query"] or "UpdatePost" in calls[0]["query"]
