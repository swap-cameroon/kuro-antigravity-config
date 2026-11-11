# Team Kuro - Antigravity multi-agent configuration

A portable, versioned setup for **Google Antigravity (`agy`)**: a 17-agent engineering team (9 core, 7 on-demand specialists, 1 support) that picks the smallest safe workflow for each instruction, runs independent work in parallel waves, shows the user a live board of who is doing what, and keeps a handover so any session (or colleague) resumes instantly. 53 skills are loaded on demand.

## What you get

| Piece | Where | Purpose |
| :-- | :-- | :-- |
| Team rules (always on) | `plugins/team-kuro/` | Roles, tiers, parallel waves, honesty rules |
| Token rules (always on) | `plugins/token-optimization/` | Output/read/command discipline, model routing |
| Skills (on demand) | `skills/` | Domain playbooks - see [docs/SKILLS.md](docs/SKILLS.md) |
| Team roster | `team/roster.json` | Single source of truth: skills, gate, domain, model class, routing triggers, lifecycle waves |
| Huddle hook | `team/hooks/kuro_huddle.py` | Routes each instruction to a tier and its owners, with zero model tokens |
| Ledger and live board | `team/tools/kuro_ledger.py` | Task claims, file-overlap guard, heartbeats, `watch`, handoff packets |
| Handover | `skills/project-state/` | `PROJECT_STATE.md` template + resume/update protocol |

Design rule: **always-loaded files stay tiny; detail lives in skills** that are read only when the task needs them.

## Performance budget (measured, enforced in CI)

Estimated with 1 token ~ 4 characters (`python scripts/validate.py --report`):

| | Initial import | Now |
| :-- | --: | --: |
| Always-on rules (every turn) | ~2,250 | ~1,140 |
| Skill names + descriptions (every turn, if your host lists them) | ~3,880 | ~3,900 (53 skills instead of 35) |
| **Baseline per turn** | **~6,130** | **~5,040 (-18%)** |
| Heaviest SKILL.md on activation | ~8,070 | ~5,810 |

The baseline is the small part of the bill. What costs most is a subagent started for nothing, so the huddle hook never asks for one on a rename, a typo, an explanation or a lookup, and in the default `auto` mode it injects nothing at all on those turns.

How: oversized skills (`secure-by-design-coding`, `angular-structure`, `angular-security`, `security-auditor`, `perf`, `code-reviewer-angular`) keep their core rules in `SKILL.md` and expose the rest as `references/*.md` behind a "Load on demand" index; content is moved verbatim, never rewritten. Descriptions were tightened while keeping their routing triggers. CI fails if the always-on rules exceed 1,200 tokens, descriptions exceed 3,900 tokens in total, or a description exceeds 520 characters, and warns when a `SKILL.md` exceeds ~3,500 tokens.

## Team

| Member | Role | Core skills | Gate they enforce |
| :-- | :-- | :-- | :-- |
| **Ngono** | Product & domain strategy | `product-requirements`, `spec-miner` | Acceptance criteria exist and are testable |
| **Njoya** | Architecture & critical review | `first-principles`, `system-design-architect` | ADRs with rejected alternatives |
| **Kouam** | UI/UX engineering | `angular-*`, `react-nextjs`, `ui-design-a11y` | WCAG 2.2 AA, safe DOM |
| **Kamdem** | Backend & DBA | `spring-data-jpa`, `postgres`, `api-design`, `backend-performance-review` | Reversible migrations, explain plans |
| **Hayatou** | Security | `security-auditor`, `threat-modeling`, `llm-sast-scanner`, `secure-by-design-coding`, `secrets-scanner` | No open critical/high, no secrets |
| **Lukong** | QA lead | `test-strategy`, `spring-testing`, `api-contract-testing`, `code-reviewer` | Every criterion has a test |
| **Ayuk** | E2E & UI tests (real browser) | `e2e-testing` | Journeys green on the real stack |
| **Tchinda** | Independent UAT / exploratory | `exploratory-testing` | Hand-run journeys, no open S1, GO/NO-GO |
| *Oumarou* | Load & resilience | `perf` | SLOs hold at 2x peak |
| **Endeley** | DevOps, cloud, SRE | `devops-engineer`, `cloud-architect`, `sre-engineer`, `observability` | Green pipeline, rollback documented |
| *Ondoua* | Node/TS and Python backends | `node-typescript-backend`, `python-fastapi` | Strict typing, boundary validation |
| *Bouba* | Mobile (Flutter, RN, native) | `mobile-engineering` | Keychain/Keystore, staged rollout |
| *Manga* | Data & AI | `data-engineering`, `llm-app-engineering` | Idempotent jobs, LLM regression evals |
| *Matip* | Debugging & refactoring | `systematic-debugging`, `refactoring-legacy` | Reproduce before fix, behaviour preserved |
| *Nchare* | Documentation & DX | `technical-writing` | Every documented command was run |
| *Ndumbe* | Release & git | `git-workflow-release` | Green main, SemVer matches changes, rollback |
| *Mbarga* | Reporter & continuity | `team-reporting` | Ledger written before and after each task |

