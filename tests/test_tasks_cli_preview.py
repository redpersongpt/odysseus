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
    db.ScheduledTask = MagicMock()
    db.TaskRun = MagicMock()
    monkeypatch.setitem(sys.modules, "core.database", db)
    path = ROOT / "scripts" / "odysseus-tasks"
    loader = importlib.machinery.SourceFileLoader("odysseus_tasks_cli", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_preview_text_ignores_non_string_values(monkeypatch):
    cli = _load_cli(monkeypatch)

    assert cli._preview_text(None) == ""
    assert cli._preview_text({"bad": "row"}) == ""
    assert cli._preview_text("x" * 201) == ("x" * 200) + "…"


def test_serialize_task_normalizes_bad_run_count(monkeypatch):
    cli = _load_cli(monkeypatch)
    task = SimpleNamespace(
        id="t1",
        name="task",
        task_type="prompt",
        action="run",
        prompt="hello",
        schedule="manual",
        scheduled_time="",
        next_run=None,
        last_run=None,
        status="active",
        model="m",
        run_count="bad",
        cron_expression=None,
    )

    assert cli._serialize_task(task)["run_count"] == 0
