# Architecture Roadmap Tracker — testable requirements

**Status:** Proposed M0 baseline. Each `ART-xxx` requirement is independently traceable and must remain stable; approved scope changes require a reviewed ADR or requirement-change record. Design requirement != evidence of implementation.

## Tree and inspector

- **ART-001:** Support multi-project workspaces with independent permissions and project bindings.
- **ART-002:** Present one canonical ordered roadmap tree with arbitrary nesting depth and stable node IDs.
- **ART-003:** Expand/collapse, keyboard navigate, filter/search and restore tree selection and expansion without losing context.
- **ART-004:** Add, rename, move, reorder, archive and restore nodes transactionally; prevent cycles, duplicates and data loss.
- **ART-005:** Support typed, directed, auditable dependencies across nodes and explicit cross-project references.
- **ART-006:** Selecting any node opens an inspector without replacing or losing tree position.
- **ART-007:** Inspector shows multiple linked PRs, reviews, commits, checks, jobs, findings, requirements, architecture decisions and dependencies.
- **ART-008:** Node presentation handles large trees without forced fixed-size cards or overlapping content; preserve accessibility and focus.
- **ART-009:** Progress rollups are derived from accepted child requirements and validation, not manually maintained totals.

## Governance and traceability

- **ART-010:** Distinguish planned, implemented, reviewed, verified, blocked, accepted and complete states with definitions.
- **ART-011:** Require explicit per-node acceptance criteria and trace each criterion to specific revision-aware evidence.
- **ART-012:** Never infer milestone complete solely from merge, CI green, job finished or assistant claims.
- **ART-013:** Mark evidence stale on relevant code, review, policy or requirement revisions and explain invalidated gates.
- **ART-014:** Persist review findings, severity, correction/waiver history and exact revision/attempt.
- **ART-015:** Record human decisions with identity, rationale, time, scope and immutable history; cannot silently rewrite an ADR.
- **ART-016:** Make final acceptance and merge dependent on mandatory checks and explicit human authorization.

## GitHub and jobs

- **ART-017:** Bind multiple GitHub repositories per project; sync live PR, branch, issue, review and CI state with exact SHAs.
- **ART-018:** Webhook ingestion is authenticated, idempotent and reconcilable after missed events or API throttling.
- **ART-019:** Launch scoped development, independent review, fixes and tests from a selected roadmap node.
- **ART-020:** Every job has a stable target node, actor/approval, runner, exact base/ref, requested scope, state, attempts and results.
- **ART-021:** Provide a Job Center with logs, retry/cancel controls, status, errors, costs/quotas and links to the node.
- **ART-022:** Failed, stale, cancelled and partially successful jobs never masquerade as verified completion.
- **ART-023:** Require explicit human confirmation for merge, deploy, destructive and architectural-policy changes.

## Product integration and safety

- **ART-024:** A responsive cloud-hosted application works without the user's PC or a ChatGPT session.
- **ART-025:** Expose authenticated read/propose/execute tools to ChatGPT via an adapter sharing the core command engine.
- **ART-026:** Apply least-privilege per-project permissions; protect against injected instructions from GitHub and job output.
- **ART-027:** Maintain curated continuity checkpoints and independent live-status verification on every new session.
- **ART-028:** Run deterministic synthetic regression checks and exact-head required CI on every scoped PR.
- **ART-029:** Keep approved architecture, roadmap definitions and ADRs version-controlled; distinguish them from derived live status.
- **ART-030:** All UI and CLI state-changing operations must use validated commands, with an auditable result or failure.

## Minimum acceptance scenario

Import or synthesize a ReportMaker-like M6.5 hierarchy: foundation child is reviewed/passed and its PR merged; other mandatory children are unfinished. The tracker must report the parent as **incomplete**, display missing conditions and permit starting only an authorized next job. Add a newer commit after review and prove that the affected review/CI evidence becomes **stale**. No real customer data is used.

Requirement traceability must be explicit in every implementation PR. Deferred requirements remain visibly open rather than being dropped from the roadmap.
