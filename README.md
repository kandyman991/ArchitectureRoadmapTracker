# Architecture Roadmap Tracker

Tree-first, GitHub-connected development control center. **T0 architecture and governance are merged. T1.1 canonical model is in draft PR #3; no production UI or cloud jobs exist yet.**

## Project contracts

- ARCHITECTURE.md — binding architecture and trust boundaries
- REQUIREMENTS.md — numbered acceptance requirements
- ROADMAP.md — milestone and submilestone plan
- AGENTS.md — mandatory engineering and PR rules
- DECISIONS.md — approved architecture decisions and change process
- CHAT_HANDOFF.md and docs/CHECKPOINTS.md — curated cross-session progress

## T1.1 structural prototype

The dependency-free in-memory Python core is in src/architecture_roadmap_tracker and described in docs/T1_1_CANONICAL_TREE.md. It implements stable-ID projects/nodes, a single ordered unlimited-depth hierarchy, safe moves/reordering, archive/restore, snapshot traversal, and validated commands.

Run from the repository root (Python 3.10+):

    PYTHONPATH=src python3 -m unittest discover -s tests -v

The required architecture-contract CI checks these regressions on each PR. **No persistent database, web UI, GitHub synchronization, ChatGPT tool adapter or cloud job runner has been implemented.**

## Product workflow

The roadmap tree is navigation, the Inspector is for decisions, and the Job Center is for controlling remote jobs. Each tree node may eventually reference multiple PRs, reviews, decisions, jobs and dependencies. A merged PR alone never means milestone acceptance.

See the live [T1.1 draft PR #3](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/3). Do not merge without the owner's explicit authorization.
