# T1.3 — Deterministic projections and snapshot persistence

**Status:** Draft PR #5, under development. **Storage ADR-0009 is proposed,
not approved.** No hosted/multi-user deployment or acceptance workflow.

## Canonical model and read-only projections

`project_outline(engine, project_id)` derives ordered nodes, depths, associated
requirement IDs, and outgoing active dependency IDs from the same canonical
T1.1/T1.2 command-engine state. No second hierarchy or persistent projection
table exists. An archived node remains in the outline. Cross-project target
details are not returned; the projection itself is not a permission boundary.
Status/verification/acceptance are **not inferred** in T1.3.

## Portable typed snapshot

`export_snapshot(engine) -> bytes` creates byte-deterministic version 1 JSON
for unchanged state, including all project/node/requirement/dependency/proposal
records and the entire in-memory historical audit journal with exact typed
before/after snapshots and UTC times. Stable IDs and sibling positions survive
round-trip. `import_snapshot(payload)` always returns a **new** validated
`CommandEngine`; it never mutates a running engine in place.

Input is hostile unless validated. The decoder rejects extra/unknown type
tags, wrong collections, duplicate IDs, invalid enum/approval states, malformed
timestamps, missing cross-references, orphaned parents, noncontiguous sibling
positions, dependency cycles, and invalid audit sequences. Unknown future
format versions fail closed. Maximum snapshot size: 32 MiB. This is not a
signed interchange format; no identity/authentication is claimed.

## Reference SQLite storage

`PersistentCommandEngine(path)` is the same validated command surface, with
persist-before-publish semantics in `_publish`: construct a candidate
canonical snapshot containing the new audit entry, validate, commit atomically
to SQLite with an optimistic database revision, and only then publish the
candidate in-memory. Failed I/O or stale writers leave state/audit unchanged.
Restart reloads and validates the committed snapshot. Database migration
v0 -> v1 -> v2 is transactional; v1 -> v2 preserves stored payloads and adds
revision/digest columns. SHA-256 digest detects accidental corruption, but
is **not** tamper evidence against an attacker with database write access.

This is a reference implementation with one JSON snapshot blob rather than a
scalable normalized online schema. Commands are serialized across cooperating
processes by SQLite CAS. In-process concurrent command evaluation on one
engine instance is **not thread-safe**. There is no lock manager, real user
authentication, per-project authorization, durable adversary-proof audit,
remote storage/backup orchestration, or end-to-end migration of real user data.
Backups and deployment are out of scope; no private data is present.
`DECISIONS.md` remains unchanged pending ADR approval.

## Regression gates

Run from repository root:

    PYTHONPATH=src python3 -m unittest discover -s tests -v

Synthetic tests exercise deterministic projected order/depth, project scope,
full graph and journal round trip, corrupt records, future formats, deep
hierarchy import, restart consistency, stale concurrent writers, SQLite
transaction failure, v1->v2 migration, and digest failure.

Traceability: ART-002, ART-004, ART-005, ART-011, ART-015, ART-027,
ART-028, ART-030. Later T4 work must still implement real revision-aware
evidence staleness, accepted status, and human approval gates.

**Merge gate:** independent architecture/security/data-integrity review,
correct all findings, fresh mandatory CI on exact final PR head, reviewed
ADR-0009 owner decision, and explicit owner authorization to merge. Green CI
or this implementation alone does not mean T1 is accepted.
