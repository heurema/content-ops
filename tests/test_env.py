"""Tests for tools/shared/env.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import importlib.util
import pathlib


def load_env_module():
    spec = importlib.util.spec_from_file_location(
        "env",
        pathlib.Path(__file__).parent.parent / "tools" / "shared" / "env.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_load_parses_key_value(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("MY_KEY=my_value\n")
    monkeypatch.delenv("MY_KEY", raising=False)
    monkeypatch.delenv("CONTENT_OPS_NO_DOTENV", raising=False)
    monkeypatch.chdir(tmp_path)
    mod = load_env_module()
    mod.load()
    assert os.environ.get("MY_KEY") == "my_value"


def test_load_strips_quotes(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text('KEY1="double"\nKEY2=\'single\'\n')
    monkeypatch.delenv("KEY1", raising=False)
    monkeypatch.delenv("KEY2", raising=False)
    monkeypatch.delenv("CONTENT_OPS_NO_DOTENV", raising=False)
    monkeypatch.chdir(tmp_path)
    mod = load_env_module()
    mod.load()
    assert os.environ.get("KEY1") == "double"
    assert os.environ.get("KEY2") == "single"


def test_load_does_not_overwrite_existing(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING=from_file\n")
    monkeypatch.setenv("EXISTING", "from_env")
    monkeypatch.delenv("CONTENT_OPS_NO_DOTENV", raising=False)
    monkeypatch.chdir(tmp_path)
    mod = load_env_module()
    mod.load()
    assert os.environ.get("EXISTING") == "from_env"


def test_load_skips_comments_and_blank_lines(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\n\nVALID=yes\n# another comment\n")
    monkeypatch.delenv("VALID", raising=False)
    monkeypatch.delenv("CONTENT_OPS_NO_DOTENV", raising=False)
    monkeypatch.chdir(tmp_path)
    mod = load_env_module()
    mod.load()
    assert os.environ.get("VALID") == "yes"


def test_no_dotenv_flag_disables_load(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("SHOULD_NOT_LOAD=yes\n")
    monkeypatch.delenv("SHOULD_NOT_LOAD", raising=False)
    monkeypatch.setenv("CONTENT_OPS_NO_DOTENV", "1")
    monkeypatch.chdir(tmp_path)
    mod = load_env_module()
    mod.load()
    assert os.environ.get("SHOULD_NOT_LOAD") is None


def test_load_skips_line_without_equals(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("NOEQUALSSIGN\nGOOD=yes\n")
    monkeypatch.delenv("GOOD", raising=False)
    monkeypatch.delenv("NOEQUALSSIGN", raising=False)
    monkeypatch.delenv("CONTENT_OPS_NO_DOTENV", raising=False)
    monkeypatch.chdir(tmp_path)
    mod = load_env_module()
    mod.load()
    assert os.environ.get("GOOD") == "yes"
    assert os.environ.get("NOEQUALSSIGN") is None


def test_global_fallback_loaded_when_no_cwd_env(tmp_path, monkeypatch):
    """Global ~/.config/content-ops/.env loaded when no CWD .env present."""
    global_dir = tmp_path / "config" / "content-ops"
    global_dir.mkdir(parents=True)
    (global_dir / ".env").write_text("GLOBAL_KEY=global_value\n")
    monkeypatch.delenv("GLOBAL_KEY", raising=False)
    monkeypatch.delenv("CONTENT_OPS_NO_DOTENV", raising=False)

    # CWD has no .env
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)

    mod = load_env_module()
    # Patch the module's _GLOBAL_ENV_PATH
    import pathlib as _pl
    monkeypatch.setattr(mod, "_GLOBAL_ENV_PATH", global_dir / ".env")
    mod.load()
    assert os.environ.get("GLOBAL_KEY") == "global_value"


def test_cwd_env_takes_precedence_over_global(tmp_path, monkeypatch):
    """CWD .env takes precedence over global .env for same key."""
    global_dir = tmp_path / "config" / "content-ops"
    global_dir.mkdir(parents=True)
    (global_dir / ".env").write_text("SHARED_KEY=global\n")

    cwd = tmp_path / "cwd"
    cwd.mkdir()
    (cwd / ".env").write_text("SHARED_KEY=local\n")

    monkeypatch.delenv("SHARED_KEY", raising=False)
    monkeypatch.delenv("CONTENT_OPS_NO_DOTENV", raising=False)
    monkeypatch.chdir(cwd)

    mod = load_env_module()
    monkeypatch.setattr(mod, "_GLOBAL_ENV_PATH", global_dir / ".env")
    mod.load()
    assert os.environ.get("SHARED_KEY") == "local"
