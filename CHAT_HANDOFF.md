# Architecture Roadmap Tracker — curated handoff

**Current:** T1.2 implementation on [draft PR #4](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4), not merged or accepted.

## Verified baseline

- T0 governance PR #1 merged 2026-10-29, commit 5eecd748a32a106bb9bcdff3b695a5d169fa256d.
- T1.1 [PR #3](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/3) merged with explicit owner authorization at commit adceec5eabbdad0a52dc95bc2bf11ec3b51dc003 (2026-10-29). Corrected duplicate criterion and unsafe repository binding findings. Exact PR head 95a7c60d3ae0dd057f52039a1dfc55d92848e7a6 passed 31 tests in run 40892263612; merged main passed required check [40892711724](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40892711724).
- Review of T1.1 was performed in a separate ChatGPT session, **not** an external human approval. Provenance recorded in PR review #5699454523.
- Main protection [ruleset 26127238](https://github.com/kandyman991/ArchitectureRoadmapTracker/rules/26127238) was previously verified active, including strict required architecture-contract check. Inspect live settings again before merge.

## T1.2 scope — under development

- Branch feature/t1-2-governance-audit from merged T1.1 main adceec5eabbdad0a52dc95bc2bf11ec3b51dc003.
- Add immutable project-owned versioned requirements, typed directed dependency edges with global iterative blocking-cycle prevention and explicit cross-project links, architecture/human decision proposals, immutable project-scoped audit events.
- T1.1 structural command engine now records before/after events in the same in-memory journal. Unattributed legacy actors remain None and proposal records do **not** assert permission or human approval.
- Source, tests and design limitations: see docs/T1_2_GOVERNANCE.md and tests/test_governance.py. Traceability: ART-005, ART-011, ART-015 and ART-030 (partial); T1.1 invariants remain applicable.
- No DB, durable audit, concurrency guarantees, authenticated actor, approval workflow, acceptance evidence, GitHub sync, cloud runner or UI. These are future milestones.
- A **separate ChatGPT conversation** reviewed the T1.2 architecture, security and data integrity at PR head d425fd7214bbfd712e8152290fd50b13871ca2c7; [review #5700453288](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4#pullrequestreview-5700453288). This is a separate-session AI code review, **not** external human approval or a different authenticated GitHub reviewer.

## Latest verified T1.2 implementation checkpoint

- Exact implementation SHA **7744eaa2c7c896ba217088a6a8202a1184eaaa4b** passed mandatory [architecture-contract run #40901141881](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40901141881) with **48 tests** on 2026-10-29. The final PR head after any newer documentation or correction commits must be checked separately.
- Self-review hardening added immutable UTC timestamps to decision/ADR proposals and rejects multiline actor/action fields that could misrepresent an audit log.
- Separate-session review findings (2026-10-29): **M1** requirement node/ADR link writes lacked expected-version guards; **M2** ADR links could not be removed through a validated command; **L1** target lookup preceded cross-project intent check, revealing foreign ID existence. Corrected with required optimistic versions, immutable audited unlink, and deny-before-lookup plus synthetic regressions.
- The previous green run 40901283308 applies only to pre-fix head d425fd7214bbfd712e8152290fd50b13871ca2c7. **Fresh required CI must pass the final corrected head** before merge.
- The authoring workflow and green CI are **not independent technical review**. A separate architecture/security/data-integrity review remains the next gate.

## Next gate

Verify required architecture-contract CI on the corrected exact final head, confirm main protection and outstanding review threads, then merge only under the owner's explicit 2026-10-29 authorization if every gate is green. Do not represent this separate-session AI review as external human approval. T1.3 begins on a new branch after T1.2 acceptance.
