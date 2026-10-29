# T1.1 — Canonical project/node tree

**Scope:** pure, dependency-free, in-memory Python reference core. This is not the web app, persistence, GitHub integration, acceptance engine, audit history, Job Center or ChatGPT adapter.

## Requirements and boundaries

- Structural subset of ART-001 (multiple isolated projects), ART-002 (one ordered unlimited-depth tree), ART-004 (validated create/rename/move/reorder/archive/restore).
- Begins the command API foundation for ART-030, but UI/CLI external command sharing is not yet implemented.
- T1.2 will provide dependencies, decisions and audit; T1.3 storage, versioning, migrations and concurrency; T2 the UI.
- Do not infer evidence, review status or milestone completion from any node state; T4 owns that engine.

## Canonical model

- Frozen typed Project and RoadmapNode data, with stable UUID-based opaque IDs.
- Every node belongs to exactly one project; parent_id and contiguous zero-based sibling position are authoritative. No duplicate outline or status tree.
- Node kinds are descriptive (milestone, submilestone, task, other); child nesting is not restricted by kind or maximum depth.
- Ordered children and preorder traversal are **derived** from canonical nodes, never separately stored.
- Commands stage changes in a private copy, check foreign parents, orphans, cycles and sibling positions, then replace the canonical dictionary only on success.
- Moving a node preserves its subtree and IDs. The position parameter is an index in the **final** sibling list; omitted position means append.
- A parent archive is effective for descendants; individually archived descendants stay archived after restoring the parent. Archived subtrees remain present in the canonical tree.

## Explicit limitations

- State is process-local only. Restarting the engine discards data. Do not deploy as a durable multi-user service.
- No locks or concurrent editors, event log, authentication, permissions or persisted rollback. These need separate milestones, not undocumented shortcuts.
- Repository bindings are strings, not authenticated GitHub connections.
- Python stdlib is used to exercise invariants, not to approve a future web UI or backend framework/hosting choice.
- Full-state structural validation and derived child lookup are intentionally simple; large-tree performance must be profiled before production.

## Regression checks

Synthetic tests cover 1,500 nested levels, 300 siblings, stable IDs including simulated collision, deterministic insertion/reordering, atomic rejection of cycles and illegal positions, cross-project isolation, immutable snapshots, subtree preservation and archive inheritance.

Run: PYTHONPATH=src python3 -m unittest discover -s tests -v

The existing mandatory architecture-contract CI now imports the source tree to execute these regressions on every PR. A green CI run is not independent design review or final T1 acceptance.
