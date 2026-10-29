# Curated development checkpoints

## CP-T2.1 — draft tree-first local web shell

- **2026-10-29:** [Draft PR #6](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/6), isolated branch `feature/t2-1-tree-shell` from merged T1.3 main `e787ad8756b0f9a05d4ab8a517596b4cd39d9a8f`. No competing open PR at branch creation. Unmerged, unaccepted.
- **Scope:** ART-002, ART-003 (partial), ART-004 (partial), ART-006 (selection only), ART-008 (responsive layout only), ART-027, ART-028 and ART-030. Reference dependency-free HTML/CSS/ES module tree with project switch, nested expansion, keyboard selection, contextual create/rename/reorder/archive/restore, and persisted authoritative commands through T1.3 reference SQLite + audit. No second stored hierarchy.
- **Security/architecture boundaries:** server restricted to loopback without public network binding, Host/Origin checks, bounded JSON-only POST and whitelist, synthetic data, no fabricated acceptance, no authenticated actor or tenant permission. Framework and production hosting remain undecided. T2.2 Inspector, T2.3 advanced accessibility/focus/large-tree performance, T3 GitHub integration and T5 jobs are not implemented.
- **Synthetic regression coverage:** T1/T1.3 existing 64 Python tests plus T2.1 Python HTTP checks (4 classes) and five Node test cases for tree visibility, folding and keyboard navigation. `architecture-contract` CI now requires both Python and JavaScript model checks. No manual-browser test/visual accessibility pass claimed.
- **Authoring checkpoint:** required [CI #40909798381](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40909798381) succeeded on `5182bf669a16c45063a14bd18430f333055bca0f` with **68 Python + 5 JS tests** and architecture contract check. Earlier failed runs on other heads are superseded; this success is not final-head CI after subsequent commits.
- **Outstanding:** separate-session architecture/security/data-integrity/UI review; fix all findings, rerun mandatory CI at final corrected head, inspect branch protection, and obtain new explicit owner authorization for merge. Draft PR, green self-tests and deployment reference are **not** independent acceptance.

## CP-T1.3 — merged projections and reversible storage reference

- **2026-10-29:** [PR #5](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/5) reviewed, corrected and **merged** to main as `e787ad8756b0f9a05d4ab8a517596b4cd39d9a8f`. Base was T1.2 `843f9a8bcbbabb509f4fa4b1ebb112fc826a6fe2`; ADR-0009 remained proposed.
- Scope: deterministic read-only canonical tree projections; versioned typed snapshot export/import preserving immutable audit before/after history; strict graph/journal replay validation; SQLite reference persist-before-publish command storage, transactional v1-to-v2 migration, optimistic revision conflict rejection, and synthetic regressions.
- **Proposed ADR-0009:** evaluate SQLite versus atomic JSON and PostgreSQL. SQLite is a reversible reference adapter only; no final production datastore selection or change to `DECISIONS.md` is approved.
- Limits: no authenticated identity, project permission gate, hosted multi-user storage, signed audit, production backup/restore, acceptance/evidence engine, UI or cloud jobs. Per-instance concurrent command evaluation remains out of scope; separate process writers use SQLite CAS.
- **Verified authoring checkpoint:** PR head `ab5355bdfa707cd8676cb0d7795fc06616c47718` passed mandatory [architecture-contract run #40905434303](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40905434303), **60 tests** and baseline check. This check predates the checkpoint documentation commit and is not proof for a later final head; reverify after it. CI/self-review is not independent technical review.
- **Separate-session AI review:** [PR review #5700838111](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/5#pullrequestreview-5700838111) examined head `caa346657c432499f355572b8b550b9cc05a7879` for architecture/security/data integrity and the SQLite migration/ADR design. Different ChatGPT session, **not** external human or distinct authenticated GitHub approval.
- **Four findings corrected:** (M1) prevalidate historical v1 snapshot inside migration transaction, rollback unchanged on corruption; (M2) fail closed on bad persisted digest before overwriting; (M3) reject cyclical ADR supersession on import; (M4) reject cross-project node rewrites in replay audit. Added four synthetic regressions.
- **Corrected code CI:** exact corrected code head `e4cbc2115eee8e3d0ac5515447942560f7d60178` passed required [architecture-contract run 40907004507](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40907004507) with **64 tests** and governance validation. Documentation edits **after** this commit require a new final-head run.
- **Live protection:** `main` still `843f9a8bcbbabb509f4fa4b1ebb112fc826a6fe2`; ruleset 26127238 active, strict required `architecture-contract`, zero mandatory GitHub reviewer approvals and no bypass actors.
- **Owner decision:** user's 2026-10-29 conditional instruction authorizes merge after review/corrections/CI of T1.3's **reversible reference** storage adapter. It does **not** select permanent SQLite production hosting; ADR-0009 stays **proposed**, and `DECISIONS.md` remains unchanged.
- **Final merge evidence:** corrected final PR head `43b779603e32047396f7f5db458ee40deb7eea79` passed required [CI #40907271929](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40907271929) (64 Python tests); main merge `e787ad8756b0f9a05d4ab8a517596b4cd39d9a8f` verified and [post-merge push CI #40907554828](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40907554828) succeeded. Merge does not automatically mark entire T1 accepted.

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
