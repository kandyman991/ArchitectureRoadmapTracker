"""Portable, deterministic, strictly validated T1.3 snapshot interchange.

The snapshot is NOT an authentication token or an approved architecture contract.
Import constructs a new command engine; failure never mutates an existing one.
"""
from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import re

from .errors import TreeError
from .governance import (
    ArchitectureDecision, AuditEntry, DecisionProposal, Dependency, DependencyKind,
    ProposalState, Requirement, _criteria, _ids, _text,
)
from .tree import CommandEngine, NodeKind, Project, RoadmapNode, _repository_binding, _title

FORMAT_VERSION = 1
MAX_SNAPSHOT_BYTES = 32 * 1024 * 1024
_BUCKETS = (
    ("projects", "_projects", Project),
    ("nodes", "_nodes", RoadmapNode),
    ("requirements", "_requirements", Requirement),
    ("dependencies", "_dependencies", Dependency),
    ("architecture_decisions", "_architecture_decisions", ArchitectureDecision),
    ("decision_proposals", "_decision_proposals", DecisionProposal),
)
_RECORDS = {cls.__name__: cls for _, _, cls in _BUCKETS}
_RECORDS[AuditEntry.__name__] = AuditEntry
_ENUMS = {cls.__name__: cls for cls in (NodeKind, DependencyKind, ProposalState)}


def _encode(value: object) -> object:
    if isinstance(value, Enum):
        if type(value).__name__ not in _ENUMS:
            raise TreeError("Unsupported enum in snapshot")
        return {"$enum": type(value).__name__, "value": value.value}
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise TreeError("Snapshot timestamp must be UTC")
        return {"$datetime": value.isoformat().replace("+00:00", "Z")}
    if is_dataclass(value) and not isinstance(value, type):
        name = type(value).__name__
        if name not in _RECORDS or type(value) is not _RECORDS[name]:
            raise TreeError("Unknown snapshot record")
        return {"$record": name, "fields": {
            item.name: _encode(getattr(value, item.name)) for item in fields(value)
        }}
    if isinstance(value, tuple):
        return {"$tuple": [_encode(item) for item in value]}
    if value is None or type(value) in (str, int, bool):
        return value
    raise TreeError("Unsupported snapshot value")


def _decode(value: object) -> object:
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is not dict:
        raise TreeError("Invalid tagged snapshot value")
    if set(value) == {"$tuple"} and type(value["$tuple"]) is list:
        return tuple(_decode(item) for item in value["$tuple"])
    if set(value) == {"$datetime"} and type(value["$datetime"]) is str:
        try:
            stamp = datetime.fromisoformat(value["$datetime"].replace("Z", "+00:00"))
            if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
                raise ValueError("not UTC")
            return stamp
        except ValueError as exc:
            raise TreeError("Invalid snapshot timestamp") from exc
    if set(value) == {"$enum", "value"} and type(value["$enum"]) is str:
        cls = _ENUMS.get(value["$enum"])
        if cls is None or type(value["value"]) is not str:
            raise TreeError("Unknown snapshot enum")
        try:
            return cls(value["value"])
        except ValueError as exc:
            raise TreeError("Invalid snapshot enum") from exc
    if set(value) == {"$record", "fields"} and type(value["$record"]) is str:
        cls = _RECORDS.get(value["$record"])
        content = value["fields"]
        if cls is None or type(content) is not dict:
            raise TreeError("Unknown snapshot record")
        if set(content) != {field.name for field in fields(cls)}:
            raise TreeError("Snapshot record field mismatch")
        return cls(**{key: _decode(item) for key, item in content.items()})
    raise TreeError("Invalid snapshot tag")


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise TreeError("Duplicate JSON key")
        result[key] = value
    return result


