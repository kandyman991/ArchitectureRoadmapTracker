"""T1.3 reference SQLite persistence behind the canonical CommandEngine.

This is a reversible evaluation adapter, not a selected production datastore.
A successful command commits a new canonical snapshot and audit in one SQLite
transaction before publishing it to the live in-memory engine.
"""
from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
import hmac
import os
from pathlib import Path
import sqlite3

from .errors import TreeError
from .snapshots import MAX_SNAPSHOT_BYTES, export_snapshot, import_snapshot
from .tree import CommandEngine

SCHEMA_VERSION = 2


class RevisionConflict(TreeError):
    """Another engine committed first; reopen before issuing more commands."""


class SQLiteSnapshotStore:
    """Portable single-file reference adapter with optimistic transaction CAS.

    Each operation uses its own connection. SQLite serializes cooperating
    writers through BEGIN IMMEDIATE; no external locking service is needed.
    """

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self.path = os.fspath(path)
        if not isinstance(self.path, str) or not self.path or self.path == ":memory:":
            raise TreeError("SQLite store requires a persistent filesystem path")
        self._migrate()

    @contextmanager
    def _connection(self):
        con = sqlite3.connect(self.path, timeout=10.0, isolation_level=None)
        try:
            yield con
        finally:
            con.close()

    def _migrate(self) -> None:
        with self._connection() as con:
            con.execute("BEGIN IMMEDIATE")
            try:
                version = con.execute("PRAGMA user_version").fetchone()[0]
                if version not in (0, 1, 2):
                    raise TreeError("Unsupported future SQLite schema")
                if version == 0:
                    con.execute(
                        "CREATE TABLE snapshots ("
                        "id INTEGER PRIMARY KEY CHECK(id=1), payload BLOB NOT NULL)"
                    )
                    con.execute("PRAGMA user_version=1")
                    version = 1
                if version == 1:
                    # Validate historic content before changing the schema. On a
                    # failed import BEGIN IMMEDIATE rolls back *all* DDL and DML.
                    historic_rows = con.execute("SELECT id, payload FROM snapshots").fetchall()
                    for identity, payload in historic_rows:
                        if identity != 1 or type(payload) is not bytes:
                            raise TreeError("Invalid historic snapshot row")
                        import_snapshot(payload)
                    con.execute("ALTER TABLE snapshots ADD COLUMN revision INTEGER NOT NULL DEFAULT 0")
                    con.execute("ALTER TABLE snapshots ADD COLUMN digest TEXT NOT NULL DEFAULT ''")
                    for identity, payload in historic_rows:
                        con.execute("UPDATE snapshots SET digest=? WHERE id=?",
                                    (sha256(payload).hexdigest(), identity))
                    con.execute("PRAGMA user_version=2")
                con.commit()
            except BaseException:
                con.rollback()
                raise

    def read(self) -> tuple[bytes | None, int]:
        with self._connection() as con:
            row = con.execute("SELECT payload, revision, digest FROM snapshots WHERE id=1").fetchone()
        if row is None:
            return None, 0
        payload, revision, digest = row
        if (type(payload) is not bytes or type(revision) is not int or revision < 0
                or type(digest) is not str or
                not hmac.compare_digest(sha256(payload).hexdigest(), digest)):
            raise TreeError("Snapshot digest or revision invalid")
        return payload, revision

    def commit(self, payload: bytes, *, expected_revision: int) -> int:
        if type(expected_revision) is not int or expected_revision < 0:
            raise TreeError("Invalid expected snapshot revision")
        # Export/validation has already finished: DB transaction is short.
        with self._connection() as con:
            con.execute("BEGIN IMMEDIATE")
            try:
                row = con.execute(
                    "SELECT payload, revision, digest FROM snapshots WHERE id=1"
                ).fetchone()
                if row is not None:
                    stored_payload, actual, digest = row
                    if (type(stored_payload) is not bytes
                            or len(stored_payload) > MAX_SNAPSHOT_BYTES
                            or type(actual) is not int or actual < 0
                            or type(digest) is not str
                            or not hmac.compare_digest(sha256(stored_payload).hexdigest(), digest)):
                        raise TreeError("Existing snapshot is corrupt; refusing to overwrite")
                else:
                    actual = 0
                if actual != expected_revision:
                    raise RevisionConflict("Storage revision conflict; reopen from disk")
                new_revision = expected_revision + 1
                if row is None:
                    con.execute(
                        "INSERT INTO snapshots (id, payload, revision, digest) VALUES (1, ?, ?, ?)",
                        (payload, new_revision, sha256(payload).hexdigest()),
                    )
                else:
                    con.execute(
                        "UPDATE snapshots SET payload=?, revision=?, digest=? WHERE id=1",
                        (payload, new_revision, sha256(payload).hexdigest()),
                    )
                con.commit()
                return new_revision
            except BaseException:
                con.rollback()
                raise


class PersistentCommandEngine(CommandEngine):
    """Same validated domain commands; persistence happens before publication.

    Two separate engine instances detect cross-process stale writes via a
    database revision. Command *evaluation within one instance* is not yet a
    fully thread-safe API; callers must serialize operations per instance.
    """

    def __init__(self, path: str | os.PathLike[str]) -> None:
        super().__init__()
        self._store = SQLiteSnapshotStore(path)
        payload, revision = self._store.read()
        self._revision = revision
        if payload is not None:
            restored = import_snapshot(payload)
            for bucket in (
                "_projects", "_nodes", "_requirements", "_dependencies",
                "_architecture_decisions", "_decision_proposals", "_audit",
            ):
                setattr(self, bucket, getattr(restored, bucket))

    @property
    def storage_revision(self) -> int:
        return self._revision

    def _publish(self, bucket: str, proposed: dict, event: object) -> None:
        if bucket not in (
            "_projects", "_nodes", "_requirements", "_dependencies",
            "_architecture_decisions", "_decision_proposals",
        ):
            raise TreeError("Unknown storage publication bucket")
        candidate = CommandEngine()
        for name in (
            "_projects", "_nodes", "_requirements", "_dependencies",
            "_architecture_decisions", "_decision_proposals",
        ):
            setattr(candidate, name, proposed if name == bucket else getattr(self, name))
        candidate._audit = (*self._audit, event)
        payload = export_snapshot(candidate)  # Full graph validation before I/O.
        next_revision = self._store.commit(payload, expected_revision=self._revision)
        # No publication (including journal) was made if storage failed.
        super()._publish(bucket, proposed, event)
        self._revision = next_revision
