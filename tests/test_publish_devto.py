"""Tests for tools/publish_devto.py"""
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


def test_missing_api_key_exits(tmp_path, monkeypatch, capsys):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [python]\nlang: en\n---\nBody.\n")
    monkeypatch.delenv("DEVTO_API_KEY", raising=False)
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    with pytest.raises(SystemExit) as exc:
        mod = load_script("publish_devto")
        mod.main([str(md)])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "DEVTO_API_KEY" in captured.out or "DEVTO_API_KEY" in captured.err


def test_dry_run_prints_payload(tmp_path, monkeypatch, capsys):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: Test Post\ndescription: A desc\ndate: 2026-01-01\ntags: [python]\nlang: en\n---\nBody.\n")
    monkeypatch.setenv("DEVTO_API_KEY", "fake-key")
    mod = load_script("publish_devto")
    mod.main([str(md), "--dry-run"])
    out = capsys.readouterr().out
    assert "Test Post" in out
    assert "DRY RUN" in out.upper() or "dry" in out.lower()


def test_tag_truncation_to_four(tmp_path, monkeypatch, capsys):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a,b,c,d,e,f]\nlang: en\n---\nBody.\n")
    monkeypatch.setenv("DEVTO_API_KEY", "fake-key")
    mod = load_script("publish_devto")
    payloads = []

    def fake_post(url, *, headers, json, **kwargs):
        payloads.append(json)
        r = MagicMock()
        r.status_code = 201
        r.json.return_value = {"id": 1, "url": "https://dev.to/p/1"}
        return r

    with patch("requests.post", side_effect=fake_post), \
         patch("requests.put", side_effect=fake_post):
        mod.main([str(md), "--confirm"])
    assert len(payloads) == 1
    tags = payloads[0]["article"]["tags"]
    assert len(tags) <= 4, f"Expected ≤4 tags, got {len(tags)}: {tags}"


def test_put_when_devto_id_exists(tmp_path, monkeypatch, capsys):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [python]\nlang: en\ndevto_id: 999\ndevto_url: https://dev.to/p/999\n---\nBody.\n")
    monkeypatch.setenv("DEVTO_API_KEY", "fake-key")
    mod = load_script("publish_devto")
    put_calls = []

    def fake_put(url, *, headers, json, **kwargs):
        put_calls.append(url)
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = {"id": 999, "url": "https://dev.to/p/999"}
        return r

    with patch("requests.put", side_effect=fake_put), \
         patch("requests.post") as mock_post:
        mod.main([str(md), "--confirm"])
    assert len(put_calls) == 1
    assert "999" in put_calls[0]
    mock_post.assert_not_called()
