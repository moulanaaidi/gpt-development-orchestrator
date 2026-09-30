#!/usr/bin/env python3
"""Summarize paired runtime benchmark usage without inventing missing telemetry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

USAGE_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def normalize_usage(payload: dict[str, Any] | None) -> dict[str, int | None] | None:
    if payload is None:
        return None
    source: Any = payload
    for key in ("root_cli_usage", "worker_cli_usage", "usage"):
        if isinstance(payload.get(key), dict):
            source = payload[key]
            break
    if not isinstance(source, dict):
        return None
    normalized: dict[str, int | None] = {}
    any_known = False
    for key in USAGE_KEYS:
        value = source.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            normalized[key] = None
        else:
            normalized[key] = value
            any_known = True
    return normalized if any_known else None


def _sum_if_known(*values: int | None) -> int | None:
    return sum(values) if all(value is not None for value in values) else None


def usage_total(usage: dict[str, int | None] | None) -> int | None:
    if usage is None:
        return None
    return _sum_if_known(
        usage["input_tokens"],
        usage["output_tokens"],
        usage["reasoning_output_tokens"],
    )


def aggregate_usage(
    root: dict[str, int | None] | None,
    worker: dict[str, int | None] | None,
    *,
    worker_required: bool,
) -> dict[str, int | None]:
    if root is None or (worker_required and worker is None):
        return {
            "input_tokens": None,
            "cached_input_tokens": None,
            "output_tokens": None,
            "reasoning_output_tokens": None,
            "total_reported_tokens": None,
        }
    worker_values = worker or {key: 0 for key in USAGE_KEYS}
    result = {
        key: _sum_if_known(root[key], worker_values[key])
        for key in USAGE_KEYS
    }
    result["total_reported_tokens"] = usage_total(result)
    return result


def reduction_pct(baseline: int | None, candidate: int | None) -> float | None:
    if baseline in (None, 0) or candidate is None:
        return None
    return round((baseline - candidate) / baseline * 100, 1)


def build_summary(
    direct_payload: dict[str, Any],
    orchestrated_payload: dict[str, Any],
    worker_payload: dict[str, Any] | None,
    *,
    direct_accepted: bool,
    orchestrated_accepted: bool,
) -> dict[str, Any]:
    direct_root = normalize_usage(direct_payload)
    orchestrated_root = normalize_usage(orchestrated_payload)

    embedded_worker = None
    if isinstance(orchestrated_payload.get("worker_cli_usage"), dict):
        embedded_worker = {"worker_cli_usage": orchestrated_payload["worker_cli_usage"]}
    orchestrated_worker = normalize_usage(worker_payload or embedded_worker)

    direct_aggregate = aggregate_usage(direct_root, None, worker_required=False)
    orchestrated_aggregate = aggregate_usage(
        orchestrated_root, orchestrated_worker, worker_required=True
    )

    limitations: list[str] = []
    if orchestrated_worker is None:
        limitations.append(
            "worker usage is unknown; aggregate orchestrated usage cannot be calculated"
        )
    if not direct_accepted or not orchestrated_accepted:
        limitations.append("both candidates did not pass the same acceptance gate")

    comparable = (
        direct_accepted
        and orchestrated_accepted
        and orchestrated_worker is not None
    )
    return {
        "direct": {
            "accepted": direct_accepted,
            "root_usage": direct_root,
            "worker_usage": None,
            "aggregate_usage": direct_aggregate,
        },
        "orchestrated": {
            "accepted": orchestrated_accepted,
            "root_usage": orchestrated_root,
            "worker_usage": orchestrated_worker,
            "aggregate_usage": orchestrated_aggregate,
        },
        "comparison": {
            "root_input_reduction_pct": reduction_pct(
                None if direct_root is None else direct_root["input_tokens"],
                None if orchestrated_root is None else orchestrated_root["input_tokens"],
            ),
            "aggregate_input_reduction_pct": reduction_pct(
                direct_aggregate["input_tokens"],
                orchestrated_aggregate["input_tokens"],
            ),
            "aggregate_total_reported_token_reduction_pct": reduction_pct(
                direct_aggregate["total_reported_tokens"],
                orchestrated_aggregate["total_reported_tokens"],
            ),
            "equal_quality_efficiency_claim_eligible": comparable,
            "limitations": limitations,
        },
    }


def _accepted(value: str) -> bool:
    return value == "pass"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--direct-root", type=Path, required=True)
    parser.add_argument("--orchestrated-root", type=Path, required=True)
    parser.add_argument("--orchestrated-worker", type=Path)
    parser.add_argument("--direct-acceptance", choices=("pass", "fail"), required=True)
    parser.add_argument("--orchestrated-acceptance", choices=("pass", "fail"), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    summary = build_summary(
        _read_json(args.direct_root),
        _read_json(args.orchestrated_root),
        _read_json(args.orchestrated_worker) if args.orchestrated_worker else None,
        direct_accepted=_accepted(args.direct_acceptance),
        orchestrated_accepted=_accepted(args.orchestrated_acceptance),
    )
    rendered = json.dumps(summary, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
