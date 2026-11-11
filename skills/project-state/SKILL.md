---
name: project-state
description: "Create, resume from and update PROJECT_STATE.md, the Git-tracked handover file that lets a new session or colleague continue without re-reading the codebase. Use at session start when it exists, when starting or onboarding a project, after a milestone or decision, before ending a session, or when asked to hand over, resume or checkpoint."
license: MIT
metadata:
  version: "1.0.0"
---

# Project state (handover protocol)

`PROJECT_STATE.md` at the repo root is the single source of truth for where the project stands. It is written for a human and an agent reading it cold. Template: [templates/PROJECT_STATE.md](templates/PROJECT_STATE.md).

## Resume (session start)
1. Read `PROJECT_STATE.md`. Do not crawl the repo unless the file is missing or stale.
2. **Verify freshness cheaply**: compare the recorded branch and `Last verified commit` with `git rev-parse --short HEAD` and `git status --short`. If HEAD has moved past it, read `git log --oneline <recorded>..HEAD` and reconcile the file before trusting it.
3. Greet in two lines: last completed milestone and in-flight task; then list the next 3 actions from the file. Start on action 1 unless the user redirects.

## Create (no file yet, project is non-trivial)
Fill the template from evidence only: `git log`, manifest files (package.json, pom.xml, pyproject...), README, CI config. Mark anything you could not confirm as `UNVERIFIED` rather than guessing. Commit it with the work that it describes.

## Update (checkpoint)
Update when a milestone ends, a decision is taken, a blocker appears or clears, or the session closes. Keep edits surgical:
- Move finished items to Completed with the commit hash.
- Rewrite **Current in-flight task** precisely (file, function, what is half done, how to continue).
- Re-rank the roadmap: `P0` = blocks other work or the release (auth, schema, API contract, security finding); `P1` = needed for completeness; `P2` = nice to have.
- Record decisions and gotchas in **Invariants & gotchas** with the reason.
- Refresh `Last verified commit` and the date.

## Project conventions (what makes the output yours, not generic)
`CONVENTIONS.md` at the repo root records how **this** project is written: stack, verified commands, naming, architecture rules, review rules, things never to do. It outranks the generic advice of any skill, and every agent reads it before touching code.
- Missing on a non-trivial project: draft it from evidence with `python <TEAM>/tools/kuro_check.py --root <project> conventions --init` (reads manifests, lockfiles, linters, CI, commit history). It marks commands `UNVERIFIED` and leaves `TODO(user)` lines.
- Run each detected command once, then remove the `UNVERIFIED` mark. Ask the user the `TODO(user)` questions in one batch (max 5); never invent a team rule.
- When the user corrects a style or architecture choice twice, add the rule here so it is not corrected a third time.

## Decisions
One ADR per load-bearing decision in `docs/adr/NNNN-title.md`, from [templates/ADR.md](templates/ADR.md): status, context, decision, rejected alternatives, consequences. Link them from section 1 of `PROJECT_STATE.md`; never copy them.

## Mechanical check
`python <TEAM>/tools/kuro_check.py --root <project> state` fails when the file is still a template, holds a secret, has no concrete next action, or names a commit the repo does not know; it warns with the exact `git log` command when HEAD has moved. `... adr` and `... conventions` check the two files above; `... all` runs everything. `<TEAM>` is `~/.gemini/config/team`. Run it at session start and before each checkpoint; fix what fails instead of explaining it away.

## Quality bar
- Under ~200 lines; link to ADRs/PRD instead of copying them.
- **Never store secrets**. Name the variable and where it is obtained (vault, `.env.example`), never its value.
- Run commands must be copy-pasteable and were actually run; note the OS/tool versions that matter.
- No vague items ("improve performance"). Each task is a verifiable outcome with an owner role.
- If a statement may have gone stale, say so with a date.
