"""Read-only diagnostics for the local orchestration package."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .filesystem import FileSafetyError, directory_digest, ensure_plain_directory, ensure_plain_file_or_missing
from .paths import (
    POLICY_BEGIN,
    POLICY_END,
    default_skill_source,
    installed_skill_path,
    policy_path,
    resolve_codex_home,
)


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class DoctorReport:
    checks: list[DoctorCheck] = field(default_factory=list)

    @property
    def healthy(self) -> bool:
        return not any(check.status == "FAIL" for check in self.checks)

    def to_json(self) -> str:
        return json.dumps({"healthy": self.healthy, "checks": [asdict(check) for check in self.checks]}, indent=2)


def _check_python() -> DoctorCheck:
    version = sys.version_info
    if version >= (3, 11):
        return DoctorCheck("python", "PASS", f"Python {version.major}.{version.minor}.{version.micro} is supported")
    return DoctorCheck("python", "FAIL", "Python 3.11 or newer is required")


def _check_source(source: Path) -> tuple[DoctorCheck, str | None]:
    try:
        ensure_plain_directory(source, "Skill source")
        if not source.exists():
            return DoctorCheck("source", "WARN", f"Skill source is not present yet: {source}"), None
        digest = directory_digest(source)
    except (FileSafetyError, OSError) as error:
        return DoctorCheck("source", "FAIL", str(error)), None
    return DoctorCheck("source", "PASS", f"Skill source is readable: {source}"), digest


def _check_installed(destination: Path, source_digest: str | None) -> DoctorCheck:
    try:
        ensure_plain_directory(destination, "Installed skill")
        if not destination.exists():
            return DoctorCheck("installed-skill", "WARN", f"Not installed: {destination}. Run install.py --apply.")
        installed_digest = directory_digest(destination)
    except (FileSafetyError, OSError) as error:
        return DoctorCheck("installed-skill", "FAIL", str(error))
    if source_digest is None:
        return DoctorCheck("installed-skill", "WARN", "Installed skill found, but source is unavailable for integrity comparison")
    if installed_digest != source_digest:
        return DoctorCheck(
            "installed-skill",
            "FAIL",
            "Installed skill differs from the source. Run install.py --apply after reviewing local changes.",
        )
    return DoctorCheck("installed-skill", "PASS", "Installed skill matches source integrity digest")


def _check_policy(path: Path) -> DoctorCheck:
    try:
        ensure_plain_file_or_missing(path, "AGENTS.md")
        if not path.exists():
            return DoctorCheck("policy", "PASS", "No global policy installed (optional)")
        content = path.read_bytes()
    except (FileSafetyError, OSError) as error:
        return DoctorCheck("policy", "FAIL", str(error))
    begin = content.count(POLICY_BEGIN.encode("ascii"))
    end = content.count(POLICY_END.encode("ascii"))
    if begin == 0 and end == 0:
        return DoctorCheck("policy", "PASS", "No orchestrator policy block installed (optional)")
    if begin == 1 and end == 1 and content.find(POLICY_BEGIN.encode("ascii")) < content.find(POLICY_END.encode("ascii")):
        return DoctorCheck("policy", "PASS", "One owned orchestrator policy block is present")
    return DoctorCheck("policy", "FAIL", "AGENTS.md has incomplete or duplicate orchestrator policy markers")


def _check_validator(repository_root: Path) -> DoctorCheck:
    validator = repository_root / "tools" / "validate_plan.py"
    if not validator.is_file():
        return DoctorCheck("validator", "WARN", "Plan validator is not present yet; complete LUNA-02")
    try:
        completed = subprocess.run(
            [sys.executable, str(validator), "--help"],
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return DoctorCheck("validator", "FAIL", f"Plan validator could not be executed: {error}")
    if completed.returncode != 0:
        return DoctorCheck("validator", "FAIL", "Plan validator failed its read-only --help check")
    return DoctorCheck("validator", "PASS", f"Plan validator is available and executable: {validator}")


def run_doctor(
    *,
    codex_home: str | Path | None = None,
    source_skill: str | Path | None = None,
) -> DoctorReport:
    """Inspect only known package paths; this function never writes files."""
    home = resolve_codex_home(codex_home)
    source = Path(source_skill).expanduser().resolve() if source_skill else default_skill_source()
    source_check, source_digest = _check_source(source)
    repository_root = source.parent.parent if source.parent.name == "skill" else Path(__file__).resolve().parent.parent
    checks = [
        _check_python(),
        DoctorCheck("codex-home", "PASS", f"Using Codex home: {home}"),
        source_check,
        _check_installed(installed_skill_path(home), source_digest),
        _check_policy(policy_path(home)),
        _check_validator(repository_root),
    ]
    return DoctorReport(checks=checks)
