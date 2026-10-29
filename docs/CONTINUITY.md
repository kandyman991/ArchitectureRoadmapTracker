# GitHub-based continuity and release governance

This file defines an operational process. It is **not** evidence that the app or any automation is deployed.

## Session start

1. Read `AGENTS.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `DECISIONS.md`.
2. Read `CHAT_HANDOFF.md` and `docs/CHECKPOINTS.md` for curated intent, decisions and outstanding work.
3. Fetch live `main` SHA, open PRs, issues and CI; compare with curated checkpoints. The live API wins for current status.
4. Pick one submilestone and declare exact scope, acceptance tests, PR branch, shared-file coordination and non-goals.
5. Never repeat assumptions or report unverified milestones as complete.

## During work

- Branch from latest `main`; no direct pushes to `main`. Keep PR scoped to one small submilestone.
- Update tests alongside changes. Every claim of verification must cite exact commit SHA, check run and observed result; a pending check is not passed.
- Link requirement `ART-xxx`, implementation evidence and review findings. Reject stale findings/CI from prior heads.
- Require a separate independent review and no unapproved merge. If owner is sole collaborator, record that independent AI review does **not** replace GitHub's required human review setting; account/plan limitations may require adding a reviewer.
- Any deviation in a locked architectural boundary requires proposed ADR approval first.

## Handoff

Curate `CHAT_HANDOFF.md` and `docs/CHECKPOINTS.md` at milestone/PR boundaries. Include scope completed, exact PR and revision, validated checks, unresolved blockers and next command; avoid constantly rewriting these files for no-op events. Do not auto-generate claims of architectural truth.

## GitHub settings requiring an authorized administrator

In `Settings → Rules → Rulesets` (or branch protection for `main` where available), enable:
- Require a pull request before merging; no direct pushes and no force pushes or deletions.
- Require at least one approved independent review and dismiss stale approvals on new commits where available.
- Require successful status check **`architecture-contract`** from the `Architecture contract` workflow, and require branch up to date before merge (when supported).
- Block unresolved conversations; limit bypass permissions and administrators according to supported account/repository rules.
- Do not turn on an overly broad required check that does not run on every PR; re-evaluate required checks when CI changes.
- Configure repository Actions permissions as read-only by default and limit approved action provenance.

**Important:** Public personal repositories, plan types and ruleset UI availability vary. Inspect actual effective protection before claiming enforcement; a policy described here is NOT equivalent to a configured GitHub rule.

## Initial work model

M0 docs and local offline checks; no tokens or external dependencies. Subsequent milestones add real automated tests, code-quality gates, job and security checks. GitHub-hosted Actions minutes, rate limits and future cloud runner costs remain subject to the provider's plan.
