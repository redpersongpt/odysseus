import importlib.machinery
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace


def _load_sessions_cli():
    core_mod = ModuleType("core")
    database_mod = ModuleType("core.database")
    database_mod.SessionLocal = object
    database_mod.Session = object
    sys.modules["core"] = core_mod
    sys.modules["core.database"] = database_mod
    path = Path(__file__).resolve().parent.parent / "scripts" / "odysseus-sessions"
    loader = importlib.machinery.SourceFileLoader("odysseus_sessions_cli_under_test", str(path))
    return loader.load_module()


def test_serialize_normalizes_numeric_counters():
    cli = _load_sessions_cli()
    session = SimpleNamespace(
        id="s1",
        name="chat",
        model="m",
        endpoint_url="",
        owner=None,
        folder=None,
        archived=False,
        rag=False,
        is_important=False,
        message_count="12",
        total_input_tokens="bad",
        total_output_tokens=None,
        last_accessed=None,
        created_at=None,
    )

    out = cli._serialize(session)

    assert out["message_count"] == 12
    assert out["total_input_tokens"] == 0
    assert out["total_output_tokens"] == 0
