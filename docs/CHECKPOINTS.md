# Curated development checkpoints

## CP-T1.2 — draft domain governance / audit

- **2026-10-29:** [Draft PR #4](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4), branch feature/t1-2-governance-audit, based on main adceec5eabbdad0a52dc95bc2bf11ec3b51dc003. Under development; not merged or accepted.
- **Scope:** ART-005 typed edges (including cross-project explicit references, cycle prevention and deactivation); ART-011 versioned testable requirement records and many-to-many node links; ART-015 immutable decision and ADR proposals; ART-030 immutable before/after audit journal shared by all existing structural and new domain commands.
- **Privacy and trust:** test data synthetic; actor strings are unverified, proposals are not approvals. In-memory only; T1.3 persistence/recovery/concurrency, T3 authorization, and T4 acceptance remain unimplemented.
- **Verification:** code/documentation revision **7744eaa2c7c896ba217088a6a8202a1184eaaa4b** passed mandatory [CI run 40901141881](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40901141881), **48 tests**. This is evidence only for that exact SHA; commits after checkpoint recording require their own check.
- **Hardening:** immutable UTC proposal timestamps, multiline actor/action rejection to avoid spoofed audit text; proposal rationale/content may remain multiline.
- **Separate-session AI review:** PR review [#5700453288](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/4#pullrequestreview-5700453288) reviewed head d425fd7214bbfd712e8152290fd50b13871ca2c7 against architecture/security/data-integrity contracts. This is a distinct ChatGPT conversation, not an external human review or a separate GitHub identity.
- **Review corrections:** M1 stale requirement node/ADR link edits now require matching expected version; M2 erroneous ADR links can be removed through an audited, version-bumping command; L1 cross-project intent validation now precedes foreign target lookup. New synthetic regressions added.
- **Fresh verification:** old run 40901283308 was green for d425fd7214bbfd712e8152290fd50b13871ca2c7 only. The **final corrected PR head** requires a new successful architecture-contract run; do not infer clearance from an earlier revision.
- **Pending:** reverify live CI on the exact corrected final head, inspect merge protection/review conversations, merge only if green under the owner's explicit 2026-10-29 authorization. T1.3 remains a separate milestone.

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