def export_snapshot(engine: CommandEngine) -> bytes:
    """Stable byte-identical export for unchanged canonical state/journal."""
    _validate_engine(engine)
    envelope = {"format_version": FORMAT_VERSION}
    for key, attr, _ in _BUCKETS:
        envelope[key] = [_encode(obj) for _, obj in sorted(getattr(engine, attr).items())]
    envelope["audit"] = [_encode(item) for item in engine._audit]
    raw = json.dumps(envelope, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(raw) > MAX_SNAPSHOT_BYTES:
        raise TreeError("Snapshot too large")
    return raw


def import_snapshot(payload: bytes) -> CommandEngine:
    """Validate fully before making a reconstructed engine visible."""
    if type(payload) is not bytes or len(payload) > MAX_SNAPSHOT_BYTES:
        raise TreeError("Invalid snapshot bytes or size")
    try:
        data = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(TreeError("Nonfinite JSON")))
        keys = {"format_version", "audit", *(key for key, _, _ in _BUCKETS)}
        if type(data) is not dict or set(data) != keys:
            raise TreeError("Snapshot envelope mismatch")
        if type(data["format_version"]) is not int or data["format_version"] != FORMAT_VERSION:
            raise TreeError("Unsupported snapshot format")
        engine = CommandEngine()
        for key, attr, expected_type in _BUCKETS:
            records = data[key]
            if type(records) is not list:
                raise TreeError("Snapshot bucket must be an array")
            decoded = [_decode(item) for item in records]
            if any(type(item) is not expected_type for item in decoded):
                raise TreeError("Snapshot bucket contains wrong record")
            entries = {item.id: item for item in decoded}
            if len(entries) != len(decoded):
                raise TreeError("Duplicate record ID")
            setattr(engine, attr, entries)
        if type(data["audit"]) is not list:
            raise TreeError("Invalid audit array")
        engine._audit = tuple(_decode(item) for item in data["audit"])
        _validate_engine(engine)
        return engine
    except (ValueError, TypeError, OverflowError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, TreeError):
            raise
        raise TreeError("Invalid snapshot") from exc


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise TreeError(message)


def _valid_audit_value(value: object) -> bool:
    if value is None:
        return True
    if type(value) is tuple:
        return all(type(item) in _RECORDS.values() and type(item) is not AuditEntry for item in value)
    return type(value) in _RECORDS.values() and type(value) is not AuditEntry


