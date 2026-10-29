"""Synthetic offline regression tests for the bootstrap contract."""
import tempfile
import unittest
from pathlib import Path
from scripts.check_contract import ROOT, REQUIRED, validate


class ContractTests(unittest.TestCase):
    def test_baseline_is_valid(self):
        self.assertGreaterEqual(validate(), 30)

    def test_missing_contract_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in REQUIRED:
                if path == "AGENTS.md":
                    continue
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((ROOT / path).read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "AGENTS.md"):
                validate(root)

    def test_duplicate_requirement_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in REQUIRED:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((ROOT / path).read_text(encoding="utf-8"), encoding="utf-8")
            requirements = root / "REQUIREMENTS.md"
            requirements.write_text(
                requirements.read_text(encoding="utf-8") +
                "\n- **ART-001**: duplicate synthetic requirement\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicated"):
                validate(root)


if __name__ == "__main__":
    unittest.main()
