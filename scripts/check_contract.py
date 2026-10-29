"""Offline, dependency-free governance checks; never reads GitHub credentials or network."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md", "ARCHITECTURE.md", "REQUIREMENTS.md", "ROADMAP.md",
    "AGENTS.md", "DECISIONS.md", "CHAT_HANDOFF.md", "docs/CHECKPOINTS.md",
    "docs/CONTINUITY.md", ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/CODEOWNERS", ".github/workflows/contract.yml",
)

def validate(root=ROOT):
    missing = [path for path in REQUIRED if not (root / path).is_file()]
    if missing:
        raise ValueError("Missing required contract files: " + ", ".join(missing))
    read = lambda path: (root / path).read_text(encoding="utf-8")
    reqs = re.findall(r"(?m)^- \*\*(ART-\d{3})\*\*:", read("REQUIREMENTS.md"))
    if len(reqs) < 30 or len(reqs) != len(set(reqs)):
        raise ValueError("Numbered requirements missing or duplicated")
    for name in ("ARCHITECTURE.md", "AGENTS.md", "ROADMAP.md"):
        body = read(name).lower()
        if not any(key in body for key in ("canonical", "tree-first")):
            raise ValueError(name + " misses canonical tree requirement")
        if "merge" not in body or "review" not in body:
            raise ValueError(name + " misses review/merge governance")
    roadmap = read("ROADMAP.md")
    for label in ("T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7"):
        if not re.search(rf"(?m)^## {label} — ", roadmap):
            raise ValueError("Roadmap missing " + label)
    agents = read("AGENTS.md")
    for word in ("CHAT_HANDOFF.md", "docs/CHECKPOINTS.md", "DECISIONS.md", "ART-xxx"):
        if word not in agents:
            raise ValueError("Agent contract missing " + word)
    workflow = read(".github/workflows/contract.yml")
    for snippet in ("pull_request:", "push:", "branches: [main]", "contents: read", "scripts/check_contract.py", "architecture-contract"):
        if snippet not in workflow:
            raise ValueError("Governance workflow missing " + snippet)
    if "contents: write" in workflow or "self-hosted" in workflow:
        raise ValueError("Governance workflow must not write to repository or use self-hosted runners")
    if "required check" not in read("docs/CONTINUITY.md").lower():
        raise ValueError("Document how to enable required status checks")
    return len(reqs)

if __name__ == "__main__":
    count = validate()
    print(f"Governance contract OK ({count} stable requirements).")
