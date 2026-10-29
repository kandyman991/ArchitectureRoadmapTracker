# Curated development checkpoints

## CP-T1.3 — draft projections, storage reference and migration

- **2026-10-29:** [Draft PR #5](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/5), branch `feature/t1-3-projections-storage` based on merged T1.2 main `843f9a8bcbbabb509f4fa4b1ebb112fc826a6fe2`. Not accepted or merged.
- Scope: deterministic read-only canonical tree projections; versioned typed snapshot export/import preserving immutable audit before/after history; strict graph/journal replay validation; SQLite reference persist-before-publish command storage, transactional v1-to-v2 migration, optimistic revision conflict rejection, and synthetic regressions.
- **Proposed ADR-0009:** evaluate SQLite versus atomic JSON and PostgreSQL. SQLite is a reversible reference adapter only; no final production datastore selection or change to `DECISIONS.md` is approved.
- Limits: no authenticated identity, project permission gate, hosted multi-user storage, signed audit, production backup/restore, acceptance/evidence engine, UI or cloud jobs. Per-instance concurrent command evaluation remains out of scope; separate process writers use SQLite CAS.
- **Verification:** first implementation CI may precede later code/docs commits. Inspect live required run on the **exact final PR head**; never promote a prior run to final verification.
- **Next:** independent architecture/security/data-integrity review and ADR decision, fix all findings, rerun final-head CI, and request explicit owner authorization before merge. Self-review is not independent.

## CP-T1.2 — merged and reviewed governance / audit

- [PR #4](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4) merged with explicit owner authorization as `843f9a8bcbbabb509f4fa4b1ebb112fc826a6fe2` on 2026-10-29.
- Final head `ae61fac8977257017ee4449f0f04a2e3f66e34a3` passed required [architecture-contract CI #40903141414](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40903141414), **50 tests**.
- [Separate-session ChatGPT review #5700453288](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4#pullrequestreview-5700453288) found and corrected (M1) stale link writes, (M2) missing ADR unlink and (L1) cross-project target existence disclosure. Review is not an independent human or distinct GitHub approval.
- Implemented in-memory versioned requirements, typed directed dependencies, immutable proposals and shared audit journal. Durable storage/auth/acceptance remain deferred to later milestones.

## CP-T1.1 — canonical tree accepted

- [PR #3](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/3) merged with owner authorization on 2026-10-29 at adceec5eabbdad0a52dc95bc2bf11ec3b51dc003.
- Final PR head 95a7c60d3ae0dd057f52039a1dfc55d92848e7a6 passed required CI [40892263612](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40892263612), 31 tests; post-merge main [40892711724](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40892711724) passed.
- Two medium findings resolved: duplicate normalized acceptance criteria and unsafe control/credential-bearing repository bindings. Review was separate ChatGPT session, **not external human approval**.
- In-memory tree with stable IDs, iterative arbitrary-depth traversal, atomic validated reorder/reparent, archive and project isolation. Not durable.

## CP-T0 — governance accepted

- [PR #1](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/1) merged 2026-10-29 at 5eecd748a32a106bb9bcdff3b695a5d169fa256d.
- T0 CI [40888078278](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40888078278) passed and main push CI [40888260255](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40888260255) passed.
- [Main ruleset 26127238](https://github.com/kandyman991/ArchitectureRoadmapTracker/rules/26127238) active at verification; solo maintainer has zero required external approvals; owner-authorized PR merge still mandatory.

## Checkpoint procedure

At each PR boundary record main/PR exact SHAs, required CI run and conclusion, review provenance, corrected and unresolved findings, scope boundaries, remaining work and next authorized step. Live GitHub state overrides old checkpoint text.
