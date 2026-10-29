"""In-memory canonical roadmap tree (T1.1).

No persistence, permissions, GitHub, runner, acceptance engine or UI yet.
Mutations publish only after all structural invariants pass.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Iterator
from .errors import InvalidMove, NotFound, TreeError
from .governance import AuditEntry, GovernanceCommands, _text
from urllib.parse import urlsplit
from uuid import uuid4


class NodeKind(str, Enum):
    MILESTONE = "milestone"
    SUBMILESTONE = "submilestone"
    TASK = "task"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Project:
    id: str
    name: str
    repositories: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RoadmapNode:
    id: str
    project_id: str
    parent_id: str | None
    position: int
    title: str
    kind: NodeKind = NodeKind.TASK
    description: str = ""
    acceptance_criteria: tuple[str, ...] = ()
    archived: bool = False


def _title(value: str) -> str:
    if not isinstance(value, str):
        raise TreeError("Title must be a string")
    value = value.strip()
    if not value or len(value) > 300 or "\x00" in value:
        raise TreeError("Title must contain 1 to 300 non-null characters")
    return value


def _repository_binding(value: str) -> str:
    """Keep opaque bindings free of controls and credential-bearing URLs.

    This is input hygiene, not identity verification or permission enforcement.
    The future GitHub adapter must independently validate authorization.
    """
    if not isinstance(value, str):
        raise TreeError("Repository binding must be a string")
    normalized = value.strip()
    if not normalized or any(ord(char) < 32 or ord(char) == 127 for char in normalized):
        raise TreeError("Repository binding contains invalid characters")
    if "://" in normalized:
        try:
            parsed = urlsplit(normalized)
        except ValueError:
            raise TreeError("Invalid repository URL") from None
        if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
            raise TreeError("Repository URLs must not contain credentials or query/fragment data")
    return normalized


def _position(position: int | None, count: int) -> int:
    if position is None:
        return count
    if isinstance(position, bool) or not isinstance(position, int) or not 0 <= position <= count:
        raise TreeError(f"Position must be an integer between 0 and {count}")
    return position


class CommandEngine(GovernanceCommands):
    """Only in-memory mutation surface for canonical projects/nodes.

    Frozen models prevent accidental mutation outside commands. Moves operate
    on private copies and run invariant checks before publication. Sibling
    positions and parent IDs are canonical; UI views must derive from them.
    """

    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}
        self._nodes: dict[str, RoadmapNode] = {}
        self._requirements = {}
        self._dependencies = {}
        self._architecture_decisions = {}
        self._decision_proposals = {}
        self._audit: tuple[AuditEntry, ...] = ()

    def _allocate_id(self) -> str:
        for _ in range(10):
            candidate = uuid4().hex
            if all(candidate not in records for records in (
                self._projects, self._nodes, self._requirements,
                self._dependencies, self._architecture_decisions,
                self._decision_proposals,
            )):
                return candidate
        raise TreeError("Unable to allocate unique identity")

    def project(self, project_id: str) -> Project:
        try:
            return self._projects[project_id]
        except (KeyError, TypeError):
            raise NotFound("Project not found") from None

    def projects(self) -> tuple[Project, ...]:
        return tuple(self._projects.values())

    def create_project(
        self, name: str, repositories: tuple[str, ...] = (), *,
        actor: str | None = None, rationale: str = "",
    ) -> Project:
        name = _title(name)
        if not isinstance(repositories, tuple):
            raise TreeError("Repository bindings must be a tuple")
        normalized = tuple(_repository_binding(repo) for repo in repositories)
        if len(normalized) != len(set(normalized)):
            raise TreeError("Duplicate repository binding")
        project = Project(self._allocate_id(), name, normalized)
        event = self._event(project.id, "project.create", "project", project.id,
                            None, project, actor=actor, rationale=rationale)
        self._publish("_projects", {**self._projects, project.id: project}, event)
        return project

    def rename_project(
        self, project_id: str, name: str, *, actor: str | None = None, rationale: str = "",
    ) -> Project:
        current = self.project(project_id)
        renamed = replace(current, name=_title(name))
        if renamed == current:
            return current
        event = self._event(project_id, "project.rename", "project", current.id,
                            current, renamed, actor=actor, rationale=rationale)
        self._publish("_projects", {**self._projects, current.id: renamed}, event)
        return renamed

    def node(self, project_id: str, node_id: str) -> RoadmapNode:
        self.project(project_id)
        try:
            node = self._nodes[node_id]
        except (KeyError, TypeError):
            raise NotFound("Node not found in project") from None
        if node.project_id != project_id:
            raise NotFound("Node not found in project")
        return node

    @staticmethod
    def _siblings(
        nodes: dict[str, RoadmapNode], project_id: str, parent_id: str | None
    ) -> list[str]:
        return [
            item.id for item in sorted(
                (node for node in nodes.values()
                 if node.project_id == project_id and node.parent_id == parent_id),
                key=lambda node: node.position,
            )
        ]

    @staticmethod
    def _renumber(nodes: dict[str, RoadmapNode], identifiers: list[str]) -> None:
        for position, node_id in enumerate(identifiers):
            node = nodes[node_id]
            if node.position != position:
                nodes[node_id] = replace(node, position=position)

    def _is_effectively_archived(self, node_id: str | None) -> bool:
        while node_id is not None:
            node = self._nodes[node_id]
            if node.archived:
                return True
            node_id = node.parent_id
        return False

    def effectively_archived(self, project_id: str, node_id: str) -> bool:
        self.node(project_id, node_id)
        return self._is_effectively_archived(node_id)

    def create_node(
        self, project_id: str, title: str, *,
        parent_id: str | None = None,
        position: int | None = None,
        kind: NodeKind = NodeKind.TASK,
        description: str = "",
        acceptance_criteria: tuple[str, ...] = (),
        actor: str | None = None, rationale: str = "",
    ) -> RoadmapNode:
        self.project(project_id)
        title = _title(title)
        if not isinstance(kind, NodeKind):
            raise TreeError("Node kind must be NodeKind")
        if not isinstance(description, str) or "\x00" in description:
            raise TreeError("Invalid description")
        if not isinstance(acceptance_criteria, tuple) or any(
            not isinstance(x, str) or not x.strip() or "\x00" in x
            for x in acceptance_criteria
        ):
            raise TreeError("Acceptance criteria must be nonempty string tuple")
        criteria = tuple(x.strip() for x in acceptance_criteria)
        if len(criteria) != len(set(criteria)):
            raise TreeError("Duplicate acceptance criterion")
        if parent_id is not None:
            self.node(project_id, parent_id)
            if self._is_effectively_archived(parent_id):
                raise InvalidMove("Cannot create under archived parent")
        siblings = self._siblings(self._nodes, project_id, parent_id)
        index = _position(position, len(siblings))
        node = RoadmapNode(
            id=self._allocate_id(), project_id=project_id, parent_id=parent_id,
            position=index, title=title, kind=kind, description=description,
            acceptance_criteria=criteria,
        )
        proposed = self._nodes.copy()
        proposed[node.id] = node
        siblings.insert(index, node.id)
        self._renumber(proposed, siblings)
        self._commit(proposed, project_id=project_id, action="node.create",
                     target_id=node.id, actor=actor, rationale=rationale)
        return self._nodes[node.id]

    def rename_node(
        self, project_id: str, node_id: str, title: str, *,
        actor: str | None = None, rationale: str = "",
    ) -> RoadmapNode:
        original = self.node(project_id, node_id)
        title = _title(title)
        if self._is_effectively_archived(node_id):
            raise TreeError("Cannot edit archived node")
        proposed = self._nodes.copy()
        proposed[node_id] = replace(original, title=title)
        self._commit(proposed, project_id=project_id, action="node.rename",
                     target_id=node_id, actor=actor, rationale=rationale)
        return self._nodes[node_id]

    def move_node(
        self, project_id: str, node_id: str, *,
        new_parent_id: str | None,
        position: int | None = None,
        actor: str | None = None, rationale: str = "",
    ) -> RoadmapNode:
        original = self.node(project_id, node_id)
        if self._is_effectively_archived(node_id):
            raise InvalidMove("Cannot move archived node")
        if new_parent_id is not None:
            self.node(project_id, new_parent_id)
            if self._is_effectively_archived(new_parent_id):
                raise InvalidMove("Cannot move into archived parent")
        ancestor = new_parent_id
        while ancestor is not None:
            if ancestor == node_id:
                raise InvalidMove("Cannot move into self or descendant")
            ancestor = self._nodes[ancestor].parent_id

        old_order = self._siblings(self._nodes, project_id, original.parent_id)
        old_order.remove(node_id)
        new_order = (
            old_order if original.parent_id == new_parent_id
            else self._siblings(self._nodes, project_id, new_parent_id)
        )
        index = _position(position, len(new_order))
        new_order.insert(index, node_id)
        proposed = self._nodes.copy()
        proposed[node_id] = replace(original, parent_id=new_parent_id, position=index)
        if original.parent_id != new_parent_id:
            self._renumber(proposed, old_order)
        self._renumber(proposed, new_order)
        self._commit(proposed, project_id=project_id, action="node.move",
                     target_id=node_id, actor=actor, rationale=rationale)
        return self._nodes[node_id]

    def archive_node(
        self, project_id: str, node_id: str, *,
        actor: str | None = None, rationale: str = "",
    ) -> RoadmapNode:
        return self._set_archive(project_id, node_id, True, actor=actor, rationale=rationale)

    def restore_node(
        self, project_id: str, node_id: str, *,
        actor: str | None = None, rationale: str = "",
    ) -> RoadmapNode:
        return self._set_archive(project_id, node_id, False, actor=actor, rationale=rationale)

    def _set_archive(
        self, project_id: str, node_id: str, archived: bool, *,
        actor: str | None, rationale: str,
    ) -> RoadmapNode:
        original = self.node(project_id, node_id)
        if not archived and original.parent_id is not None and self._is_effectively_archived(original.parent_id):
            raise TreeError("Restore archived ancestor first")
        if original.archived == archived:
            return original
        proposed = self._nodes.copy()
        proposed[node_id] = replace(original, archived=archived)
        self._commit(proposed, project_id=project_id,
                     action="node.archive" if archived else "node.restore",
                     target_id=node_id, actor=actor, rationale=rationale)
        return self._nodes[node_id]

    def children(
        self, project_id: str, parent_id: str | None = None
    ) -> tuple[RoadmapNode, ...]:
        self.project(project_id)
        if parent_id is not None:
            self.node(project_id, parent_id)
        return tuple(
            self._nodes[node_id]
            for node_id in self._siblings(self._nodes, project_id, parent_id)
        )

    def walk(self, project_id: str, node_id: str | None = None) -> Iterator[RoadmapNode]:
        """Snapshot-consistent, iterative preorder traversal; no depth limit."""
        self.project(project_id)
        if node_id is not None:
            self.node(project_id, node_id)
        snapshot = self._nodes  # Published dictionaries are never mutated in-place.
        root_ids = (
            [node_id] if node_id is not None
            else self._siblings(snapshot, project_id, None)
        )

        def traverse() -> Iterator[RoadmapNode]:
            pending = list(reversed(root_ids))
            while pending:
                current_id = pending.pop()
                current = snapshot[current_id]
                yield current
                pending.extend(
                    reversed(self._siblings(snapshot, project_id, current_id))
                )

        return traverse()

    def audit_log(self, project_id: str) -> tuple[AuditEntry, ...]:
        """Immutable, project-scoped journal snapshot; no public mutation API."""
        self.project(project_id)
        return tuple(item for item in self._audit if item.project_id == project_id)

    def _event(
        self, project_id: str, action: str, target_type: str, target_id: str,
        before: object | None, after: object | None, *,
        actor: str | None = None, rationale: str = "",
    ) -> AuditEntry:
        actor = None if actor is None else _text(actor, "actor", limit=300)
        rationale = _text(rationale, "audit rationale", allow_blank=True, multiline=True)
        return AuditEntry(
            sequence=len(self._audit) + 1,
            project_id=project_id, action=action, target_type=target_type,
            target_id=target_id, occurred_at=datetime.now(timezone.utc),
            actor=actor, rationale=rationale, before=before, after=after,
        )

    def _publish(self, bucket: str, proposed: dict, event: AuditEntry) -> None:
        """Publish validated candidate and append audit only after validation.

        No disk-backed transaction or concurrent readers/writers in T1.2.
        """
        new_log = (*self._audit, event)
        setattr(self, bucket, proposed)
        self._audit = new_log

    def _commit(
        self, proposed: dict[str, RoadmapNode], *,
        project_id: str, action: str, target_id: str,
        actor: str | None = None, rationale: str = "",
    ) -> None:
        self._validate(proposed)
        changed = sorted(
            node_id for node_id in (self._nodes.keys() | proposed.keys())
            if self._nodes.get(node_id) != proposed.get(node_id)
        )
        if not changed:
            return
        previous = tuple(self._nodes[node_id] for node_id in changed if node_id in self._nodes)
        updated = tuple(proposed[node_id] for node_id in changed if node_id in proposed)
        event = self._event(project_id, action, "node", target_id, previous, updated,
                            actor=actor, rationale=rationale)
        self._publish("_nodes", proposed, event)

    def _validate(self, nodes: dict[str, RoadmapNode]) -> None:
        groups: dict[tuple[str, str | None], list[int]] = {}
        for node_id, node in nodes.items():
            if node_id != node.id or node.project_id not in self._projects:
                raise TreeError("Corrupt node identity/project")
            if node.parent_id is not None:
                parent = nodes.get(node.parent_id)
                if parent is None or parent.project_id != node.project_id:
                    raise TreeError("Orphan or cross-project parent")
            if isinstance(node.position, bool) or not isinstance(node.position, int) or node.position < 0:
                raise TreeError("Invalid position")
            groups.setdefault((node.project_id, node.parent_id), []).append(node.position)
        for positions in groups.values():
            if sorted(positions) != list(range(len(positions))):
                raise TreeError("Sibling positions must be contiguous and unique")
        settled: set[str] = set()
        for node_id in nodes:
            if node_id in settled:
                continue
            visiting: set[str] = set()
            cursor: str | None = node_id
            while cursor is not None and cursor not in settled:
                if cursor in visiting:
                    raise TreeError("Cycle in canonical tree")
                visiting.add(cursor)
                cursor = nodes[cursor].parent_id
            settled.update(visiting)
