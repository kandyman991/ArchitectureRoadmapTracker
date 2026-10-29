# Architecture Roadmap Tracker

Tree-first, GitHub-connected development control center. **T0 and T1.1–T1.3 are merged. T2.1 is under development in draft PR #6. No production deployment, authentication or cloud jobs exist yet.**

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
- T1.3 (merged): read-only deterministic projections, strict versioned typed snapshots and a transaction-safe SQLite **reference** adapter with migrations; see docs/T1_3_STORAGE.md. ADR-0009 remains proposed, not a production datastore selection.
- T2.1 (draft): responsive tree-first browser reference shell, fold/selection, and contextual commands through the **same** canonical engine. See docs/T2_1_WEB_SHELL.md.

Run from repository root using Python 3.10+:

    PYTHONPATH=src python3 -m unittest discover -s tests -v

Required architecture-contract CI runs Python and T2.1 JavaScript model regressions on each PR. **T2.1 is a loopback-only development web prototype, not a hosted or authenticated application.** No GitHub synchronization, verified user permissions, accepted high-impact actions, full Inspector, Job Center, ChatGPT adapter or cloud runner has been implemented. Prototype actor text is unverified.

Run the synthetic T2.1 prototype on the development branch with Python 3.10+:

    PYTHONPATH=src python3 -m architecture_roadmap_tracker.web --db .local/tree-shell.db --demo

Open http://127.0.0.1:8765. Never expose this unauthenticated server to a public network or real customer data. No Node/npm installation is needed for the runtime; Node.js runs display-model tests in CI.

## Product workflow

The roadmap tree is navigation, the Inspector is for decisions, and the Job Center is for controlling remote jobs. Each tree node may eventually reference multiple PRs, reviews, decisions, jobs and dependencies. A merged PR or green CI run alone never means milestone acceptance.

[T1.3 PR #5](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/5) was separately reviewed, corrected, and merged at `e787ad8756b0f9a05d4ab8a517596b4cd39d9a8f`. Review [draft T2.1 PR #6](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/6) independently before any merge. No merge without explicit owner authorization.
