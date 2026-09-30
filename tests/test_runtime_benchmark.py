"""Tests for runtime benchmark aggregation and claim gating."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "summarize_runtime_benchmark.py"
SPEC = importlib.util.spec_from_file_location("runtime_benchmark", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
runtime_benchmark = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime_benchmark)


def payload(input_tokens: int, cached: int, output: int, reasoning: int) -> dict:
    return {
        "root_cli_usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached,
            "output_tokens": output,
            "reasoning_output_tokens": reasoning,
        }
    }


class RuntimeBenchmarkTests(unittest.TestCase):
    def test_missing_worker_usage_stays_unknown(self) -> None:
        result = runtime_benchmark.build_summary(
            payload(100, 50, 10, 5),
            payload(40, 20, 4, 2),
            None,
            direct_accepted=True,
            orchestrated_accepted=True,
        )
        self.assertIsNone(result["orchestrated"]["worker_usage"])
        self.assertIsNone(result["orchestrated"]["aggregate_usage"]["input_tokens"])
        self.assertIsNone(result["comparison"]["aggregate_input_reduction_pct"])
        self.assertFalse(result["comparison"]["equal_quality_efficiency_claim_eligible"])

    def test_worker_usage_is_aggregated_when_reported(self) -> None:
        worker = {
            "usage": {
                "input_tokens": 30,
                "cached_input_tokens": 10,
                "output_tokens": 3,
                "reasoning_output_tokens": 1,
            }
        }
        result = runtime_benchmark.build_summary(
            payload(100, 50, 10, 5),
            payload(40, 20, 4, 2),
            worker,
            direct_accepted=True,
            orchestrated_accepted=True,
        )
        self.assertEqual(result["orchestrated"]["aggregate_usage"]["input_tokens"], 70)
        self.assertEqual(
            result["orchestrated"]["aggregate_usage"]["total_reported_tokens"], 80
        )
        self.assertEqual(result["comparison"]["aggregate_input_reduction_pct"], 30.0)
        self.assertTrue(result["comparison"]["equal_quality_efficiency_claim_eligible"])

    def test_failed_acceptance_blocks_equal_quality_claim(self) -> None:
        worker = {
            "usage": {
                "input_tokens": 30,
                "cached_input_tokens": 10,
                "output_tokens": 3,
                "reasoning_output_tokens": 1,
            }
        }
        result = runtime_benchmark.build_summary(
            payload(100, 50, 10, 5),
            payload(40, 20, 4, 2),
            worker,
            direct_accepted=True,
            orchestrated_accepted=False,
        )
        self.assertFalse(result["comparison"]["equal_quality_efficiency_claim_eligible"])
        self.assertIn(
            "both candidates did not pass the same acceptance gate",
            result["comparison"]["limitations"],
        )

    def test_partial_usage_is_not_silently_zero_filled(self) -> None:
        result = runtime_benchmark.build_summary(
            payload(100, 50, 10, 5),
            payload(40, 20, 4, 2),
            {"usage": {"input_tokens": 30}},
            direct_accepted=True,
            orchestrated_accepted=True,
        )
        self.assertEqual(result["orchestrated"]["aggregate_usage"]["input_tokens"], 70)
        self.assertIsNone(result["orchestrated"]["aggregate_usage"]["output_tokens"])
        self.assertIsNone(
            result["orchestrated"]["aggregate_usage"]["total_reported_tokens"]
        )


if __name__ == "__main__":
    unittest.main()