def _validate_engine(engine: CommandEngine) -> None:
    """Validate relationships and low-level types after untrusted deserialization."""
    _ensure(type(engine) is CommandEngine or isinstance(engine, CommandEngine), "Invalid engine")
    global_ids: set[str] = set()
    for _, attr, cls in _BUCKETS:
        bucket = getattr(engine, attr)
        _ensure(type(bucket) is dict, "Invalid snapshot bucket")
        for identity, item in bucket.items():
            _ensure(type(item) is cls and type(identity) is str and identity == item.id,
                    "Invalid record identity")
            _ensure(bool(re.fullmatch(r"[0-9a-f]{32}", identity)), "Invalid record ID")
            _ensure(identity not in global_ids, "Reused global identity")
            global_ids.add(identity)
    for item in engine._projects.values():
        _ensure(type(item.name) is str and _title(item.name) == item.name, "Invalid project name")
        _ensure(type(item.repositories) is tuple, "Invalid repository collection")
        _ensure(all(type(repo) is str and _repository_binding(repo) == repo
                    for repo in item.repositories), "Invalid repository binding")
        _ensure(len(set(item.repositories)) == len(item.repositories), "Duplicate repository binding")
    for item in engine._nodes.values():
        _ensure(type(item.project_id) is str and type(item.kind) is NodeKind, "Invalid node types")
        _ensure(type(item.title) is str and _title(item.title) == item.title, "Invalid node title")
        _ensure(type(item.description) is str and "\x00" not in item.description, "Invalid node description")
        _ensure(type(item.acceptance_criteria) is tuple and all(
            type(v) is str and v.strip() == v and bool(v) and "\x00" not in v
            for v in item.acceptance_criteria
        ), "Invalid node criteria")
        _ensure(len(set(item.acceptance_criteria)) == len(item.acceptance_criteria),
                "Duplicate node criterion")
        _ensure(type(item.archived) is bool, "Invalid node archive flag")
    engine._validate(engine._nodes)
    req_codes: set[tuple[str, str]] = set()
    for item in engine._requirements.values():
        _ensure(item.project_id in engine._projects, "Unknown requirement project")
        _ensure(type(item.code) is str and bool(re.fullmatch(r"[A-Z][A-Z0-9-]{1,63}", item.code)),
                "Invalid requirement code")
        _ensure((item.project_id, item.code) not in req_codes, "Duplicate requirement code")
        req_codes.add((item.project_id, item.code))
        _ensure(type(item.title) is str and _text(item.title, "requirement title", limit=300) == item.title,
                "Invalid requirement title")
        _ensure(type(item.version) is int and item.version > 0, "Invalid requirement version")
        _ensure(type(item.criteria) is tuple and _criteria(item.criteria) == item.criteria,
                "Invalid requirement criteria")
        _ensure(type(item.node_ids) is tuple and _ids(item.node_ids, "node links") == item.node_ids,
                "Invalid requirement links")
        _ensure(type(item.decision_ids) is tuple and _ids(item.decision_ids, "decision links") == item.decision_ids,
                "Invalid decision links")
        _ensure(all(node_id in engine._nodes and engine._nodes[node_id].project_id == item.project_id
                    for node_id in item.node_ids), "Foreign requirement node")
        _ensure(all(adr_id in engine._architecture_decisions and
                    engine._architecture_decisions[adr_id].project_id == item.project_id
                    for adr_id in item.decision_ids), "Foreign requirement ADR")
    adr_refs: set[tuple[str, str]] = set()
    for item in engine._architecture_decisions.values():
        _ensure(item.project_id in engine._projects, "Unknown ADR project")
        _ensure(type(item.state) is ProposalState and item.state is ProposalState.PROPOSED,
                "Non-proposed ADR state")
        _ensure(type(item.reference) is str and bool(re.fullmatch(r"ADR-[0-9]{4,}", item.reference)),
                "Invalid ADR reference")
        _ensure((item.project_id, item.reference) not in adr_refs, "Duplicate ADR reference")
        adr_refs.add((item.project_id, item.reference))
        _ensure(type(item.title) is str and _text(item.title, "ADR title", limit=300) == item.title,
                "Invalid ADR title")
        _ensure(type(item.rationale) is str and
                _text(item.rationale, "ADR rationale", multiline=True) == item.rationale,
                "Invalid ADR rationale")
        _ensure(type(item.actor) is str and _text(item.actor, "actor", limit=300) == item.actor,
                "Invalid ADR actor")
        _ensure(type(item.created_at) is datetime and item.created_at.utcoffset() == timedelta(0),
                "Invalid ADR time")
        if item.supersedes_id is not None:
            _ensure(item.supersedes_id in engine._architecture_decisions and
                    engine._architecture_decisions[item.supersedes_id].project_id == item.project_id
                    and item.supersedes_id != item.id, "Invalid ADR supersession")
    for item in engine._decision_proposals.values():
        _ensure(item.project_id in engine._projects, "Unknown proposal project")
        _ensure(type(item.state) is ProposalState and item.state is ProposalState.PROPOSED,
                "Non-proposed decision state")
        _ensure(item.node_id is None or
                (item.node_id in engine._nodes and engine._nodes[item.node_id].project_id == item.project_id),
                "Foreign proposal node")
        for field in ("actor", "action"):
            value = getattr(item, field)
            _ensure(type(value) is str and _text(value, field, limit=300) == value,
                    "Invalid proposal actor/action")
        for field, blank in (("rationale", False), ("previous_value", True), ("proposed_value", False)):
            value = getattr(item, field)
            _ensure(type(value) is str and
                    _text(value, field, allow_blank=blank, multiline=True) == value,
                    "Invalid proposal value")
        _ensure(type(item.created_at) is datetime and item.created_at.utcoffset() == timedelta(0),
                "Invalid proposal time")

    active_keys: set[tuple[str, str, DependencyKind]] = set()
    adjacent: dict[str, list[str]] = {}
    for edge in engine._dependencies.values():
        source = engine._nodes.get(edge.source_node_id)
        target = engine._nodes.get(edge.target_node_id)
        _ensure(source is not None and target is not None and
                source.project_id == edge.source_project_id and
                target.project_id == edge.target_project_id, "Invalid dependency ownership")
        _ensure(type(edge.kind) is DependencyKind and type(edge.active) is bool,
                "Invalid dependency types")
        _ensure(edge.source_node_id != edge.target_node_id, "Self dependency")
        key = (edge.source_node_id, edge.target_node_id, edge.kind)
        if edge.active:
            _ensure(key not in active_keys, "Duplicate dependency")
            active_keys.add(key)
            if edge.kind is DependencyKind.BLOCKS:
                adjacent.setdefault(edge.source_node_id, []).append(edge.target_node_id)
    # Iterative DFS, no stack overflow on deep dependency chains.
    done: set[str] = set()
    for start in adjacent:
        if start in done:
            continue
        visiting: set[str] = set()
        stack: list[tuple[str, bool]] = [(start, False)]
        while stack:
            current, exit_node = stack.pop()
            if exit_node:
                visiting.remove(current)
                done.add(current)
            elif current not in done:
                _ensure(current not in visiting, "Blocking dependency cycle")
                visiting.add(current)
                stack.append((current, True))
                for target_id in reversed(adjacent.get(current, [])):
                    if target_id not in done:
                        stack.append((target_id, False))

    _ensure(type(engine._audit) is tuple, "Invalid audit journal")
    for number, entry in enumerate(engine._audit, 1):
        _ensure(type(entry) is AuditEntry and type(entry.sequence) is int and
                entry.sequence == number, "Invalid audit sequence")
        _ensure(entry.project_id in engine._projects, "Foreign audit project")
        _ensure(type(entry.action) is str and bool(re.fullmatch(r"[a-z_]+\.[a-z_]+", entry.action)),
                "Invalid audit action")
        _ensure(type(entry.target_type) is str and entry.target_type in
                ("project", "node", "requirement", "dependency", "architecture_decision", "decision_proposal"),
                "Invalid audit target")
        _ensure(type(entry.target_id) is str and bool(re.fullmatch(r"[0-9a-f]{32}", entry.target_id)),
                "Invalid audit target identity")
        _ensure(type(entry.occurred_at) is datetime and
                entry.occurred_at.utcoffset() == timedelta(0), "Invalid audit UTC time")
        _ensure(entry.actor is None or
                (type(entry.actor) is str and _text(entry.actor, "actor", limit=300) == entry.actor),
                "Invalid audit actor")
        _ensure(type(entry.rationale) is str and
                _text(entry.rationale, "rationale", allow_blank=True, multiline=True) == entry.rationale,
                "Invalid audit rationale")
        _ensure(_valid_audit_value(entry.before) and _valid_audit_value(entry.after),
                "Invalid audit before/after")
    _verify_audit_replay(engine)


