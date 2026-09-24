from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "install.py"


class CliLifecycleTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        return result

    def test_preview_apply_doctor_reapply_and_undo(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "codex-home"
            home_arg = str(home)

            preview = self.run_cli("install", "--codex-home", home_arg, "--with-policy")
            self.assertIn("PREVIEW: changes planned/applied", preview.stdout)
            self.assertFalse(home.exists(), "preview must not create the Codex home")

            applied = self.run_cli(
                "install", "--codex-home", home_arg, "--with-policy", "--apply"
            )
            self.assertIn("APPLIED: changes planned/applied", applied.stdout)
            skill = home / "skills" / "gpt-development-orchestrator"
            self.assertTrue((skill / "SKILL.md").is_file())
            self.assertTrue((home / "AGENTS.md").is_file())

            receipts = list(
                (home / ".gpt-development-orchestrator" / "receipts").glob("*.json")
            )
            self.assertEqual(1, len(receipts))
            receipt = str(receipts[0])

            doctor = self.run_cli("doctor", "--codex-home", home_arg)
            self.assertIn("PASS python", doctor.stdout)
            self.assertIn("PASS installed-skill", doctor.stdout)
            self.assertIn("PASS policy", doctor.stdout)

            reapplied = self.run_cli(
                "install", "--codex-home", home_arg, "--with-policy", "--apply"
            )
            self.assertIn("APPLIED: already up to date", reapplied.stdout)
            self.assertEqual(1, len(list(Path(receipt).parent.glob("*.json"))))

            undo_preview = self.run_cli("undo", "--receipt", receipt)
            self.assertIn("PREVIEW: undo planned/applied", undo_preview.stdout)
            self.assertTrue(skill.exists())

            undo_applied = self.run_cli("undo", "--receipt", receipt, "--apply")
            self.assertIn("APPLIED: undo planned/applied", undo_applied.stdout)
            self.assertFalse(skill.exists())
            self.assertFalse((home / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
