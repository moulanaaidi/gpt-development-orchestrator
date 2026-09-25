"""Check documented thin-root workflow text; this does not enforce host behavior."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def normalized(relative_path: str) -> str:
    return " ".join(read(relative_path).split())


class WorkflowContractTests(unittest.TestCase):
    def test_policy_scopes_orchestration_to_substantial_work(self) -> None:
        policy = normalized("POLICY.md").lower()
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        for text in (policy, skill):
            self.assertIn("substantial", text)
            self.assertIn("trivial", text)
        self.assertNotIn("every implementation task", policy)

    def test_external_spec_path_skips_replanning(self) -> None:
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        self.assertIn("approved external specification", skill)
        self.assertIn("implement directly without recreating the plan", skill)
        self.assertIn("do not add an in-codex planning or review loop", skill)

    def test_thin_root_shape_is_documented(self) -> None:
        policy = normalized("POLICY.md").lower()
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        self.assertIn("one planning batch, one dispatch, one wait, one batched independent acceptance review", policy)
        self.assertIn("one planning batch, one dispatch, one wait, one batched review", skill)

    def test_luna_owns_high_volume_implementation_loop(self) -> None:
        worker = normalized("WORKER-INSTRUCTIONS.md").lower()
        delegation = normalized("skill/gpt-development-orchestrator/references/delegation.md").lower()
        for text in (worker, delegation):
            self.assertIn("repository discovery", text)
            self.assertIn("implementation", text)
            self.assertIn("debug", text)
            self.assertIn("verification", text)

    def test_review_is_one_batch_with_two_lenses(self) -> None:
        review = normalized("skill/gpt-development-orchestrator/references/review.md").lower()
        self.assertIn("two lenses in the same pass", review)
        self.assertIn("specification compliance", review)
        self.assertIn("engineering quality", review)
        self.assertIn("default to one correction cycle", review)

    def test_no_polling_and_no_tiny_worker_split(self) -> None:
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        delegation = normalized("skill/gpt-development-orchestrator/references/delegation.md").lower()
        self.assertIn("do not poll", skill)
        self.assertIn("tiny worker calls", skill)
        self.assertIn("do not poll", delegation)

    def test_routing_defaults_to_luna_without_per_task_ranking(self) -> None:
        routing = normalized("skill/gpt-development-orchestrator/references/routing.md").lower()
        self.assertIn("gpt_luna_builder", routing)
        self.assertIn("gpt-6 luna", routing)
        self.assertIn("do not perform a fresh model ranking", routing)
        self.assertIn("do not silently substitute another model", routing)

    def test_external_effect_boundaries_remain(self) -> None:
        policy = normalized("POLICY.md").lower()
        worker = normalized("WORKER-INSTRUCTIONS.md").lower()
        for text in (policy, worker):
            self.assertIn("commit", text)
            self.assertIn("push", text)
            self.assertIn("deploy", text)


if __name__ == "__main__":
    unittest.main()
