# Architecture decisions — register

**Status:** Proposed 2026-10-29; ratified by acceptance/merge of M0. Decisions must not be silently rewritten. Superseding a decision requires a new reviewed ADR under `docs/adr/` with motivation, alternatives, migration/risks, regression gates and explicit user authorization.

| ID | Decision | Rationale / non-goal |
| --- | --- | --- |
| ADR-0001 | Tree-first UX with Inspector and Job Center | The roadmap hierarchy is the main navigator, not a generic kanban clone. |
| ADR-0002 | Canonical ordered unlimited-depth node model | No fixed hierarchy level or duplicate status tree; stable IDs and atomic reparent. |
| ADR-0003 | Evidence-based derived completion | PR merge, job completion and green CI do not automatically complete milestones. |
| ADR-0004 | Unified command engine with authorized external adapters | UI/ChatGPT/CLI cannot disagree or bypass validation. |
| ADR-0005 | Cloud-first, multi-project, runner-agnostic | No dependency on a user's local machine or one agent provider. |
| ADR-0006 | Git-versioned approved contracts + live GitHub execution evidence | No separate unverifiable architecture copy; sync is not authoritative approval. |
| ADR-0007 | Human authorization for high-impact actions | No auto-merge, silent policy modification, destructive jobs or unattended release. |
| ADR-0008 | PR-first governance and curated cross-chat continuity | Prevent previous architectural drift, scope expansion and missing acceptance. |

## Explicitly undecided — do not assume

Web UI framework, backend/runtime language, datastore/hosting, GitHub Apps authorization specifics, cloud runner/provider, ChatGPT plugin distribution and pricing. Decide by small documented evaluation and ADR at the relevant milestone, not by an arbitrary early commitment.

## Decision change workflow

1. Create `docs/adr/NNNN-short-title.md` as a **proposal** linked to affected `ART-xxx` requirements.
2. Record alternatives, chosen trade-off, migration/security impacts and exact regression gates.
3. Request user authorization and independent review; do not implement policy-changing code first.
4. After accepted merge, update this register and relevant contracts in the same explicitly scoped PR.
5. Keep superseded decisions available for audit.
