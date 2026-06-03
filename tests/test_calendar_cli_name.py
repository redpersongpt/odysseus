import importlib.machinery
import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parents[1]


def _load_cli(monkeypatch):
    db = types.ModuleType("core.database")
    db.SessionLocal = MagicMock()
    db.CalendarCal = MagicMock()
    db.CalendarEvent = MagicMock()
    monkeypatch.setitem(sys.modules, "core.database", db)
    path = ROOT / "scripts" / "odysseus-calendar"
    loader = importlib.machinery.SourceFileLoader("odysseus_calendar_cli", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_calendar_name_handles_missing_relation(monkeypatch):
    cli = _load_cli(monkeypatch)

    assert cli._calendar_name(SimpleNamespace(calendar=None)) == ""
    assert cli._calendar_name(SimpleNamespace(calendar=SimpleNamespace(name=123))) == ""
    assert cli._calendar_name(SimpleNamespace(calendar=SimpleNamespace(name="Work"))) == "Work"


def test_calendar_event_count_handles_bad_relationship(monkeypatch):
    cli = _load_cli(monkeypatch)

    assert cli._calendar_event_count(SimpleNamespace(events=[1, 2])) == 2
    assert cli._calendar_event_count(SimpleNamespace(events=None)) == 0
    assert cli._calendar_event_count(SimpleNamespace(events=object())) == 0
