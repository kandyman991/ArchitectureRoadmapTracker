# ADR-0009 (PROPOSED) — T1.3 reference storage and snapshot boundary

**Status:** Proposal for independent review and owner decision; NOT an approved change to `DECISIONS.md`.
**Scope:** ART-002, ART-004, ART-005, ART-011, ART-015, ART-027, ART-028, ART-030.
**Date:** 2026-10-29. This proposal does not authorize production deployment.

## Problem

The T1.1/T1.2 command engine owns one in-memory canonical graph and an in-memory audit journal.
T1.3 needs deterministic views, round-trip reconstruction, versioned migrations, and durable
all-or-nothing publication without choosing a permanent cloud hosting provider or replacing
the existing canonical write surface. No externally derived status may become authoritative.

## Alternatives evaluated

1. **Standard-library SQLite reference adapter (preferred *for T1.3 verification*):**
   cross-platform, transactional database with portable file format, exclusive writer
   serialization, rollback and a supported migration path; no external service/SDK.
   Limits: single database file, local file locking, no distributed tenancy, no production
   access control, and snapshot-rewrite amplification at scale.
2. **Atomic JSON file:** simple and deterministic but difficult to safely coordinate two
   processes, handle crash/recovery across platforms or migrate multiple documents.
3. **PostgreSQL:** stronger hosted multi-user story, but assumes an external service,
   hosting/budget and migration dependencies before the T1 evaluation is accepted.

## Proposed reversible reference implementation

- Keep the T1.1/T1.2 `CommandEngine` as the sole validated writer; keep projections
  ephemeral and read-only, derived from that canonical state.
- Use a `PersistentCommandEngine` subclass with a storage port. A command validates
  a candidate graph, commits the candidate plus its journal in one SQLite transaction,
  then publishes the in-memory candidate. On I/O, conflict or database failure the
  in-memory state and journal remain unchanged.
- Include a deterministic, versioned JSON *snapshot interchange* independent of the
  selected database backend. Import creates a new fully validated engine; never partially
  replaces a live engine. The format preserves explicit dataclass/enumeration types,
  UTC times, immutable audit before/after records, stable identities, and ordering.
- A versioned SQLite schema and migration (v1->v2) are exercised using synthetic
  historic fixtures. Digest checking detects accidental snapshot corruption but is
  **not** cryptographic authentication or tamper-proof auditing.
- Optimistic revisions are checked atomically inside SQLite transactions to reject
  stale, concurrent writers. This does not claim fully thread-safe in-process command
  evaluation or a hosted multi-user database.
- Keep repository architecture/ADR text in Git. Stored proposals **never** approve,
  overwrite, or supersede an authoritative Git contract.

## Migration and rollback

Start from an empty v0 DB or migrate a synthetic v1 snapshot to v2 in a transaction.
Reject unsupported future schema versions and malformed records before publishing.
Keep a restorable prior DB backup before any production migration (not implemented
here). Existing main branch databases do not exist; no user data migration is implied.
A future chosen production store may implement the same snapshot boundary.

## Security, risks and required regressions

Untrusted snapshots must reject unknown types, extra fields, duplicate IDs,
inconsistent parent or relationship ownership, invalid audit sequence/timestamps,
dependency cycles, malformed UTF-8/JSON, and unsupported formats.
Test deep trees, isolation, deterministic repeated exports, restart round-trips,
migration preservation, corrupted payload rollback, stale writer conflicts,
disk transaction failures, and audit continuity. Do not advertise the reference
SQLite adapter as a security boundary or production-ready multi-user storage.

**Decision gate:** this ADR stays a proposal until independent review and explicit
owner authorization. Do not update `DECISIONS.md`, select production hosting, or merge
PR #5 without those gates.
