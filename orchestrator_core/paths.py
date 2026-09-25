"""Path discovery and containment checks used by the installer."""

from __future__ import annotations

import os
from pathlib import Path


SKILL_NAME = "gpt-development-orchestrator"
WORKER_ROLE_NAME = "gpt_luna_builder"
MANAGED_DIRECTORY = ".gpt-development-orchestrator"
POLICY_BEGIN = "<!-- GPT-DEVELOPMENT-ORCHESTRATOR:BEGIN -->"
POLICY_END = "<!-- GPT-DEVELOPMENT-ORCHESTRATOR:END -->"


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def resolve_codex_home(value: str | Path | None) -> Path:
    return Path(value).expanduser().resolve() if value else default_codex_home().resolve()


def default_skill_source() -> Path:
    return repository_root() / "skill" / SKILL_NAME


def managed_root(codex_home: Path) -> Path:
    return codex_home / MANAGED_DIRECTORY


def backups_root(codex_home: Path) -> Path:
    return managed_root(codex_home) / "backups"


def receipts_root(codex_home: Path) -> Path:
    return managed_root(codex_home) / "receipts"


def installed_skill_path(codex_home: Path) -> Path:
    return codex_home / "skills" / SKILL_NAME


def worker_role_path(codex_home: Path) -> Path:
    return codex_home / "agents" / f"{WORKER_ROLE_NAME}.toml"


def policy_path(codex_home: Path) -> Path:
    return codex_home / "AGENTS.md"


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _is_redirect(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def assert_contained_managed_path(codex_home: Path, path: Path, label: str) -> None:
    """Reject any managed path that escapes home through a link or junction."""
    home = codex_home.resolve()
    try:
        relative_parts = path.relative_to(home).parts
    except ValueError as error:
        raise RuntimeError(f"{label} is not under the selected Codex home: {path}") from error

    try:
        path.resolve().relative_to(home)
    except ValueError as error:
        raise RuntimeError(f"{label} resolves outside the selected Codex home: {path}") from error

    cursor = home
    for part in relative_parts:
        cursor = cursor / part
        if (cursor.exists() or cursor.is_symlink()) and _is_redirect(cursor):
            raise RuntimeError(f"{label} uses a symbolic link or junction and is not allowed: {cursor}")


def assert_managed_layout(codex_home: Path) -> None:
    """Verify every installer-controlled path stays in the selected home."""
    home = codex_home.resolve()
    for path, label in (
        (installed_skill_path(home), "Installed skill"),
        (worker_role_path(home), "Luna worker role"),
        (policy_path(home), "AGENTS.md"),
        (managed_root(home), "Managed state"),
        (receipts_root(home), "Managed receipts"),
        (backups_root(home), "Managed backups"),
    ):
        assert_contained_managed_path(home, path, label)
