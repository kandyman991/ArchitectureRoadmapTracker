"""Offline governance baseline checks, NOT proof that future app architecture is correct."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md", "ARCHITECTURE.md", "REQUIREMENTS.md", "ROADMAP.md",
    "AGENTS.md", "DECISIONS.md", "CHAT_HANDOFF.md", "docs/CHECKPOINTS.md",
    "docs/CONTINUITY.md", ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/CODEOWNERS", ".github/workflows/contract.yml",
)
BASELINE_IDS = [f"ART-{i:03d}" for i in range(1, 31)]


def validate(root=ROOT):
    missing = [path for path in REQUIRED if not (root / path).is_file()]
    if missing:
        raise ValueError("Missing contract files: " + ", ".join(missing))

    def read(path):
        return (root / path).read_text(encoding="utf-8")

    matches = re.findall(r"(?m)^- \*\*(ART-\d{3,}):\*\*\s*(.+)$",
                         read("REQUIREMENTS.md"))
    ids = [item[0] for item in matches]
    if len(ids) != len(set(ids)):
        raise ValueError("Numbered requirements duplicated")
    expected = [f"ART-{i:03d}" for i in range(1, len(ids) + 1)]
    if len(ids) < len(BASELINE_IDS) or ids[:30] != BASELINE_IDS or ids != expected:
        raise ValueError("Requirement IDs missing, reordered or renumbered")
    if any(len(description.strip()) < 15 for _, description in matches):
        raise ValueError("Requirement descriptions must be substantive")

    architecture = read("ARCHITECTURE.md").lower()
    for marker in (
        "unlimited-depth tree", "canonical domain model", "same command engine",
        "exact relevant revision", "explicit human", "untrusted",
        "pull_request_target",
    ):
        if marker not in architecture:
            raise ValueError(f"Architecture contract missing invariant: {marker}")

    agents = read("AGENTS.md")
    for marker in (
        "CHAT_HANDOFF.md", "docs/CHECKPOINTS.md", "DECISIONS.md",
        "ART-xxx", "Never merge", "independent",
    ):
        if marker not in agents:
            raise ValueError(f"Agent contract missing: {marker}")

    roadmap = read("ROADMAP.md")
    for milestone in ("T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7"):
        if not re.search(rf"(?m)^## {milestone} — ", roadmap):
            raise ValueError(f"Roadmap missing {milestone}")
    for submilestone in ("T0.1", "T0.2", "T0.3", "T1.1", "T2.1",
                         "T3.1", "T4.1", "T5.1", "T6.1", "T7.1"):
        if submilestone not in roadmap:
            raise ValueError(f"Missing development scope: {submilestone}")

    workflow = read(".github/workflows/contract.yml")
    forbidden = (
        r"(?m)^\s*pull_request_target\s*:",
        r"(?m)^\s*contents\s*:\s*write\s*$",
        r"(?m)^\s*id-token\s*:\s*write\s*$",
        r"(?m)^\s*runs-on\s*:\s*self-hosted\s*$",
    )
    if any(re.search(pattern, workflow) for pattern in forbidden):
        raise ValueError("Governance workflow grants unsafe privileges")
    for marker in (
        "pull_request:", "push:", "branches: [main]", "contents: read",
        "scripts/check_contract.py", "architecture-contract",
        "python3 -m unittest discover -s tests",
    ):
        if marker not in workflow:
            raise ValueError("Governance workflow missing " + marker)

    for path in ("CHAT_HANDOFF.md", "docs/CHECKPOINTS.md"):
        body = read(path)
        if "main" not in body or "PR" not in body:
            raise ValueError(f"Continuity document {path} is incomplete")
    for marker in ("required status check", "ruleset", "26127238"):
        if marker not in read("docs/CONTINUITY.md").lower():
            raise ValueError("Ruleset and required status check must be documented")
    return len(ids)


if __name__ == "__main__":
    count = validate()
    print(f"Governance baseline OK ({count} requirements); not runtime architecture proof.")
