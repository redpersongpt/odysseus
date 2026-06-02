import importlib.machinery
from pathlib import Path


def _load_dispatcher():
    path = Path(__file__).resolve().parent.parent / "scripts" / "odysseus"
    loader = importlib.machinery.SourceFileLoader("odysseus_dispatcher_under_test", str(path))
    return loader.load_module()


def test_is_runnable_subcommand_requires_executable_file(tmp_path):
    cli = _load_dispatcher()
    sub = tmp_path / "odysseus-demo"
    sub.write_text("#!/bin/sh\n")
    sub.chmod(0o644)

    assert cli._is_runnable_subcommand(sub) is False

    sub.chmod(0o755)
    assert cli._is_runnable_subcommand(sub) is True
