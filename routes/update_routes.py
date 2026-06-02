"""Check-only software update status routes."""

from __future__ import annotations

import os
import subprocess
from typing import Any
from urllib.parse import urlparse, urlunparse

from fastapi import APIRouter, Request

from core.constants import APP_VERSION, BASE_DIR
from core.middleware import require_admin


GIT_TIMEOUT_SECONDS = 2.5

_MODE_COMMANDS = {
    "source_docker": [
        "git pull --ff-only",
        "docker compose up -d --build",
    ],
    "source_native": [
        "git pull --ff-only",
        "python -m pip install -r requirements.txt",
        "python setup.py",
    ],
}


def _scrub_remote_url(remote_url: str | None) -> str | None:
    if not remote_url:
        return None
    remote_url = remote_url.strip()
    if "://" not in remote_url:
        return remote_url
    parsed = urlparse(remote_url)
    if not (parsed.username or parsed.password):
        return remote_url
    netloc = parsed.hostname or ""
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    return urlunparse(parsed._replace(netloc=netloc))


def _remote_url_allowed(remote_url: str | None) -> bool:
    if not remote_url:
        return False
    value = remote_url.strip()
    if not value:
        return False
    if "://" in value:
        return urlparse(value).scheme.lower() in {"https", "http", "ssh", "git"}
    return "@" in value and ":" in value and not value.startswith(("/", "."))


def _run_git(repo_dir: str, args: list[str], timeout: float = GIT_TIMEOUT_SECONDS) -> dict[str, Any]:
    try:
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        env.setdefault("GIT_SSH_COMMAND", "ssh -oBatchMode=yes")
        proc = subprocess.run(
            ["git", *args],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            env=env,
        )
        return {
            "ok": True,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except FileNotFoundError as exc:
        return {"ok": False, "error": "git_missing", "details": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {"ok": False, "error": "timeout", "details": str(exc)}
    except Exception as exc:  # pragma: no cover - defensive guard.
        return {"ok": False, "error": "unexpected", "details": str(exc)}


def _git_output(repo_dir: str, args: list[str], state: dict[str, Any], timeout_tag: str) -> str | None:
    result = _run_git(repo_dir, args)
    if not result.get("ok"):
        if result.get("error") == "timeout":
            state["git"]["timeouts"].append(timeout_tag)
        else:
            state["git"]["errors"].append(f"git {' '.join(args)} failed")
        return None
    if result.get("returncode") != 0:
        return None
    return (result.get("stdout") or "").strip()


def _parse_ahead_behind(raw: str | None) -> tuple[int | None, int | None]:
    if not raw:
        return None, None
    parts = raw.split()
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        return None, None
    return int(parts[0]), int(parts[1])


def _detect_install_mode(repo_dir: str, git_available: bool) -> str:
    if git_available and os.path.exists(os.path.join(repo_dir, "docker-compose.yml")):
        return "source_docker"
    return "source_native"


def collect_update_status(repo_dir: str | None = None) -> dict[str, Any]:
    repo_dir = os.path.abspath(repo_dir or BASE_DIR)
    state: dict[str, Any] = {
        "version": APP_VERSION,
        "git": {
            "available": False,
            "commit": None,
            "short_commit": None,
            "branch": None,
            "detached_head": False,
            "dirty": None,
            "remote": None,
            "remote_branch": None,
            "remote_url": None,
            "remote_commit": None,
            "ahead": None,
            "behind": None,
            "warnings": [],
            "errors": [],
            "timeouts": [],
        },
        "update": {
            "checkable": False,
            "available": False,
            "reason": None,
        },
        "install": {
            "mode": None,
            "manual_commands": [],
            "apply_supported": False,
        },
    }

    toplevel = _git_output(repo_dir, ["rev-parse", "--show-toplevel"], state, "rev-parse")
    if not toplevel:
        state["git"]["errors"].append("Repository metadata is unavailable.")
        state["install"]["mode"] = _detect_install_mode(repo_dir, False)
        state["install"]["manual_commands"] = _MODE_COMMANDS[state["install"]["mode"]]
        state["update"]["reason"] = "not_a_git_checkout"
        return state

    repo_dir = os.path.abspath(toplevel)
    state["git"]["available"] = True

    commit = _git_output(repo_dir, ["rev-parse", "HEAD"], state, "rev-parse HEAD")
    if commit:
        state["git"]["commit"] = commit
        state["git"]["short_commit"] = commit[:12]

    branch = _git_output(repo_dir, ["rev-parse", "--abbrev-ref", "HEAD"], state, "rev-parse branch")
    if branch:
        state["git"]["branch"] = branch
        state["git"]["detached_head"] = branch == "HEAD"

    status = _git_output(repo_dir, ["status", "--porcelain"], state, "status")
    if status is not None:
        state["git"]["dirty"] = bool(status.strip())

    if state["git"]["detached_head"]:
        state["git"]["warnings"].append("Detached HEAD; branch update checks are not available.")
    elif branch:
        remote = _git_output(repo_dir, ["config", "--get", f"branch.{branch}.remote"], state, "branch remote")
        merge_ref = _git_output(repo_dir, ["config", "--get", f"branch.{branch}.merge"], state, "branch merge")
        remote_branch = None
        if merge_ref and merge_ref.startswith("refs/heads/"):
            remote_branch = merge_ref.replace("refs/heads/", "", 1)
        if remote and remote_branch:
            state["git"]["remote"] = remote
            state["git"]["remote_branch"] = remote_branch
            remote_url = _git_output(repo_dir, ["config", "--get", f"remote.{remote}.url"], state, "remote url")
            state["git"]["remote_url"] = _scrub_remote_url(remote_url)
            if remote_url and _remote_url_allowed(remote_url):
                remote_head = _git_output(
                    repo_dir,
                    ["ls-remote", "--heads", remote, remote_branch],
                    state,
                    "ls-remote",
                )
                if remote_head:
                    state["git"]["remote_commit"] = remote_head.split()[0]
                    state["update"]["checkable"] = True
                    state["update"]["available"] = state["git"]["remote_commit"] != state["git"]["commit"]
                    if state["update"]["available"]:
                        state["update"]["reason"] = "remote_head_changed"
                ahead_behind = _git_output(
                    repo_dir,
                    ["rev-list", "--left-right", "--count", "HEAD...@{u}"],
                    state,
                    "rev-list",
                )
                ahead, behind = _parse_ahead_behind(ahead_behind)
                state["git"]["ahead"] = ahead
                state["git"]["behind"] = behind
            elif remote_url:
                state["git"]["warnings"].append("Remote URL is not supported for update checks.")
        else:
            state["git"]["warnings"].append("No upstream tracking branch configured.")

    if state["git"]["dirty"]:
        state["git"]["warnings"].append("Working tree has uncommitted changes.")

    state["install"]["mode"] = _detect_install_mode(repo_dir, True)
    state["install"]["manual_commands"] = _MODE_COMMANDS[state["install"]["mode"]]
    if state["update"]["checkable"] and not state["update"]["reason"]:
        state["update"]["reason"] = "up_to_date"
    return state


def setup_update_routes() -> APIRouter:
    router = APIRouter(prefix="/api/admin", tags=["admin"])

    @router.get("/update/status")
    def get_update_status(request: Request) -> dict[str, Any]:
        require_admin(request)
        return collect_update_status()

    return router
