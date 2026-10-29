# Architecture Roadmap Tracker

Tree-first, GitHub-connected development control center. **T0 and T1.1 are merged; T1.2 is under development in draft PR #4. No production UI or cloud jobs exist yet.**

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
- T1.2 (draft): versioned requirement records, explicit typed dependencies, immutable architecture/human decision proposals and a shared append-only in-memory audit journal. See docs/T1_2_GOVERNANCE.md.

Run from repository root using Python 3.10+:

    PYTHONPATH=src python3 -m unittest discover -s tests -v

Required architecture-contract CI runs regressions on each PR. **No persistent database, real permissions, approved action execution, web UI, GitHub synchronization, ChatGPT adapter or cloud job runner has been implemented.** Actor text in the prototype is not authenticated.

## Product workflow

The roadmap tree is navigation, the Inspector is for decisions, and the Job Center is for controlling remote jobs. Each tree node may eventually reference multiple PRs, reviews, decisions, jobs and dependencies. A merged PR or green CI run alone never means milestone acceptance.

Review [T1.2 draft PR #4](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4) independently before merging. No merge without explicit owner authorization.
