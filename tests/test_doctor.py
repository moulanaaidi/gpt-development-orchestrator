from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from orchestrator_core.doctor import run_doctor
from orchestrator_core.installer import install
from orchestrator_core.paths import POLICY_BEGIN


class DoctorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.source = self.root / "source" / "gpt-development-orchestrator"
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text("# Skill\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _check(self, report, name: str):
        return next(check for check in report.checks if check.name == name)

    def test_reports_missing_install_actionably_without_writing(self) -> None:
        report = run_doctor(codex_home=self.home, source_skill=self.source)
        self.assertTrue(report.healthy)
        self.assertEqual(self._check(report, "installed-skill").status, "WARN")
        self.assertFalse(self.home.exists())

    def test_reports_matching_install(self) -> None:
        install(codex_home=self.home, source_skill=self.source, apply=True)
        report = run_doctor(codex_home=self.home, source_skill=self.source)
        self.assertTrue(report.healthy)
        self.assertEqual(self._check(report, "installed-skill").status, "PASS")

    def test_detects_installed_integrity_difference(self) -> None:
        install(codex_home=self.home, source_skill=self.source, apply=True)
        installed = self.home / "skills" / "gpt-development-orchestrator" / "SKILL.md"
        installed.write_text("changed", encoding="utf-8")
        report = run_doctor(codex_home=self.home, source_skill=self.source)
        self.assertFalse(report.healthy)
        self.assertEqual(self._check(report, "installed-skill").status, "FAIL")

    def test_detects_incomplete_policy_markers(self) -> None:
        agents = self.home / "AGENTS.md"
        agents.parent.mkdir(parents=True)
        agents.write_text(f"{POLICY_BEGIN}\n", encoding="utf-8")
        report = run_doctor(codex_home=self.home, source_skill=self.source)
        self.assertFalse(report.healthy)
        self.assertEqual(self._check(report, "policy").status, "FAIL")

    def test_validator_check_is_present(self) -> None:
        report = run_doctor(codex_home=self.home, source_skill=self.source)
        self.assertIn(self._check(report, "validator").status, {"PASS", "WARN"})


if __name__ == "__main__":
    unittest.main()
