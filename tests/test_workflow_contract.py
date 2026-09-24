"""Check documented workflow text; this does not enforce host behavior."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def normalized(relative_path: str) -> str:
    return " ".join(read(relative_path).split())


class WorkflowContractTests(unittest.TestCase):
    def test_policy_and_skill_require_sol_worker_review_and_fail_closed(self) -> None:
        policy = normalized("POLICY.md").lower()
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md").lower()
        self.assertIn("actual sol-authored plan", policy)
        self.assertIn("lower gpt worker", policy)
        self.assertIn("independent two-pass review by sol", policy)
        self.assertIn("sol creates an actual, task-specific plan", skill)
        self.assertIn("lower-gpt worker", skill)
        self.assertIn("sol independently reviews", skill)
        self.assertIn("two passes: specification compliance, then engineering quality", skill)
        for text in (policy, skill):
            self.assertIn("fail closed", text)
            self.assertIn("stop and report", text)
            self.assertIn("repeatedly retry", text)

    def test_policy_bounds_compatibility_checks_and_corrections(self) -> None:
        policy = normalized("POLICY.md")
        self.assertIn("Before implementation in a session, check once", policy)
        self.assertIn("Verify identity evidence for every Sol and worker", policy)
        self.assertIn("host changes or an invocation fails", policy)
        self.assertIn("at most two correction cycles", policy)
        self.assertIn("does not reset this limit", policy)

    def test_skill_covers_visual_gate_and_distinct_acceptance(self) -> None:
        skill = normalized("skill/gpt-development-orchestrator/SKILL.md")
        self.assertIn("representative production-quality screen", skill)
        self.assertIn("visual acceptance separately from structural validation", skill)
        self.assertIn("only when required by the target repository", skill)

    def test_briefs_are_compact_and_outcome_evidence_is_host_based(self) -> None:
        delegation = normalized("skill/gpt-development-orchestrator/references/delegation.md")
        brief = normalized("skill/gpt-development-orchestrator/templates/task-brief.md")
        checkpoint = normalized("skill/gpt-development-orchestrator/templates/checkpoint.md")
        self.assertIn("instead of copying their contents", delegation)
        self.assertIn("host-reported usage (or `unknown`)", brief)
        self.assertIn("Usage reported by host (or `unknown`)", checkpoint)

    def test_policy_is_guidance_not_a_host_enforcement_claim(self) -> None:
        policy = normalized("POLICY.md")
        self.assertIn("are strong process guidance, not a technical enforcement boundary", policy)
        self.assertIn("host-level gate", policy)


if __name__ == "__main__":
    unittest.main()