Each agent has a Cameroonian name and a persona drawn from the heritage it honours (traits, voice and a *blind spot* that peers challenge); the full profiles are in [docs/TEAM.md](docs/TEAM.md). Personas shape tone and working style only: technical standards and gates are identical for everyone, and they make no claim about real people. Edit `team/roster.json` to adjust any name or persona, then regenerate the docs.

Lifecycle, in waves (members joined by `+` work in parallel): Ngono -> Njoya -> Kouam + Kamdem -> Hayatou + Lukong + Ayuk -> Tchinda -> Endeley. Security, tests and E2E review the same diff at the same time instead of queuing; specialists (italic) join the build wave when Njoya selects them, and Oumarou joins the review wave when SLOs are stated. The order lives in `team/roster.json` (`lifecycle`) and CI checks that the rules, this README and `skills/team-orchestration` repeat it exactly.

## Install

Windows (PowerShell):
```powershell
git clone https://github.com/swap-cameroon/kuro-antigravity-config.git
cd kuro-antigravity-config
powershell -ExecutionPolicy Bypass -File .\install.ps1 -DryRun   # preview
powershell -ExecutionPolicy Bypass -File .\install.ps1           # install
```
macOS / Linux:
```bash
./install.sh --dry-run && ./install.sh
./install.sh --enable-team-hook --enable-interceptor   # optional hooks, same as the PowerShell switches
```

The installer is **non-destructive**:
- validates the repo first (`scripts/validate.py`);
- backs up replaced folders to `<target>/.kuro-backup/<timestamp>` (last 3 kept);
- **never overwrites** `config.json`, `hooks.json`, `mcp_config.json` - it only creates them when missing;
- keeps your tuned `team/config.json` across installs;
- removes legacy duplicates and skills that a previous install shipped but the repo dropped (tracked in `.kuro-manifest`); skills you added yourself are never touched;
- verifies every skill and plugin landed, and exits non-zero on failure.

Optional prompt firewall (blocks vague or runaway prompts before they burn tokens):
```powershell
.\install.ps1 -EnableInterceptor    # merges a PreInvocation hook into hooks.json, keeps existing hooks
```

## Usage guide

### 1. First run
1. Install with the team hook: `.\install.ps1 -EnableTeamHook` (or `./install.sh --enable-team-hook`), then restart `agy`.
2. Open your project and type your request in plain language, French or English. You never have to name an agent or a skill: the hook routes for you.
3. On the first turn the team reads `PROJECT_STATE.md` if it exists and greets you in two lines with the next 3 actions. On a non-trivial project without one, it creates it.

Upgrading from an earlier version: the installer keeps your existing `~/.gemini/config/team/config.json`. If it still says `"concertation": "always"`, change it to `"auto"` to get the cheaper behaviour described below.

### 2. What happens to your instruction
| You type | Tier | What you get |
| :-- | :-- | :-- |
| `merci` | SOLO | a direct answer |
| `renomme la variable x en total dans utils.py`, `explain this function`, `fix the typo in the README` | TRIVIAL | the edit or the answer, no subagent, nothing injected after the first turn |
| `pourquoi ce test échoue ? NullPointerException ...` | FOCUSED | Matip reproduces and fixes; one owner, no debate |
| `ajoute un endpoint REST de réservation avec Spring et Postgres` | FOCUSED | Kamdem does it; Hayatou or Lukong review only if auth, data or a public API changes |
| `crée une application de réservation avec frontend Angular, backend Spring, auth JWT et déploiement` | FEATURE | PRD, architecture, parallel build, parallel review gates, UAT, deploy |

The hint is advisory. If the team over- or under-reacts, say so (`fais-le directement`, `use the whole team`): judgement wins over the hint, and the orchestrator escalates by itself when it finds hidden scope (auth, data model, public API, money, personal data).

