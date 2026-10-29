"""T1.3: deterministic read-only views over the sole canonical command engine."""
from __future__ import annotations

from dataclasses import dataclass

from .tree import CommandEngine, RoadmapNode


@dataclass(frozen=True, slots=True)
class NodeProjection:
    """Derived display data; never persisted or used as authoritative state."""

    node: RoadmapNode
    depth: int
    requirement_ids: tuple[str, ...]
    dependency_ids: tuple[str, ...]


def project_outline(engine: CommandEngine, project_id: str) -> tuple[NodeProjection, ...]:
    """Deterministic preorder; unlimited depth, no independent hierarchy.

    Project-scoped outgoing links only. Cross-project target details are not
    disclosed by this projection (real access enforcement is a later layer).
    """
    engine.project(project_id)
    requirements: dict[str, list[tuple[str, str]]] = {}
    for item in engine.requirements(project_id):
        for node_id in item.node_ids:
            requirements.setdefault(node_id, []).append((item.code, item.id))
    dependencies: dict[str, list[tuple[str, str, str]]] = {}
    for edge in engine.dependencies(project_id, include_inactive=False):
        dependencies.setdefault(edge.source_node_id, []).append(
            (edge.kind.value, edge.target_node_id, edge.id)
        )

    # walk() is snapshot-based. Child depth derives solely from each parent.
    depth_by_id: dict[str, int] = {}
    result: list[NodeProjection] = []
    for node in engine.walk(project_id):
        depth = 0 if node.parent_id is None else depth_by_id[node.parent_id] + 1
        depth_by_id[node.id] = depth
        result.append(NodeProjection(
            node=node,
            depth=depth,
            requirement_ids=tuple(ident for _, ident in sorted(requirements.get(node.id, ()))),
            dependency_ids=tuple(ident for _, _, ident in sorted(dependencies.get(node.id, ()))),
        ))
    return tuple(result)
