# Architecture Roadmap Tracker — development roadmap

**Status:** Proposed baseline; no development milestones accepted yet. **T0 is only complete after documentation review, exact-head CI, verified protection and explicit owner-authorized merge.** Milestones below are a plan, not completed features.

The first useful user experience is **the roadmap tree and node inspector**. Do not defer them while building a generic issue tracker. Complete each submilestone independently with a small PR and exact-head checks.

## T0 — Project architecture, governance and continuity

- **T0.1:** Approve architecture, requirements, decisions, roadmap, agent rules and PR template.
- **T0.2:** Add offline contract CI, reviewed handoff/checkpoint convention and secure public-repository defaults.
- **T0.3:** Configure GitHub `main` protection/ruleset with required PRs, verified technical review, no bypass, and required exact-head checks. The solo-maintainer ruleset currently uses zero mandatory GitHub approvals; external independent review is a recommended process, not an enforced GitHub gate.
- **Exit:** Documentation review findings resolved, exact-head CI green, effective protection inspected, reviewer identity and limitations honestly recorded, and user-authorized merge. Governance bootstrap does not implement app features.

## T1 — Canonical domain and command engine

- **T1.1:** Typed projects, nodes, ordered unbounded tree, stable IDs, moves and cycle prevention.
- **T1.2:** Requirements, dependencies, decisions and append-only audit model.
- **T1.3:** Deterministic projections, validated commands, storage/migration and round-trip tests.
- **Exit:** Synthetic deep-tree, rollback, concurrency, import/export and isolation regressions pass.

## T2 — Tree-first UI and inspector (first user-visible prototype)

- **T2.1:** Cloud-ready web shell, primary tree, selection, folding and contextual actions.
- **T2.2:** Inspector for requirements, acceptance, PR/review/job placeholders and decisions.
- **T2.3:** Accessible large-tree behavior, layout expansion, search/filter and preserved focus.
- **Exit:** User can organize real-sized synthetic hierarchy and make draft decisions without a detached second roadmap.

## T3 — GitHub evidence integration

- **T3.1:** Authentication/permissions, repo binding, paging/rate-limit resilience.
- **T3.2:** Import/synchronize issues, multiple PR links, commits, reviews, checks, attempts and change events.
- **T3.3:** Webhook signatures/idempotency/replay/reconciliation and source provenance.
- **Exit:** Exact GitHub head and source-linked state consistent after missed/duplicate deliveries. No code execution yet.

## T4 — Acceptance and architecture enforcement

- **T4.1:** Acceptance policy, requirement evidence, rollups and blockers.
- **T4.2:** Review findings, stale evidence, independent-review verification and explicit human acceptance.
- **T4.3:** Architecture ADR linking/deviation reports, dependency analysis and audit.
- **Exit:** Regression reproduces merged foundation PR yet incomplete M6.5 milestone and proves stale-on-new-head behavior.

## T5 — Job Center and cloud execution

- **T5.1:** Scoped job model and provider/runner interface with explicit authorizations.
- **T5.2:** Development/review/fix/test jobs with exact-ref input, logs, cancellation and retries.
- **T5.3:** Outbox/webhooks, recovery, costs/quotas, approvals and human-only merge gate.
- **Exit:** Synthetic runner and one supported cloud runner show auditable correct states; failures/duplicates cannot mark nodes complete.

## T6 — ChatGPT adapter

- **T6.1:** Authenticated read-only project and node/status tools.
- **T6.2:** Safe propose/update and scoped job-request commands via the common engine.
- **T6.3:** Permission/approval UX, prompt-injection defenses and failure recovery.
- **Exit:** ChatGPT and UI observe the same state; no hidden machine or unapproved write path.

## T7 — Multi-project hardening and release

- **T7.1:** Cross-project authorization, recovery, audit exports and migration policies.
- **T7.2:** Security review, accessibility/usability and load/regression benchmarks.
- **T7.3:** Public deployment, documented quotas/operating costs and production release checklist.
- **Exit:** Independent review, validated recovery/rollback, accepted project onboarding and explicit release authorization.

## Universal gates

For every development PR: map requirement IDs, define tests and evidence, retain architecture boundaries, update checkpoint and handoff, verify CI at final head, resolve review findings, seek an independent reviewer when available (otherwise record the limitation), and do **not** merge without user's explicit authorization. No milestone auto-completion from a PR merge or optimistic job progress.
