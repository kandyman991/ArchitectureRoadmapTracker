"""T1.3 synthetic deterministic projections, snapshot, migration and failure tests."""
from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path
import unittest

from architecture_roadmap_tracker import CommandEngine, DependencyKind, TreeError
from architecture_roadmap_tracker.projections import project_outline
from architecture_roadmap_tracker.snapshots import export_snapshot, import_snapshot
from architecture_roadmap_tracker.storage import (
    PersistentCommandEngine, RevisionConflict, SCHEMA_VERSION,
)


class SnapshotTests(unittest.TestCase):
    def make_engine(self):
        e = CommandEngine()
        p = e.create_project("Primary", actor="synthetic:tester")
        q = e.create_project("Secondary", actor="synthetic:tester")
        parent = e.create_node(p.id, "Parent", actor="synthetic:tester")
        child = e.create_node(p.id, "Child", parent_id=parent.id, actor="synthetic:tester")
        sibling = e.create_node(p.id, "Sibling", actor="synthetic:tester")
        foreign = e.create_node(q.id, "Foreign", actor="synthetic:tester")
        requirement = e.create_requirement(
            p.id, "REQ-01", "Verification", ("Synthetic evidence",),
            node_ids=(parent.id, child.id), actor="synthetic:tester",
        )
        adr = e.propose_architecture_decision(
            p.id, "ADR-0099", "Proposed only", "Not approved",
            actor="synthetic:tester",
        )
        e.link_requirement_decision(
            p.id, requirement.id, adr.id, expected_version=1,
            actor="synthetic:tester",
        )
        e.propose_decision(
            p.id, "Consider", "Review required", node_id=child.id,
            proposed_value="Not approved", actor="synthetic:tester",
        )
        e.add_dependency(p.id, parent.id, sibling.id, actor="synthetic:tester")
        e.add_dependency(
            p.id, sibling.id, foreign.id, target_project_id=q.id,
            allow_cross_project=True, kind=DependencyKind.RELATES_TO,
            actor="synthetic:tester",
        )
        return e, p, q, parent, child, sibling, requirement

    def test_projection_is_deterministic_and_read_only(self):
        e, p, _, parent, child, sibling, requirement = self.make_engine()
        before = export_snapshot(e)
        outline = project_outline(e, p.id)
        self.assertEqual([row.node.title for row in outline], ["Parent", "Child", "Sibling"])
        self.assertEqual([row.depth for row in outline], [0, 1, 0])
        self.assertEqual(outline[0].requirement_ids, (requirement.id,))
        self.assertEqual(outline[1].requirement_ids, (requirement.id,))
        self.assertEqual(len(outline[0].dependency_ids), 1)
        self.assertEqual(len(outline[2].dependency_ids), 1)
        self.assertEqual(project_outline(e, p.id), outline)
        self.assertEqual(export_snapshot(e), before)
        e.move_node(p.id, sibling.id, new_parent_id=parent.id, position=0)
        self.assertEqual([row.node.title for row in project_outline(e, p.id)],
                         ["Parent", "Sibling", "Child"])
        self.assertEqual([row.depth for row in project_outline(e, p.id)], [0, 1, 1])

    def test_deterministic_roundtrip_including_audit_and_relationships(self):
        e, p, q, parent, child, sibling, requirement = self.make_engine()
        raw = export_snapshot(e)
        recovered = import_snapshot(raw)
        self.assertEqual(export_snapshot(recovered), raw)
        self.assertEqual(project_outline(recovered, p.id), project_outline(e, p.id))
        self.assertEqual(recovered.requirement(p.id, requirement.id).version, 2)
        self.assertEqual(recovered.dependencies(q.id), ())
        self.assertEqual(recovered.audit_log(p.id), e.audit_log(p.id))
        self.assertEqual(recovered.audit_log(q.id), e.audit_log(q.id))
        # Returned snapshots are immutable and modifying restored state uses commands.
        recovered.rename_node(p.id, child.id, "Changed", actor="synthetic:tester")
        self.assertEqual(e.node(p.id, child.id).title, "Child")
        self.assertNotEqual(export_snapshot(recovered), raw)

    def test_untrusted_snapshot_rejects_graph_corruption_and_duplicate_keys(self):
        e, p, q, parent, child, sibling, requirement = self.make_engine()
        original = export_snapshot(e)
        base = json.loads(original)
        cases = []
        corrupt = json.loads(original)
        corrupt["nodes"][0]["fields"]["project_id"] = "f" * 32
        cases.append(corrupt)
        corrupt = json.loads(original)
        corrupt["nodes"].append(corrupt["nodes"][0])
        cases.append(corrupt)
        corrupt = json.loads(original)
        corrupt["requirements"][0]["fields"]["version"] = True
        cases.append(corrupt)
        corrupt = json.loads(original)
        corrupt["audit"][0]["fields"]["sequence"] = 17
        cases.append(corrupt)
        corrupt = json.loads(original)
        corrupt["architecture_decisions"][0]["fields"]["state"]["value"] = "approved"
        cases.append(corrupt)
        corrupt = json.loads(original)
        corrupt["nodes"][0]["fields"]["kind"] = {"$enum": "UnexpectedKind", "value": "task"}
        cases.append(corrupt)
        corrupt = json.loads(original)
        corrupt["dependencies"][0]["fields"]["source_node_id"] = (
            corrupt["dependencies"][0]["fields"]["target_node_id"]
        )
        cases.append(corrupt)
        for case in cases:
            with self.subTest(kind=case.keys()):
                with self.assertRaises(TreeError):
                    import_snapshot(json.dumps(case).encode("utf-8"))
        for data in (
            b"{}",
            b'{"format_version":1,"format_version":1}',
            b'{"format_version":999}',
            b"\xff",
            b"[]" ,
        ):
            with self.assertRaises(TreeError):
                import_snapshot(data)
        self.assertEqual(export_snapshot(e), original)

    def test_deep_tree_roundtrip_without_recursive_hierarchy_serialization(self):
        e = CommandEngine()
        p = e.create_project("Deep")
        last = None
        for index in range(125):
            last = e.create_node(p.id, f"Level {index}", parent_id=last).id
        restored = import_snapshot(export_snapshot(e))
        self.assertEqual(len(project_outline(restored, p.id)), 125)
        self.assertEqual(project_outline(restored, p.id)[-1].depth, 124)


class SQLitePersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "synthetic.db"

    def test_restart_and_audit_continuity(self):
        e = PersistentCommandEngine(self.path)
        p = e.create_project("Saved", actor="synthetic:tester")
        parent = e.create_node(p.id, "Parent", actor="synthetic:tester")
        child = e.create_node(p.id, "Child", parent_id=parent.id, actor="synthetic:tester")
        e.create_requirement(p.id, "REQ-01", "Acceptance", ("Pass",),
                             node_ids=(child.id,), actor="synthetic:tester")
        old_audit = e.audit_log(p.id)
        old_revision = e.storage_revision
        recovered = PersistentCommandEngine(self.path)
        self.assertEqual(recovered.storage_revision, old_revision)
        self.assertEqual(recovered.audit_log(p.id), old_audit)
        self.assertEqual([row.depth for row in project_outline(recovered, p.id)], [0, 1])
        recovered.rename_node(p.id, child.id, "After restart", actor="synthetic:tester")
        third = PersistentCommandEngine(self.path)
        self.assertEqual(third.node(p.id, child.id).title, "After restart")
        self.assertEqual([x.sequence for x in third.audit_log(p.id)],
                         list(range(1, len(third.audit_log(p.id)) + 1)))

    def test_two_writers_have_optimistic_conflict_and_no_phantom_event(self):
        first = PersistentCommandEngine(self.path)
        stale = PersistentCommandEngine(self.path)
        first.create_project("Winner", actor="synthetic:tester")
        prior = stale._audit
        with self.assertRaises(RevisionConflict):
            stale.create_project("Stale", actor="synthetic:tester")
        self.assertEqual(stale._audit, prior)
        self.assertEqual(stale.projects(), ())
        self.assertEqual(len(PersistentCommandEngine(self.path).projects()), 1)

    def test_failed_sql_commit_does_not_publish_data_or_audit(self):
        e = PersistentCommandEngine(self.path)
        project = e.create_project("Original", actor="synthetic:tester")
        before = e.audit_log(project.id)
        revision = e.storage_revision
        with sqlite3.connect(self.path) as con:
            con.execute(
                "CREATE TRIGGER reject_update BEFORE UPDATE ON snapshots "
                "BEGIN SELECT RAISE(ABORT, 'synthetic write failure'); END"
            )
        with self.assertRaises(sqlite3.DatabaseError):
            e.rename_project(project.id, "Not persisted", actor="synthetic:tester")
        self.assertEqual(e.project(project.id).name, "Original")
        self.assertEqual(e.audit_log(project.id), before)
        self.assertEqual(e.storage_revision, revision)
        self.assertEqual(PersistentCommandEngine(self.path).project(project.id).name, "Original")

    def test_detects_corruption_and_rejects_unknown_schema_without_replay(self):
        e = PersistentCommandEngine(self.path)
        e.create_project("Untampered", actor="synthetic:tester")
        with sqlite3.connect(self.path) as con:
            con.execute("UPDATE snapshots SET payload=?", (b"corrupted",))
        with self.assertRaises(TreeError):
            PersistentCommandEngine(self.path)
        with sqlite3.connect(self.path) as con:
            con.execute("PRAGMA user_version=123")
        with self.assertRaises(TreeError):
            PersistentCommandEngine(self.path)

    def test_v1_to_v2_migration_preserves_snapshot(self):
        engine = CommandEngine()
        project = engine.create_project("Historical", actor="synthetic:tester")
        engine.create_node(project.id, "Before migration", actor="synthetic:tester")
        old_payload = export_snapshot(engine)
        with sqlite3.connect(self.path) as con:
            con.execute(
                "CREATE TABLE snapshots (id INTEGER PRIMARY KEY CHECK(id=1), "
                "payload BLOB NOT NULL)"
            )
            con.execute("INSERT INTO snapshots (id, payload) VALUES (1, ?)", (old_payload,))
            con.execute("PRAGMA user_version=1")
        migrated = PersistentCommandEngine(self.path)
        self.assertEqual(migrated.storage_revision, 0)
        self.assertEqual(export_snapshot(migrated), old_payload)
        with sqlite3.connect(self.path) as con:
            self.assertEqual(con.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
        migrated.rename_project(project.id, "After migration", actor="synthetic:tester")
        self.assertEqual(PersistentCommandEngine(self.path).project(project.id).name,
                         "After migration")

    def test_new_database_is_migrated_to_v2(self):
        e = PersistentCommandEngine(self.path)
        self.assertEqual(e.projects(), ())
        with sqlite3.connect(self.path) as con:
            self.assertEqual(con.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)


if __name__ == "__main__":
    unittest.main()
