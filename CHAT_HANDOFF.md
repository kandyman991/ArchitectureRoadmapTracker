# Architecture Roadmap Tracker — curated handoff

**Current:** T1.3 is under development in [draft PR #5](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/5). The branch is `feature/t1-3-projections-storage`; **do not merge** without an explicit new owner authorization.

## Verified merged foundation

- T0 governance [PR #1](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/1) merged as `5eecd748a32a106bb9bcdff3b695a5d169fa256d`.
- T1.1 [PR #3](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/3) merged as `adceec5eabbdad0a52dc95bc2bf11ec3b51dc003`, after 31-test required CI on exact PR head and separate-session AI review (not external human approval).
- T1.2 [PR #4](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4) merged with owner authorization as **`843f9a8bcbbabb509f4fa4b1ebb112fc826a6fe2`** on 2026-10-29. Independent-in-a-separate-ChatGPT-session review [#5700453288](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4#pullrequestreview-5700453288) found stale requirement-link writes, missing ADR unlink, and cross-project lookup information exposure; all were corrected. Final PR head `ae61fac8977257017ee4449f0f04a2e3f66e34a3` passed [required CI run #40903141414](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40903141414), **50 tests**. Separate-session AI review is **not** an external human/GitHub approval.
- Existing [main ruleset 26127238](https://github.com/kandyman991/ArchitectureRoadmapTracker/rules/26127238) was previously verified active; **recheck live** settings and CI at merge gate.

## T1.3 isolated development

- Starting base: T1.2 merged `main` `843f9a8bcbbabb509f4fa4b1ebb112fc826a6fe2`. No other open PR at branch creation.
- Scope (ART-002, ART-004, ART-005, ART-011, ART-015, ART-027, ART-028, ART-030): deterministic read-only project/node projections, typed versioned full canonical snapshot import/export, audited persist-before-publish command adapter, SQLite reference schema migration and optimistic stale-writer guard, failure and round-trip tests.
- Files: `src/architecture_roadmap_tracker/projections.py`, `snapshots.py`, `storage.py`, `tests/test_t1_3.py`, `docs/T1_3_STORAGE.md`.
- Storage comparison and constraints in **proposed, not approved** [ADR-0009](docs/adr/0009-t1-3-reference-storage.md). Standard-library SQLite is only a **reversible T1.3 reference**, not approved as permanent production storage. `DECISIONS.md` remains unchanged.
- Snapshot codec rejects unknown types, invalid entity relationships, cycles, duplicate records, invalid journal sequence, and audited before/after history that does not reconstruct the final canonical records. SQLite transactional CAS handles distinct writer instances, not simultaneous command evaluation on the same instance.
- No auth, real user permissions, cloud hosting, UI, GitHub sync, evidence acceptance, background jobs, or ChatGPT tool surface. No production-grade signed audit or backup system. No human decision is inferred from a proposal.

## Current gate / next action

Verify CI at the **latest live PR #5 head** (do not reuse older run evidence); correct any findings; review the ADR and storage trade-offs independently; obtain a **separate** architecture/security/data-integrity review with honest provenance; correct findings and rerun exact-head CI. Seek explicit owner decision on ADR-0009 and explicit approval to merge. The authoring session is not an independent review, and neither green CI nor an open draft PR implies T1.3 acceptance. Do not begin T2 on the same branch.
