"""Preview-first, receipt-driven installation and undo mechanics."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from .filesystem import (
    FileSafetyError,
    atomic_remove_directory,
    atomic_replace_directory,
    atomic_write_bytes,
    copy_directory_snapshot,
    directory_digest,
    ensure_plain_directory,
    ensure_plain_file_or_missing,
    file_digest,
    regular_file_mode,
    stage_directory_copy,
)
from .paths import (
    POLICY_BEGIN,
    POLICY_END,
    assert_managed_layout,
    backups_root,
    default_skill_source,
    installed_skill_path,
    is_within,
    managed_root,
    policy_path,
    receipts_root,
    resolve_codex_home,
)


RECEIPT_SCHEMA = "gpt-development-orchestrator/receipt-v1"
INSTALL_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class InstallerError(RuntimeError):
    """Raised for an actionable installer or undo failure."""


@dataclass(frozen=True)
class InstallResult:
    applied: bool
    changed: bool
    actions: list[str] = field(default_factory=list)
    receipt_path: Path | None = None


@dataclass(frozen=True)
class UndoResult:
    applied: bool
    changed: bool
    actions: list[str] = field(default_factory=list)


class _InstallLock:
    def __init__(self, codex_home: Path) -> None:
        self.path = managed_root(codex_home) / "install.lock"
        self.acquired = False

    def __enter__(self) -> "_InstallLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as error:
            raise InstallerError(
                f"Another installation appears to be active: {self.path}. "
                "Wait for it to finish, then remove this stale lock only after verifying it is inactive."
            ) from error
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(f"pid={os.getpid()}\n")
        self.acquired = True
        return self

    def __exit__(self, *_: object) -> None:
        if self.acquired:
            self.path.unlink(missing_ok=True)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _read_policy_source(path: Path) -> bytes:
    ensure_plain_file_or_missing(path, "Policy source")
    if not path.exists():
        raise InstallerError(f"Policy source is missing: {path}")
    return path.read_bytes()


def _validate_source(source_skill: Path) -> str:
    try:
        ensure_plain_directory(source_skill, "Skill source")
    except FileSafetyError as error:
        raise InstallerError(str(error)) from error
    if not source_skill.exists():
        raise InstallerError(
            f"Skill source is missing: {source_skill}. "
            "Build or provide the skill package before applying installation."
        )
    entrypoint = source_skill / "SKILL.md"
    try:
        ensure_plain_file_or_missing(entrypoint, "Skill source SKILL.md")
    except FileSafetyError as error:
        raise InstallerError(str(error)) from error
    if not entrypoint.exists():
        raise InstallerError(f"Skill source requires a regular SKILL.md file: {entrypoint}")
    return directory_digest(source_skill)


def _owned_policy_block(policy_body: bytes) -> bytes:
    normalized = policy_body.replace(b"\r\n", b"\n").rstrip(b"\n")
    if POLICY_BEGIN.encode("ascii") in normalized or POLICY_END.encode("ascii") in normalized:
        raise InstallerError("Policy source must not include installer-owned policy markers.")
    return POLICY_BEGIN.encode("ascii") + b"\n" + normalized + b"\n" + POLICY_END.encode("ascii") + b"\n"


def _replace_owned_policy_block(existing: bytes, expected_block: bytes) -> bytes:
    begin = POLICY_BEGIN.encode("ascii")
    end = POLICY_END.encode("ascii")
    start = existing.find(begin)
    finish = existing.find(end)
    if (start == -1) != (finish == -1):
        raise InstallerError("AGENTS.md contains an incomplete orchestrator policy marker pair.")
    if start != -1:
        if finish < start:
            raise InstallerError("AGENTS.md contains an invalid orchestrator policy marker order.")
        if existing.find(begin, start + len(begin)) != -1 or existing.find(end, finish + len(end)) != -1:
            raise InstallerError("AGENTS.md contains duplicate orchestrator policy marker pairs.")
        line_end = existing.find(b"\n", finish)
        after = len(existing) if line_end == -1 else line_end + 1
        return existing[:start] + expected_block + existing[after:]
    separator = b"" if not existing or existing.endswith(b"\n") else b"\n"
    return existing + separator + expected_block


def _default_receipt_path(codex_home: Path, install_id: str) -> Path:
    return receipts_root(codex_home) / f"install-{install_id}.json"


def _safe_receipt_path(value: Path, codex_home: Path) -> Path:
    resolved = value.expanduser().resolve()
    if resolved.exists() and resolved.is_dir():
        raise InstallerError(f"Receipt path is a directory: {resolved}")
    if not is_within(resolved, receipts_root(codex_home)):
        raise InstallerError(
            f"Receipt path must stay inside the managed receipts directory: {receipts_root(codex_home)}"
        )
    if resolved.exists():
        raise InstallerError(f"Receipt path already exists and will not be overwritten: {resolved}")
    return resolved


def _receipt_backup_root(codex_home: Path, install_id: str) -> Path:
    return backups_root(codex_home) / install_id


def _build_receipt(
    *,
    install_id: str,
    codex_home: Path,
    source_skill: Path,
    source_digest: str,
    skill_changed: bool,
    skill_existed: bool,
    policy_changed: bool,
    policy_existed: bool,
    post_policy: bytes | None,
) -> dict[str, object]:
    return {
        "schema": RECEIPT_SCHEMA,
        "install_id": install_id,
        "created_at": _utc_now(),
        "python": sys.version.split()[0],
        "codex_home": str(codex_home),
        "source_skill": str(source_skill),
        "operations": {
            "skill": {
                "changed": skill_changed,
                "preexisting": skill_existed,
                "post_digest": source_digest if skill_changed else None,
            },
            "policy": {
                "changed": policy_changed,
                "preexisting": policy_existed,
                "post_digest": file_digest(post_policy) if policy_changed and post_policy is not None else None,
            },
        },
    }


def _write_receipt(path: Path, receipt: dict[str, object]) -> None:
    atomic_write_bytes(path, (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _restore_skill_snapshot(destination: Path, backup_root: Path, preexisting: bool) -> None:
    if preexisting:
        prior_skill = backup_root / "skill"
        if not prior_skill.is_dir():
            raise InstallerError(f"Required skill backup is missing: {prior_skill}")
        staged = stage_directory_copy(prior_skill, destination.parent, destination.name)
        atomic_replace_directory(staged, destination)
    else:
        atomic_remove_directory(destination)


def _restore_policy_snapshot(destination: Path, backup_root: Path, preexisting: bool) -> None:
    if preexisting:
        prior_policy = backup_root / "policy"
        if not prior_policy.is_file():
            raise InstallerError(f"Required policy backup is missing: {prior_policy}")
        atomic_write_bytes(destination, prior_policy.read_bytes())
    else:
        destination.unlink(missing_ok=True)


def install(
    *,
    codex_home: str | Path | None = None,
    source_skill: str | Path | None = None,
    apply: bool = False,
    with_policy: bool = False,
    policy_source: str | Path | None = None,
    receipt_path: str | Path | None = None,
) -> InstallResult:
    """Preview or apply a skill installation. Mutation requires ``apply=True``."""
    home = resolve_codex_home(codex_home)
    try:
        assert_managed_layout(home)
    except RuntimeError as error:
        raise InstallerError(str(error)) from error
    source = Path(source_skill).expanduser().resolve() if source_skill else default_skill_source()
    source_digest = _validate_source(source)
    destination = installed_skill_path(home)
    ensure_plain_directory(destination, "Installed skill")

    policy_content: bytes | None = None
    destination_policy = policy_path(home)
    if with_policy:
        source_policy = Path(policy_source).expanduser().resolve() if policy_source else source.parent.parent / "POLICY.md"
        policy_content = _owned_policy_block(_read_policy_source(source_policy))
        ensure_plain_file_or_missing(destination_policy, "AGENTS.md")

    current_digest = directory_digest(destination) if destination.exists() else None
    skill_changed = current_digest != source_digest
    existing_policy = destination_policy.read_bytes() if with_policy and destination_policy.exists() else b""
    desired_policy = _replace_owned_policy_block(existing_policy, policy_content) if policy_content is not None else None
    policy_changed = desired_policy is not None and desired_policy != existing_policy

    actions: list[str] = []
    if skill_changed:
        actions.append(f"install skill: {source} -> {destination}")
    else:
        actions.append(f"skill already matches source: {destination}")
    if with_policy:
        actions.append(
            f"{'merge' if policy_changed else 'retain'} explicitly requested policy block: {destination_policy}"
        )
    if not skill_changed and not policy_changed:
        actions.append("no changes required; no receipt will be created")
        return InstallResult(applied=apply, changed=False, actions=actions)

    install_id = uuid.uuid4().hex
    receipt = _safe_receipt_path(
        Path(receipt_path) if receipt_path else _default_receipt_path(home, install_id), home
    )
    actions.append(f"create undo receipt: {receipt}")
    if not apply:
        return InstallResult(applied=False, changed=True, actions=actions, receipt_path=receipt)

    with _InstallLock(home):
        try:
            assert_managed_layout(home)
            ensure_plain_directory(destination, "Installed skill")
            ensure_plain_file_or_missing(destination_policy, "AGENTS.md")
        except (RuntimeError, FileSafetyError) as error:
            raise InstallerError(str(error)) from error
        locked_digest = directory_digest(destination) if destination.exists() else None
        locked_policy = destination_policy.read_bytes() if with_policy and destination_policy.exists() else b""
        if locked_digest != current_digest or locked_policy != existing_policy:
            raise InstallerError(
                "Managed installation state changed before the lock was acquired; review it and retry."
            )
        backup_root = _receipt_backup_root(home, install_id)
        skill_existed = destination.exists()
        policy_existed = destination_policy.exists()
        if skill_changed and skill_existed:
            copy_directory_snapshot(destination, backup_root / "skill")
        if policy_changed and policy_existed:
            (backup_root / "policy").parent.mkdir(parents=True, exist_ok=True)
            atomic_write_bytes(backup_root / "policy", existing_policy)
        receipt_data = _build_receipt(
            install_id=install_id,
            codex_home=home,
            source_skill=source,
            source_digest=source_digest,
            skill_changed=skill_changed,
            skill_existed=skill_existed,
            policy_changed=policy_changed,
            policy_existed=policy_existed,
            post_policy=desired_policy,
        )
        staged = stage_directory_copy(source, destination.parent, destination.name) if skill_changed else None
        if staged is not None and directory_digest(staged) != source_digest:
            shutil.rmtree(staged, ignore_errors=True)
            raise InstallerError("Skill source changed while it was being staged; review it and retry.")
        skill_published = False
        policy_published = False
        try:
            if staged is not None:
                atomic_replace_directory(staged, destination)
                skill_published = True
            if policy_changed and desired_policy is not None:
                atomic_write_bytes(destination_policy, desired_policy)
                policy_published = True
            _write_receipt(receipt, receipt_data)
        except Exception:
            rollback_errors: list[str] = []
            try:
                if policy_published:
                    _restore_policy_snapshot(destination_policy, backup_root, policy_existed)
            except Exception as rollback_error:  # pragma: no cover - catastrophic filesystem failure
                rollback_errors.append(str(rollback_error))
            try:
                if skill_published:
                    _restore_skill_snapshot(destination, backup_root, skill_existed)
            except Exception as rollback_error:  # pragma: no cover - catastrophic filesystem failure
                rollback_errors.append(str(rollback_error))
            if rollback_errors:
                raise InstallerError("Installation failed and rollback also failed: " + "; ".join(rollback_errors))
            raise
    actions.append("applied atomically with managed backup snapshots")
    return InstallResult(applied=True, changed=True, actions=actions, receipt_path=receipt)


def _load_receipt(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise InstallerError(f"Undo receipt was not found: {path}") from error
    except json.JSONDecodeError as error:
        raise InstallerError(f"Undo receipt is not valid JSON: {path}") from error
    if not isinstance(data, dict) or data.get("schema") != RECEIPT_SCHEMA:
        raise InstallerError("Undo receipt has an unsupported schema.")
    install_id = data.get("install_id")
    codex_home = data.get("codex_home")
    if not isinstance(install_id, str) or not INSTALL_ID_PATTERN.fullmatch(install_id):
        raise InstallerError("Undo receipt has an invalid install_id.")
    if not isinstance(codex_home, str) or not codex_home.strip():
        raise InstallerError("Undo receipt is missing required identity fields.")
    operations = data.get("operations")
    if not isinstance(operations, dict) or set(operations) != {"skill", "policy"}:
        raise InstallerError("Undo receipt is missing operation metadata.")
    for name in ("skill", "policy"):
        operation = operations[name]
        if not isinstance(operation, dict) or set(operation) != {"changed", "preexisting", "post_digest"}:
            raise InstallerError(f"Undo receipt has invalid {name} operation metadata.")
        changed = operation["changed"]
        preexisting = operation["preexisting"]
        post_digest = operation["post_digest"]
        if type(changed) is not bool or type(preexisting) is not bool:
            raise InstallerError(f"Undo receipt has non-boolean {name} operation flags.")
        if changed and (not isinstance(post_digest, str) or not DIGEST_PATTERN.fullmatch(post_digest)):
            raise InstallerError(f"Undo receipt has an invalid {name} post_digest.")
        if not changed and post_digest is not None:
            raise InstallerError(f"Undo receipt has an unexpected {name} post_digest.")
    return data


def _operation(receipt: dict[str, object], name: str) -> dict[str, object]:
    operations = receipt["operations"]
    assert isinstance(operations, dict)
    operation = operations.get(name)
    if not isinstance(operation, dict):
        raise InstallerError(f"Undo receipt is missing {name} operation metadata.")
    return operation


def _assert_post_state(
    *,
    target: Path,
    operation: dict[str, object],
    kind: str,
) -> None:
    expected = operation.get("post_digest")
    if not isinstance(expected, str) or not DIGEST_PATTERN.fullmatch(expected):
        raise InstallerError(f"Undo receipt has an invalid {kind} post_digest.")
    actual = directory_digest(target) if kind == "directory" and target.exists() else (
        file_digest(target.read_bytes()) if kind == "file" and target.exists() else None
    )
    if actual != expected:
        raise InstallerError(
            f"Refusing undo because the installed {kind} changed after this receipt was created: {target}. "
            "Restore it manually or use a receipt that matches its current state."
        )


def undo(
    receipt_path: str | Path,
    *,
    codex_home: str | Path | None = None,
    apply: bool = False,
) -> UndoResult:
    """Preview or restore exactly the state captured in an installer receipt."""
    receipt_file = Path(receipt_path).expanduser().resolve()
    receipt = _load_receipt(receipt_file)
    receipt_home = Path(str(receipt["codex_home"])).expanduser().resolve()
    if not is_within(receipt_file, receipts_root(receipt_home)):
        raise InstallerError(
            f"Undo receipt must be inside the managed receipts directory: {receipts_root(receipt_home)}"
        )
    home = resolve_codex_home(codex_home) if codex_home else receipt_home
    if home != receipt_home:
        raise InstallerError("The requested Codex home does not match the undo receipt.")
    try:
        assert_managed_layout(home)
    except RuntimeError as error:
        raise InstallerError(str(error)) from error

    install_id = str(receipt["install_id"])
    backup_root = _receipt_backup_root(home, install_id)
    if not is_within(backup_root, backups_root(home)):
        raise InstallerError("Undo receipt resolved an unsafe backup location.")
    skill_operation = _operation(receipt, "skill")
    policy_operation = _operation(receipt, "policy")
    destination = installed_skill_path(home)
    destination_policy = policy_path(home)
    ensure_plain_directory(destination, "Installed skill")
    ensure_plain_file_or_missing(destination_policy, "AGENTS.md")

    skill_changed = skill_operation.get("changed") is True
    policy_changed = policy_operation.get("changed") is True
    actions: list[str] = []
    if skill_changed:
        _assert_post_state(target=destination, operation=skill_operation, kind="directory")
        actions.append(f"restore prior skill state: {destination}")
    if policy_changed:
        _assert_post_state(target=destination_policy, operation=policy_operation, kind="file")
        actions.append(f"restore prior AGENTS.md state: {destination_policy}")
    if not actions:
        actions.append("receipt contains no changes to undo")
        return UndoResult(applied=apply, changed=False, actions=actions)
    if not apply:
        return UndoResult(applied=False, changed=True, actions=actions)

    with _InstallLock(home):
        post_skill = stage_directory_copy(destination, destination.parent, destination.name) if skill_changed else None
        post_policy = destination_policy.read_bytes() if policy_changed else None
        post_policy_mode = regular_file_mode(destination_policy) if policy_changed else None
        skill_restored = False
        try:
            if skill_changed:
                _restore_skill_snapshot(destination, backup_root, skill_operation.get("preexisting") is True)
                skill_restored = True
            if policy_changed:
                _restore_policy_snapshot(destination_policy, backup_root, policy_operation.get("preexisting") is True)
        except Exception:
            rollback_errors: list[str] = []
            try:
                if policy_changed and post_policy is not None:
                    atomic_write_bytes(destination_policy, post_policy, mode=post_policy_mode)
            except Exception as rollback_error:  # pragma: no cover - catastrophic filesystem failure
                rollback_errors.append(str(rollback_error))
            try:
                if skill_restored and post_skill is not None:
                    atomic_replace_directory(post_skill, destination)
                    post_skill = None
            except Exception as rollback_error:  # pragma: no cover - catastrophic filesystem failure
                rollback_errors.append(str(rollback_error))
            if rollback_errors:
                raise InstallerError("Undo failed and rollback to installed state also failed: " + "; ".join(rollback_errors))
            raise
        finally:
            if post_skill is not None and post_skill.exists():
                shutil.rmtree(post_skill, ignore_errors=True)
    actions.append("undo applied using the managed receipt backup")
    return UndoResult(applied=True, changed=True, actions=actions)
