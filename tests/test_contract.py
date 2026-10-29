"""Synthetic mutation regressions for T0 governance contracts."""
import tempfile
import unittest
from pathlib import Path

from scripts.check_contract import ROOT, REQUIRED, validate


class ContractTests(unittest.TestCase):
    def copy_contract(self):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        for path in REQUIRED:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT / path).read_text(encoding="utf-8"), encoding="utf-8")
        return directory, root

    def mutate(self, path, original, replacement, expected):
        directory, root = self.copy_contract()
        try:
            file = root / path
            text = file.read_text(encoding="utf-8")
            self.assertIn(original, text)
            file.write_text(text.replace(original, replacement, 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, expected):
                validate(root)
        finally:
            directory.cleanup()

    def test_baseline_valid(self):
        self.assertEqual(validate(), 30)

    def test_missing_contract_fails(self):
        directory, root = self.copy_contract()
        try:
            (root / "AGENTS.md").unlink()
            with self.assertRaisesRegex(ValueError, "AGENTS.md"):
                validate(root)
        finally:
            directory.cleanup()

    def test_duplicate_id_fails(self):
        directory, root = self.copy_contract()
        try:
            file = root / "REQUIREMENTS.md"
            file.write_text(file.read_text(encoding="utf-8") +
                            "\n- **ART-001:** duplicate requirement text\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicated"):
                validate(root)
        finally:
            directory.cleanup()

    def test_missing_or_renumbered_id_fails(self):
        self.mutate("REQUIREMENTS.md", "ART-030", "ART-031", "missing, reordered")

    def test_swapped_id_fails(self):
        self.mutate("REQUIREMENTS.md", "ART-002", "ART-032", "missing, reordered")

    def test_new_sequential_requirement_allowed(self):
        directory, root = self.copy_contract()
        try:
            file = root / "REQUIREMENTS.md"
            text = file.read_text(encoding="utf-8")
            insertion = "- **ART-031:** A newly reviewed synthetic requirement may be added to the baseline.\n"
            text = text.replace("## Minimum acceptance scenario", insertion + "\n## Minimum acceptance scenario")
            file.write_text(text, encoding="utf-8")
            self.assertEqual(validate(root), 31)
        finally:
            directory.cleanup()

    def test_erased_architecture_invariant_fails(self):
        self.mutate("ARCHITECTURE.md", "unlimited-depth tree",
                    "nested project nodes", "Architecture contract missing")

    def test_privileged_pr_trigger_fails(self):
        self.mutate(".github/workflows/contract.yml", "  workflow_dispatch:",
                    "  pull_request_target:", "unsafe privileges")

    def test_write_permission_fails(self):
        self.mutate(".github/workflows/contract.yml", "  contents: read",
                    "  contents: write", "unsafe privileges")


if __name__ == "__main__":
    unittest.main()