### 3. Follow the work live
For FEATURE work, and whenever a subagent runs, the team keeps a ledger in `<project>/.kuro/`. Open a second terminal:
```bash
python ~/.gemini/config/team/tools/kuro_ledger.py --root <project> watch
```
```text
TEAM KURO - Demo   2026-11-11 10:42:06
[#######-----------------------] 1/4 done (25%)

NOW (agent | task | running for | last sign of life)
  > Kamdem    T-1     schema                3m12s   8s ago  migration 2/5 applied

NEXT (* = can start in parallel right now)
  * T-5     Nchare    API docs
    T-3     Kamdem    seed data

LAST DONE
  v T-2     Kouam     login page
```
`*` marks tasks that can start right now without touching a file someone else is editing. A task with no heartbeat for a long time is the one to ask about. Options: `--interval 5` (refresh period), `--journal 20` (more history), `--once` (print and exit). The same information is in `.kuro/STATUS.md` if you prefer a file.

### 4. Ask for parallel work
Say it in your request (`en parallèle`, `in parallel`) or let a FEATURE run. The orchestrator plans tasks with their files, takes the batch from `next --parallel` and starts those agents together. You can check or drive it yourself:
```bash
K="python ~/.gemini/config/team/tools/kuro_ledger.py --root <project>"
$K next --parallel                      # what can start together now
$K claim T-3 --agent Kamdem             # refused if T-3 is held or shares a file with running work
$K log "2/5 migrations applied" --level heartbeat --task T-3 --agent Kamdem
$K set T-3 done --agent Kamdem --note "tests green" --commit <sha>
$K set T-4 blocked --note "waiting for the API key"     # notifies you
```
Two tasks that list the same file never run at the same time; that is why every task should carry `--files`.

### 5. Stop and resume
- **Next session, same tool**: just start; the team reads `PROJECT_STATE.md` and `.kuro/STATUS.md` and continues.
- **Session died or quota ran out**: nothing is lost. Tasks left `in_progress` carry a note saying where they started; the next session checks the repo before trusting it.
- **Continue in another tool** (Claude Code, Codex, opencode): `$K handoff --all-runnable --inline-skills` writes self-contained packets in `.kuro/handoff/` and prints the launch command for each tool. `.kuro/RESUME.md` is the entry point for any fresh session.

### 6. Tune it
| Goal | Setting |
| :-- | :-- |
| Fewest tokens (default) | `team/config.json`: `"concertation": "auto"` |
| A hint on every turn, even trivial ones | `"concertation": "always"` |
| No team hint at all for one session | env `KURO_CONCERTATION=off` |
| Fewer agents per request | `"max_participants": 2` |
| Phone or chat notifications | `reporter.channels`: add `ntfy` or `webhook` and set `ntfy_topic` / `webhook_url` (the message leaves your machine) |
| Route a word to a member | add it, lower-case, to that member's `triggers` in `team/roster.json` |
| Change who runs in parallel | edit the waves in `roster.lifecycle`, then `python scripts/validate.py` tells you which docs to update |

### 7. When something looks wrong
| Symptom | Check |
| :-- | :-- |
| No `[TEAM KURO HUDDLE]` on a real task | hook not registered: rerun the installer with the team-hook switch and look at `~/.gemini/config/hooks.json`; or `concertation` is `off` |
| Subagents on small requests | your installed `team/config.json` still says `always`; or the request matched several domains: add or remove `triggers` |
| `COVERAGE GAP` | no skill and no member matched; the team will propose to author or acquire a skill and asks before installing anything |
| `claim` refused | another agent holds the task, or a running task lists the same file; wait, or `--force` if you are sure |
| `ledger is busy` | a crashed process left `.kuro/.lock`; it is cleared automatically after 30 seconds |
| `watch` shows nobody working | no task was claimed: the work is running outside the ledger; ask the team to plan it (`skill team-reporting`) |

## How it works

### Automatic team start and per-instruction huddle
```powershell
.\install.ps1 -EnableTeamHook      # merges the "kuro-team-huddle" PreInvocation hook into hooks.json
```
Before every turn, `team/hooks/kuro_huddle.py` (pure Python, no model tokens, 40 to 240 tokens injected) routes your instruction to roster members and installed skills and tells the orchestrator the smallest workflow that is safe:

| Tier | When | Team behaviour |
| :-- | :-- | :-- |
| SOLO | chit-chat | direct answer, no subagents |
| TRIVIAL | rename, typo, explanation, lookup | done directly in the owner's voice, no subagents |
| FOCUSED | one or two domains | the owning role does the work; two owners with disjoint files run in parallel; cross-review only for auth, data or public API |
| FEATURE | three or more domains, new product | parallel waves, ADRs, gates, ledger and live board |

The tier follows the number of domains the request touches (roster `triggers` and `domain`), not the length of the prompt. Each suggested agent comes with an advisory model class (`flash` or `pro`, roster `model_tier`). On the first turn of a session the hook also triggers the bootstrap (roster + `PROJECT_STATE.md` + two-line greeting). Agents are instantiated lazily and reused, never all at once. If no skill and no team member match, it flags a **coverage gap** and the team follows `skills/team-orchestration/references/capability-acquisition.md`: reuse, author a skill, acquire a vetted one (quarantine, scan, your approval, pinned SHA, `skills.lock.json`) or create a specialist agent.

