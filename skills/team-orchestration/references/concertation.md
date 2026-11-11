# Concertation: how the team answers every instruction

Triggered automatically: the PreInvocation hook `team/hooks/kuro_huddle.py` injects a `[TEAM KURO HUDDLE]` message with a tier, candidate skills and owners. Follow it; if it is absent (hook not installed, or `auto` mode on a SOLO/TRIVIAL turn), apply the same triage yourself. Mode and limits come from `team/config.json` (`concertation`: `auto` (default) | `always` | `off`).

## Session start (first turn only)
1. Read `team/roster.json` and `PROJECT_STATE.md` (skill `project-state`); greet in two lines (last milestone, in-flight task) and give the next 3 actions.
2. Do **not** spawn all agents. Instantiate lazily on first need and reuse: run `manage_subagents list` before creating anyone.

## Per-instruction tiers
| Tier | When | What the team does | Cost |
| :-- | :-- | :-- | :-- |
| SOLO | chit-chat, thanks | Answer directly. No subagents. | ~0 |
| TRIVIAL | rename, typo, explanation, lookup, one-file edit | Do it yourself in the owner's voice. No subagents, no debate. | ~0 |
| FOCUSED | one or two domains | The owning role does the work (one subagent only if it saves context; two owners with disjoint files in parallel). Cross-review by Hayatou or Lukong only when auth, data or a public API changes. Consult (below) only on a real design choice. | low |
| FEATURE | three or more domains, new product | Waves from `roster.lifecycle` (SKILL.md section 3), parallel inside a wave, ledger and live board, ADRs, `PROJECT_STATE.md` update. | high |

How the hook decides: roster `triggers` name the members concerned, each member has a `domain`, and the tier follows the number of distinct domains. Prompt length does not count. Escalate when you discover hidden scope (auth, data model, public API, money, personal data). De-escalate when the hint over-triggered; say so in one line.

## Running a consultation (only for a real design choice)
1. **Frame** the instruction as a question + constraints + evidence (files, errors, decisions). Do not include the answer or a peer's position.
2. **Select participants** from the hint (max `max_participants`), then add Njoya to arbitrate and Hayatou/Lukong as gates if code changes. Prefer an existing live subagent over a new one.
3. **Blind round** in parallel: each participant returns position, arguments, risks, assumptions, what would change its mind (short).
4. **Exchange** only if positions differ or a gate objects: relay the real texts (or let agents `send_message` each other), max `max_rounds`.
5. **Synthesize** for the user: recommendation first, then who said what in one line each, open disagreements, what was executed vs not. Keep the user's language; stay concise.
6. **Act**: implementation goes to the owning role; gates before "done".

## Budget rules
- Never run FEATURE deliberation for a SOLO/TRIVIAL/FOCUSED question; the hint can over-trigger, judgement wins.
- Give each subagent the roster `model_tier` (`flash` for tests, docs, releases, reporting; `pro` for architecture, security, code, debugging).
- Independent work is launched as one parallel batch (`kuro_ledger.py next --parallel`), never serially.
- Reuse context: pass summaries and file paths, not whole conversations.
- Stop an exchange that is not converging after `max_rounds`: escalate to the user with a 3-line comparison.

## Integrity
Log only real events (who messaged whom, excerpt). If agents were not able to talk directly, say "relayed by orchestrator". Personas affect tone only.
