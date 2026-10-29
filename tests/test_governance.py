"""T1.2 requirement/dependency/decision/audit regressions; synthetic only."""
import dataclasses
from datetime import timezone
import unittest

from architecture_roadmap_tracker import (
    CommandEngine, DependencyKind, NotFound, ProposalState, TreeError,
)


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.e = CommandEngine()
        self.p = self.e.create_project("Primary", actor="synthetic:tester")
        self.a = self.e.create_node(self.p.id, "A", actor="synthetic:tester")
        self.b = self.e.create_node(self.p.id, "B", actor="synthetic:tester")
        self.c = self.e.create_node(self.p.id, "C", actor="synthetic:tester")

    def make_requirement(self, code="REQ-01"):
        return self.e.create_requirement(
            self.p.id, code, "Automated validation",
            ("Regression check passes",), node_ids=(self.a.id,),
            actor="synthetic:tester",
        )

    def test_requirement_codes_are_scoped_and_ids_remain_stable(self):
        item = self.make_requirement()
        other = self.e.create_project("Other")
        foreign = self.e.create_requirement(
            other.id, item.code, "Independent obligation", ("Evidence",),
            actor="synthetic:tester",
        )
        self.assertNotEqual(item.id, foreign.id)
        self.assertEqual(self.e.requirements(self.p.id, self.a.id), (item,))
        self.assertEqual(self.e.requirements(self.p.id, self.b.id), ())
        with self.assertRaises(NotFound):
            self.e.requirement(other.id, item.id)
        with self.assertRaises(TreeError):
            self.make_requirement()
        self.assertEqual(self.e.requirement(self.p.id, item.id), item)

    def test_requirement_revisions_monotonic_and_optimistic(self):
        item = self.make_requirement()
        changed = self.e.revise_requirement(
            self.p.id, item.id, expected_version=1,
            criteria=("New evidence required",), actor="synthetic:tester",
            rationale="Acceptance scope changed",
        )
        self.assertEqual(changed.id, item.id)
        self.assertEqual(changed.version, 2)
        self.assertEqual(item.criteria, ("Regression check passes",))
        audit_before = self.e.audit_log(self.p.id)
        with self.assertRaises(TreeError):
            self.e.revise_requirement(
                self.p.id, item.id, expected_version=1,
                title="Stale writer", actor="synthetic:tester", rationale="Stale",
            )
        self.assertEqual(self.e.audit_log(self.p.id), audit_before)
        unchanged = self.e.revise_requirement(
            self.p.id, item.id, expected_version=2,
            actor="synthetic:tester", rationale="No changes",
        )
        self.assertEqual(unchanged.version, 2)
        self.assertEqual(self.e.audit_log(self.p.id), audit_before)

    def test_requirement_criteria_and_links_reject_duplicates_atomically(self):
        log = self.e.audit_log(self.p.id)
        for criteria in ((), ("OK", "  OK  "), ["Not a tuple"]):
            with self.assertRaises(TreeError):
                self.e.create_requirement(
                    self.p.id, "REQ-FAIL", "Invalid", criteria,
                    actor="synthetic:tester",
                )
        with self.assertRaises(TreeError):
            self.e.create_requirement(
                self.p.id, "REQ-FAIL", "Invalid", ("OK",),
                node_ids=(self.a.id, self.a.id), actor="synthetic:tester",
            )
        self.assertEqual(self.e.audit_log(self.p.id), log)
        self.assertEqual(self.e.requirements(self.p.id), ())

    def test_node_links_are_derived_without_duplicate_authority(self):
        item = self.make_requirement()
        linked = self.e.link_requirement_node(
            self.p.id, item.id, self.b.id, actor="synthetic:tester",
        )
        self.assertEqual(linked.version, 2)
        self.assertEqual(linked.node_ids, (self.a.id, self.b.id))
        log = self.e.audit_log(self.p.id)
        self.e.link_requirement_node(
            self.p.id, item.id, self.b.id, actor="synthetic:tester",
        )
        self.assertEqual(self.e.audit_log(self.p.id), log)
        unlinked = self.e.unlink_requirement_node(
            self.p.id, item.id, self.a.id, actor="synthetic:tester",
        )
        self.assertEqual(unlinked.node_ids, (self.b.id,))
        self.assertEqual(self.e.requirements(self.p.id, self.a.id), ())
        self.assertEqual(self.e.requirements(self.p.id, self.b.id), (unlinked,))
        self.e.archive_node(self.p.id, self.c.id)
        with self.assertRaises(TreeError):
            self.e.link_requirement_node(
                self.p.id, item.id, self.c.id, actor="synthetic:tester",
            )

    def test_cross_project_requirement_link_is_denied(self):
        item = self.make_requirement()
        p2 = self.e.create_project("Secondary")
        alien = self.e.create_node(p2.id, "Foreign")
        before = self.e.audit_log(self.p.id)
        with self.assertRaises(NotFound):
            self.e.link_requirement_node(
                self.p.id, item.id, alien.id, actor="synthetic:tester",
            )
        self.assertEqual(self.e.audit_log(self.p.id), before)

    def test_blocking_dependency_cycle_is_rejected_atomically(self):
        first = self.e.add_dependency(
            self.p.id, self.a.id, self.b.id, actor="synthetic:tester",
        )
        self.e.add_dependency(self.p.id, self.b.id, self.c.id, actor="synthetic:tester")
        audit = self.e.audit_log(self.p.id)
        with self.assertRaises(TreeError):
            self.e.add_dependency(
                self.p.id, self.c.id, self.a.id, actor="synthetic:tester",
            )
        self.assertEqual(self.e.audit_log(self.p.id), audit)
        self.assertEqual(len(self.e.dependencies(self.p.id)), 2)
        with self.assertRaises(TreeError):
            self.e.add_dependency(
                self.p.id, self.a.id, self.b.id, actor="synthetic:tester",
            )
        self.assertEqual(self.e.dependency(self.p.id, first.id).kind, DependencyKind.BLOCKS)
        self.e.add_dependency(
            self.p.id, self.c.id, self.a.id,
            kind=DependencyKind.RELATES_TO, actor="synthetic:tester",
        )

    def test_explicit_cross_project_edges_and_global_cycle_rejection(self):
        foreign_project = self.e.create_project("Secondary")
        foreign = self.e.create_node(foreign_project.id, "Foreign")
        with self.assertRaises(TreeError):
            self.e.add_dependency(
                self.p.id, self.a.id, foreign.id,
                target_project_id=foreign_project.id, actor="synthetic:tester",
            )
        self.e.add_dependency(
            self.p.id, self.a.id, foreign.id, target_project_id=foreign_project.id,
            allow_cross_project=True, actor="synthetic:tester",
        )
        prior = self.e.audit_log(foreign_project.id)
        with self.assertRaises(TreeError):
            self.e.add_dependency(
                foreign_project.id, foreign.id, self.a.id, target_project_id=self.p.id,
                allow_cross_project=True, actor="synthetic:tester",
            )
        self.assertEqual(self.e.audit_log(foreign_project.id), prior)
        self.assertEqual(self.e.dependencies(foreign_project.id), ())
        with self.assertRaises(NotFound):
            self.e.dependency(foreign_project.id, self.e.dependencies(self.p.id)[0].id)

    def test_large_dependency_chain_is_iterative(self):
        # Chain is deliberately larger than Python's recursion limit.
        nodes = [self.a.id, self.b.id]
        # Structural insertion is O(N^2) in this reference core; 60 nodes is
        # sufficient here while the deep-tree test already checks 1,500 levels.
        for i in range(60):
            nodes.append(self.e.create_node(self.p.id, f"Dependency {i}").id)
        for a, b in zip(nodes, nodes[1:]):
            self.e.add_dependency(self.p.id, a, b, actor="synthetic:tester")
        with self.assertRaises(TreeError):
            self.e.add_dependency(self.p.id, nodes[-1], nodes[0],
                                  actor="synthetic:tester")

    def test_deactivate_preserves_history_and_allows_new_edge(self):
        edge = self.e.add_dependency(self.p.id, self.a.id, self.b.id,
                                     actor="synthetic:tester")
        disabled = self.e.deactivate_dependency(
            self.p.id, edge.id, actor="synthetic:tester", rationale="Replanned",
        )
        self.assertFalse(disabled.active)
        self.assertEqual(self.e.dependencies(self.p.id, include_inactive=False), ())
        events = self.e.audit_log(self.p.id)
        self.e.deactivate_dependency(self.p.id, edge.id, actor="synthetic:tester",
                                     rationale="No-op")
        self.assertEqual(self.e.audit_log(self.p.id), events)
        later = self.e.add_dependency(self.p.id, self.a.id, self.b.id,
                                      actor="synthetic:tester")
        self.assertNotEqual(later.id, edge.id)
        self.assertFalse(self.e.dependency(self.p.id, edge.id).active)
        with self.assertRaises(TreeError):
            self.e.deactivate_dependency(self.p.id, later.id,
                                          actor="synthetic:tester", rationale="")

    def test_archived_nodes_do_not_accept_new_dependency(self):
        self.e.archive_node(self.p.id, self.a.id)
        count = len(self.e.audit_log(self.p.id))
        with self.assertRaises(TreeError):
            self.e.add_dependency(self.p.id, self.b.id, self.a.id,
                                  actor="synthetic:tester")
        self.assertEqual(len(self.e.audit_log(self.p.id)), count)

    def test_adr_proposal_is_not_approval_and_links_are_scoped(self):
        proposal = self.e.propose_architecture_decision(
            self.p.id, "ADR-0009", "Typed relationships", "Needs independent review",
            actor="synthetic:author",
        )
        self.assertEqual(proposal.state, ProposalState.PROPOSED)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            proposal.state = "approved"
        requirement = self.make_requirement()
        linked = self.e.link_requirement_decision(
            self.p.id, requirement.id, proposal.id, actor="synthetic:tester",
        )
        self.assertEqual(linked.decision_ids, (proposal.id,))
        with self.assertRaises(TreeError):
            self.e.propose_architecture_decision(
                self.p.id, "ADR-0009", "Duplicate", "Same ID", actor="synthetic:author",
            )
        next_proposal = self.e.propose_architecture_decision(
            self.p.id, "ADR-0010", "Alternative", "Supersession is proposed only",
            actor="synthetic:author", supersedes_id=proposal.id,
        )
        self.assertEqual(next_proposal.supersedes_id, proposal.id)
        self.assertEqual(self.e.architecture_decision(self.p.id, proposal.id), proposal)
        another = self.e.create_project("Other")
        with self.assertRaises(NotFound):
            self.e.architecture_decision(another.id, proposal.id)

    def test_decision_records_are_only_proposals(self):
        decision = self.e.propose_decision(
            self.p.id, "Reconsider milestone scope", "Requires explicit owner authorization",
            actor="synthetic:author", node_id=self.a.id,
            previous_value="draft", proposed_value="revised",
        )
        self.assertEqual(decision.state, ProposalState.PROPOSED)
        self.assertEqual(self.e.decision_proposals(self.p.id), (decision,))
        self.assertEqual(self.e.node(self.p.id, self.a.id).title, "A")
        other = self.e.create_project("Other")
        with self.assertRaises(NotFound):
            self.e.propose_decision(
                other.id, "Invalid", "Foreign node", actor="synthetic:author",
                node_id=self.a.id, proposed_value="X",
            )

    def test_journal_tracks_every_structural_mutation_with_before_after(self):
        self.assertEqual([x.action for x in self.e.audit_log(self.p.id)],
                         ["project.create", "node.create", "node.create", "node.create"])
        prior = self.e.audit_log(self.p.id)
        self.e.move_node(self.p.id, self.a.id, new_parent_id=self.b.id,
                         actor="synthetic:editor", rationale="Reorganize")
        event = self.e.audit_log(self.p.id)[-1]
        self.assertEqual(event.action, "node.move")
        self.assertEqual(event.actor, "synthetic:editor")
        self.assertEqual(event.rationale, "Reorganize")
        self.assertTrue(event.before)
        self.assertTrue(event.after)
        self.assertEqual(event.occurred_at.tzinfo, timezone.utc)
        self.assertEqual(len(self.e.audit_log(self.p.id)), len(prior) + 1)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            event.actor = "synthetic:forged"
        with self.assertRaises(AttributeError):
            prior.append(event)
        self.e.rename_node(self.p.id, self.a.id, "Renamed")
        self.e.archive_node(self.p.id, self.b.id)
        self.e.restore_node(self.p.id, self.b.id)
        self.e.rename_project(self.p.id, "Renamed project")
        self.assertEqual(
            [x.sequence for x in self.e.audit_log(self.p.id)],
            list(range(1, len(self.e.audit_log(self.p.id)) + 1)),
        )
        self.assertIsNone(self.e.audit_log(self.p.id)[-4].actor)

    def test_invalid_structural_command_leaves_journal_unchanged(self):
        before = self.e.audit_log(self.p.id)
        with self.assertRaises(TreeError):
            self.e.move_node(
                self.p.id, self.a.id, new_parent_id=self.b.id, position=200,
                actor="synthetic:editor",
            )
        self.assertEqual(self.e.audit_log(self.p.id), before)
        self.assertEqual(self.e.node(self.p.id, self.a.id).parent_id, None)

    def test_audit_is_project_scoped_and_records_actor_limits(self):
        q = self.e.create_project("Other")
        self.e.create_requirement(
            q.id, "REQ-01", "Scope", ("Criteria",), actor="synthetic:tester",
        )
        self.assertEqual([x.project_id for x in self.e.audit_log(self.p.id)],
                         [self.p.id] * 4)
        self.assertEqual(len(self.e.audit_log(q.id)), 2)
        self.assertIsNone(self.e.audit_log(self.p.id)[0].before)
        with self.assertRaises(NotFound):
            self.e.audit_log("not-a-project")
        before = self.e.audit_log(self.p.id)
        with self.assertRaises(TreeError):
            self.e.create_requirement(
                self.p.id, "REQ-NEW", "Title", ("Criteria",), actor="",
            )
        self.assertEqual(self.e.audit_log(self.p.id), before)


if __name__ == "__main__":
    unittest.main()
