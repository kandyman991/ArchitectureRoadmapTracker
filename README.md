# Architecture Roadmap Tracker

Tree-first, GitHub-connected development control center. **T0, T1.1 and T1.2 are merged. T1.3 is under development in draft PR #5. No production UI or cloud jobs exist yet.**

## Project contracts

- ARCHITECTURE.md — binding architecture and trust boundaries
- REQUIREMENTS.md — numbered acceptance requirements
- ROADMAP.md — milestone and submilestone plan
- AGENTS.md — mandatory engineering and PR rules
- DECISIONS.md — approved architecture decisions and change process
- CHAT_HANDOFF.md and docs/CHECKPOINTS.md — curated cross-session progress

## Canonical core

The dependency-free in-memory Python core lives in src/architecture_roadmap_tracker.

- T1.1 (merged): stable-ID projects/nodes, one ordered unlimited-depth tree, safe moves and reordering, archive/restore and snapshot traversal. See docs/T1_1_CANONICAL_TREE.md.
- T1.2 (merged): versioned requirements, explicit typed dependencies, immutable decision proposals and a shared in-memory audit journal. See docs/T1_2_GOVERNANCE.md.
- T1.3 (draft): read-only deterministic projections, strict versioned typed snapshots and a transaction-safe SQLite **reference** adapter with migrations; see docs/T1_3_STORAGE.md and the unapproved ADR-0009 proposal.

Run from repository root using Python 3.10+:

    PYTHONPATH=src python3 -m unittest discover -s tests -v

Required architecture-contract CI runs regressions on each PR. **The T1.3 branch adds only a reference SQLite database, not production storage. No real permissions, approved action execution, web UI, GitHub synchronization, ChatGPT adapter or cloud job runner has been implemented.** Actor text in the prototype is not authenticated.

## Product workflow

The roadmap tree is navigation, the Inspector is for decisions, and the Job Center is for controlling remote jobs. Each tree node may eventually reference multiple PRs, reviews, decisions, jobs and dependencies. A merged PR or green CI run alone never means milestone acceptance.

Review [draft T1.3 PR #5](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/5) and proposed [ADR-0009](docs/adr/0009-t1-3-reference-storage.md) separately before authorizing a merge. No merge without explicit owner authorization.
