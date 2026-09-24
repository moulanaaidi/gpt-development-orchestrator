from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_plan  # noqa: E402


def valid_plan() -> dict:
    return {
        "schema_version": "1.0",
        "plan": {
            "id": "test-plan",
            "title": "Test plan",
            "objective": "Exercise plan validation.",
            "status": "ready",
        },
        "model_registry": {
            "controller": ["sample-controller"],
            "worker": ["sample-worker", "sample-specialist"],
        },
        "tasks": [
            {
                "id": "TASK-1",
                "title": "First task",
                "readiness": "ready",
                "role": "worker",
                "model": "sample-worker",
                "dependencies": [],
                "write_set": ["src/one.py"],
                "mutates": True,
                "acceptance_criteria": ["Behavior is covered."],
                "validation_commands": ["python -m unittest"],
                "risk": "low",
                "parallel_group": "parallel-a",
            },
            {
                "id": "TASK-2",
                "title": "Second task",
                "readiness": "ready",
                "role": "worker",
                "model": "sample-specialist",
                "dependencies": ["TASK-1"],
                "write_set": ["docs/two.md"],
                "mutates": True,
                "acceptance_criteria": ["Documentation is complete."],
                "validation_commands": ["python tools/check_docs.py"],
                "risk": "medium",
            },
        ],
    }


