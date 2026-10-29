# Curated development checkpoints

## CP-T1.2 — draft domain governance / audit

- **2026-10-29:** [Draft PR #4](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4), branch feature/t1-2-governance-audit, based on main adceec5eabbdad0a52dc95bc2bf11ec3b51dc003. Under development; not merged or accepted.
- **Scope:** ART-005 typed edges (including cross-project explicit references, cycle prevention and deactivation); ART-011 versioned testable requirement records and many-to-many node links; ART-015 immutable decision and ADR proposals; ART-030 immutable before/after audit journal shared by all existing structural and new domain commands.
- **Privacy and trust:** test data synthetic; actor strings are unverified, proposals are not approvals. In-memory only; T1.3 persistence/recovery/concurrency, T3 authorization, and T4 acceptance remain unimplemented.
- **Verification:** new tests in tests/test_governance.py; exact final-head workflow results must be inspected live. No self-review is an independent technical review.
- **Pending:** complete CI, correct findings, obtain separate architecture/security/data-integrity review, reverify latest head CI, and request explicit owner authorization before merge.

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
