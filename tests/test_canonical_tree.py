"""T1.1 structural regressions using synthetic projects."""
import dataclasses
import unittest
from unittest.mock import patch

from architecture_roadmap_tracker import (
    CommandEngine, InvalidMove, NodeKind, NotFound, TreeError,
)


class CanonicalTreeTests(unittest.TestCase):
    def setUp(self):
        self.engine = CommandEngine()
        self.project = self.engine.create_project("Demo")

    def labels(self, parent=None):
        return [node.title for node in self.engine.children(self.project.id, parent)]

    def test_ids_are_stable_unique_and_typed(self):
        parent = self.engine.create_node(self.project.id, "M1", kind=NodeKind.MILESTONE)
        child = self.engine.create_node(
            self.project.id, "M1.1", parent_id=parent.id, kind=NodeKind.SUBMILESTONE
        )
        self.assertEqual(child.parent_id, parent.id)
        self.assertNotEqual(child.id, parent.id)
        self.assertEqual(child.kind, NodeKind.SUBMILESTONE)
        self.assertEqual(len(parent.id), 32)
        self.assertEqual(self.engine.node(self.project.id, parent.id).id, parent.id)

    def test_root_order_and_insert(self):
        self.engine.create_node(self.project.id, "A")
        self.engine.create_node(self.project.id, "C")
        self.engine.create_node(self.project.id, "B", position=1)
        self.assertEqual(self.labels(), ["A", "B", "C"])
        self.assertEqual(
            [n.position for n in self.engine.children(self.project.id)], [0, 1, 2]
        )

    def test_reorder_same_parent_uses_final_index(self):
        nodes = [self.engine.create_node(self.project.id, label) for label in "ABCD"]
        self.engine.move_node(self.project.id, nodes[1].id, new_parent_id=None, position=3)
        self.assertEqual(self.labels(), ["A", "C", "D", "B"])
        self.engine.move_node(self.project.id, nodes[1].id, new_parent_id=None, position=0)
        self.assertEqual(self.labels(), ["B", "A", "C", "D"])

    def test_move_parent_renumbers_both_groups(self):
        x = self.engine.create_node(self.project.id, "X")
        y = self.engine.create_node(self.project.id, "Y")
        a = self.engine.create_node(self.project.id, "a", parent_id=x.id)
        b = self.engine.create_node(self.project.id, "b", parent_id=x.id)
        c = self.engine.create_node(self.project.id, "c", parent_id=y.id)
        result = self.engine.move_node(self.project.id, b.id, new_parent_id=y.id, position=0)
        self.assertEqual(result.id, b.id)
        self.assertEqual(self.labels(x.id), ["a"])
        self.assertEqual(self.labels(y.id), ["b", "c"])
        self.assertEqual(self.engine.node(self.project.id, a.id).position, 0)
        self.assertEqual(self.engine.node(self.project.id, c.id).position, 1)

    def test_reparent_preserves_subtree(self):
        a = self.engine.create_node(self.project.id, "A")
        b = self.engine.create_node(self.project.id, "B")
        child = self.engine.create_node(self.project.id, "Child", parent_id=a.id)
        grand = self.engine.create_node(self.project.id, "Grand", parent_id=child.id)
        before = {n.id for n in self.engine.walk(self.project.id)}
        self.engine.move_node(self.project.id, child.id, new_parent_id=b.id)
        self.assertEqual({n.id for n in self.engine.walk(self.project.id)}, before)
        self.assertEqual(self.engine.node(self.project.id, grand.id).parent_id, child.id)
        self.assertEqual(self.labels(b.id), ["Child"])

    def test_self_and_descendant_cycles_fail_atomically(self):
        top = self.engine.create_node(self.project.id, "Top")
        mid = self.engine.create_node(self.project.id, "Mid", parent_id=top.id)
        leaf = self.engine.create_node(self.project.id, "Leaf", parent_id=mid.id)
        before = tuple(self.engine.walk(self.project.id))
        for target in (top.id, mid.id, leaf.id):
            with self.assertRaises(InvalidMove):
                self.engine.move_node(self.project.id, top.id, new_parent_id=target)
            self.assertEqual(tuple(self.engine.walk(self.project.id)), before)

    def test_project_isolation_and_foreign_parents(self):
        other = self.engine.create_project("Other")
        x = self.engine.create_node(self.project.id, "X")
        y = self.engine.create_node(other.id, "Y")
        before = tuple(self.engine.walk(self.project.id))
        with self.assertRaises(NotFound):
            self.engine.node(other.id, x.id)
        with self.assertRaises(NotFound):
            self.engine.create_node(other.id, "Invalid", parent_id=x.id)
        with self.assertRaises(NotFound):
            self.engine.move_node(self.project.id, x.id, new_parent_id=y.id)
        self.assertEqual(tuple(self.engine.walk(self.project.id)), before)
        self.assertEqual([n.title for n in self.engine.children(other.id)], ["Y"])

    def test_invalid_positions_and_types_leave_tree_intact(self):
        self.engine.create_node(self.project.id, "A")
        before = tuple(self.engine.walk(self.project.id))
        for position in (-1, 2, True, 1.5, "0"):
            with self.assertRaises(TreeError):
                self.engine.create_node(self.project.id, "Bad", position=position)
            self.assertEqual(tuple(self.engine.walk(self.project.id)), before)
        with self.assertRaises(TreeError):
            self.engine.create_node(self.project.id, " ")
        with self.assertRaises(TreeError):
            self.engine.create_node(self.project.id, "Bad", kind="task")
        self.assertEqual(tuple(self.engine.walk(self.project.id)), before)

    def test_bad_same_parent_move_does_not_change_order(self):
        nodes = [self.engine.create_node(self.project.id, name) for name in "ABC"]
        before = tuple(self.engine.walk(self.project.id))
        with self.assertRaises(TreeError):
            self.engine.move_node(self.project.id, nodes[0].id,
                                  new_parent_id=None, position=3)
        self.assertEqual(tuple(self.engine.walk(self.project.id)), before)

    def test_archive_parent_and_restore_preserves_child_archive(self):
        parent = self.engine.create_node(self.project.id, "Parent")
        child = self.engine.create_node(self.project.id, "Child", parent_id=parent.id)
        grandchild = self.engine.create_node(self.project.id, "Grand", parent_id=child.id)
        self.engine.archive_node(self.project.id, child.id)
        self.engine.archive_node(self.project.id, parent.id)
        self.assertTrue(self.engine.effectively_archived(self.project.id, grandchild.id))
        with self.assertRaises(TreeError):
            self.engine.restore_node(self.project.id, child.id)
        with self.assertRaises(InvalidMove):
            self.engine.create_node(self.project.id, "New", parent_id=parent.id)
        self.engine.restore_node(self.project.id, parent.id)
        self.assertTrue(self.engine.effectively_archived(self.project.id, grandchild.id))
        self.engine.restore_node(self.project.id, child.id)
        self.assertFalse(self.engine.effectively_archived(self.project.id, grandchild.id))

    def test_archived_node_edits_are_rejected(self):
        a = self.engine.create_node(self.project.id, "A")
        b = self.engine.create_node(self.project.id, "B")
        self.engine.archive_node(self.project.id, a.id)
        with self.assertRaises(TreeError):
            self.engine.rename_node(self.project.id, a.id, "Changed")
        with self.assertRaises(InvalidMove):
            self.engine.move_node(self.project.id, a.id, new_parent_id=b.id)
        self.assertEqual(self.labels(), ["A", "B"])

    def test_frozen_snapshots_are_not_externally_editable(self):
        node = self.engine.create_node(self.project.id, "Safe")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            node.parent_id = "fake"
        with self.assertRaises(dataclasses.FrozenInstanceError):
            self.project.name = "Unexpected"
        self.assertIsInstance(self.engine.children(self.project.id), tuple)

    def test_criteria_are_immutable_strings(self):
        item = self.engine.create_node(
            self.project.id, "Gate", description="Text",
            acceptance_criteria=("  Pass regression  ",)
        )
        self.assertEqual(item.acceptance_criteria, ("Pass regression",))
        with self.assertRaises(TreeError):
            self.engine.create_node(self.project.id, "Bad", acceptance_criteria=["Mutable"])

    def test_multiple_projects_have_independent_order(self):
        other = self.engine.create_project("Other")
        self.engine.create_node(self.project.id, "First")
        self.engine.create_node(other.id, "Another")
        self.engine.create_node(self.project.id, "Second")
        self.assertEqual(self.labels(), ["First", "Second"])
        self.assertEqual([n.position for n in self.engine.children(other.id)], [0])

    def test_1500_levels_have_no_recursion_limit(self):
        node = self.engine.create_node(self.project.id, "root")
        root_id = node.id
        for index in range(1500):
            node = self.engine.create_node(self.project.id, f"child-{index}", parent_id=node.id)
        walked = tuple(self.engine.walk(self.project.id, root_id))
        self.assertEqual(len(walked), 1501)
        self.assertEqual(walked[-1].id, node.id)
        with self.assertRaises(InvalidMove):
            self.engine.move_node(self.project.id, root_id, new_parent_id=node.id)

    def test_300_sibling_positions_remain_contiguous(self):
        for i in range(300):
            self.engine.create_node(self.project.id, f"Item-{i}")
        before = self.engine.children(self.project.id)
        self.engine.move_node(self.project.id, before[0].id, new_parent_id=None, position=299)
        after = self.engine.children(self.project.id)
        self.assertEqual(after[-1].id, before[0].id)
        self.assertEqual([n.position for n in after], list(range(300)))

    def test_started_iterator_is_snapshot_consistent_after_move(self):
        root = self.engine.create_node(self.project.id, "Root")
        a = self.engine.create_node(self.project.id, "A", parent_id=root.id)
        b = self.engine.create_node(self.project.id, "B", parent_id=root.id)
        iterator = self.engine.walk(self.project.id)
        self.assertEqual(next(iterator).id, root.id)
        self.engine.move_node(self.project.id, a.id, new_parent_id=None)
        remaining = list(iterator)
        self.assertEqual([n.id for n in remaining], [a.id, b.id])
        self.assertEqual([n.id for n in self.engine.walk(self.project.id)],
                         [root.id, b.id, a.id])

    def test_missing_project_or_node_raises_not_found(self):
        with self.assertRaises(NotFound):
            self.engine.node(self.project.id, "missing")
        with self.assertRaises(NotFound):
            self.engine.children(self.project.id, "missing")
        with self.assertRaises(NotFound):
            tuple(self.engine.walk("missing"))

    def test_uuid_collision_does_not_overwrite(self):
        with patch("architecture_roadmap_tracker.tree.uuid4") as fake:
            fake.side_effect = [
                type("U", (), {"hex": "a" * 32})(),
                type("U", (), {"hex": "a" * 32})(),
                type("U", (), {"hex": "b" * 32})(),
            ]
            first = self.engine.create_node(self.project.id, "A")
            second = self.engine.create_node(self.project.id, "B")
        self.assertEqual(first.id, "a" * 32)
        self.assertEqual(second.id, "b" * 32)
        self.assertEqual(self.labels(), ["A", "B"])

    def test_normalized_duplicate_criteria_fail_atomically(self):
        before = tuple(self.engine.walk(self.project.id))
        with self.assertRaises(TreeError):
            self.engine.create_node(
                self.project.id, "Invalid",
                acceptance_criteria=("Check builds", "  Check builds  "),
            )
        self.assertEqual(tuple(self.engine.walk(self.project.id)), before)

    def test_repository_binding_rejects_unsafe_values_atomically(self):
        before = self.engine.projects()
        unsafe = (
            "org/repo\\nforged",
            "org/repo\\x7f",
            "https://user:secret@github.com/org/repo",
            "https://github.com/org/repo?access_token=secret",
        )
        for binding in unsafe:
            with self.subTest(binding=binding):
                with self.assertRaises(TreeError):
                    self.engine.create_project("Rejected", (binding,))
                self.assertEqual(self.engine.projects(), before)
        valid = self.engine.create_project(
            "Safe", ("  https://github.com/org/repo  ", "git@github.com:org/other")
        )
        self.assertEqual(
            valid.repositories,
            ("https://github.com/org/repo", "git@github.com:org/other"),
        )

    def test_project_rename_preserves_id_and_bindings(self):
        project = self.engine.create_project(" New ", ("company/repo",))
        renamed = self.engine.rename_project(project.id, "Revised")
        self.assertEqual(renamed.id, project.id)
        self.assertEqual(renamed.name, "Revised")
        self.assertEqual(renamed.repositories, ("company/repo",))
        with self.assertRaises(TreeError):
            self.engine.create_project("Bad", ("duplicate", "duplicate"))


if __name__ == "__main__":
    unittest.main()
