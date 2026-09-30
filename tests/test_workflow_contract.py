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
    def test_planner_reviewer_is_model_agnostic(self) -> None:
        routing = normalized("skill/gpt-development-orchestrator/references/routing.md").lower()
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        readme = normalized("README.md").lower()

        self.assertIn("best suitable available model", routing)
        self.assertIn("explicit user model choice", routing)
        self.assertIn("do not hard-code a planner/reviewer", routing)
        self.assertIn("do not hard-code a planner/reviewer model family or name", skill)
        self.assertIn("does not name a mandatory planner/reviewer model", readme)

    def test_bundled_worker_role_is_consistent(self) -> None:
        worker = tomllib.loads(read("skill/gpt-development-orchestrator/agents/gpt_luna_builder.toml"))
        self.assertEqual(worker["model"], "gpt-6-luna")
        self.assertEqual(worker["model_reasoning_effort"], "medium")

    def test_root_selection_does_not_claim_automatic_switching(self) -> None:
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        self.assertIn("a skill cannot switch the active root model", skill)
        self.assertIn("capable planner/reviewer must be selected", skill)

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
        self.assertIn("do not add an in-session planning or review loop", skill)

    def test_thin_root_shape_is_documented(self) -> None:
        policy = normalized("POLICY.md").lower()
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        self.assertIn("one planning batch, one dispatch, one wait, one batched independent acceptance review", policy)
        self.assertIn("one planning batch, one dispatch, one wait, one batched review", skill)

    def test_prompt_surface_has_size_guardrails(self) -> None:
        self.assertLessEqual(len(read("skill/gpt-development-orchestrator/SKILL.md")), 3800)
        self.assertLessEqual(len(read("POLICY.md")), 1900)
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

    def test_worker_owns_high_volume_implementation_loop(self) -> None:
        worker = normalized("skill/gpt-development-orchestrator/agents/gpt_luna_builder.toml").lower()
        for term in ("discovery", "implementation", "debug", "verification"):
            self.assertIn(term, worker)

    def test_review_is_one_batch_with_two_lenses(self) -> None:
        review = normalized("skill/gpt-development-orchestrator/references/review.md").lower()
        self.assertIn("two lenses in the same pass", review)
        self.assertIn("specification compliance", review)
        self.assertIn("engineering quality", review)
        self.assertIn("default to one correction cycle", review)

    def test_compact_handoffs_and_delta_first_review(self) -> None:
        delegation = normalized("skill/gpt-development-orchestrator/references/delegation.md").lower()
        review = normalized("skill/gpt-development-orchestrator/references/review.md").lower()
        continuity = normalized("skill/gpt-development-orchestrator/references/continuity.md").lower()
        checkpoint = normalized("skill/gpt-development-orchestrator/templates/checkpoint.md").lower()

        self.assertIn("500 words", delegation)
        self.assertIn("delta-first review", review)
        self.assertIn("changed-file names and diff statistics", review)
        self.assertIn("300 words", continuity)
        self.assertIn("target <=300 words", checkpoint)

    def test_no_polling_and_no_tiny_worker_split(self) -> None:
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        self.assertIn("do not poll", skill)
        self.assertIn("tiny worker calls", skill)

    def test_routing_avoids_per_task_benchmarking(self) -> None:
        routing = normalized("skill/gpt-development-orchestrator/references/routing.md").lower()
        self.assertIn("do not perform a fresh model ranking", routing)
        self.assertIn("do not silently substitute models", routing)
        self.assertIn("re-evaluate routing only when", routing)

    def test_efficiency_claim_is_scoped_and_reproducible(self) -> None:
        readme = normalized("README.md").lower()
        benchmark = normalized("docs/BENCHMARK.md").lower()
        self.assertIn("measured context efficiency", readme)
        self.assertIn("29.2%", readme)
        self.assertIn("not a claim", readme)
        self.assertIn("static context-surface", benchmark)
        self.assertIn("runtime", benchmark)
        self.assertIn("909500bc8cf67b8b78fb6a90645ccea288772c30", benchmark)

    def test_external_effect_boundaries_remain(self) -> None:
        policy = normalized("POLICY.md").lower()
        worker = normalized("skill/gpt-development-orchestrator/agents/gpt_luna_builder.toml").lower()
        for text in (policy, worker):
            self.assertIn("commit", text)
            self.assertIn("push", text)
            self.assertIn("deploy", text)


if __name__ == "__main__":
    unittest.main()
