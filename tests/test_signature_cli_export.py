import importlib.machinery
import sys
from pathlib import Path
from types import ModuleType


def _load_signature_cli():
    sqlalchemy_mod = ModuleType("sqlalchemy")
    sqlalchemy_mod.text = lambda value: value
    core_mod = ModuleType("core")
    database_mod = ModuleType("core.database")
    database_mod.engine = object()
    sys.modules["sqlalchemy"] = sqlalchemy_mod
    sys.modules["core"] = core_mod
    sys.modules["core.database"] = database_mod

    path = Path(__file__).resolve().parent.parent / "scripts" / "odysseus-signature"
    loader = importlib.machinery.SourceFileLoader("odysseus_signature_cli_under_test", str(path))
    return loader.load_module()


def test_decode_png_data_accepts_data_url():
    cli = _load_signature_cli()

    assert cli._decode_png_data("data:image/png;base64,aGVsbG8=") == b"hello"


def test_decode_png_data_rejects_invalid_base64():
    cli = _load_signature_cli()

    try:
        cli._decode_png_data("not valid!!!")
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("expected invalid base64 to exit")
