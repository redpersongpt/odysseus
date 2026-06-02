import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import routes.update_routes as update_routes


def _admin_request(is_admin=True):
    return SimpleNamespace(
        state=SimpleNamespace(current_user="alice"),
        headers={},
        app=SimpleNamespace(
            state=SimpleNamespace(
                auth_manager=SimpleNamespace(
                    is_configured=True,
                    is_admin=lambda _user: is_admin,
                )
            )
        ),
    )


def _route_endpoint():
    router = update_routes.setup_update_routes()
    for route in router.routes:
        if route.path == "/api/admin/update/status":
            return route.endpoint
    raise AssertionError("update status route missing")


def _fake_git(commands):
    def run(_repo_dir, args, timeout=2.5):
        result = commands.get(" ".join(args))
        if result is None:
            return {"ok": False, "error": "missing_stub", "details": " ".join(args)}
        return result

    return run


def _ok(stdout=""):
    return {"ok": True, "returncode": 0, "stdout": stdout, "stderr": ""}


def test_update_status_requires_admin():
    endpoint = _route_endpoint()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(endpoint(request=_admin_request(is_admin=False)))
    assert exc.value.status_code == 403


def test_collect_update_status_reports_remote_change(monkeypatch, tmp_path):
    (tmp_path / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
    local = "a" * 40
    remote = "b" * 40
    monkeypatch.setattr(
        update_routes,
        "_run_git",
        _fake_git(
            {
                "rev-parse --show-toplevel": _ok(str(tmp_path)),
                "rev-parse HEAD": _ok(local),
                "rev-parse --abbrev-ref HEAD": _ok("main"),
                "status --porcelain": _ok(""),
                "config --get branch.main.remote": _ok("origin"),
                "config --get branch.main.merge": _ok("refs/heads/main"),
                "config --get remote.origin.url": _ok("https://user:secret@example.com/repo.git"),
                "ls-remote --heads origin main": _ok(f"{remote}\trefs/heads/main"),
                "rev-list --left-right --count HEAD...@{u}": _ok("0\t1"),
            }
        ),
    )

    status = update_routes.collect_update_status(str(tmp_path))

    assert status["version"]
    assert status["git"]["available"] is True
    assert status["git"]["short_commit"] == local[:12]
    assert status["git"]["remote_commit"] == remote
    assert status["git"]["remote_url"] == "https://example.com/repo.git"
    assert status["git"]["ahead"] == 0
    assert status["git"]["behind"] == 1
    assert status["update"]["checkable"] is True
    assert status["update"]["available"] is True
    assert status["install"]["mode"] == "source_docker"
    assert "docker compose up -d --build" in status["install"]["manual_commands"]


def test_collect_update_status_handles_missing_git(monkeypatch, tmp_path):
    monkeypatch.setattr(
        update_routes,
        "_run_git",
        lambda *_args, **_kwargs: {"ok": False, "error": "git_missing", "details": "git missing"},
    )

    status = update_routes.collect_update_status(str(tmp_path))

    assert status["git"]["available"] is False
    assert status["update"]["checkable"] is False
    assert status["update"]["available"] is False
    assert status["update"]["reason"] == "not_a_git_checkout"
    assert status["install"]["mode"] == "source_native"


def test_remote_url_policy_and_scrubbing():
    assert update_routes._remote_url_allowed("https://github.com/a/b.git") is True
    assert update_routes._remote_url_allowed("git@github.com:a/b.git") is True
    assert update_routes._remote_url_allowed("file:///tmp/repo.git") is False
    assert update_routes._remote_url_allowed("/tmp/repo.git") is False
    assert (
        update_routes._scrub_remote_url("https://alice:token@example.com/a/b.git")
        == "https://example.com/a/b.git"
    )
