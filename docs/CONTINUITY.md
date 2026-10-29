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
- Seek a separate independent reviewer; when unavailable, record the reviewer's identity and limitation honestly. An author/self-review is not independent. The current solo-maintainer ruleset requires **zero GitHub approvals**, so review quality is a documented process responsibility, not a GitHub-enforced approval. No merges without explicit owner authorization.
- Any deviation in a locked architectural boundary requires proposed ADR approval first.

## Handoff

Curate `CHAT_HANDOFF.md` and `docs/CHECKPOINTS.md` at milestone/PR boundaries. Include scope completed, exact PR and revision, validated checks, unresolved blockers and next command; avoid constantly rewriting these files for no-op events. Do not auto-generate claims of architectural truth.

## GitHub settings requiring an authorized administrator

In `Settings → Rules → Rulesets` (or branch protection for `main` where available), enable:
- Require a pull request before merging; no direct pushes and no force pushes or deletions.
- The solo-maintainer ruleset may use zero GitHub approvals to avoid deadlock; seek separate independent review as a process and document reviewer limitations. Increase required approvals when independent collaborators are available. Dismiss stale approvals on new commits where available.
- Require successful status check **`architecture-contract`** from the `Architecture contract` workflow, and require branch up to date before merge (when supported).
- Block unresolved conversations; limit bypass permissions and administrators according to supported account/repository rules.
- Do not turn on an overly broad required check that does not run on every PR; re-evaluate required checks when CI changes.
- Configure repository Actions permissions as read-only by default and limit approved action provenance.

**Verified on 2026-10-29:** [Main Branch Protection](https://github.com/kandyman991/ArchitectureRoadmapTracker/rules/26127238) was active on the default branch: PR required, zero mandatory GitHub approvals, dismiss stale reviews, resolve conversations, strict required status check `architecture-contract`, block deletion and force push, and no bypass actors. Inspect live settings again each session. The contract workflow checks the documentation baseline, not future application architecture or independent review.

**Important:** Ruleset state and available controls may change. A documented policy is not evidence of effective GitHub protection.

## Initial work model

M0 docs and local offline checks; no tokens or external dependencies. Subsequent milestones add real automated tests, code-quality gates, job and security checks. GitHub-hosted Actions minutes, rate limits and future cloud runner costs remain subject to the provider's plan.
