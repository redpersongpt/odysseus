import importlib.machinery
import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parents[1]


def _load_cli(monkeypatch):
    routes = types.ModuleType("routes.contacts_routes")
    routes._get_carddav_config = MagicMock()
    routes._fetch_contacts = MagicMock()
    routes._create_contact = MagicMock()
    monkeypatch.setitem(sys.modules, "routes.contacts_routes", routes)
    path = ROOT / "scripts" / "odysseus-contacts"
    loader = importlib.machinery.SourceFileLoader("odysseus_contacts_cli", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_contact_rows_skips_invalid_rows(monkeypatch):
    cli = _load_cli(monkeypatch)

    assert cli._contact_rows([
        {"name": "Ada", "email": "ada@example.test"},
        "bad-row",
        None,
    ]) == [{"name": "Ada", "email": "ada@example.test"}]


def test_search_ignores_non_string_contact_fields(monkeypatch):
    cli = _load_cli(monkeypatch)
    cli._get_carddav_config.return_value = {"url": "https://carddav.example.test"}
    cli._fetch_contacts.return_value = [
        {"name": "Ada Lovelace", "email": "ada@example.test"},
        {"name": ["Ada"], "email": None},
        {"name": None, "email": 123},
    ]
    emitted = []
    monkeypatch.setattr(cli, "emit", lambda value, args: emitted.append(value))

    cli.cmd_search(SimpleNamespace(query="ada"))

    assert emitted == [[{"name": "Ada Lovelace", "email": "ada@example.test"}]]
