"""T1.2 in-memory requirement, dependency, and proposal commands.

All writes go through the same CommandEngine as the T1.1 tree. This layer
does NOT authorize users, execute proposed decisions or persist the journal.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import re
from typing import TYPE_CHECKING

from .errors import NotFound, TreeError

if TYPE_CHECKING:
    from .tree import CommandEngine


class DependencyKind(str, Enum):
    BLOCKS = "blocks"  # source node depends on target node
    RELATES_TO = "relates_to"


class ProposalState(str, Enum):
    PROPOSED = "proposed"  # never an authorization or approval


@dataclass(frozen=True, slots=True)
class Requirement:
    id: str
    project_id: str
    code: str
    title: str
    criteria: tuple[str, ...]
    version: int = 1
    node_ids: tuple[str, ...] = ()
    decision_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Dependency:
    id: str
    source_project_id: str
    source_node_id: str
    target_project_id: str
    target_node_id: str
    kind: DependencyKind
    active: bool = True


@dataclass(frozen=True, slots=True)
class ArchitectureDecision:
    id: str
    project_id: str
    reference: str
    title: str
    rationale: str
    actor: str
    created_at: datetime
    supersedes_id: str | None = None
    state: ProposalState = ProposalState.PROPOSED


@dataclass(frozen=True, slots=True)
class DecisionProposal:
    id: str
    project_id: str
    node_id: str | None
    actor: str
    action: str
    rationale: str
    previous_value: str
    proposed_value: str
    created_at: datetime
    state: ProposalState = ProposalState.PROPOSED


@dataclass(frozen=True, slots=True)
class AuditEntry:
    sequence: int
    project_id: str
    action: str
    target_type: str
    target_id: str
    occurred_at: datetime
    actor: str | None  # None = unattributed legacy structural command, never a forged identity
    rationale: str
    before: object | None  # only immutable domain snapshots or tuples thereof
    after: object | None


def _text(
    value: str, field: str, *, limit: int = 4000,
    allow_blank: bool = False, multiline: bool = False,
) -> str:
    if not isinstance(value, str):
        raise TreeError(f"{field} must be a string")
    normalized = value.strip()
    if (not allow_blank and not normalized) or len(normalized) > limit or any(
        (ord(c) < 32 and (not multiline or c not in "\n\t")) or ord(c) == 127
        for c in normalized
    ):
        raise TreeError(f"Invalid {field}")
    return normalized


def _criteria(values: tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(values, tuple) or not values:
        raise TreeError("Requirement must have testable criteria tuple")
    normalized = tuple(_text(v, "criterion") for v in values)
    if len(set(normalized)) != len(normalized):
        raise TreeError("Duplicate requirement criterion")
    return normalized


def _ids(values: tuple[str, ...], label: str) -> tuple[str, ...]:
    if not isinstance(values, tuple) or any(not isinstance(v, str) or not v for v in values):
        raise TreeError(f"{label} must be an ID tuple")
    if len(set(values)) != len(values):
        raise TreeError(f"Duplicate {label}")
    return values


class GovernanceCommands:
    """Validated domain operations mixed into the single CommandEngine.

    The engine owns dictionaries and the append-only journal. A full
    transaction/persistence/concurrency layer is explicitly deferred to T1.3.
    """

    def requirement(self: CommandEngine, project_id: str, requirement_id: str) -> Requirement:
        self.project(project_id)
        try:
            item = self._requirements[requirement_id]
        except (KeyError, TypeError):
            raise NotFound("Requirement not found in project") from None
        if item.project_id != project_id:
            raise NotFound("Requirement not found in project")
        return item

    def requirements(self: CommandEngine, project_id: str, node_id: str | None = None) -> tuple[Requirement, ...]:
        self.project(project_id)
        if node_id is not None:
            self.node(project_id, node_id)
        return tuple(
            item for item in self._requirements.values()
            if item.project_id == project_id and (node_id is None or node_id in item.node_ids)
        )

    def create_requirement(
        self: CommandEngine, project_id: str, code: str, title: str,
        criteria: tuple[str, ...], *, node_ids: tuple[str, ...] = (),
        actor: str, rationale: str = "",
    ) -> Requirement:
        self.project(project_id)
        code = _text(code, "requirement code", limit=64)
        if not re.fullmatch(r"[A-Z][A-Z0-9-]{1,63}", code):
            raise TreeError("Requirement code must be uppercase letters, numbers and hyphens")
        title = _text(title, "requirement title", limit=300)
        criteria = _criteria(criteria)
        node_ids = _ids(node_ids, "node links")
        for node_id in node_ids:
            self.node(project_id, node_id)
            if self.effectively_archived(project_id, node_id):
                raise TreeError("Cannot link new requirement to archived node")
        if any(item.project_id == project_id and item.code == code for item in self._requirements.values()):
            raise TreeError("Requirement code already exists in project")
        item = Requirement(self._allocate_id(), project_id, code, title, criteria, node_ids=node_ids)
        event = self._event(project_id, "requirement.create", "requirement", item.id, None, item,
                            actor=actor, rationale=rationale)
        self._publish("_requirements", {**self._requirements, item.id: item}, event)
        return item

    def revise_requirement(
        self: CommandEngine, project_id: str, requirement_id: str, *,
        expected_version: int, title: str | None = None,
        criteria: tuple[str, ...] | None = None, actor: str, rationale: str,
    ) -> Requirement:
        from dataclasses import replace
        prior = self.requirement(project_id, requirement_id)
        if isinstance(expected_version, bool) or not isinstance(expected_version, int) or expected_version != prior.version:
            raise TreeError("Requirement version conflict")
        title = prior.title if title is None else _text(title, "requirement title", limit=300)
        criteria = prior.criteria if criteria is None else _criteria(criteria)
        if title == prior.title and criteria == prior.criteria:
            return prior
        revised = replace(prior, title=title, criteria=criteria, version=prior.version + 1)
        event = self._event(project_id, "requirement.revise", "requirement", prior.id, prior,
                            revised, actor=actor, rationale=_text(rationale, "revision rationale"))
        self._publish("_requirements", {**self._requirements, prior.id: revised}, event)
        return revised

    def link_requirement_node(
        self: CommandEngine, project_id: str, requirement_id: str, node_id: str, *,
        actor: str, rationale: str = "",
    ) -> Requirement:
        return self._change_requirement_link(project_id, requirement_id, node_id, True, actor, rationale)

    def unlink_requirement_node(
        self: CommandEngine, project_id: str, requirement_id: str, node_id: str, *,
        actor: str, rationale: str = "",
    ) -> Requirement:
        return self._change_requirement_link(project_id, requirement_id, node_id, False, actor, rationale)

    def _change_requirement_link(
        self: CommandEngine, project_id: str, requirement_id: str, node_id: str,
        add: bool, actor: str, rationale: str,
    ) -> Requirement:
        from dataclasses import replace
        original = self.requirement(project_id, requirement_id)
        self.node(project_id, node_id)
        if add and self.effectively_archived(project_id, node_id):
            raise TreeError("Cannot link archived node")
        linked = node_id in original.node_ids
        if linked == add:
            return original
        links = (*original.node_ids, node_id) if add else tuple(x for x in original.node_ids if x != node_id)
        changed = replace(original, node_ids=links, version=original.version + 1)
        event = self._event(
            project_id, "requirement.link_node" if add else "requirement.unlink_node",
            "requirement", original.id, original, changed, actor=actor, rationale=rationale,
        )
        self._publish("_requirements", {**self._requirements, original.id: changed}, event)
        return changed

    def link_requirement_decision(
        self: CommandEngine, project_id: str, requirement_id: str, decision_id: str, *,
        actor: str, rationale: str = "",
    ) -> Requirement:
        from dataclasses import replace
        original = self.requirement(project_id, requirement_id)
        self.architecture_decision(project_id, decision_id)
        if decision_id in original.decision_ids:
            return original
        changed = replace(original, decision_ids=(*original.decision_ids, decision_id),
                          version=original.version + 1)
        event = self._event(project_id, "requirement.link_decision", "requirement", original.id,
                            original, changed, actor=actor, rationale=rationale)
        self._publish("_requirements", {**self._requirements, original.id: changed}, event)
        return changed

    def dependency(self: CommandEngine, project_id: str, dependency_id: str) -> Dependency:
        self.project(project_id)
        try:
            edge = self._dependencies[dependency_id]
        except (KeyError, TypeError):
            raise NotFound("Dependency not found") from None
        if edge.source_project_id != project_id:
            raise NotFound("Dependency not found")
        return edge

    def dependencies(self: CommandEngine, project_id: str, *,
                     include_inactive: bool = True) -> tuple[Dependency, ...]:
        self.project(project_id)
        return tuple(
            item for item in self._dependencies.values()
            if item.source_project_id == project_id and (include_inactive or item.active)
        )

    def add_dependency(
        self: CommandEngine, project_id: str, source_node_id: str, target_node_id: str,
        *, target_project_id: str | None = None,
        kind: DependencyKind = DependencyKind.BLOCKS,
        allow_cross_project: bool = False, actor: str, rationale: str = "",
    ) -> Dependency:
        target_project_id = project_id if target_project_id is None else target_project_id
        self.node(project_id, source_node_id)
        self.node(target_project_id, target_node_id)
        if project_id != target_project_id and allow_cross_project is not True:
            raise TreeError("Explicit cross-project reference required")
        if not isinstance(kind, DependencyKind):
            raise TreeError("Unknown dependency kind")
        if self.effectively_archived(project_id, source_node_id) or self.effectively_archived(target_project_id, target_node_id):
            raise TreeError("Cannot add dependency to archived node")
        if source_node_id == target_node_id:
            raise TreeError("Self dependency")
        if any(edge.active and edge.source_node_id == source_node_id
               and edge.target_node_id == target_node_id and edge.kind == kind
               for edge in self._dependencies.values()):
            raise TreeError("Duplicate active dependency")
        if kind == DependencyKind.BLOCKS:
            # Iterative reachability; reversed path would form a directed cycle.
            adjacency: dict[str, list[str]] = {}
            for edge in self._dependencies.values():
                if edge.active and edge.kind == DependencyKind.BLOCKS:
                    adjacency.setdefault(edge.source_node_id, []).append(edge.target_node_id)
            pending = [target_node_id]
            visited: set[str] = set()
            while pending:
                candidate = pending.pop()
                if candidate == source_node_id:
                    raise TreeError("Blocking dependency cycle")
                if candidate not in visited:
                    visited.add(candidate)
                    pending.extend(adjacency.get(candidate, ()))
        edge = Dependency(self._allocate_id(), project_id, source_node_id,
                          target_project_id, target_node_id, kind)
        event = self._event(project_id, "dependency.add", "dependency", edge.id, None, edge,
                            actor=actor, rationale=rationale)
        self._publish("_dependencies", {**self._dependencies, edge.id: edge}, event)
        return edge

    def deactivate_dependency(
        self: CommandEngine, project_id: str, dependency_id: str, *, actor: str, rationale: str,
    ) -> Dependency:
        from dataclasses import replace
        old = self.dependency(project_id, dependency_id)
        if not old.active:
            return old
        changed = replace(old, active=False)
        event = self._event(project_id, "dependency.deactivate", "dependency", old.id,
                            old, changed, actor=actor, rationale=_text(rationale, "deactivation rationale"))
        self._publish("_dependencies", {**self._dependencies, old.id: changed}, event)
        return changed

    def architecture_decision(
        self: CommandEngine, project_id: str, decision_id: str,
    ) -> ArchitectureDecision:
        self.project(project_id)
        try:
            item = self._architecture_decisions[decision_id]
        except (KeyError, TypeError):
            raise NotFound("Architecture decision not found") from None
        if item.project_id != project_id:
            raise NotFound("Architecture decision not found")
        return item

    def architecture_decisions(self: CommandEngine, project_id: str) -> tuple[ArchitectureDecision, ...]:
        self.project(project_id)
        return tuple(x for x in self._architecture_decisions.values() if x.project_id == project_id)

    def propose_architecture_decision(
        self: CommandEngine, project_id: str, reference: str, title: str,
        rationale: str, *, actor: str, supersedes_id: str | None = None,
    ) -> ArchitectureDecision:
        self.project(project_id)
        reference = _text(reference, "ADR reference", limit=32)
        if not re.fullmatch(r"ADR-[0-9]{4,}", reference):
            raise TreeError("ADR reference must be ADR-NNNN")
        title = _text(title, "ADR title", limit=300)
        rationale = _text(rationale, "ADR rationale", multiline=True)
        actor = _text(actor, "actor", limit=300)
        if supersedes_id is not None:
            self.architecture_decision(project_id, supersedes_id)
        if any(x.project_id == project_id and x.reference == reference
               for x in self._architecture_decisions.values()):
            raise TreeError("ADR reference already exists")
        item = ArchitectureDecision(self._allocate_id(), project_id, reference, title, rationale,
                                    actor, datetime.now(timezone.utc), supersedes_id=supersedes_id)
        event = self._event(project_id, "architecture_decision.propose", "architecture_decision",
                            item.id, None, item, actor=actor, rationale=rationale)
        self._publish("_architecture_decisions", {**self._architecture_decisions, item.id: item}, event)
        return item

    def decision_proposals(self: CommandEngine, project_id: str) -> tuple[DecisionProposal, ...]:
        self.project(project_id)
        return tuple(x for x in self._decision_proposals.values() if x.project_id == project_id)

    def propose_decision(
        self: CommandEngine, project_id: str, action: str, rationale: str, *,
        actor: str, node_id: str | None = None,
        previous_value: str = "", proposed_value: str,
    ) -> DecisionProposal:
        self.project(project_id)
        if node_id is not None:
            self.node(project_id, node_id)
        actor = _text(actor, "actor", limit=300)
        action = _text(action, "action", limit=300)
        rationale = _text(rationale, "decision rationale", multiline=True)
        previous_value = _text(previous_value, "previous value", allow_blank=True)
        proposed_value = _text(proposed_value, "proposed value")
        item = DecisionProposal(self._allocate_id(), project_id, node_id, actor, action,
                                rationale, previous_value, proposed_value,
                                datetime.now(timezone.utc))
        event = self._event(project_id, "decision.propose", "decision_proposal", item.id,
                            None, item, actor=actor, rationale=rationale)
        self._publish("_decision_proposals", {**self._decision_proposals, item.id: item}, event)
        return item
