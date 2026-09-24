#!/usr/bin/env python3
"""Install, undo, or diagnose GPT Development Orchestrator safely."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from orchestrator_core.doctor import run_doctor
from orchestrator_core.filesystem import FileSafetyError
from orchestrator_core.installer import InstallerError, install, undo


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--codex-home", type=Path, help="Codex home; defaults to CODEX_HOME then ~/.codex")
    parser.add_argument("--source", type=Path, help="Skill source; defaults to this repository's skill package")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview-first installer and doctor for GPT Development Orchestrator."
    )
    subcommands = parser.add_subparsers(dest="command")

    install_parser = subcommands.add_parser("install", help="Preview or install the skill (default)")
    _add_common_arguments(install_parser)
    install_parser.add_argument("--apply", action="store_true", help="Apply changes; omitted means preview only")
    install_parser.add_argument(
        "--with-policy", action="store_true", help="Explicitly merge this package's owned policy block into AGENTS.md"
    )
    install_parser.add_argument("--policy-file", type=Path, help="Policy source used with --with-policy")
    install_parser.add_argument("--receipt", type=Path, help="Where to write the undo receipt after --apply")

    undo_parser = subcommands.add_parser("undo", help="Preview or apply receipt-driven restoration")
    undo_parser.add_argument("--receipt", type=Path, required=True, help="Receipt produced by an applied install")
    undo_parser.add_argument("--codex-home", type=Path, help="Must match the home recorded in the receipt")
    undo_parser.add_argument("--apply", action="store_true", help="Apply undo; omitted means preview only")

    doctor_parser = subcommands.add_parser("doctor", help="Read-only installation diagnostics")
    _add_common_arguments(doctor_parser)
    doctor_parser.add_argument("--policy-file", type=Path, help="Policy source to compare against installed AGENTS.md")
    doctor_parser.add_argument("--json", action="store_true", help="Emit structured JSON")
    return parser


def _normalise_default_command(argv: list[str]) -> list[str]:
    commands = {"install", "undo", "doctor", "-h", "--help"}
    if not argv or argv[0] not in commands:
        return ["install", *argv]
    return argv


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(_normalise_default_command(list(argv or sys.argv[1:])))
    try:
        if arguments.command == "install":
            result = install(
                codex_home=arguments.codex_home,
                source_skill=arguments.source,
                apply=arguments.apply,
                with_policy=arguments.with_policy,
                policy_source=arguments.policy_file,
                receipt_path=arguments.receipt,
            )
            heading = "APPLIED" if result.applied else "PREVIEW"
            print(f"{heading}: {'changes planned/applied' if result.changed else 'already up to date'}")
            for action in result.actions:
                print(f"- {action}")
            if result.receipt_path:
                print(f"Receipt: {result.receipt_path}")
            return 0
        if arguments.command == "undo":
            result = undo(arguments.receipt, codex_home=arguments.codex_home, apply=arguments.apply)
            heading = "APPLIED" if result.applied else "PREVIEW"
            print(f"{heading}: {'undo planned/applied' if result.changed else 'nothing to undo'}")
            for action in result.actions:
                print(f"- {action}")
            return 0
        if arguments.command == "doctor":
            report = run_doctor(
                codex_home=arguments.codex_home,
                source_skill=arguments.source,
                policy_source=arguments.policy_file,
            )
            if arguments.json:
                print(report.to_json())
            else:
                for check in report.checks:
                    print(f"{check.status:<4} {check.name}: {check.detail}")
            return 0 if report.healthy else 1
    except (FileSafetyError, InstallerError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    parser.error("No command selected")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
