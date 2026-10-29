# Curated development checkpoints

## CP-T1.1 — canonical project/node tree implementation

- **Date:** 2026-10-29.
- **State:** draft implementation in [PR #3](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/3); NOT merged or accepted.
- **Starting base:** verified main SHA 5eecd748a32a106bb9bcdff3b695a5d169fa256d.
- **Branch:** feature/t1-1-canonical-tree. Check live GitHub for the current head, review findings, and exact-head CI; do not assume an old check applies.
- **Scope:** pure in-memory project/node tree, typed IDs, unlimited nesting, contiguous sibling order, safe structural commands and synthetic regression tests. Structural ART-001, ART-002, ART-004 only; ART-030 external adapters not implemented.
- **Validation plan:** existing architecture-contract plus deep/wide tree regression tests. CI and independent review remain unverified until inspected on final head.
- **Not in T1.1:** durable persistence, concurrency, audit/dependencies, app UI, GitHub integration, evidence acceptance, cloud job execution and ChatGPT plugin.
- **Next:** inspect PR #3 CI, correct any regression failures, obtain independent technical review if available, and await explicit owner authorization before merge.

## CP-T0 — accepted governance foundation

- PR [#1](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/1) merged on 2026-10-29 as main commit 5eecd748a32a106bb9bcdff3b695a5d169fa256d.
- Final-head [CI run 40888078278](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40888078278) passed 9 tests; post-merge main [run 40888260255](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40888260255) passed.
- Branch-protection [ruleset 26127238](https://github.com/kandyman991/ArchitectureRoadmapTracker/rules/26127238) active; configuration issue [#2](https://github.com/kandyman991/ArchitectureRoadmapTracker/issues/2) closed.
- T0 review was part of the original assistant workflow, not a separate external reviewer. Do not claim otherwise.

## Handoff procedure

At PR and milestone boundaries record exact main/PR SHAs, verified check URL/conclusion, reviewer provenance, unresolved findings and the next authorized task. Live GitHub wins over historical checkpoints.
