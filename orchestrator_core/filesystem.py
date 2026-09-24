"""Small atomic filesystem primitives. They never discover unrelated files."""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import tempfile
import uuid
from pathlib import Path


class FileSafetyError(RuntimeError):
    """Raised when an expected managed path has an unsafe shape."""


def directory_digest(directory: Path) -> str:
    """Return a deterministic digest of regular files beneath *directory*."""
    if not directory.is_dir():
        raise FileSafetyError(f"Expected directory: {directory}")

    root = directory.resolve()
    digest = hashlib.sha256()
    all_paths = sorted(directory.rglob("*"))
    for path in all_paths:
        is_junction = getattr(path, "is_junction", None)
        if path.is_symlink() or bool(is_junction and is_junction()):
            raise FileSafetyError(f"Links and junctions are not supported in managed directories: {path}")
        try:
            path.resolve().relative_to(root)
        except ValueError as error:
            raise FileSafetyError(f"Managed directory entry resolves outside its root: {path}") from error
        if not path.is_file() and not path.is_dir():
            raise FileSafetyError(f"Unsupported managed directory entry: {path}")
    files = [path for path in all_paths if path.is_file()]
    for path in files:
        relative = path.relative_to(directory).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def ensure_plain_directory(path: Path, label: str) -> None:
    if path.exists() and not path.is_dir():
        raise FileSafetyError(f"{label} exists but is not a directory: {path}")
    if path.is_symlink():
        raise FileSafetyError(f"{label} must not be a symbolic link: {path}")


def ensure_plain_file_or_missing(path: Path, label: str) -> None:
    if path.exists() and not path.is_file():
        raise FileSafetyError(f"{label} exists but is not a regular file: {path}")
    if path.is_symlink():
        raise FileSafetyError(f"{label} must not be a symbolic link: {path}")


def copy_directory_snapshot(source: Path, destination: Path) -> None:
    """Create a durable snapshot before a managed directory is replaced."""
    if destination.exists():
        raise FileSafetyError(f"Backup destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, symlinks=False)


def stage_directory_copy(source: Path, parent: Path, prefix: str) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    stage = parent / f".{prefix}.staging-{uuid.uuid4().hex}"
    shutil.copytree(source, stage, symlinks=False)
    return stage


def atomic_replace_directory(staged: Path, target: Path) -> None:
    """Publish a fully staged directory, restoring the old target on failure."""
    if not staged.is_dir():
        raise FileSafetyError(f"Staged directory is missing: {staged}")
    target.parent.mkdir(parents=True, exist_ok=True)
    displaced: Path | None = None
    try:
        if target.exists():
            displaced = target.parent / f".{target.name}.displaced-{uuid.uuid4().hex}"
            os.replace(target, displaced)
        os.replace(staged, target)
    except Exception:
        if displaced is not None and displaced.exists() and not target.exists():
            os.replace(displaced, target)
        raise
    finally:
        if staged.exists():
            shutil.rmtree(staged, ignore_errors=True)
    if displaced is not None and displaced.exists():
        shutil.rmtree(displaced, ignore_errors=True)


def atomic_remove_directory(target: Path) -> None:
    """Remove a directory only after atomically moving it out of its live path."""
    if not target.exists():
        return
    retired = target.parent / f".{target.name}.retired-{uuid.uuid4().hex}"
    os.replace(target, retired)
    shutil.rmtree(retired, ignore_errors=True)


def atomic_write_bytes(target: Path, content: bytes, *, mode: int | None = None) -> None:
    """Atomically replace a file, preserving its mode unless one is supplied."""
    inherited_mode: int | None = None
    if target.exists() and target.is_file() and not target.is_symlink():
        inherited_mode = stat.S_IMODE(target.stat().st_mode)
    target.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if mode is not None or inherited_mode is not None:
            os.chmod(temporary, mode if mode is not None else inherited_mode)
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink(missing_ok=True)


def file_digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def regular_file_mode(path: Path) -> int | None:
    """Return a regular file's permission bits without following links."""
    if not path.exists() or not path.is_file() or path.is_symlink():
        return None
    return stat.S_IMODE(path.stat().st_mode)
