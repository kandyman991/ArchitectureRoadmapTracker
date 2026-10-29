# T2.1 — Tree-first local web-shell reference

**Status:** Development PR, not independently reviewed, merged, deployed or accepted.
**Traceability:** ART-002, ART-003 (partial), ART-004 (partial), ART-006 (selection only),
ART-008 (responsive content flow only), ART-027, ART-028 and ART-030.

## Purpose and boundaries

The browser is a **projection and command client**, not a second roadmap.
The Python canonical `CommandEngine` and T1.3 reference `PersistentCommandEngine`
remain the sole source of truth. The UI never persists its own hierarchy or
manufactures statuses, reviews, approvals, PR evidence or milestone acceptance.

This prototype uses dependency-free HTML/CSS/JavaScript ES modules for a
**reversible framework evaluation**. It is not a final frontend selection; the
framework/runtime/cloud-hosting decision in `DECISIONS.md` remains open.
The thin JSON API is deliberately separate from the DOM implementation so
future authenticated cloud hosting may replace the current development server.

**Not a public cloud service:** `make_server` binds only to `127.0.0.1`.
The browser API is unauthenticated and has no project read-permission system.
It must **never** be bound to `0.0.0.0`, deployed through a public proxy, or
used with production/customer content without the T3 authentication,
authorization, tenancy, CSRF and operational review. "Cloud-ready" means the
UI/backend boundary is portable, **not** that cloud deployment is completed.

## Running the local prototype

From the repository root, using Python 3.10+:

    PYTHONPATH=src python3 -m architecture_roadmap_tracker.web \
      --db .local/tree-shell.db --demo

Visit `http://127.0.0.1:8765`. `--demo` creates **synthetic** nodes
only when the database contains no projects. Without `--demo`, start from
an empty workspace and create your own local synthetic project.

The web runtime needs Python's standard library plus a modern browser.
Node.js is used **only in CI** for pure display-model tests; no npm installs,
production dependency lock-in or build-chain changes.

## Canonical API contract

- `GET /api/workspace` returns the storage revision, projects and per-project
  **read-only preorder** derived from `project_outline`: stable ID,
  parent ID, depth, sibling position, node kind, title, archived and inherited archived state and
  whether the node has children.
- `POST /api/commands` accepts a **closed allowlist** of commands:
  `project.create`, `node.create`, `node.rename`, `node.move`,
  `node.archive` and `node.restore`. All include the current
  `expected_revision` and are routed directly to T1/T1.3 validated
  commands with SQLite persist-before-publish and the audit journal.
- A stale revision returns HTTP 409; the UI reloads before asking users
  to retry. Invalid field/type/relationship errors are rejected, not
  converted into unrecorded client-side mutations.
- The `actor` in a T2.1 audit event is a fixed string
  `prototype:unverified-local-operator`. It is **not authenticated identity**
  or a human approval.
- Strict loopback Host/Origin validation, JSON-only writes, bounded request
  bodies, static asset route allowlist, escaping via `textContent`,
  no external scripts, CSP and no-store headers reduce prototype exposure.
  These do **not** replace production authentication and permission checks.

## Interaction

- A **single primary tree** that expands and collapses at arbitrary depths.
  The browser view uses only projection rows and an ephemeral expanded-ID set.
- Click or keyboard navigate to select a node. Left/Right, Up/Down and Home/End
  operate on visible rows, preserving selected IDs across rerenders and folding.
  Selection/expanded IDs can be cached in session storage **as display
  preferences only**, never as canonical records.
- Context actions: create project/root/child/sibling, rename, reorder among
  siblings, archive and restore. All writes go to the canonical command API.
- The contextual panel currently shows **only node identity and actions**.
  It does not impersonate the full Inspector: requirement/acceptance/evidence/
  PR/review/job records and decisions are reserved for T2.2 and later.
- No fixed-height nested scrolling or forced card size. The page grows with
  content, with a responsive single-column layout on narrow screens.
  Accessibility performance at very large scale, focus restoration across
  more complex action dialogs and virtualized rendering belong to T2.3.

## Required tests and remaining gates

    PYTHONPATH=src python3 -m unittest discover -s tests -v
    node --test tests/web/*.test.mjs

Synthetic HTTP tests cover bootstrap, real validated command writes/restart,
project ownership isolation, stale write rejection, loopback/Origin enforcement,
static asset allowlist, no phantom audit on rejected mutations, and errors.
Pure JS tests cover arbitrary-depth folding, nearest-visible selection and
keyboard navigation. A browser/manual accessibility check remains important
before acceptance; passing Node unit tests is **not** proof of full UI testing.

**Merge gate:** separate-session architecture/security/data-integrity/UI review,
fix every finding, rerun required `architecture-contract` CI on the **exact
corrected final PR head**, then obtain explicit owner authorization to merge.
Green CI, draft status and PR merging cannot mark T2 accepted.
