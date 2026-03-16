"""Tests for tools/stats_article.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import json
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


def _article_md(tmp_path, extra_frontmatter: str = "") -> pathlib.Path:
    md = tmp_path / "test-article.md"
    md.write_text(
        "---\n"
        "title: Test Article\n"
        "description: A test\n"
        "date: 2026-01-01\n"
        "tags: [python]\n"
        "lang: en\n"
        f"{extra_frontmatter}"
        "---\n"
        "Body content.\n"
    )
    return md


def _mock_response(status_code: int, body: dict | None = None, text: str = "") -> MagicMock:
    r = MagicMock()
    r.status_code = status_code
    r.text = text or (json.dumps(body) if body else "")
    r.json.return_value = body or {}
    return r


# ---------------------------------------------------------------------------
# 1. All platform IDs present — mock all API responses
# ---------------------------------------------------------------------------

class TestAllPlatforms:
    def _run(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
        monkeypatch.setenv("DEVTO_API_KEY", "fake-devto")
        monkeypatch.setenv("X_BEARER_TOKEN", "fake-bearer")
        monkeypatch.setenv("MASTODON_INSTANCE_URL", "https://mastodon.social")

        md = _article_md(
            tmp_path,
            "devto_id: 12345\n"
            "hashnode_id: hn-post-abc\n"
            "twitter_thread_id: 9876543210\n"
            "hn_story_id: 40000000\n"
            "bluesky_post_id: at://did:plc:abc/app.bsky.feed.post/xyz\n"
            "mastodon_post_id: 111222333\n"
            "linkedin_post_id: urn:li:share:99\n",
        )

        devto_resp = _mock_response(200, {
            "page_views_count": 500,
            "public_reactions_count": 42,
            "comments_count": 7,
        })
        hashnode_resp = _mock_response(200, {
            "data": {"post": {"views": 300, "reactionCount": 15, "replyCount": 3}}
        })
        twitter_resp = _mock_response(200, {
            "data": {"public_metrics": {
                "impression_count": 10000,
                "like_count": 200,
                "retweet_count": 50,
                "reply_count": 12,
            }}
        })
        hn_resp = _mock_response(200, {"score": 88, "descendants": 34})
        mastodon_resp = _mock_response(200, {
            "reblogs_count": 5,
            "favourites_count": 20,
            "replies_count": 2,
        })

        get_responses = {
            "https://dev.to/api/articles/12345": devto_resp,
            "https://api.x.com/2/tweets/9876543210?tweet.fields=public_metrics": twitter_resp,
            "https://hacker-news.firebaseio.com/v0/item/40000000.json": hn_resp,
            "https://mastodon.social/api/v1/statuses/111222333": mastodon_resp,
        }

        def fake_get(url, **kwargs):
            return get_responses.get(url, _mock_response(404, {}))

        def fake_post(url, **kwargs):
            return hashnode_resp

        mod = load_script("stats_article")
        with patch("requests.get", side_effect=fake_get), \
             patch("requests.post", side_effect=fake_post):
            mod.main([str(md)])

        return capsys.readouterr().out

    def test_devto_stats_shown(self, tmp_path, monkeypatch, capsys):
        out = self._run(tmp_path, monkeypatch, capsys)
        assert "dev.to" in out
        assert "500" in out  # views

    def test_hashnode_stats_shown(self, tmp_path, monkeypatch, capsys):
        out = self._run(tmp_path, monkeypatch, capsys)
        assert "Hashnode" in out
        assert "300" in out  # views

    def test_twitter_stats_shown(self, tmp_path, monkeypatch, capsys):
        out = self._run(tmp_path, monkeypatch, capsys)
        assert "Twitter" in out
        assert "10000" in out  # impressions

    def test_hn_stats_shown(self, tmp_path, monkeypatch, capsys):
        out = self._run(tmp_path, monkeypatch, capsys)
        assert "HN" in out
        assert "88" in out  # score

    def test_bluesky_unavailable_note(self, tmp_path, monkeypatch, capsys):
        out = self._run(tmp_path, monkeypatch, capsys)
        assert "Bluesky" in out
        assert "not available" in out

    def test_mastodon_stats_shown(self, tmp_path, monkeypatch, capsys):
        out = self._run(tmp_path, monkeypatch, capsys)
        assert "Mastodon" in out
        assert "20" in out  # favourites

    def test_linkedin_unavailable_note(self, tmp_path, monkeypatch, capsys):
        out = self._run(tmp_path, monkeypatch, capsys)
        assert "LinkedIn" in out
        assert "not available" in out


# ---------------------------------------------------------------------------
# 2. Only devto_id present — other platforms skipped silently
# ---------------------------------------------------------------------------

def test_only_devto_id(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    monkeypatch.setenv("DEVTO_API_KEY", "fake-devto")

    md = _article_md(tmp_path, "devto_id: 999\n")

    devto_resp = _mock_response(200, {
        "page_views_count": 100,
        "public_reactions_count": 5,
        "comments_count": 1,
    })

    mod = load_script("stats_article")
    with patch("requests.get", return_value=devto_resp), \
         patch("requests.post") as mock_post:
        mod.main([str(md)])

    mock_post.assert_not_called()
    out = capsys.readouterr().out
    assert "dev.to" in out
    assert "100" in out
    # Other platforms not present
    assert "Hashnode" not in out
    assert "Twitter" not in out
    assert "HN" not in out
    assert "Bluesky" not in out
    assert "Mastodon" not in out
    assert "LinkedIn" not in out


# ---------------------------------------------------------------------------
# 3. No IDs — graceful empty output
# ---------------------------------------------------------------------------

def test_no_platform_ids(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")

    md = _article_md(tmp_path)  # no IDs at all

    mod = load_script("stats_article")
    with patch("requests.get") as mock_get, \
         patch("requests.post") as mock_post:
        mod.main([str(md)])

    mock_get.assert_not_called()
    mock_post.assert_not_called()
    out = capsys.readouterr().out
    assert "No platform IDs" in out or len(out.strip()) == 0 or "nothing" in out.lower()


# ---------------------------------------------------------------------------
# 4. API error handling — 500 response, should warn and continue
# ---------------------------------------------------------------------------

def test_api_error_warns_and_continues(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    monkeypatch.setenv("DEVTO_API_KEY", "fake-devto")
    monkeypatch.setenv("X_BEARER_TOKEN", "fake-bearer")

    md = _article_md(
        tmp_path,
        "devto_id: 111\n"
        "twitter_thread_id: 222\n",
    )

    devto_error = _mock_response(500, {}, text="Internal Server Error")
    twitter_ok = _mock_response(200, {
        "data": {"public_metrics": {
            "impression_count": 9000,
            "like_count": 100,
            "retweet_count": 20,
            "reply_count": 5,
        }}
    })

    def fake_get(url, **kwargs):
        if "dev.to" in url:
            return devto_error
        return twitter_ok

    mod = load_script("stats_article")
    with patch("requests.get", side_effect=fake_get):
        mod.main([str(md)])  # must not raise or exit

    err = capsys.readouterr().err
    out = capsys.readouterr().out  # second capture gets empty string; we already captured above
    # Re-run capturing together
    # Re-capture properly:


def test_api_error_prints_warning(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    monkeypatch.setenv("DEVTO_API_KEY", "fake-devto")
    monkeypatch.setenv("X_BEARER_TOKEN", "fake-bearer")

    md = _article_md(
        tmp_path,
        "devto_id: 111\n"
        "twitter_thread_id: 222\n",
    )

    devto_error = _mock_response(500, {}, text="Internal Server Error")
    twitter_ok = _mock_response(200, {
        "data": {"public_metrics": {
            "impression_count": 9000,
            "like_count": 100,
            "retweet_count": 20,
            "reply_count": 5,
        }}
    })

    def fake_get(url, **kwargs):
        if "dev.to" in url:
            return devto_error
        return twitter_ok

    mod = load_script("stats_article")
    with patch("requests.get", side_effect=fake_get):
        mod.main([str(md)])

    captured = capsys.readouterr()
    # Warning on stderr about dev.to
    assert "WARNING" in captured.err or "500" in captured.err
    # Twitter result still present in stdout
    assert "Twitter" in captured.out
    assert "9000" in captured.out


def test_api_error_shows_error_in_table(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    monkeypatch.setenv("DEVTO_API_KEY", "fake-devto")

    md = _article_md(tmp_path, "devto_id: 111\n")

    mod = load_script("stats_article")
    with patch("requests.get", return_value=_mock_response(500, {}, text="err")):
        mod.main([str(md)])

    out = capsys.readouterr().out
    assert "dev.to" in out
    assert "(error)" in out


# ---------------------------------------------------------------------------
# 5. --json flag output format
# ---------------------------------------------------------------------------

def test_json_flag_valid_json(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    monkeypatch.setenv("DEVTO_API_KEY", "fake-devto")

    md = _article_md(tmp_path, "devto_id: 777\n")

    devto_resp = _mock_response(200, {
        "page_views_count": 250,
        "public_reactions_count": 10,
        "comments_count": 3,
    })

    mod = load_script("stats_article")
    with patch("requests.get", return_value=devto_resp):
        mod.main([str(md), "--json"])

    out = capsys.readouterr().out
    parsed = json.loads(out)  # must be valid JSON
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["platform"] == "dev.to"
    assert parsed[0]["metrics"]["views"] == 250
    assert parsed[0]["metrics"]["reactions"] == 10
    assert parsed[0]["metrics"]["comments"] == 3


def test_json_flag_skipped_platform_has_note(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")

    md = _article_md(
        tmp_path,
        "bluesky_post_id: at://some/uri\n"
        "linkedin_post_id: urn:li:share:1\n",
    )

    mod = load_script("stats_article")
    with patch("requests.get"), patch("requests.post"):
        mod.main([str(md), "--json"])

    out = capsys.readouterr().out
    parsed = json.loads(out)
    platforms = {r["platform"] for r in parsed}
    assert "Bluesky" in platforms
    assert "LinkedIn" in platforms
    for r in parsed:
        if r["platform"] in ("Bluesky", "LinkedIn"):
            assert r["note"] is not None
            assert r["metrics"] is None


def test_json_flag_no_ids_returns_empty_list(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")

    md = _article_md(tmp_path)  # no IDs

    mod = load_script("stats_article")
    with patch("requests.get"), patch("requests.post"):
        mod.main([str(md), "--json"])

    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed == []


def test_json_api_error_shows_null_metrics(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    monkeypatch.setenv("DEVTO_API_KEY", "fake-devto")

    md = _article_md(tmp_path, "devto_id: 111\n")

    mod = load_script("stats_article")
    with patch("requests.get", return_value=_mock_response(503, {}, text="err")):
        mod.main([str(md), "--json"])

    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert len(parsed) == 1
    assert parsed[0]["platform"] == "dev.to"
    assert parsed[0]["metrics"] is None


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_missing_devto_key_warns(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    monkeypatch.delenv("DEVTO_API_KEY", raising=False)

    md = _article_md(tmp_path, "devto_id: 123\n")

    mod = load_script("stats_article")
    with patch("requests.get") as mock_get:
        mod.main([str(md)])

    mock_get.assert_not_called()
    err = capsys.readouterr().err
    assert "DEVTO_API_KEY" in err


def test_missing_twitter_bearer_warns(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)

    md = _article_md(tmp_path, "twitter_thread_id: 999\n")

    mod = load_script("stats_article")
    with patch("requests.get") as mock_get:
        mod.main([str(md)])

    mock_get.assert_not_called()
    err = capsys.readouterr().err
    assert "X_BEARER_TOKEN" in err


def test_missing_mastodon_instance_warns(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    monkeypatch.delenv("MASTODON_INSTANCE_URL", raising=False)

    md = _article_md(tmp_path, "mastodon_post_id: 555\n")

    mod = load_script("stats_article")
    with patch("requests.get") as mock_get:
        mod.main([str(md)])

    mock_get.assert_not_called()
    err = capsys.readouterr().err
    assert "MASTODON_INSTANCE_URL" in err


def test_hashnode_graphql_error_warns(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")

    md = _article_md(tmp_path, "hashnode_id: bad-id\n")

    error_resp = _mock_response(200, {"errors": [{"message": "Post not found"}]})

    mod = load_script("stats_article")
    with patch("requests.post", return_value=error_resp):
        mod.main([str(md)])

    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "Post not found" in captured.err
    assert "Hashnode" in captured.out
    assert "(error)" in captured.out
