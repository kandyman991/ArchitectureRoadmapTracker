# Architecture Roadmap Tracker — curated handoff

**Current:** T1.1 canonical project/node tree, [draft PR #3](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/3), unmerged and not yet accepted.

## Verified baseline

- T0 [PR #1](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/1) merged into main SHA 5eecd748a32a106bb9bcdff3b695a5d169fa256d.
- [Post-merge main CI #40888260255](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40888260255): success.
- Ruleset [26127238](https://github.com/kandyman991/ArchitectureRoadmapTracker/rules/26127238): previously verified active; check live current state before merging.
- Before T1.1: no other open PRs/issues.

## T1.1 implementation evidence

- Branch: feature/t1-1-canonical-tree; based on main SHA above.
- Exact implementation commit **46e7183bc086a741dd1d372716cf4a1cf11c7e6f** passed required [GitHub CI run #40890002136](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40890002136), 29 tests, 2026-10-29.
- Any subsequent documentation commit changes the PR head and MUST be verified independently before claiming exact-head CI.
- Scope: in-memory immutable project/node models, stable IDs, unlimited-depth ordered parent tree, atomic structural commands, cycle/project isolation, archive safety, snapshot reads, synthetic regressions.
- **Not implemented:** durable storage, requirements/dependencies/audit, UI, GitHub sync, milestone acceptance, cloud jobs, ChatGPT tools.
- No separate independent technical review has been obtained; a same-author review must not be represented as independent.

## Separate T1.1 architecture/security/data-integrity review (2026-10-29)

- A separate ChatGPT review session inspected PR #3 code and synthetic tests against AGENTS.md, ARCHITECTURE.md, REQUIREMENTS.md, ROADMAP.md and DECISIONS.md. This is **not an independent human/external reviewer or a GitHub approval from a distinct identity**.
- F1 (data integrity): acceptance criteria were normalized without rejecting duplicates. Now rejected atomically; regression added.
- F2 (security/input hygiene): opaque repository bindings accepted embedded control characters and credential-bearing or query-string URLs. Now rejected before publishing project records; regression added. This is not a substitute for T3 identity, authentication and authorization checks.
- Corrections and review evidence are in draft PR #3. **Verify the actual final PR SHA and fresh required CI after these documentation updates; do not infer success from the earlier green runs.**
- No external execution, storage, permissions or concurrency was added; T1.2/T1.3/T3 retain those obligations. PR remains unmerged pending owner authorization.

## Next action

Inspect live PR #3 final head/CI, perform independent architecture/data-integrity review, fix findings, and seek explicit owner approval before merge. T1.2 must begin only on a new scoped branch after T1.1 acceptance.
