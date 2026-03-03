"""Tests for tools/lint_article.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import importlib.util
import pathlib
import pytest


def load_script(name):
    spec = importlib.util.spec_from_file_location(
        name,
        pathlib.Path(__file__).parent.parent / "tools" / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def mod(monkeypatch):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    return load_script("lint_article")


@pytest.fixture
def good_md(tmp_path):
    md = tmp_path / "article.md"
    md.write_text(
        "---\ntitle: Good Article\ndescription: A short description.\ndate: 2026-01-01\ntags: [python, ai]\nlang: en\n---\nBody text here.\n"
    )
    return md


# ---------------------------------------------------------------------------
# check_em_dashes
# ---------------------------------------------------------------------------

def test_em_dash_in_prose_detected(mod):
    body = "This is a sentence — with em dash."
    issues = mod.check_em_dashes(body)
    assert len(issues) == 1
    assert issues[0][0] == "ERROR"
    assert "—" in issues[0][1]


def test_em_dash_in_fenced_code_ignored(mod):
    body = "Prose here.\n\n```\ncode — with dash\n```\n"
    issues = mod.check_em_dashes(body)
    assert issues == []


def test_em_dash_in_inline_code_ignored(mod):
    body = "Use `foo—bar` for something."
    issues = mod.check_em_dashes(body)
    assert issues == []


def test_em_dash_in_prose_and_inline_code(mod):
    """Em dash in prose should be detected; inline code should not affect count."""
    body = "Use `foo—bar` and also — this."
    issues = mod.check_em_dashes(body)
    assert len(issues) == 1
    assert "1×" in issues[0][1]  # only 1 prose em-dash counted


def test_no_em_dash(mod):
    body = "Clean text with hyphens - and more."
    assert mod.check_em_dashes(body) == []


# ---------------------------------------------------------------------------
# check_en_dashes
# ---------------------------------------------------------------------------

def test_en_dash_in_prose_warned(mod):
    body = "Range: 1–10."
    issues = mod.check_en_dashes(body)
    assert len(issues) == 1
    assert issues[0][0] == "WARNING"


def test_en_dash_in_inline_code_ignored(mod):
    body = "Use `1–10` for range."
    assert mod.check_en_dashes(body) == []


# ---------------------------------------------------------------------------
# check_description_length
# ---------------------------------------------------------------------------

def test_description_over_160_is_error(mod):
    desc = "x" * 161
    issues = mod.check_description_length(desc)
    assert any(i[0] == "ERROR" for i in issues)


def test_description_151_to_160_is_warning(mod):
    desc = "x" * 155
    issues = mod.check_description_length(desc)
    assert issues[0][0] == "WARNING"


def test_description_under_150_ok(mod):
    assert mod.check_description_length("x" * 150) == []


# ---------------------------------------------------------------------------
# check_required_frontmatter
# ---------------------------------------------------------------------------

def test_missing_title_is_error(tmp_path, mod, monkeypatch):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "a.md"
    md.write_text("---\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nBody.\n")
    from shared.article import parse_article
    article = parse_article(str(md))
    issues = mod.check_required_frontmatter(article)
    assert any("title" in msg for _, msg in issues)


def test_missing_date_is_warning(tmp_path, mod):
    md = tmp_path / "a.md"
    md.write_text("---\ntitle: T\ndescription: D\ntags: [a]\nlang: en\n---\nBody.\n")
    from shared.article import parse_article
    article = parse_article(str(md))
    issues = mod.check_required_frontmatter(article)
    date_issues = [(lvl, msg) for lvl, msg in issues if "date" in msg]
    assert date_issues and date_issues[0][0] == "WARNING"


# ---------------------------------------------------------------------------
# check_tag_format
# ---------------------------------------------------------------------------

def test_hyphenated_tags_warn(mod):
    issues = mod.check_tag_format(["developer-tools", "ai"])
    assert issues[0][0] == "WARNING"
    assert "developer-tools" in issues[0][1]


def test_clean_tags_ok(mod):
    assert mod.check_tag_format(["python", "ai", "devtools"]) == []


# ---------------------------------------------------------------------------
# lint() integration
# ---------------------------------------------------------------------------

def test_lint_clean_article_exits_0(good_md, mod, monkeypatch):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    result = mod.lint(str(good_md))
    assert result == 0


def test_lint_em_dash_fails(tmp_path, mod, monkeypatch):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "a.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nSome — text.\n")
    assert mod.lint(str(md)) == 1


def test_lint_strict_warning_fails(good_md, mod, monkeypatch):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    # Add a tag with hyphen to trigger WARNING
    md = good_md.parent / "warn.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [python-dev]\nlang: en\n---\nBody.\n")
    assert mod.lint(str(md), strict=False) == 0
    assert mod.lint(str(md), strict=True) == 1


def test_lint_warning_passes_non_strict(good_md, mod, monkeypatch):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = good_md.parent / "warn.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [python-dev]\nlang: en\n---\nBody.\n")
    assert mod.lint(str(md), strict=False) == 0


# ---------------------------------------------------------------------------
# --fix
# ---------------------------------------------------------------------------

def test_fix_replaces_em_dash(tmp_path, mod, monkeypatch):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "a.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nSome — text.\n")
    n = mod.fix_dashes(str(md))
    assert n >= 1
    assert "—" not in md.read_text()


def test_fix_leaves_fenced_code_intact(tmp_path, mod, monkeypatch):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "a.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\n```\ncode — dash\n```\n")
    mod.fix_dashes(str(md))
    assert "—" in md.read_text()  # preserved inside fence


def test_fix_leaves_inline_code_intact(tmp_path, mod, monkeypatch):
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    md = tmp_path / "a.md"
    md.write_text("---\ntitle: T\ndescription: D\ndate: 2026-01-01\ntags: [a]\nlang: en\n---\nUse `foo—bar` here.\n")
    mod.fix_dashes(str(md))
    assert "`foo—bar`" in md.read_text()  # inline code preserved
