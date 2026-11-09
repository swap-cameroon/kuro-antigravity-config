# Concertation: how the team answers every instruction

Triggered automatically: the PreInvocation hook `team/hooks/kuro_huddle.py` injects a `[TEAM KURO HUDDLE]` message before each turn with a tier, candidate skills and suggested participants. Follow it; if it is absent (hook not installed), apply the same triage yourself. Mode and limits come from `team/config.json` (`concertation`: always | auto | off).

## Session start (first turn only)
1. Read `team/roster.json` and `PROJECT_STATE.md` (skill `project-state`); greet in two lines (last milestone, in-flight task) and give the next 3 actions.
2. Do **not** spawn all agents. Instantiate lazily on first need and reuse: run `manage_subagents list` before creating anyone.

## Per-instruction tiers
| Tier | When | What the team does | Cost |
| :-- | :-- | :-- | :-- |
| SOLO | chit-chat, thanks, trivial lookups | The most relevant role answers after a quick self-check. No subagents. | ~0 |
| FOCUSED | one domain or 1-2 owners | Consult the 1-2 relevant roles as real subagents (blind position, then one exchange if they disagree). Reply with their input and name who contributed. | low |
| FEATURE | several domains, new project/feature, architecture | Full deliberation (SKILL.md section 2b), gates, ADRs, `PROJECT_STATE.md` update. | high |

Escalate the tier when you discover hidden scope (auth, data model, public API, money, personal data). De-escalate when the hint over-triggered; say so in one line.

## Running a consultation
1. **Frame** the instruction as a question + constraints + evidence (files, errors, decisions). Do not include the answer or a peer's position.
2. **Select participants** from the hint (max `max_participants`), then add Njoya to arbitrate and Hayatou/Lukong as gates if code changes. Prefer an existing live subagent over a new one.
3. **Blind round** in parallel: each participant returns position, arguments, risks, assumptions, what would change its mind (short).
4. **Exchange** only if positions differ or a gate objects: relay the real texts (or let agents `send_message` each other), max `max_rounds`.
5. **Synthesize** for the user: recommendation first, then who said what in one line each, open disagreements, what was executed vs not. Keep the user's language; stay concise.
6. **Act**: implementation goes to the owning role; gates before "done".

## Budget rules
- Never run FEATURE deliberation for a SOLO/FOCUSED question; the hint can over-trigger, judgement wins.
- Reuse context: pass summaries and file paths, not whole conversations.
- Stop an exchange that is not converging after `max_rounds`: escalate to the user with a 3-line comparison.

## Integrity
Log only real events (who messaged whom, excerpt). If agents were not able to talk directly, say "relayed by orchestrator". Personas affect tone only.
