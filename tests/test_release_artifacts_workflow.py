from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_artifacts_workflow_builds_three_platforms():
    workflow = (ROOT / ".github/workflows/release-artifacts.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "tags:" in workflow
    assert "ubuntu-latest" in workflow
    assert "macos-latest" in workflow
    assert "windows-latest" in workflow
    assert "PyInstaller" in workflow
    assert "scripts/release_launcher.py" in workflow
    assert "hdiutil create" in workflow
    assert "Compress-Archive" in workflow
    assert "tar -czf" in workflow
    assert "SHA256SUMS" in workflow
    assert "gh release create" in workflow
