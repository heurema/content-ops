"""Tests for tools/publish_twitter.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import pytest
import importlib.util
import pathlib


def load_script(name):
    spec = importlib.util.spec_from_file_location(
        name, pathlib.Path(__file__).parent.parent / "tools" / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_missing_credentials_exits(tmp_path, monkeypatch, capsys):
    for v in ["X_API_KEY", "X_API_KEY_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]:
        monkeypatch.delenv(v, raising=False)
    md = tmp_path / "test.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nBody.\n")
    with pytest.raises(SystemExit) as exc:
        mod = load_script("publish_twitter")
        mod.main([str(md)])
    assert exc.value.code == 1


def test_tweet_over_280_chars_rejected(monkeypatch):
    monkeypatch.setenv("X_API_KEY", "a")
    monkeypatch.setenv("X_API_KEY_SECRET", "b")
    monkeypatch.setenv("X_ACCESS_TOKEN", "c")
    monkeypatch.setenv("X_ACCESS_TOKEN_SECRET", "d")
    mod = load_script("publish_twitter")
    long_tweet = "x" * 281
    with pytest.raises(SystemExit) as exc:
        mod.validate_thread([long_tweet])
    assert exc.value.code != 0


def test_tweet_exactly_280_chars_ok(monkeypatch):
    monkeypatch.setenv("X_API_KEY", "a")
    monkeypatch.setenv("X_API_KEY_SECRET", "b")
    monkeypatch.setenv("X_ACCESS_TOKEN", "c")
    monkeypatch.setenv("X_ACCESS_TOKEN_SECRET", "d")
    mod = load_script("publish_twitter")
    ok_tweet = "x" * 280
    # Should not raise
    mod.validate_thread([ok_tweet])


def test_dry_run_prints_thread(tmp_path, monkeypatch, capsys):
    for v, val in [("X_API_KEY", "a"), ("X_API_KEY_SECRET", "b"),
                   ("X_ACCESS_TOKEN", "c"), ("X_ACCESS_TOKEN_SECRET", "d")]:
        monkeypatch.setenv(v, val)
    md = tmp_path / "test.md"
    md.write_text(
        "---\ntitle: My Article\ndescription: Short\ndate: 2026-01-01\ntags: [python]\nlang: en\n---\n"
        "# My Article\n\nParagraph one.\n\nParagraph two.\n"
    )
    mod = load_script("publish_twitter")
    mod.main([str(md), "--dry-run"])
    out = capsys.readouterr().out
    assert "DRY RUN" in out.upper() or "dry" in out.lower()
    assert "Tweet 1" in out or "1/" in out


def test_validation_before_api_call():
    """validate_thread must appear before create_tweet in source."""
    src = pathlib.Path(__file__).parent.parent / "tools" / "publish_twitter.py"
    text = src.read_text()
    validate_line = next(i for i, l in enumerate(text.splitlines()) if "280" in l)
    api_line = next((i for i, l in enumerate(text.splitlines()) if "create_tweet" in l), None)
    assert validate_line < (api_line or float("inf")), \
        "validate_thread (280 check) must appear before create_tweet call"
