import importlib.machinery
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load_cli():
    path = ROOT / "scripts" / "odysseus-theme"
    loader = importlib.machinery.SourceFileLoader("odysseus_theme_cli", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


@pytest.mark.parametrize("payload", ["[]", '{"_users": []}'])
def test_load_prefs_rejects_non_object_user_store(tmp_path, capsys, payload):
    cli = _load_cli()
    cli._USER_PREFS_PATH = tmp_path / "user_prefs.json"
    cli._USER_PREFS_PATH.write_text(payload)

    with pytest.raises(SystemExit):
        cli._load_prefs()

    assert "is corrupt" in capsys.readouterr().err


def test_users_tolerates_malformed_user_pref_entry(tmp_path, monkeypatch):
    cli = _load_cli()
    cli._USER_PREFS_PATH = tmp_path / "user_prefs.json"
    cli._USER_PREFS_PATH.write_text(json.dumps({
        "_users": {
            "bad": "not-a-pref-object",
            "good": {"theme": {"name": "chatgpt", "font": "system"}},
        }
    }))
    emitted = []
    monkeypatch.setattr(cli, "emit", lambda value, args: emitted.append(value))

    cli.cmd_users(SimpleNamespace())

    assert emitted == [[
        {"user": "bad", "preset": "", "has_custom_colors": False, "font": "", "density": ""},
        {"user": "good", "preset": "chatgpt", "has_custom_colors": False, "font": "system", "density": ""},
    ]]


def test_set_replaces_malformed_user_pref_entry(tmp_path, monkeypatch):
    cli = _load_cli()
    cli._USER_PREFS_PATH = tmp_path / "user_prefs.json"
    cli._USER_PREFS_PATH.write_text(json.dumps({"_users": {"bad": "not-a-pref-object"}}))
    monkeypatch.setattr(cli, "_builtin_preset_names", lambda: ["chatgpt"])
    monkeypatch.setattr(cli, "emit", lambda value, args: None)

    cli.cmd_set(SimpleNamespace(user="bad", preset="chatgpt", keep_colors=False))

    data = json.loads(cli._USER_PREFS_PATH.read_text())
    assert data["_users"]["bad"] == {"theme": {"name": "chatgpt"}}
