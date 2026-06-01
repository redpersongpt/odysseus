from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_research_start_uses_user_time_limit_for_hard_timeout():
    source = (ROOT / "routes" / "research_routes.py").read_text()

    assert "max_time: int = Field(default=300, ge=60, le=1800)" in source
    assert "hard_timeout = max(600, body.max_time + 60)" in source
    assert "hard_timeout=hard_timeout" in source


def test_research_panel_sends_time_limit_setting():
    source = (ROOT / "static" / "js" / "research" / "panel.js").read_text()

    assert 'id="research-max-time"' in source
    assert "max_time: document.getElementById('research-max-time')?.value || '300'" in source
    assert "max_time: parseInt(document.getElementById('research-max-time')?.value || '300', 10)" in source
    assert "if (maxTime && saved.max_time !== undefined) maxTime.value = saved.max_time;" in source
