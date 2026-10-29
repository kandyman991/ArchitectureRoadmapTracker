"""In-memory canonical roadmap tree (T1.1).

No persistence, permissions, GitHub, runner, acceptance engine or UI yet.
Mutations publish only after all structural invariants pass.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterator
from uuid import uuid4


class TreeError(ValueError):
    """Rejected command. The canonical tree remains unchanged."""


class NotFound(TreeError):
    """Project or project-scoped node does not exist."""


class InvalidMove(TreeError):
    """Invalid reparenting, cycle or archived-node operation."""


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


def _position(position: int | None, count: int) -> int:
    if position is None:
        return count
    if isinstance(position, bool) or not isinstance(position, int) or not 0 <= position <= count:
        raise TreeError(f"Position must be an integer between 0 and {count}")
    return position


class CommandEngine:
    """Only in-memory mutation surface for canonical projects/nodes.

    Frozen models prevent accidental mutation outside commands. Moves operate
    on private copies and run invariant checks before publication. Sibling
    positions and parent IDs are canonical; UI views must derive from them.
    """

    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}
        self._nodes: dict[str, RoadmapNode] = {}

    def _allocate_id(self) -> str:
        for _ in range(10):
            candidate = uuid4().hex
            if candidate not in self._projects and candidate not in self._nodes:
                return candidate
        raise TreeError("Unable to allocate unique identity")

    def project(self, project_id: str) -> Project:
        try:
            return self._projects[project_id]
        except (KeyError, TypeError):
            raise NotFound("Project not found") from None

    def projects(self) -> tuple[Project, ...]:
        return tuple(self._projects.values())

    def create_project(self, name: str, repositories: tuple[str, ...] = ()) -> Project:
        name = _title(name)
        if not isinstance(repositories, tuple) or any(
            not isinstance(repo, str) or not repo.strip() or "\x00" in repo
            for repo in repositories
        ):
            raise TreeError("Repository bindings must be a tuple of nonempty strings")
        normalized = tuple(repo.strip() for repo in repositories)
        if len(normalized) != len(set(normalized)):
            raise TreeError("Duplicate repository binding")
        project = Project(self._allocate_id(), name, normalized)
        self._projects = {**self._projects, project.id: project}
        return project

    def rename_project(self, project_id: str, name: str) -> Project:
        current = self.project(project_id)
        renamed = replace(current, name=_title(name))
        self._projects = {**self._projects, current.id: renamed}
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
        self._commit(proposed)
        return self._nodes[node.id]

    def rename_node(self, project_id: str, node_id: str, title: str) -> RoadmapNode:
        original = self.node(project_id, node_id)
        title = _title(title)
        if self._is_effectively_archived(node_id):
            raise TreeError("Cannot edit archived node")
        proposed = self._nodes.copy()
        proposed[node_id] = replace(original, title=title)
        self._commit(proposed)
        return self._nodes[node_id]

    def move_node(
        self, project_id: str, node_id: str, *,
        new_parent_id: str | None,
        position: int | None = None,
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
        self._commit(proposed)
        return self._nodes[node_id]

    def archive_node(self, project_id: str, node_id: str) -> RoadmapNode:
        return self._set_archive(project_id, node_id, True)

    def restore_node(self, project_id: str, node_id: str) -> RoadmapNode:
        return self._set_archive(project_id, node_id, False)

    def _set_archive(self, project_id: str, node_id: str, archived: bool) -> RoadmapNode:
        original = self.node(project_id, node_id)
        if not archived and original.parent_id is not None and self._is_effectively_archived(original.parent_id):
            raise TreeError("Restore archived ancestor first")
        if original.archived == archived:
            return original
        proposed = self._nodes.copy()
        proposed[node_id] = replace(original, archived=archived)
        self._commit(proposed)
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
        """Iterative preorder traversal, including node_id when given."""
        self.project(project_id)
        if node_id is None:
            pending = [node.id for node in reversed(self.children(project_id))]
        else:
            self.node(project_id, node_id)
            pending = [node_id]
        while pending:
            current_id = pending.pop()
            yield self._nodes[current_id]
            pending.extend(
                node.id for node in reversed(self.children(project_id, current_id))
            )

    def _commit(self, proposed: dict[str, RoadmapNode]) -> None:
        self._validate(proposed)
        self._nodes = proposed

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
