# Curated development checkpoints

## CP-T0-BOOTSTRAP — PR #1 proposed architecture/governance baseline

- **Date:** 2026-10-29.
- **Scope:** T0 documents, rule conventions, PR template and synthetic offline validation. No application features.
- **Initial main:** `a59759de5af1bb19c8a3a2fe16560b695ad2a98a`.
- **PR:** [#1](https://github.com/kandyman991/ArchitectureRoadmapTracker/pull/1) on `bootstrap/m0-governance-contract`. Earlier head `3145a723d223920998bc2aa546c22fb4b1d9afd3` passed [workflow run 40881560366](https://github.com/kandyman991/ArchitectureRoadmapTracker/actions/runs/40881560366); this does not verify later review commits.
- **Rules:** live [ruleset 26127238](https://github.com/kandyman991/ArchitectureRoadmapTracker/rules/26127238) observed active 2026-10-29: PR required, strict `architecture-contract` check, up-to-date branch, unresolved conversations blocking, zero mandatory approvals, no bypass, no force push or deletion.
- **Review findings:** (1) mismatch between mandated GitHub review approvals and actual solo-maintainer rules; (2) checkpoints incorrectly said branch protection was missing; (3) weak requirements/CI contract regression checks. Corrections proposed; **same-agent review is not independent external review**.
- **Pending:** verify final-head CI, reviewer provenance, authorized PR merge and resulting main, then close [issue #2](https://github.com/kandyman991/ArchitectureRoadmapTracker/issues/2).
- **Not implemented:** core model, persistence, tree UI, GitHub synchronization, jobs, ChatGPT plugin or hosting.
- **Next:** once T0 accepted, start T1.1 in a separate PR.
- **Privacy:** public repo; synthetic fixtures, no credentials/customer or proprietary data.

## New checkpoint procedure

At each PR/milestone handoff record (1) exact main SHA, (2) PR number, base/head SHA, (3) required check/run/conclusion, (4) findings, provenance and resolutions, (5) requirement scope, (6) blockers/unverified conditions, (7) next action. Curated facts must not be replaced by mechanical or chat-derived status; compare with GitHub live each session.
