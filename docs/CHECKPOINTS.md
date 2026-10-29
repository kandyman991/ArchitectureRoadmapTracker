# Curated development checkpoints

## CP-T1.1 — draft canonical tree implementation

- **2026-10-29:** [PR #3](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/3), branch feature/t1-1-canonical-tree, base main 5eecd748a32a106bb9bcdff3b695a5d169fa256d; unmerged.
- **Verified implementation revision:** 46e7183bc086a741dd1d372716cf4a1cf11c7e6f. [Run #40890002136](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40890002136) succeeded with 29 tests. Verify any later commits separately.
- **Scope:** structural parts of ART-001/ART-002/ART-004: project isolation, immutable typed nodes, stable UUIDs, arbitrary nesting, deterministic sibling positions, atomic reparent/reorder, cycle rejection, archive/restore, snapshot iteration.
- **Corrections before green CI:** repaired an incorrect reorder test expectation and made traversal stable under later commands.
- **Pending:** independent technical review of T1.1, final-head CI on any later changes, explicit owner authorization to merge.
- **Still missing:** T1.2 requirements, dependencies, decision audit; T1.3 persistence/migrations/concurrency; T2 UI; T3 GitHub; T4 acceptance; T5 jobs; T6 ChatGPT.
- **Separate-session review:** a different ChatGPT review session inspected T1.1 architecture, security and data integrity against the repository contracts on 2026-10-29; it is **not an external/human independent approval**. F1: normalized duplicate acceptance criteria could be stored; F2: repo binding accepted control characters and credential-bearing/query URLs. Corrections and new synthetic regressions were pushed to PR #3; inspect the live final head and its CI before clearance.
- **Remaining limitations:** T1.1 has no durable storage, permission checks, asynchronous jobs or concurrency controls; those are explicitly future milestones, not silently accepted production capabilities.
- **Next:** verify exact post-correction PR head and architecture-contract run, record review limitations, then await explicit owner authorization; leave main untouched.

## CP-T0 — governance accepted

- [PR #1](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/1) merged 2026-10-29 at 5eecd748a32a106bb9bcdff3b695a5d169fa256d following explicit authorization.
- Final PR [CI #40888078278](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40888078278) passed 9 tests, and main push [CI #40888260255](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40888260255) passed.
- [Main branch ruleset 26127238](https://github.com/kandyman991/ArchitectureRoadmapTracker/rules/26127238) active at verification; setup issue #2 closed.
- Technical review was in the same authoring workflow, not a separate independent review.

## New checkpoint procedure

At PR and milestone boundaries record exact main/PR SHAs, check URL and result, review provenance, remaining scope and next authorized step. Live GitHub wins over old snapshots.
