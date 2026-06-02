from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
GUIDE = ROOT / "docs" / "beginner-setup.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_links_to_beginner_setup_guide():
    readme = _read(README)

    assert "[beginner setup guide](docs/beginner-setup.md)" in readme


def test_beginner_guide_covers_supported_first_install_paths():
    guide = _read(GUIDE)

    required_phrases = [
        "MacBook, Apple Silicon",
        "Windows, native launcher",
        "Docker",
        "Manual Python setup",
        "Download ZIP vs git clone",
        "About \"virus detected\" on the ZIP",
        "First login",
        "What to include when asking for help",
    ]

    for phrase in required_phrases:
        assert phrase in guide


def test_beginner_guide_keeps_launcher_commands_exact():
    guide = _read(GUIDE)

    assert "./start-macos.sh" in guide
    assert r"powershell -ExecutionPolicy Bypass -File .\launch-windows.ps1" in guide
    assert r".\launch-windows-ps1" in guide
    assert r".\launch-windows.ps1" in guide


def test_beginner_guide_explains_local_urls_and_admin_password():
    guide = _read(GUIDE)

    assert "localhost" in guide
    assert "127.0.0.1" in guide
    assert "The password is printed in the terminal during setup." in guide
    assert "docker compose logs odysseus" in guide
