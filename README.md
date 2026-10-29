# Architecture Roadmap Tracker

**Status: M0 architecture/governance bootstrap in review. No application functionality has been implemented.**

Architecture Roadmap Tracker is a **tree-first, GitHub-connected development control center** for multiple software projects. Users navigate an unlimited-depth roadmap, inspect a selected node, make recorded decisions, and initiate authorized development, review and verification jobs. Each job returns traceable evidence to its roadmap node.

## Start here

1. [ARCHITECTURE.md](ARCHITECTURE.md) — binding product and system boundaries.
2. [REQUIREMENTS.md](REQUIREMENTS.md) — numbered, testable requirements.
3. [ROADMAP.md](ROADMAP.md) — milestones and explicit exit gates.
4. [AGENTS.md](AGENTS.md) — mandatory rules for people and coding assistants.
5. [DECISIONS.md](DECISIONS.md) — approved choices and ADR change process.
6. [CHAT_HANDOFF.md](CHAT_HANDOFF.md) and [docs/CHECKPOINTS.md](docs/CHECKPOINTS.md) — curated cross-session continuity.
7. [docs/CONTINUITY.md](docs/CONTINUITY.md) — live GitHub verification and handoff procedure.

## Non-negotiable design

- One canonical, ordered, unlimited-depth tree with stable IDs, not independent copies for roadmap and progress.
- Tree navigation, node inspector and job center are the primary workspace.
- Nodes can link multiple requirements, PRs, code reviews, findings, CI runs, decisions, jobs and dependencies.
- Implementation, review, verification, completion and merge are **different** states; no inferred milestone completion on PR merge.
- External execution requires explicit scope, permissions, approval and audit trail. Never silently merge, deploy or change architecture.
- Cloud-first, multi-project, usable without ChatGPT; ChatGPT is one authorized client of the same command interface.

## First real-world validation

Use a **read-only/synthetic** import based on ReportMaker's M6.5 review and follow-up history to prove the tracker does not mistake a merged PR for full milestone acceptance. Do not copy private reports, customer data, repository tokens or credentials into this public repository.

## Development

This bootstrap PR is documentation and a dependency-free governance check only; it does **not** choose a web framework, database, hosting provider or runner vendor. See the reviewed gates in [ROADMAP.md](ROADMAP.md). Run the offline check:

```sh
python3 scripts/check_contract.py
python3 -m unittest discover -s tests -v
```

Do not treat this README as evidence of live CI or finished functionality. Verify the exact GitHub PR head and check results before merge.
