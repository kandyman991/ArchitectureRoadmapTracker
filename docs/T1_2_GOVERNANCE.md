# T1.2 — Requirements, dependencies, proposals and audit journal

**Scope:** dependency-free, in-memory domain commands on the same CommandEngine as
T1.1. This is a reviewable prototype, not durable multi-user governance.

## Model and ownership

- Requirements are stable-ID, project-owned records with an independent unique
  code, nonempty testable criteria, monotonic version and direct links to any
  number of same-project roadmap nodes and proposed architecture decisions.
  Expected-version checks reject stale requirement revisions; link/unlink
  changes also increment the version.
- Dependencies are typed directed edges; for BLOCKS, **source depends on
  target**. Edges may target another project only when explicitly requested;
  target project/node existence is checked, and blocking cycles are rejected
  across the whole in-memory graph using iterative reachability. RELATES_TO
  is nonblocking. Deactivation retains history and allows a new edge.
- Architecture decisions are immutable ADR **proposals** with unique
  project-scoped references and optional proposed supersession links. Human
  decision records are immutable **proposals** associated with a project and
  optional node, with action, previous/proposed values, rationale and actor.
  Neither form can be marked approved or enact a protected action here.
- Commands append immutable audit entries with sequence, UTC observation
  timestamp, project, action, target ID, actor/rationale and frozen before/after
  snapshots. The preexisting T1.1 structural commands now share that journal;
  their actor may be None because the legacy API has no verified principal.
  An actor string is **not** an authenticated identity. Audit snapshots are
  returned as project-scoped tuples, with no public editing API.

## Invariants

- No second roadmap tree, no disconnected mutation controller, no implicit
  status/acceptance from linked requirements, proposals, or dependency edges.
- Reject duplicate requirement codes/criteria, duplicate active typed edges,
  self/indirect blocking cycles, unknown/foreign node references, archived
  targets for new links, invalid action input and revision conflicts.
- A failed command does not mutate the canonical records or append audit.
  A no-op does not create a false modification event.
- Reorders include snapshots of **all** affected sibling positions; archived
  records/links remain visible and are not physically deleted.
- No ADR proposal modifies version-controlled decisions or approvals.

## Security and limitations

All data is process-local. This milestone DOES NOT provide real authorization,
permission checks, identity verification, persistent append-only audit, durable
transactions, concurrency safety, migration, replay, webhook trust, secrets
management, actor signatures or authoritative evidence. These require later
T1.3/T3/T4/T5 milestones. A Python caller can still access underscored
in-memory members: the in-memory model must not be exposed as a security
boundary. Review and permissions are mandatory before any real integrations.
Published source and tests use only synthetic data.

## Regression verification

Run: PYTHONPATH=src python3 -m unittest discover -s tests -v.
Tests exercise requirement versions, node/decision links, global dependency
cycles, explicit cross-project references, archival, deactivation, proposal-
not-approval semantics, audit before/after snapshots, isolation and failure
atomicity. CI is necessary but **not** independent design review.

**Merge gate:** exact-head green architecture-contract, separate review
with real provenance and findings resolved, curated checkpoint, and explicit
owner authorization. No auto-merge.
