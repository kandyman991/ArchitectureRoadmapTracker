# Architecture Roadmap Tracker — curated handoff

**Current:** T2.1 is under development in [draft PR #6](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/6), isolated branch `feature/t2-1-tree-shell` from T1.3 merged main `e787ad8756b0f9a05d4ab8a517596b4cd39d9a8f`. **Do not merge** without a new, explicit owner authorization after separate review and final-head CI.

## Verified merged foundation

- T0 governance [PR #1](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/1) merged as `5eecd748a32a106bb9bcdff3b695a5d169fa256d`.
- T1.1 [PR #3](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/3) merged as `adceec5eabbdad0a52dc95bc2bf11ec3b51dc003`, after 31-test required CI on exact PR head and separate-session AI review (not external human approval).
- T1.2 [PR #4](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4) merged with owner authorization as **`843f9a8bcbbabb509f4fa4b1ebb112fc826a6fe2`** on 2026-10-29. Independent-in-a-separate-ChatGPT-session review [#5700453288](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4#pullrequestreview-5700453288) found stale requirement-link writes, missing ADR unlink, and cross-project lookup information exposure; all were corrected. Final PR head `ae61fac8977257017ee4449f0f04a2e3f66e34a3` passed [required CI run #40903141414](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40903141414), **50 tests**. Separate-session AI review is **not** an external human/GitHub approval.
- T1.3 [PR #5](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/5) separately reviewed in ChatGPT, four findings corrected; final head `43b779603e32047396f7f5db458ee40deb7eea79` passed [required CI #40907271929](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40907271929), 64 tests. Owner-authorized merge committed `e787ad8756b0f9a05d4ab8a517596b4cd39d9a8f` to main on 2026-10-29; [main push CI #40907554828](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40907554828) succeeded. ADR-0009 still proposed, no production SQLite selection.
- Existing [main ruleset 26127238](https://github.com/kandyman991/ArchitectureRoadmapTracker/rules/26127238) was previously verified active; **recheck live** settings and CI at merge gate.

## T1.3 historical development (merged; retained as provenance)

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

## T2.1 implementation on draft PR #6

- **Base:** merged T1.3 main `e787ad8756b0f9a05d4ab8a517596b4cd39d9a8f`, no competing PR at branch creation. `feature/t2-1-tree-shell`, PR #6 is **draft** and unmerged.
- **Scope:** ART-002, ART-003 (partial), ART-004 (partial), ART-006 (selection), ART-008 (responsive shell), ART-027, ART-028, ART-030. Tree-first HTML/CSS/ES-module prototype displays T1.3 canonical projections. Stable selection, nested folding, Up/Down/Left/Right/Home/End keyboard model, no second tree or fabricated statuses. Contextual create/rename/move/archive/restore all call the same audited canonical command engine through a loopback-only JSON API.
- **Security boundary:** no authentication, verified project permissions or hosted cloud deployment. Server binds only to 127.0.0.1, checks Host/Origin, JSON command allowlist, revision CAS, CSP and safe DOM text. Do not expose on a network or use real customer data. Static UI is a reversible experiment, **not** a permanent framework decision. T2.2 inspector, T2.3 advanced accessibility/large-tree virtualization, T3 GitHub and later jobs remain future work.
- **Files:** `src/architecture_roadmap_tracker/web.py`, `web/index.html`, `web/app.css`, `web/app.mjs`, `web/tree-model.mjs`, Python HTTP and Node display-model regressions, `docs/T2_1_WEB_SHELL.md`; CI workflow now requires Node model tests with no npm dependency.
- **Authoring regression checkpoint:** after two earlier failing runs, fixes to HTTP test naming and domain error priority passed [required CI run #40909798381](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40909798381) on exact code head `5182bf669a16c45063a14bd18430f333055bca0f`: 68 Python tests and 5 JavaScript tests, architecture baseline. **Not final-head evidence** for commits after this.
- **Reviewer:** no separate-session independent technical/UI review has occurred for T2.1. Authoring self-tests and green CI do not count as independent review or acceptance. No new owner authorization to merge PR #6.

## Current gate / next action

Finish authoring, obtain fresh required `architecture-contract` CI on the final PR head, and hand PR #6 to a **different ChatGPT conversation or external reviewer** for architecture, security, data-integrity, UI and keyboard/accessibility inspection. Correct all findings and rerun final-head CI, then ask the owner to authorize merging explicitly. Do not start T2.2 on PR #6 and do not mark T2.1 accepted solely from authoring CI.