class ValidatePlanTests(unittest.TestCase):
    def assert_invalid(self, plan: dict, expected: str) -> None:
        errors = validate_plan.validate_plan(plan)
        self.assertTrue(errors, "plan unexpectedly passed validation")
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_example_validates(self) -> None:
        value, load_errors = validate_plan.load_plan(ROOT / "examples" / "valid-plan.json")
        self.assertEqual([], load_errors)
        self.assertEqual([], validate_plan.validate_plan(value))

    def test_accepts_disjoint_tasks_in_one_parallel_group(self) -> None:
        self.assertEqual([], validate_plan.validate_plan(valid_plan()))

    def test_rejects_missing_required_field(self) -> None:
        plan = valid_plan()
        del plan["tasks"][0]["acceptance_criteria"]
        self.assert_invalid(plan, "$.tasks[0].acceptance_criteria: required field is missing")

    def test_rejects_unknown_fields(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["surprise"] = True
        self.assert_invalid(plan, "$.tasks[0].surprise: unknown field")

    def test_rejects_wrong_field_types_without_crashing(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["dependencies"] = "TASK-2"
        self.assert_invalid(plan, "$.tasks[0].dependencies: expected an array of strings")

    def test_rejects_duplicate_task_ids(self) -> None:
        plan = valid_plan()
        plan["tasks"][1]["id"] = "TASK-1"
        self.assert_invalid(plan, "duplicate task ID 'TASK-1'")

    def test_rejects_undeclared_role(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["role"] = "missing-role"
        self.assert_invalid(plan, "undeclared role 'missing-role'")

    def test_rejects_model_not_allowed_for_declared_role(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["model"] = "sample-controller"
        self.assert_invalid(plan, "is not declared for role 'worker'")

    def test_accepts_new_model_identifiers_from_session_registry(self) -> None:
        plan = valid_plan()
        plan["model_registry"]["worker"] = ["future-model-v42"]
        plan["tasks"][0]["model"] = "future-model-v42"
        plan["tasks"][1]["model"] = "future-model-v42"
        self.assertEqual([], validate_plan.validate_plan(plan))

    def test_accepts_routing_evidence_with_unknown_cost(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["routing"] = {
            "quality_floor": "Focused implementation with passing tests",
            "selection_reason": "Host describes this worker as suitable for bounded tasks",
            "cost_evidence": "unknown",
            "uncertainty": "No price information exposed by the host",
        }
        self.assertEqual([], validate_plan.validate_plan(plan))

    def test_rejects_incomplete_or_fabricated_routing_evidence(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["routing"] = {"quality_floor": " ", "cost_evidence": "free"}
        self.assert_invalid(plan, "$.tasks[0].routing.selection_reason: required field is missing")
        self.assert_invalid(plan, "$.tasks[0].routing.quality_floor: expected a non-empty string")
        self.assert_invalid(plan, "$.tasks[0].routing.cost_evidence: expected one of")

    def test_rejects_undeclared_dependency(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["dependencies"] = ["MISSING"]
        self.assert_invalid(plan, "undeclared task ID 'MISSING'")

    def test_rejects_dependency_cycle(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["dependencies"] = ["TASK-2"]
        self.assert_invalid(plan, "dependency cycle: TASK-1 -> TASK-2 -> TASK-1")

    def test_rejects_empty_acceptance_criteria(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["acceptance_criteria"] = ["  "]
        self.assert_invalid(plan, "$.tasks[0].acceptance_criteria[0]: expected a non-empty string")

    def test_rejects_mutating_task_without_validation_command(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["validation_commands"] = []
        self.assert_invalid(plan, "mutating tasks must declare at least one validation command")

    def test_rejects_overlapping_parallel_file_and_directory_scopes(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["write_set"] = ["src"]
        plan["tasks"][1]["parallel_group"] = "parallel-a"
        plan["tasks"][1]["write_set"] = ["src/nested/file.py"]
        self.assert_invalid(plan, "overlaps task 'TASK-1' in parallel group 'parallel-a'")

    def test_rejects_overlapping_parallel_recursive_directory_scope(self) -> None:
        plan = valid_plan()
        plan["tasks"][0]["write_set"] = ["src/**"]
        plan["tasks"][1]["parallel_group"] = "parallel-a"
        plan["tasks"][1]["write_set"] = ["src/nested/file.py"]
        self.assert_invalid(plan, "overlaps task 'TASK-1' in parallel group 'parallel-a'")

    def test_rejects_wildcards_except_terminal_recursive_directory_marker(self) -> None:
        for scope in ("src/*.py", "src/**/file.py", "src/file?.py", "src/[ab].py", "src/**/**"):
            with self.subTest(scope=scope):
                plan = valid_plan()
                plan["tasks"][0]["write_set"] = [scope]
                self.assert_invalid(plan, "expected a repository-relative")

    def test_accepts_lifecycle_statuses(self) -> None:
        plan = valid_plan()
        plan["plan"]["status"] = "in_progress"
        plan["tasks"][0]["readiness"] = "complete"
        self.assertEqual([], validate_plan.validate_plan(plan))

    def test_rejects_absolute_or_parent_traversal_write_scope(self) -> None:
        for scope in ("../outside.py", "C:/outside.py", "/outside.py"):
            with self.subTest(scope=scope):
                plan = valid_plan()
                plan["tasks"][0]["write_set"] = [scope]
                self.assert_invalid(plan, "expected a repository-relative")

    def test_rejects_duplicate_json_keys_and_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "plan.json"
            path.write_text('{"schema_version":"1.0","schema_version":"1.0"}', encoding="utf-8")
            _, errors = validate_plan.load_plan(path)
            self.assertIn("duplicate JSON object key 'schema_version'", errors[0])

            path.write_text("{broken", encoding="utf-8")
            _, errors = validate_plan.load_plan(path)
            self.assertIn("malformed JSON at line 1, column 2", errors[0])

    def test_cli_valid_and_invalid_exit_codes(self) -> None:
        example = ROOT / "examples" / "valid-plan.json"
        valid_result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "validate_plan.py"), str(example)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, valid_result.returncode, valid_result.stderr)
        self.assertIn("Valid plan:", valid_result.stdout)

        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_path = Path(temp_dir) / "invalid.json"
            invalid = deepcopy(valid_plan())
            invalid["tasks"][0]["model"] = "missing-model"
            invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
            invalid_result = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "validate_plan.py"), str(invalid_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(1, invalid_result.returncode)
        self.assertIn("$.tasks[0].model", invalid_result.stderr)


if __name__ == "__main__":
    unittest.main()
