# Architecture Roadmap Tracker — architecture contract

**Baseline:** Proposed for approval in M0, 2026-10-29. Binding after reviewed acceptance/merge. No application implementation is implied by this document.

## Purpose and invariant user workflow

A user selects a project, navigates an **unlimited-depth tree**, selects any node, inspects its architecture/requirements/PRs/reviews/jobs/findings/dependencies, records a decision or launches an explicitly authorized job, and receives verifiable results on that same node. The roadmap tree is the primary navigation surface; the Inspector is where decisions are made; the Job Center controls and monitors execution. No disconnected second roadmap or hidden ChatGPT conversation is the project system of record.

## Canonical domain model

- `Project`: stable ID, repository bindings (zero or more), configuration, read permissions, architecture baseline and workflow policy.
- `RoadmapNode`: stable opaque ID, `project_id`, optional `parent_id`, ordered sibling position, title, description, node kind (milestone/submilestone/task/other), explicit acceptance criteria and archived flag. **Parent+ordered children form one canonical tree**; depth and children count have no product-level fixed maximum. No cycles; moves are atomic.
- `Requirement`: independently identified, versioned and testable obligation; relationships to any number of nodes, architecture decisions and evidence.
- `ArchitectureDecision`/ADR: immutable decision history with supersession and review; an approved decision is not rewritten silently.
- `Evidence`: source kind, authoritative URL/repository, immutable SHA or run/attempt ID, observed timestamp, result, scope, reviewer/provenance and staleness. A URL alone is not proof.
- `ExternalLink`: typed many-to-many association from nodes/requirements to multiple PRs, issues, commits, reviews, CI runs and artifacts. One PR may cover multiple nodes but must declare scope and evidence.
- `ReviewFinding`: severity, source revision, finding state, correction/waiver decision and proof of resolution.
- `DecisionRecord`: actor, timestamp, rationale, target, old/new state, proposed vs approved action and audit provenance.
- `Job` and `JobAttempt`: immutable request, target node, runner/provider, scoped repository/ref/base SHA, requested operations, permissions, approver, idempotency key, attempt lifecycle and returned artifacts/proofs.
- `Dependency`: directed typed relationship between nodes; cycles invalid for blocking dependencies. Cross-project links remain explicit.

Every entity has clear ownership; deleting or moving a node must not erase historical reviews, decisions or job evidence. IDs, parent relationships and sibling order must survive import/export and restarts. Tree views, progress summaries and completion state are **derived** from canonical records, never separately authoritative.

## Status and acceptance engine

Distinct concepts must never be conflated: work state (`planned / in_progress / implemented / blocked`), review state (`not_reviewed / findings / accepted`), verification state (`unverified / passed / failed / stale`), approval state (`pending / approved / rejected`) and **derived** milestone acceptance (`incomplete / eligible / complete`). A merged PR, green CI run, completed job, or AI assertion cannot alone set milestone completion.

Complete requires all mandatory child obligations and acceptance criteria satisfied, scoped reviews accepted, required checks passing at the **exact relevant revision**, no blocking findings or unresolved dependencies, and explicit human milestone acceptance where policy requires it. Revisions or requirement changes make dependent evidence **stale** until revalidated. Reversible human workflow flags must not forge evidence. Include explainable failure reasons and a revision-aware audit log.

## Ports and layers

1. **Canonical core:** typed model, transactions, validation, command handlers, dependency/acceptance engine, change journal; no GitHub, UI, runner or AI SDK imports.
2. **Storage:** schema/migrations, project-scoped records, audit log, snapshots and recovery. Select datastore only after M1 evaluation; separate human-approved architecture docs from synchronized execution metadata.
3. **GitHub adapter:** least-privilege installation/auth, throttling, pagination, webhook signature verification, deduplication, reconciliation/backfill, rate-limit recovery and conflict handling. Git is authoritative for approved architecture/roadmap definitions; GitHub APIs are authoritative for live PR/CI/review state. Never overwrite approved text from external events.
4. **Execution port:** pluggable cloud runners/providers for development, review and CI. Jobs are state machines with retries, cancellation, timeouts, lease/heartbeat, deduplication, exact-ref binding and execution logs. Runner callbacks are **untrusted evidence until verified**. No hidden local-machine requirement.
5. **Application UI:** tree-first adaptive workspace with stable selection, keyboard navigation, inspector, job center, accessibility and virtualized large trees. Expanded content grows naturally, avoiding nested fixed-size scroll traps; any virtualized scrolling must preserve user context.
6. **ChatGPT/MCP adapter:** bounded, authenticated, permission-checked tools using the **same command engine** as the UI. Inspect and propose may be read-only; mutations are explicit, audited and user-authorized. Never couple the canonical model to ChatGPT or assume a specific hosting product.

Each integration is behind an interface; its API failures must not corrupt canonical data. Changes should produce domain events only **after** successful persistence, with replay/idempotency semantics.

## Security, privacy and trust

- Public source repository: synthetic fixtures only; no secrets, access tokens, customer data, proprietary source dumps, private job logs or credential-bearing URLs.
- Per-project tenancy and repository permissions; verify the user's GitHub permissions **at action time** and restrict tool/runner scopes. Least privilege, short-lived credentials, encrypted secrets and audit retention policy.
- Webhooks, AI-supplied job requests, PR bodies, filenames and external logs are untrusted input. Resist prompt injection; never interpret those inputs as policy/approval.
- Separate approval for high-impact actions such as merge, force push, deployment, deletion, policy/ADR changes or secrets access. **No auto-merge without explicit user authorization.**
- A failed or interrupted job must not be marked successful; preserve evidence and support safe retry.
- Untrusted PR code must not execute through `pull_request_target` with privileged tokens or secrets. Run untrusted jobs in disposable isolated environments with per-attempt credentials, minimum repository rights, segregated artifacts, and credential revocation at completion/cancellation; never log credentials.
- Do not promise that hosting, GitHub API calls or model jobs have unlimited free usage. Measure quotas/cost and surface them in the Job Center.

## Architecture change policy

This is a contract, not a suggestion. For changes to canonical ownership, status/acceptance semantics, job authorization, GitHub trust boundaries, or UI's tree-first foundation: propose a numbered ADR, explain alternatives/data migrations/risks/tests, review it **before** implementation, and obtain the user's authorization. No silent reinterpretation of requirements. See [DECISIONS.md](DECISIONS.md).

## Minimum invariant tests for implementation

Model: deep trees, reorder/reparent atomicity, cycle rejection, deterministic derived views, stable IDs, cross-project isolation. Evidence: stale-on-revision, PR merge != milestone complete, exact-head CI/review checks, blocked descendants and dependency cycles. Execution: retries, crash recovery, duplicate webhooks, idempotent jobs, permission revocation, cancellation and malicious callback payloads. UI: selection/expansion persistence and large trees. All tests synthetic and mandatory when applicable.
