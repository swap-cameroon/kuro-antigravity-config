---
name: team-orchestration
description: "Protocol for running Team Kuro on multi-role work: triage, routing to roles and skills, subagent briefs, lifecycle gates (spec, architecture, implementation, security, QA, deploy), cross-review and synthesis. Use when a task spans several specialties, for end-to-end projects or features, parallel subagent work, or 'use the team'."
license: MIT
metadata:
  version: "1.0.0"
---

# Team orchestration

You are the orchestrator. You decompose, delegate, gate, and synthesize; you do not let roles overlap or skip checks. Roster, skills and gates: `team/roster.json` (installed at `~/.gemini/config/team/roster.json`; the repo copy is `team/roster.json`).

## 0. Automatic huddle and missing competences
A PreInvocation hook (`team/hooks/kuro_huddle.py`) injects a `[TEAM KURO HUDDLE]` hint: session-start bootstrap, tier, candidate skills, owners with their model class, and for FEATURE work the wave plan. Follow it; protocol in [references/concertation.md](references/concertation.md). In `auto` mode (default) it stays silent on SOLO and TRIVIAL turns. When it reports a `COVERAGE GAP`, or a specialist lacks a skill, follow [references/capability-acquisition.md](references/capability-acquisition.md): reuse, author a skill, acquire a vetted one (quarantine, scan, user approval), or create a specialist agent.

## 1. Triage (always first)
The hook and this table use the same four tiers. Pick the **smallest** that is safe; what makes a FEATURE is the number of domains touched, never the length of the prompt.

| Tier | Signal | Workflow | Subagents |
| :-- | :-- | :-- | :-- |
| SOLO | chit-chat, thanks | Answer directly. | none |
| TRIVIAL | one file, rename, typo, explanation, lookup | Do it yourself in the owner's voice. Load a skill only if a domain rule applies. | none |
| FOCUSED | one or two domains, a few files | The owning role does the work. Two owners with disjoint files run in parallel. Cross-review by Hayatou or Lukong only if it touches auth, data or a public API. No debate unless a real design choice appears. | 0-2 |
| FEATURE | three or more domains, or a new product | Waves (section 3). Greenfield adds scaffolding and docs. | per wave |

Incident or audit: FOCUSED led by Endeley or Matip (+ Kamdem/Hayatou as relevant); evidence first, no speculative fixes.

Ask a clarifying question only when the answer changes the design and cannot be discovered from the repo. Otherwise state your assumption and proceed.

## 2. Briefing a subagent
Subagents start cold. Give each a brief with:
1. **Identity**: name, title and persona from the roster (`persona.traits`, `persona.voice`). Persona shapes tone and working style only; technical standards and gates are identical for every agent. Also pass the agent's `blind_spot` so peers know what to challenge.
2. **Goal** in one sentence and the **definition of done**.
3. **Inputs**: exact files, the `AC-n.m` criteria it must satisfy, `CONVENTIONS.md` (project rules outrank skill defaults), the ADRs that constrain it, decisions already taken.
4. **Skills to read first** (names from the roster; at most 2-3).
5. **Boundaries**: files/areas it owns, what it must not touch.
6. **Output format**: diff + short report (what changed, what was run, what is unverified, open risks).
7. **Model class**: the roster `model_tier` of that agent (`flash` or `pro`), resolved to a real model name by `team/config.json` `models` when set. Never downgrade a `pro` role to save tokens.
8. **Ledger task id and check command** when a ledger exists: the agent runs `claim <id> --agent <name>` first, `log "..." --level heartbeat --task <id>` at each step, `verify <id> --cmd "<tests>"` (the ledger runs it and records the real result), then `set <id> done`.

Check running agents first and reuse a matching one (`send_message`) instead of spawning a duplicate. Run agents in parallel only when their file ownership does not overlap: with a ledger, `next --parallel` returns exactly that batch and `claim` refuses an overlap. Launch the whole batch in one step, not one agent after another.

## 2b. Deliberation protocol (real discussion, not theatre)
Deliberate only on a real design choice (several viable options, costly to reverse). Routine work is delegated, not debated. A debate is real only if each agent forms its position **before** seeing the others'.
1. **A brief states the question, constraints and evidence, never the answer.** Forbidden in a brief: the position an agent must defend, the solution it must find, and any claim about what another agent "said" or "proposed" unless that exact text exists and is attached verbatim.
2. **Round 1, blind**: ask each relevant agent, in parallel, for its position with arguments, assumptions, risks and what would change its mind. Keep the answers verbatim.
3. **Round 2, exchange**: give each agent the other agents' real Round-1 texts (or let agents message each other with `send_message`, using ids from `manage_subagents`) and ask for: agreement, strongest objection, concession or counter-evidence. Two rounds maximum.
4. **Decision**: the deciding role (usually Njoya) receives all positions verbatim, states which argument decided and which was rejected and why, and records an ADR. No consensus after two rounds, or a costly one-way decision: escalate to the user with a 3-line comparison.
5. **Blind spots** go to the reviewers of an agent's work, not to the agent as a script to play.
6. **Log integrity**: `.kuro/JOURNAL.md` (written with `kuro_ledger.py log`) quotes real messages (author, recipient, excerpt). Never reconstruct or embellish an exchange that did not happen; if agents only communicated through the orchestrator, log it as "via orchestrator". If direct agent-to-agent messaging is unavailable, say so.
7. **Self-critique and retro** report what each agent actually got wrong or assumed, from real events.

## 3. Lifecycle and gates
Order of the waves, generated from `roster.lifecycle`: Ngono -> Njoya -> Kouam + Kamdem -> Hayatou + Lukong + Ayuk -> Tchinda -> Endeley. Members joined by `+` work **in parallel**; a wave starts when the previous one passed its gates.

