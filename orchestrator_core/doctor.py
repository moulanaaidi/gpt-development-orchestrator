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
    WORKER_ROLE_NAME,
    default_skill_source,
    installed_skill_path,
    policy_path,
    resolve_codex_home,
    worker_role_path,
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


def _check_worker_role(destination: Path, source_skill: Path) -> DoctorCheck:
    source = source_skill / "agents" / f"{WORKER_ROLE_NAME}.toml"
    try:
        ensure_plain_file_or_missing(source, "Luna worker role source")
        ensure_plain_file_or_missing(destination, "Luna worker role")
        if not source.exists():
            return DoctorCheck("worker-role", "FAIL", f"Luna worker role source is missing: {source}")
        if not destination.exists():
            return DoctorCheck("worker-role", "WARN", f"Not installed: {destination}. Run install.py --apply.")
        expected = source.read_bytes()
        actual = destination.read_bytes()
    except (FileSafetyError, OSError) as error:
        return DoctorCheck("worker-role", "FAIL", str(error))
    if actual != expected:
        return DoctorCheck(
            "worker-role",
            "FAIL",
            "Installed Luna worker role differs from the source. Run install.py --apply after reviewing local changes.",
        )
    return DoctorCheck("worker-role", "PASS", "Installed GPT-6 Luna worker role matches source")


def _check_policy(path: Path, source: Path) -> DoctorCheck:
    try:
        ensure_plain_file_or_missing(path, "AGENTS.md")
        ensure_plain_file_or_missing(source, "Policy source")
        if not source.exists():
            return DoctorCheck("policy", "FAIL", f"Policy source is missing: {source}")
        expected = source.read_bytes().replace(b"\r\n", b"\n").rstrip(b"\n")
        if POLICY_BEGIN.encode("ascii") in expected or POLICY_END.encode("ascii") in expected:
            return DoctorCheck("policy", "FAIL", "Policy source contains reserved installer-owned markers")
        expected_block = (
            POLICY_BEGIN.encode("ascii") + b"\n" + expected + b"\n" + POLICY_END.encode("ascii") + b"\n"
        )
        if not path.exists():
            return DoctorCheck(
                "policy",
                "FAIL",
                "Global orchestration policy is missing. Run install.py --with-policy --apply.",
            )
        content = path.read_bytes().replace(b"\r\n", b"\n")
    except (FileSafetyError, OSError) as error:
        return DoctorCheck("policy", "FAIL", str(error))
    begin = content.count(POLICY_BEGIN.encode("ascii"))
    end = content.count(POLICY_END.encode("ascii"))
    if begin == 0 and end == 0:
        return DoctorCheck(
            "policy",
            "FAIL",
            "Global orchestration policy block is missing. Run install.py --with-policy --apply.",
        )
    if begin == 1 and end == 1 and content.find(POLICY_BEGIN.encode("ascii")) < content.find(POLICY_END.encode("ascii")):
        start = content.find(POLICY_BEGIN.encode("ascii"))
        finish = content.find(POLICY_END.encode("ascii"))
        line_end = content.find(b"\n", finish)
        after = len(content) if line_end == -1 else line_end + 1
        if content[start:after] != expected_block:
            return DoctorCheck(
                "policy",
                "FAIL",
                "Global orchestration policy is stale. Run install.py --with-policy --apply.",
            )
        return DoctorCheck("policy", "PASS", "Installed global orchestration policy matches the source")
    return DoctorCheck("policy", "FAIL", "AGENTS.md has incomplete or duplicate orchestrator policy markers")


def _check_validator(repository_root: Path) -> DoctorCheck:
    validator = repository_root / "tools" / "validate_plan.py"
    if not validator.is_file():
        return DoctorCheck("validator", "WARN", "Plan validator is not present yet")
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
    policy_source: str | Path | None = None,
) -> DoctorReport:
    """Inspect only known package paths; this function never writes files."""
    home = resolve_codex_home(codex_home)
    source = Path(source_skill).expanduser().resolve() if source_skill else default_skill_source()
    source_check, source_digest = _check_source(source)
    repository_root = source.parent.parent
    policy = Path(policy_source).expanduser().resolve() if policy_source else repository_root / "POLICY.md"
    checks = [
        _check_python(),
        DoctorCheck("codex-home", "PASS", f"Using Codex home: {home}"),
        source_check,
        _check_installed(installed_skill_path(home), source_digest),
        _check_worker_role(worker_role_path(home), source),
        _check_policy(policy_path(home), policy),
        _check_validator(repository_root),
    ]
    return DoctorReport(checks=checks)
