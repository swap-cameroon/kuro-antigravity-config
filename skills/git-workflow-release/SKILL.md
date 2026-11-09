---
name: git-workflow-release
description: "Git branching, Conventional Commits, PR hygiene, semantic versioning, changelogs and release checklists. Use when committing, opening or reviewing PRs, cutting a release, tagging, or fixing git history."
license: MIT
metadata:
  version: "1.0.0"
---

# Git workflow & release

## Branching
- Trunk-based by default: short-lived branches (<2 days) from `main`, `type/short-description` (`feat/login-lockout`), merged by PR with CI green. Long-lived `release/x.y` branches only when supporting multiple versions.
- `main` is always releasable; protect it (required checks, review, no force-push).
- Incomplete work ships behind a feature flag, not a long branch.

## Commits (Conventional Commits)
`type(scope)!: imperative summary` (<=72 chars) + body explaining **why**. Types: `feat`, `fix`, `perf`, `refactor`, `docs`, `test`, `build`, `ci`, `chore`, `revert`. `!` or a `BREAKING CHANGE:` footer marks a major change. One logical change per commit; every commit builds and passes tests. Never commit secrets, generated artifacts or large binaries.

## Pull requests
- Small (<400 changed lines when possible). Title in commit style. Body: what, why, how tested, risks/rollback, linked issue/AC ids, screenshots for UI.
- Self-review the diff first. Checklist: tests added/updated - docs/changelog updated - migrations reversible - no TODOs without issue - no debug code - security gate for auth/data changes.
- Reviewers: correctness and risk first, style last (automate style). Block only on real defects; label nits. Merge strategy: squash for noisy branches, rebase/merge for curated history - pick one per repo.

## Versioning & changelog
- SemVer `MAJOR.MINOR.PATCH`: breaking / additive / fix. Pre-releases `-rc.1`. Derive the bump from commit types (release-please, semantic-release, git-cliff, changesets) rather than by hand.
- Keep `CHANGELOG.md` (Keep a Changelog sections: Added/Changed/Deprecated/Removed/Fixed/Security) written for users, not a commit dump.

## Release checklist
1. `main` green; dependency and secret scans clean (`dependency-audit`, `secrets-scanner`).
2. Version bump + changelog generated; migrations reviewed and reversible; feature flags set.
3. Tag annotated and signed if policy: `git tag -a v1.4.0 -m "v1.4.0"`; push tag; CI builds the artifact **from the tag** once, promotes the same artifact across environments.
4. Deploy with progressive rollout (canary/blue-green); watch SLO dashboards (`sre-engineer`, `observability`); documented rollback.
5. Publish release notes; announce; update `PROJECT_STATE.md`.
6. Hotfix: branch from the tag, fix + test, release patch, merge back to `main`.

## Recovery recipes (non-destructive first)
- Undo a pushed commit: `git revert <sha>` (not reset). Wrong branch: `git switch -c new` then reset the old one only if unpushed.
- Lost work: `git reflog`. Secret leaked: **rotate the secret first**, then rewrite history (`git filter-repo`) and force-push only with team agreement.
- Ask before any `reset --hard`, `push --force` (use `--force-with-lease`), or `clean -fd`.