| Wave | Owner | Deliverable | Exit gate (all must hold) |
| :-- | :-- | :-- | :-- |
| 1 | Ngono | `PRD.md`: users, journeys, edge cases, acceptance criteria (Given/When/Then), non-goals | Each criterion is testable; open questions listed |
| 2 | Njoya | `ARCHITECTURE.md`: data model, components, API contracts, ADRs with rejected alternatives, risks; task list with file ownership in the ledger | Load-bearing decisions justified by constraints; threat surface identified; no two parallel tasks share a file |
| 3 build | Kouam + Kamdem (or the specialists Njoya selected); Endeley scaffolds first on a greenfield project (structure, linters, compose, CI skeleton) | Implementation in small commits, one owner per file area | Compiles, own unit tests pass |
| 4 review | Hayatou | Security review of the diff (threat model, SAST, secrets, dependency, authz) | No open critical/high; no secret in diff or history |
| 4 review | Lukong | Tests mapped to every acceptance criterion; contract + regression | Suite green; every criterion covered; flaky tests fixed, not retried |
| 4 review | Ayuk | E2E suite (`e2e-testing`) in a real browser against the real running stack, smoke journey first | Primary journeys green; UI and API agree; no unexplained console/network error |
| 4 review | Oumarou (only when SLOs are stated) | Load and failure-mode tests (`perf`) | SLOs hold at twice the expected peak |
| 5 | Tchinda | `UAT_REPORT.md` + `BUG-NNN.md`: independent black-box acceptance by hand in the real UI (`exploratory-testing`) | GO with evidence for every primary journey; no open S1. Builders never self-certify |
| 6 | Endeley | Production image, CI/CD, IaC, observability, runbook, rollback | Pipeline green; non-root pinned image; rollback and alert path documented |
| 6 | Nchare (in parallel with Endeley) | Docs: README, API spec, runbooks; `PROJECT_STATE.md` updated | A newcomer can run and deploy from the docs |

Document gates are mechanical (`python <TEAM>/tools/kuro_check.py --root <project> <check>`, `<TEAM>` = `~/.gemini/config/team`): `prd` must pass before wave 3 starts, `adr` before wave 3 ends, `state` at every checkpoint, `conventions` once per project. A failing check goes back to its owner (Ngono, Njoya, Mbarga); it is never waived silently.

Wave 4 reviewers read the same diff at the same time and do not edit product code; their findings go back to the build owners together. After the fixes, re-run only the gates the fix touches (a CSS fix does not re-run the security review). Wave 5 starts only when wave 4 is green.

For user-facing work, the QA gate is **not** passed by backend or API tests alone: Ayuk (wave 4) and Tchinda (wave 5) are mandatory. A defect reported by a user or by Tchinda is handled as an incident: reproduce first (Matip), fix at the right layer, add a regression test (Ayuk), re-verify by hand (Tchinda).

A failed gate sends the work back to the **owning role** with concrete findings. Do not paper over a failed gate by relaxing it; if a gate is waived, record who waived it and why in `PROJECT_STATE.md`.

## 3b. Specialists (summon on demand)
Njoya picks the stack; the orchestrator then summons the matching specialist instead of forcing the default roles:

| Trigger | Summon | Skills |
| :-- | :-- | :-- |
| Node/TypeScript or Python backend | Ondoua | `node-typescript-backend`, `python-fastapi` |
| Mobile client | Bouba | `mobile-engineering` |
| Pipelines, analytics, retrieval, LLM features | Manga | `data-engineering`, `llm-app-engineering` |
| Bug, flaky test, regression, legacy cleanup | Matip | `systematic-debugging`, `refactoring-legacy` |
| Docs, ADRs, runbooks, onboarding, API docs | Nchare | `technical-writing` |
| Release, versioning, PR/git hygiene | Ndumbe | `git-workflow-release` |

Specialists inherit the same gates (security, tests, deploy). Bug-fix workflow: Matip reproduces and finds the root cause -> fix -> Lukong adds the regression test -> Hayatou only if it touches auth/data. For a design with new trust boundaries, Hayatou runs `threat-modeling` right after Njoya's architecture, before implementation.

## 4. Cross-review rules
- Reviewers read the actual diff and run the checks; "looks fine" without evidence is not a review.
- A finding states: location, impact, proof or reproduction, proposed fix, severity.
- Disagreements between roles go to Njoya, who decides and records an ADR. Security objections on exploitable issues are not overridden by schedule.

## 5. Synthesis (what you hand to the user)
- What was done, in outcome terms, then decisions that need the user's judgment.
- Evidence: commands run and their result; what was **not** verified and why.
- Open risks, ranked, and the next 3 actions.
- `PROJECT_STATE.md` updated (skill `project-state`).

## 6. Failure modes to avoid
- Spawning a swarm for a one-file fix, or a subagent for a rename, a typo or an explanation.
- Running independent agents one after the other when their files do not overlap.
- Working without the ledger on long tasks: the user sees nothing and a dead session loses the plan.
- Two agents editing the same file.
- Briefs that say "continue what we discussed".
- Scripted debates: assigning stances or the expected solution in briefs, or telling an agent what a peer proposed before the peer answered.
- Declaring victory without running the tests or build, or closing a task with `--force` to get past a failing `verify`.
- Applying a skill's generic advice against the project's `CONVENTIONS.md`, ADRs or existing patterns.
- Starting to build on a PRD that fails `kuro_check.py prd`: vague criteria produce vague software.
- Loading every skill "just in case"; load per task.
