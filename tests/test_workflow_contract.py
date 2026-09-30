"""Check documented thin-root workflow text; this does not enforce host behavior."""

from pathlib import Path
import unittest
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def normalized(relative_path: str) -> str:
    return " ".join(read(relative_path).split())


class WorkflowContractTests(unittest.TestCase):
    def test_requested_model_pair_is_consistent(self) -> None:
        for path in (
            "README.md",
            "POLICY.md",
            "docs/ARCHITECTURE.md",
            "skill/gpt-development-orchestrator/SKILL.md",
            "skill/gpt-development-orchestrator/references/routing.md",
        ):
            with self.subTest(path=path):
                text = read(path)
                self.assertIn("gpt-6.1-sol", text)
                self.assertIn("GPT-6 Luna", text)
        worker = tomllib.loads(read("skill/gpt-development-orchestrator/agents/gpt_luna_builder.toml"))
        self.assertEqual(worker["model"], "gpt-6-luna")
        self.assertEqual(worker["model_reasoning_effort"], "medium")

    def test_root_selection_does_not_claim_automatic_switching(self) -> None:
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        self.assertIn("a skill cannot switch the active root model", skill)
        self.assertIn("report the blocker", skill)

    def test_policy_scopes_orchestration_to_substantial_work(self) -> None:
        policy = normalized("POLICY.md").lower()
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        for text in (policy, skill):
            self.assertIn("substantial", text)
            self.assertIn("trivial", text)

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

    def test_prompt_surface_has_size_guardrails(self) -> None:
        self.assertLessEqual(len(read("skill/gpt-development-orchestrator/SKILL.md")), 3400)
        self.assertLessEqual(len(read("POLICY.md")), 1800)
        worker = tomllib.loads(read("skill/gpt-development-orchestrator/agents/gpt_luna_builder.toml"))
        self.assertLessEqual(len(worker["developer_instructions"]), 1300)
        self.assertLessEqual(len(read("skill/gpt-development-orchestrator/templates/task-brief.md")), 900)

    def test_spec_by_reference_and_no_replay_are_explicit(self) -> None:
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        policy = normalized("POLICY.md").lower()
        worker = normalized("skill/gpt-development-orchestrator/agents/gpt_luna_builder.toml").lower()
        self.assertIn("repository path", skill)
        self.assertIn("do not replay prior model transcripts", skill)
        self.assertIn("instead of copying it", policy)
        self.assertIn("do not repeat the specification", worker)

    def test_luna_owns_high_volume_implementation_loop(self) -> None:
        worker = normalized("skill/gpt-development-orchestrator/agents/gpt_luna_builder.toml").lower()
        for term in ("discovery", "implementation", "debug", "verification"):
            self.assertIn(term, worker)

    def test_review_is_one_batch_with_two_lenses(self) -> None:
        review = normalized("skill/gpt-development-orchestrator/references/review.md").lower()
        self.assertIn("two lenses in the same pass", review)
        self.assertIn("specification compliance", review)
        self.assertIn("engineering quality", review)
        self.assertIn("default to one correction cycle", review)

    def test_no_polling_and_no_tiny_worker_split(self) -> None:
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        self.assertIn("do not poll", skill)
        self.assertIn("tiny worker calls", skill)

    def test_routing_defaults_to_luna_without_per_task_ranking(self) -> None:
        routing = normalized("skill/gpt-development-orchestrator/references/routing.md").lower()
        self.assertIn("gpt_luna_builder", routing)
        self.assertIn("gpt-6 luna", routing)
        self.assertIn("do not perform a fresh model ranking", routing)
        self.assertIn("do not silently substitute another model", routing)

    def test_external_effect_boundaries_remain(self) -> None:
        policy = normalized("POLICY.md").lower()
        worker = normalized("skill/gpt-development-orchestrator/agents/gpt_luna_builder.toml").lower()
        for text in (policy, worker):
            self.assertIn("commit", text)
            self.assertIn("push", text)
            self.assertIn("deploy", text)


if __name__ == "__main__":
    unittest.main()
