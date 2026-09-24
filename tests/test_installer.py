from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from orchestrator_core.filesystem import directory_digest
from orchestrator_core.installer import InstallerError, install, undo
from orchestrator_core.paths import POLICY_BEGIN, POLICY_END


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.home = self.root / "codex-home"
        self.source = self.root / "source" / "gpt-development-orchestrator"
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
        (self.source / "references").mkdir()
        (self.source / "references" / "workflow.md").write_text("workflow\n", encoding="utf-8")
        self.policy = self.root / "POLICY.md"
        self.policy.write_text("Use the orchestrator for substantial work.\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @property
    def destination(self) -> Path:
        return self.home / "skills" / "gpt-development-orchestrator"

    def test_preview_does_not_create_home_or_receipt(self) -> None:
        result = install(codex_home=self.home, source_skill=self.source)
        self.assertFalse(result.applied)
        self.assertTrue(result.changed)
        self.assertFalse(self.home.exists())
        self.assertIsNotNone(result.receipt_path)
        self.assertFalse(result.receipt_path.exists())

    def test_apply_installs_skill_and_is_idempotent(self) -> None:
        first = install(codex_home=self.home, source_skill=self.source, apply=True)
        self.assertTrue(first.changed)
        self.assertTrue((self.destination / "SKILL.md").is_file())
        self.assertIsNotNone(first.receipt_path)
        self.assertTrue(first.receipt_path.is_file())

        second = install(codex_home=self.home, source_skill=self.source, apply=True)
        self.assertFalse(second.changed)
        self.assertIsNone(second.receipt_path)

    def test_policy_apply_is_idempotent_and_keeps_one_owned_block(self) -> None:
        first = install(
            codex_home=self.home,
            source_skill=self.source,
            apply=True,
            with_policy=True,
            policy_source=self.policy,
        )
        self.assertTrue(first.changed)
        second = install(
            codex_home=self.home,
            source_skill=self.source,
            apply=True,
            with_policy=True,
            policy_source=self.policy,
        )
        self.assertFalse(second.changed)
        agents = (self.home / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(agents.count(POLICY_BEGIN), 1)
        self.assertEqual(agents.count(POLICY_END), 1)

    def test_apply_and_undo_restores_preexisting_skill_and_policy(self) -> None:
        self.destination.mkdir(parents=True)
        (self.destination / "old.txt").write_text("old skill", encoding="utf-8")
        agents = self.home / "AGENTS.md"
        agents.write_text("Existing policy\n", encoding="utf-8")

        result = install(
            codex_home=self.home,
            source_skill=self.source,
            apply=True,
            with_policy=True,
            policy_source=self.policy,
        )
        self.assertTrue((self.destination / "SKILL.md").is_file())
        policy_text = agents.read_text(encoding="utf-8")
        self.assertIn(POLICY_BEGIN, policy_text)
        self.assertIn(POLICY_END, policy_text)

        preview = undo(result.receipt_path)
        self.assertFalse(preview.applied)
        self.assertTrue(preview.changed)
        restored = undo(result.receipt_path, apply=True)
        self.assertTrue(restored.applied)
        self.assertEqual((self.destination / "old.txt").read_text(encoding="utf-8"), "old skill")
        self.assertEqual(agents.read_text(encoding="utf-8"), "Existing policy\n")

    def test_undo_removes_new_targets(self) -> None:
        result = install(
            codex_home=self.home,
            source_skill=self.source,
            apply=True,
            with_policy=True,
            policy_source=self.policy,
        )
        undo(result.receipt_path, apply=True)
        self.assertFalse(self.destination.exists())
        self.assertFalse((self.home / "AGENTS.md").exists())

    def test_undo_refuses_changed_installed_skill(self) -> None:
        result = install(codex_home=self.home, source_skill=self.source, apply=True)
        (self.destination / "SKILL.md").write_text("locally changed", encoding="utf-8")
        with self.assertRaisesRegex(InstallerError, "changed after"):
            undo(result.receipt_path, apply=True)

    def test_policy_is_never_touched_without_explicit_option(self) -> None:
        agents = self.home / "AGENTS.md"
        agents.parent.mkdir(parents=True)
        agents.write_text("Leave this alone\n", encoding="utf-8")
        install(codex_home=self.home, source_skill=self.source, apply=True)
        self.assertEqual(agents.read_text(encoding="utf-8"), "Leave this alone\n")

    def test_incomplete_policy_markers_fail_before_mutation(self) -> None:
        agents = self.home / "AGENTS.md"
        agents.parent.mkdir(parents=True)
        agents.write_text(f"{POLICY_BEGIN}\n", encoding="utf-8")
        with self.assertRaisesRegex(InstallerError, "incomplete"):
            install(
                codex_home=self.home,
                source_skill=self.source,
                apply=True,
                with_policy=True,
                policy_source=self.policy,
            )
        self.assertFalse(self.destination.exists())

    def test_apply_refuses_state_changed_before_lock(self) -> None:
        self.destination.mkdir(parents=True)
        (self.destination / "old.txt").write_text("old", encoding="utf-8")

        from orchestrator_core.installer import _InstallLock

        original_enter = _InstallLock.__enter__

        def mutate_then_enter(lock):
            (self.destination / "old.txt").write_text("concurrent change", encoding="utf-8")
            return original_enter(lock)

        with patch("orchestrator_core.installer._InstallLock.__enter__", mutate_then_enter):
            with self.assertRaisesRegex(InstallerError, "state changed"):
                install(codex_home=self.home, source_skill=self.source, apply=True)
        self.assertEqual(
            (self.destination / "old.txt").read_text(encoding="utf-8"),
            "concurrent change",
        )

    def test_apply_refuses_source_changed_while_staging(self) -> None:
        from orchestrator_core.filesystem import stage_directory_copy as real_stage

        def stage_then_change(source, parent, prefix):
            staged = real_stage(source, parent, prefix)
            (staged / "SKILL.md").write_text("changed during staging", encoding="utf-8")
            return staged

        with patch("orchestrator_core.installer.stage_directory_copy", stage_then_change):
            with self.assertRaisesRegex(InstallerError, "source changed"):
                install(codex_home=self.home, source_skill=self.source, apply=True)
        self.assertFalse(self.destination.exists())

    def test_receipt_contains_no_backup_path_control(self) -> None:
        result = install(codex_home=self.home, source_skill=self.source, apply=True)
        receipt = json.loads(result.receipt_path.read_text(encoding="utf-8"))
        self.assertIn("install_id", receipt)
        self.assertNotIn("backup_path", json.dumps(receipt))

    def test_receipt_cannot_be_written_outside_managed_receipts(self) -> None:
        with self.assertRaisesRegex(InstallerError, "managed receipts"):
            install(
                codex_home=self.home,
                source_skill=self.source,
                apply=True,
                receipt_path=self.root / "receipt.json",
            )

    def test_undo_rejects_receipt_outside_managed_receipts(self) -> None:
        result = install(codex_home=self.home, source_skill=self.source, apply=True)
        copied_receipt = self.root / "copied-receipt.json"
        copied_receipt.write_bytes(result.receipt_path.read_bytes())
        with self.assertRaisesRegex(InstallerError, "managed receipts"):
            undo(copied_receipt, apply=True)

    def test_codex_home_environment_default_is_used_without_writing(self) -> None:
        environment_home = self.root / "environment-home"
        with patch.dict(os.environ, {"CODEX_HOME": str(environment_home)}, clear=False):
            result = install(source_skill=self.source)
        self.assertIn(str(environment_home.resolve()), "\n".join(result.actions))
        self.assertFalse(environment_home.exists())

    def test_source_requires_regular_skill_entrypoint(self) -> None:
        entrypoint = self.source / "SKILL.md"
        entrypoint.unlink()
        entrypoint.mkdir()
        with self.assertRaisesRegex(InstallerError, "SKILL.md"):
            install(codex_home=self.home, source_skill=self.source)
        self.assertFalse(self.home.exists())

    def test_source_rejects_linked_skill_entrypoint_when_supported(self) -> None:
        entrypoint = self.source / "SKILL.md"
        entrypoint.unlink()
        external = self.root / "external-skill.md"
        external.write_text("# External\n", encoding="utf-8")
        try:
            os.symlink(external, entrypoint)
        except OSError as error:
            self.skipTest(f"symbolic links are unavailable on this host: {error}")
        with self.assertRaisesRegex(InstallerError, "symbolic link"):
            install(codex_home=self.home, source_skill=self.source)

    def test_rejects_managed_path_redirection_when_links_are_supported(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        redirect = self.home / "skills"
        self.home.mkdir()
        try:
            os.symlink(outside, redirect, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"directory links are unavailable on this host: {error}")
        with self.assertRaisesRegex(InstallerError, "symbolic link or junction|outside"):
            install(codex_home=self.home, source_skill=self.source)
        self.assertFalse((outside / "gpt-development-orchestrator").exists())

    def test_rejects_agents_redirection_when_links_are_supported(self) -> None:
        outside = self.root / "outside-agents.md"
        outside.write_text("external\n", encoding="utf-8")
        self.home.mkdir()
        agents = self.home / "AGENTS.md"
        try:
            os.symlink(outside, agents)
        except OSError as error:
            self.skipTest(f"file links are unavailable on this host: {error}")
        with self.assertRaisesRegex(InstallerError, "symbolic link or junction|outside"):
            install(codex_home=self.home, source_skill=self.source)
        self.assertEqual(outside.read_text(encoding="utf-8"), "external\n")

    def test_rejects_managed_state_redirection_when_links_are_supported(self) -> None:
        outside = self.root / "outside-managed"
        outside.mkdir()
        redirect = self.home / ".gpt-development-orchestrator"
        self.home.mkdir()
        try:
            os.symlink(outside, redirect, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"directory links are unavailable on this host: {error}")
        with self.assertRaisesRegex(InstallerError, "symbolic link or junction|outside"):
            install(codex_home=self.home, source_skill=self.source)
        self.assertFalse((outside / "receipts").exists())

    def test_rejects_receipts_and_backups_redirection_when_links_are_supported(self) -> None:
        self.home.mkdir()
        managed = self.home / ".gpt-development-orchestrator"
        managed.mkdir()
        for name in ("receipts", "backups"):
            with self.subTest(name=name):
                redirect = managed / name
                outside = self.root / f"outside-{name}"
                outside.mkdir()
                try:
                    os.symlink(outside, redirect, target_is_directory=True)
                except OSError as error:
                    self.skipTest(f"directory links are unavailable on this host: {error}")
                with self.assertRaisesRegex(InstallerError, "symbolic link or junction|outside"):
                    install(codex_home=self.home, source_skill=self.source)
                redirect.unlink()

    def test_undo_rejects_malformed_receipt_operations(self) -> None:
        result = install(codex_home=self.home, source_skill=self.source, apply=True)
        original = json.loads(result.receipt_path.read_text(encoding="utf-8"))
        cases = {
            "invalid-install-id": lambda value: value.update({"install_id": "../../bad"}),
            "missing-operation": lambda value: value["operations"].pop("policy"),
            "invalid-flag": lambda value: value["operations"]["skill"].update({"changed": "true"}),
            "null-changed-digest": lambda value: value["operations"]["skill"].update({"post_digest": None}),
            "unexpected-unchanged-digest": lambda value: value["operations"]["policy"].update({"post_digest": "a" * 64}),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name):
                malformed = json.loads(json.dumps(original))
                mutate(malformed)
                receipt = result.receipt_path.parent / f"{name}.json"
                receipt.write_text(json.dumps(malformed), encoding="utf-8")
                with self.assertRaises(InstallerError):
                    undo(receipt, apply=True)

    def test_undo_rolls_back_to_installed_state_when_policy_restore_fails(self) -> None:
        self.destination.mkdir(parents=True)
        (self.destination / "old.txt").write_text("old skill", encoding="utf-8")
        agents = self.home / "AGENTS.md"
        agents.write_text("old policy\n", encoding="utf-8")
        result = install(
            codex_home=self.home,
            source_skill=self.source,
            apply=True,
            with_policy=True,
            policy_source=self.policy,
        )
        installed_digest = directory_digest(self.destination)
        installed_policy = agents.read_bytes()
        with patch(
            "orchestrator_core.installer._restore_policy_snapshot",
            side_effect=OSError("injected policy restore failure"),
        ):
            with self.assertRaisesRegex(OSError, "injected policy restore failure"):
                undo(result.receipt_path, apply=True)
        self.assertEqual(directory_digest(self.destination), installed_digest)
        self.assertEqual(agents.read_bytes(), installed_policy)

    @unittest.skipIf(os.name == "nt", "POSIX mode semantics are not available on Windows")
    def test_policy_install_preserves_existing_file_mode_on_posix(self) -> None:
        agents = self.home / "AGENTS.md"
        agents.parent.mkdir(parents=True)
        agents.write_text("existing\n", encoding="utf-8")
        os.chmod(agents, 0o640)
        install(
            codex_home=self.home,
            source_skill=self.source,
            apply=True,
            with_policy=True,
            policy_source=self.policy,
        )
        self.assertEqual(stat.S_IMODE(agents.stat().st_mode), 0o640)


if __name__ == "__main__":
    unittest.main()
