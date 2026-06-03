import importlib.machinery
import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parents[1]


def _load_cli(monkeypatch):
    svc = types.ModuleType("services.memory.memory")
    svc.MemoryManager = MagicMock()
    monkeypatch.setitem(sys.modules, "services.memory.memory", svc)
    path = ROOT / "scripts" / "odysseus-memory"
    loader = importlib.machinery.SourceFileLoader("odysseus_memory_cli", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_memory_entries_skips_invalid_rows(monkeypatch):
    cli = _load_cli(monkeypatch)

    assert cli._memory_entries([
        {"id": "m1", "text": "ok"},
        "bad-row",
        None,
    ]) == [{"id": "m1", "text": "ok"}]


def test_search_ignores_non_string_memory_text(monkeypatch):
    cli = _load_cli(monkeypatch)
    cli._mgr = MagicMock()
    cli._mgr.load_all.return_value = [
        {"id": "m1", "text": "hello world", "timestamp": 2},
        {"id": "m2", "text": ["hello"], "timestamp": 3},
        {"id": "m3", "text": None, "timestamp": 1},
    ]
    emitted = []
    monkeypatch.setattr(cli, "emit", lambda value, args: emitted.append(value))

    cli.cmd_search(SimpleNamespace(query="hello", limit=10))

    assert emitted == [[{"id": "m1", "text": "hello world", "timestamp": 2}]]