def _verify_audit_replay(engine: CommandEngine) -> None:
    """Historical before/after changes must reproduce the final canonical graph.

    This checks internal consistency, not authentication: an attacker with
    database access can rewrite a snapshot and its unsigned digest.
    """
    names = {name.removeprefix("_"): name for _, name, _ in _BUCKETS}
    type_to_bucket = {
        "project": "_projects",
        "node": "_nodes",
        "requirement": "_requirements",
        "dependency": "_dependencies",
        "architecture_decision": "_architecture_decisions",
        "decision_proposal": "_decision_proposals",
    }
    expected_types = {attr: cls for _, attr, cls in _BUCKETS}
    replay: dict[str, dict[str, object]] = {attr: {} for _, attr, _ in _BUCKETS}
    for event in engine._audit:
        attr = type_to_bucket[event.target_type]
        records = replay[attr]
        cls = expected_types[attr]
        if attr == "_nodes":
            _ensure(type(event.before) is tuple and type(event.after) is tuple,
                    "Invalid structural audit shape")
            previous = event.before
            updated = event.after
            _ensure(all(type(v) is cls for v in (*previous, *updated)),
                    "Invalid structural audit records")
            old = {v.id: v for v in previous}
            new = {v.id: v for v in updated}
            _ensure(len(old) == len(previous) and len(new) == len(updated),
                    "Duplicate audited node")
            _ensure(all(records.get(identity) == value for identity, value in old.items()),
                    "Audit before-state mismatch")
            _ensure(all(identity in old or identity not in records for identity in new),
                    "Audit omitted pre-existing node")
            _ensure(set(old).issubset(new), "Unexpected audited node deletion")
            _ensure(event.target_id in new, "Incorrect structural audit target")
            for identity, value in new.items():
                _ensure(value.project_id == event.project_id,
                        "Audit changed node outside project")
                records[identity] = value
        else:
            _ensure(type(event.after) is cls and event.after.id == event.target_id,
                    "Invalid audit after-state")
            _ensure(event.before is None or
                    (type(event.before) is cls and event.before.id == event.target_id),
                    "Invalid audit before-state")
            _ensure(records.get(event.target_id) == event.before,
                    "Audit before-state mismatch")
            _ensure(event.target_id not in records or event.before is not None,
                    "Audit duplicate creation")
            project_id = (
                event.after.id if attr == "_projects" else
                event.after.source_project_id if attr == "_dependencies" else
                event.after.project_id
            )
            _ensure(project_id == event.project_id, "Audit writes foreign project")
            records[event.target_id] = event.after
    for _, attr, _ in _BUCKETS:
        _ensure(replay[attr] == getattr(engine, attr),
                "Audit history does not reconstruct canonical records")
