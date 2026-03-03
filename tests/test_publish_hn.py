"""Tests for tools/publish_hn.py"""
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


def test_submitlink_url_generated(tmp_path, monkeypatch, capsys):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: My Article\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nBody.\n")

    def fake_get(url, *, params=None, timeout=None):
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = {"hits": []}
        return r

    with patch("requests.get", side_effect=fake_get):
        mod = load_script("publish_hn")
        mod.main([str(md)])
    out = capsys.readouterr().out
    assert "news.ycombinator.com/submitlink" in out
    assert "My+Article" in out or "My%20Article" in out or "My Article" in out


def test_algolia_duplicate_check(tmp_path, monkeypatch, capsys):
    md = tmp_path / "test.md"
    md.write_text(
        "---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n"
        "canonical_url: https://example.com/p\n---\nBody.\n"
    )

    def fake_get(url, *, params=None, timeout=None):
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = {
            "hits": [{"objectID": "123", "title": "T", "url": "https://example.com/p"}]
        }
        return r

    with patch("requests.get", side_effect=fake_get):
        mod = load_script("publish_hn")
        mod.main([str(md)])
    out = capsys.readouterr().out
    assert "already" in out.lower() or "duplicate" in out.lower() or "found" in out.lower()


def test_algolia_timeout_graceful(tmp_path, monkeypatch, capsys):
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nBody.\n")
    import requests as req

    def fake_get(url, *, params=None, timeout=None):
        raise req.exceptions.Timeout("timeout")

    with patch("requests.get", side_effect=fake_get):
        mod = load_script("publish_hn")
        mod.main([str(md)])
    out = capsys.readouterr().out
    assert "news.ycombinator.com/submitlink" in out


def test_no_auth_credentials_needed():
    """publish_hn.py must not reference DEVTO_API_KEY or HASHNODE_TOKEN."""
    src = pathlib.Path(__file__).parent.parent / "tools" / "publish_hn.py"
    text = src.read_text()
    assert "DEVTO_API_KEY" not in text
    assert "HASHNODE_TOKEN" not in text
