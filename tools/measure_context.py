#!/usr/bin/env python3
"""Measure the orchestrator's core static context surface without model calls."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SURFACES = (
    ("Root skill", "skill/gpt-development-orchestrator/SKILL.md"),
    ("Optional global policy", "POLICY.md"),
    ("Bundled worker role", "skill/gpt-development-orchestrator/agents/gpt_luna_builder.toml"),
    ("Task brief template", "skill/gpt-development-orchestrator/templates/task-brief.md"),
)


def read_surface(path: str, ref: str | None) -> str:
    if ref is None:
        return (ROOT / path).read_text(encoding="utf-8")

    result = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{ref}:{path}"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "git show failed"
        raise RuntimeError(f"cannot read {path!r} from {ref!r}: {message}")
    return result.stdout


def measure(ref: str | None) -> list[tuple[str, str, int]]:
    return [(name, path, len(read_surface(path, ref))) for name, path in SURFACES]


def percent_reduction(base: int, head: int) -> float:
    if base <= 0:
        raise ValueError("baseline must be positive")
    return (base - head) / base * 100.0


def print_single(rows: list[tuple[str, str, int]], label: str) -> None:
    print(f"Context surface: {label}")
    print()
    print("| Surface | Characters |")
    print("| --- | ---: |")
    for name, _path, count in rows:
        print(f"| {name} | {count:,} |")
    print(f"| **Core hot-path total** | **{sum(row[2] for row in rows):,}** |")


def print_comparison(
    base_rows: list[tuple[str, str, int]],
    head_rows: list[tuple[str, str, int]],
    base_label: str,
    head_label: str,
) -> None:
    print(f"Context surface comparison: {base_label} -> {head_label}")
    print()
    print("| Surface | Baseline | Candidate | Reduction |")
    print("| --- | ---: | ---: | ---: |")
    for base, head in zip(base_rows, head_rows, strict=True):
        name, _path, base_count = base
        head_name, _head_path, head_count = head
        if name != head_name:
            raise RuntimeError("surface definitions changed during comparison")
        reduction = percent_reduction(base_count, head_count)
        print(f"| {name} | {base_count:,} | {head_count:,} | {reduction:.1f}% |")

    base_total = sum(row[2] for row in base_rows)
    head_total = sum(row[2] for row in head_rows)
    reduction = percent_reduction(base_total, head_total)
    print(
        f"| **Core hot-path total** | **{base_total:,}** | "
        f"**{head_total:,}** | **{reduction:.1f}%** |"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure deterministic static orchestration context size."
    )
    parser.add_argument(
        "--base-ref",
        help="Git ref for the baseline. Requires --head-ref.",
    )
    parser.add_argument(
        "--head-ref",
        help="Git ref for the candidate. Requires --base-ref.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if bool(args.base_ref) != bool(args.head_ref):
        print("--base-ref and --head-ref must be provided together", file=sys.stderr)
        return 2

    try:
        if args.base_ref:
            base_rows = measure(args.base_ref)
            head_rows = measure(args.head_ref)
            print_comparison(base_rows, head_rows, args.base_ref, args.head_ref)
        else:
            print_single(measure(None), "working tree")
    except (OSError, UnicodeError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
