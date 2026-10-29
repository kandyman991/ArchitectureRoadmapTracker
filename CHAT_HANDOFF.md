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

## Separate-session review and corrected code

- **2026-10-29:** separate-session ChatGPT architecture/security/data-integrity review [#5700838111](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/5#pullrequestreview-5700838111) at authoring head `caa346657c432499f355572b8b550b9cc05a7879`. This was an AI review in a **different conversation**, **not** external human review and **not** a distinct authenticated GitHub reviewer.
- Four moderate findings corrected on the PR branch: M1 corrupt v1 records were migrated before validation; M2 an existing writer could hide on-disk digest corruption; M3 imported ADR supersession cycles were accepted; M4 replay accepted cross-project node changes in a foreign event. New synthetic regressions validate rejection/rollback and no phantom audit events.
- Corrected code revision `e4cbc2115eee8e3d0ac5515447942560f7d60178` passed required [architecture-contract run #40907004507](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40907004507), **64/64 tests** plus architecture baseline. **This is not final-head CI after these documentation edits.**
- Live `main` remained `843f9a8bcbbabb509f4fa4b1ebb112fc826a6fe2`; [ruleset 26127238](https://github.com/kandyman991/ArchitectureRoadmapTracker/rules/26127238) verified active with strict required `architecture-contract`, PR requirement, conversation resolution and no mandatory separate GitHub approval.
- Owner's instruction on 2026-10-29 expressly authorizes merging **after** review, correction and fresh CI. This authorizes the reversible T1.3 reference implementation only, **not** a final production datastore decision. ADR-0009 remains proposed and `DECISIONS.md` unchanged.

## Current gate / next action

Verify a **new required CI run on the exact final PR head after these documentation changes**, inspect unresolved review threads and PR mergeability, then merge under the conditional owner authorization if all gates pass. Record merge SHA and check results in the PR timeline. T1.3 merge is not automatic milestone acceptance; T2 begins in a separate branch.
