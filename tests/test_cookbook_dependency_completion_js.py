from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_background_status_poll_persists_completed_dependency_tasks():
    source = (ROOT / "static/js/cookbookRunning.js").read_text(encoding="utf-8")

    assert "function _applyBackendTaskStatus(t)" in source
    assert "t.status !== 'completed' && t.status !== 'error'" in source
    assert "updates.status = 'done';" in source
    assert "_updateTask(t.session_id, updates);" in source
    assert "_refreshDepsAfterInstall(localTask);" in source
    assert "for (const t of tasks)" in source


def test_running_tab_count_ignores_completed_tasks():
    source = (ROOT / "static/js/cookbookRunning.js").read_text(encoding="utf-8")

    assert "function _runningTabLabel(tasks)" in source
    assert "t.status === 'running'" in source
    assert "t.status === 'queued'" in source
    assert "t.status === 'ready'" in source
    assert "t.status === 'error'" in source
    assert "t.status === 'crashed'" in source
    assert "${tasks.length}" not in source


def test_dependency_install_task_remembers_env_path_for_refresh():
    source = (ROOT / "static/js/cookbook.js").read_text(encoding="utf-8")

    assert "env_path: _envState.envPath || ''" in source
