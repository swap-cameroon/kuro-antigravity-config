---
name: team-reporting
description: "Keep a crash-proof task ledger, progress journal and notifications for long multi-agent work, and prepare handoffs to other agentic tools (Claude Code, Codex, opencode). Use for long tasks, 'keep me posted', quota or session-loss risk, or when work must be resumed or split elsewhere."
license: MIT
metadata:
  version: "1.0.0"
---

# Team reporting (Mbarga, the reporter)

Goal: the user always knows where the work stands, and nothing is lost if the session dies, the token quota runs out, or the work moves to another tool. State lives **in the project** (`<project>/.kuro/`), written by a script, not by memory.

Ledger tool: `python <TEAM>/tools/kuro_ledger.py --root <project> <command>` where `<TEAM>` is `~/.gemini/config/team` (repo copy: `team/`). Never hand-edit `tasks.json`.

## Setup (once per project, before work starts)
1. `init --project "<name>"`.
2. Turn the plan into tasks: `add --id T-001 --title "..." --owner <role> --deps T-000 --acceptance "..." --files a,b --size S|M|L --portable yes|no --skills s1,s2`.
   - **Portable = yes** only if the task is self-contained: bounded files, testable acceptance criteria, no live multi-agent debate, no interactive secrets. Otherwise `--portable no --needs subagents|secrets|browser`.
   - Small tasks (an hour or less), one owner per file area, explicit dependencies.
   - **Always list `--files`**: it is what lets the ledger run tasks in parallel safely.
3. Tell the user how to follow the work live, in a second terminal: `python <TEAM>/tools/kuro_ledger.py --root <project> watch` (who is doing what, for how long, last heartbeat, blocked, next, journal tail). Files: `.kuro/STATUS.md` (dashboard) and `.kuro/JOURNAL.md` (timeline).

## Parallel work (one owner per file, visible to the user)
1. `next --parallel` lists the runnable tasks that share no file with each other or with work in progress, with owner and model class. Launch that whole batch at once.
2. Each agent takes its task with `claim T-001 --agent <name>`. The ledger refuses if another agent holds it or if a running task touches the same files, so two agents never edit one file.
3. While working: `log "<step, progress>" --level heartbeat --task T-001 --agent <name>` at each step; the live board shows it.
4. When verified: `set T-001 done --agent <name> --note "result" --commit <sha>`; then run `next --parallel` again for the next batch.

State files have one job each: `.kuro/` is the live task state (minutes), `PROJECT_STATE.md` is the durable handover (milestones, decisions, run commands). Do not copy task lists into `PROJECT_STATE.md`; link to `.kuro/STATUS.md`.

## Write-ahead rule (what makes it crash-proof)
- **Before** starting a task: `claim T-001 --agent <name> --note "intent / where I will start"` (or `set T-001 in_progress`).
- **After** finishing: `set T-001 done --note "result" --commit <sha>` (run only after tests were really executed).
- Any task left `in_progress` after a crash has a note saying where it started; the next session verifies the repo state before trusting it.
- Decisions, blockers, gate results, errors: `log "<fact>" --level decision|blocker|error|milestone`. Facts only, what really happened.

## Notifications
`set done|blocked` and `log` with level milestone, done, blocker, error, quota, decision notify automatically per `team/config.json` (`reporter`): local toast and journal by default; `ntfy` (phone push) and `webhook` are **opt-in** because the message leaves the machine. Messages are redacted (keys, tokens, passwords) and capped at 240 chars. Non-urgent notifications are batched (`min_interval_seconds`); blockers, errors, quota and done are never delayed.
Notify on: milestone reached, gate passed/failed, decision needed from the user, blocked, error, quota risk, task done. Do **not** notify per tool call.

## Long-running work
- Heartbeat: `log "<what is running, progress, ETA if known>" --level heartbeat --task <id>` at each task boundary and at least every ~15 tool calls or ~10 minutes of wall-clock work.
- Run long commands in the background with a log file and poll it; report the outcome, not the wait.
- A bulletin to the user is 4 lines: **done** since last bulletin, **now**, **next**, **blocked/needs you**.

## Quota or session risk (token exhaustion cannot be predicted: assume it can happen any time)
On any sign of pressure (HTTP 429, RESOURCE_EXHAUSTED, "quota", sharply slower or truncated answers) or before a very long operation:
1. `log "quota risk: <context>" --level quota`.
2. Update every `in_progress` task note with the exact stopping point and next step.
3. `handoff --all-runnable --inline-skills` to prepare packets for portable tasks.
4. Tell the user which tasks can be launched elsewhere and the exact commands (printed by `handoff`).

## Handoff to another agentic tool
- `handoff T-003` or `handoff --all-runnable [--tool claude|codex|opencode|agy|all] [--inline-skills]` writes `.kuro/handoff/<id>.md`: goal, files to read, acceptance criteria, house rules, playbook skills (optionally inlined), how to record the result, plus launch commands for Claude Code, Codex, opencode and agy.
- Tasks that touch the same files are flagged: run them one after the other, never in parallel in different tools.
- Verify the CLI flags for permissions/model with `<tool> --help`; the launch lines are a starting point, not a guarantee.
- Results coming back: the other tool runs `set <id> done --note ...` (or writes `.kuro/handoff/<id>.result.md`). The reporter reviews the diff and the test output before accepting `done`.
- `.kuro/RESUME.md` is the entry point for a fresh session of any tool.

## Honesty
Journal and status contain only observed events. "Done" means verified (tests/build run), not "written". If a notification channel failed or is not configured, say so.