Tune it in `team/config.json`: `concertation` (`auto` (default: silent on SOLO and TRIVIAL turns) | `always` | `off`, or env `KURO_CONCERTATION`), `max_participants`, `max_rounds`, `skill_acquisition` (`ask` | `auto-if-scanned` | `off`), `agent_creation` (`ask` | `auto` | `off`), `skill_sources`, `allowed_licenses`. Defaults never download or create anything without asking.

### See the team work, live
In a second terminal, from anywhere:
```bash
python ~/.gemini/config/team/tools/kuro_ledger.py --root <project> watch
```
The board refreshes in place: progress bar, who is working on which task and for how long, the last heartbeat of each agent, blocked tasks, what can start in parallel next, and the tail of the journal. It only reads files, so it never slows the agents down.

Parallel work stays safe because the ledger arbitrates it: `next --parallel` returns the runnable tasks that share no file with each other or with work in progress, each agent takes its task with `claim <id> --agent <name>` (refused if another agent holds it or a running task touches the same files), reports with `log "<step>" --level heartbeat --task <id>`, and closes with `set <id> done`.

### Reporter, progress files and handoff to other tools
**Mbarga** (reporter) keeps the project resumable and keeps you informed. State lives in the project, in `.kuro/`, written by `team/tools/kuro_ledger.py` (atomic, locked, secret-redacting, stdlib only), so a dead session or an empty token quota loses nothing:

| File | Purpose |
| :-- | :-- |
| `.kuro/tasks.json` | tasks with owner, status, agent, start time, heartbeat, dependencies, acceptance criteria, files, `portable` flag |
| `.kuro/STATUS.md` | dashboard: progress %, in progress (agent, since), blocked, runnable now, parallel batch |
| `.kuro/JOURNAL.md` | append-only timeline of real events |
| `.kuro/RESUME.md` | "start here" for a fresh session of any tool |
| `.kuro/handoff/T-n.md` | self-contained task packet with launch lines for **Claude Code, Codex, opencode and agy** |

Write-ahead rule: a task is set `in_progress` before work and `done` only after verification. `python team/tools/kuro_ledger.py --root <project> handoff --all-runnable --inline-skills` prepares packets for every runnable portable task, flags tasks that touch the same files (do not run those in parallel in two tools) and prints the commands. Verify each tool's permission flags with `<tool> --help`.

Notifications (`team/config.json` -> `reporter`): local toast and journal by default; `ntfy` phone push and `webhook` are opt-in because the message (redacted, 240 chars max) leaves your machine. Routine updates are batched; blockers, errors, quota risk and completions are immediate.

### About `config.json`
Your Antigravity permission settings (auto-execution, sandbox, file access) are personal and security-relevant, so they are **not** part of this repo. `config.example.json` only carries harmless defaults. If you want fewer prompts, tune the permission preset yourself and understand that "turbo / sandbox off / non-workspace access" lets an agent run commands and touch any file without asking.

## Project continuity

Every active project keeps a Git-tracked `PROJECT_STATE.md` ([template](skills/project-state/templates/PROJECT_STATE.md)): active context, verified run commands, in-flight task, next 3 actions, P0 critical path, roadmap by domain, gotchas, gate status. A new session reads it instead of re-crawling the repo and checks it against `git HEAD` so a stale file is never trusted blindly.

## Develop this repo

```bash
python scripts/validate.py               # frontmatter, links, roster, JSON, budgets, catalog, prose vs roster (team size, lifecycle)
python scripts/validate.py --write-catalog   # regenerate docs/SKILLS.md and docs/TEAM.md after changing a skill or the roster
python scripts/validate.py --report          # token budget report
python scripts/split_skill.py <skill> --keep "Section A" --deep "Big section" [--dry-run]   # split an oversized SKILL.md
```
CI runs the same check on every push/PR (`.github/workflows/validate.yml`).

Adding a skill: create `skills/<name>/SKILL.md` with frontmatter `name` (equal to the folder), a routing-quality `description` (what it does and **when to use it**), then assign it to a member in `team/roster.json` and regenerate the catalog. Adding a member: give it a `tier`, a `domain`, a `model_tier` and lower-case `triggers` (the words that should route a request to it); the validator tells you which prose still has to mention it.

## Licensing

Most skills are third-party MIT works and keep their original notices; see [NOTICE](NOTICE). Content authored for this repo (rules, roster, scripts, installers and the skills listed as authored in `NOTICE`) is MIT, see [LICENSE](LICENSE).
