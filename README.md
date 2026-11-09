# Team Kuro - Antigravity multi-agent configuration

A portable, versioned setup for **Google Antigravity (`agy`)**: a 13-agent engineering team (7 core roles + 6 on-demand specialists) with gated delivery, 51 skills loaded on demand, token discipline, and a handover protocol so any session (or colleague) resumes instantly.

## What you get

| Piece | Where | Purpose |
| :-- | :-- | :-- |
| Team rules (always on, 27 lines) | `plugins/team-kuro/` | Roles, routing, lifecycle gates, honesty rules |
| Token rules (always on, 11 lines) | `plugins/token-optimization/` | Output/read/command discipline |
| Skills (on demand) | `skills/` | 35 domain playbooks - see [docs/SKILLS.md](docs/SKILLS.md) |
| Team roster | `team/roster.json` | Single source of truth: who owns which skill, deliverable and gate |
| Handover | `skills/project-state/` | `PROJECT_STATE.md` template + resume/update protocol |

Design rule: **always-loaded files stay tiny; detail lives in skills** that are read only when the task needs them.

## Performance budget (measured, enforced in CI)

Estimated with 1 token ~ 4 characters (`python scripts/validate.py --report`):

| | Initial import | Now |
| :-- | --: | --: |
| Always-on rules (every turn) | ~2,250 | ~1,250 |
| Skill names + descriptions (every turn, if your host lists them) | ~3,880 | ~3,760 (51 skills instead of 35) |
| **Baseline per turn** | **~6,130** | **~5,010 (-18%, with 16 more skills, personas, huddle and reporter)** |
| Heaviest SKILL.md on activation | ~8,070 | ~5,810 |
| Five heaviest SKILL.md combined | ~32,000 | ~20,600 |

How: oversized skills (`secure-by-design-coding`, `angular-structure`, `angular-security`, `security-auditor`, `perf`, `code-reviewer-angular`) keep their core rules in `SKILL.md` and expose the rest as `references/*.md` behind a "Load on demand" index; content is moved verbatim, never rewritten. Descriptions were tightened while keeping their routing triggers. CI fails if the always-on rules exceed 1,300 tokens, descriptions exceed 3,900 tokens in total, or a description exceeds 520 characters, and warns when a `SKILL.md` exceeds ~3,500 tokens.

## Team

| Member | Role | Core skills | Gate they enforce |
| :-- | :-- | :-- | :-- |
| **Ngono** | Product & domain strategy | `product-requirements`, `spec-miner` | Acceptance criteria exist and are testable |
| **Njoya** | Architecture & critical review | `first-principles`, `system-design-architect` | ADRs with rejected alternatives |
| **Kouam** | UI/UX engineering | `angular-*`, `react-nextjs`, `ui-design-a11y` | WCAG 2.2 AA, safe DOM |
| **Kamdem** | Backend & DBA | `spring-data-jpa`, `postgres`, `api-design`, `backend-performance-review` | Reversible migrations, explain plans |
| **Hayatou** | Security | `security-auditor`, `threat-modeling`, `llm-sast-scanner`, `secure-by-design-coding`, `secrets-scanner` | No open critical/high, no secrets |
| **Lukong** | QA automation | `test-strategy`, `spring-testing`, `api-contract-testing`, `code-reviewer` | Every criterion has a test |
| **Endeley** | DevOps, cloud, SRE | `devops-engineer`, `cloud-architect`, `sre-engineer`, `observability` | Green pipeline, rollback documented |
| *Ondoua* | Node/TS and Python backends | `node-typescript-backend`, `python-fastapi` | Strict typing, boundary validation |
| *Bouba* | Mobile (Flutter, RN, native) | `mobile-engineering` | Keychain/Keystore, staged rollout |
| *Manga* | Data & AI | `data-engineering`, `llm-app-engineering` | Idempotent jobs, LLM regression evals |
| *Matip* | Debugging & refactoring | `systematic-debugging`, `refactoring-legacy` | Reproduce before fix, behaviour preserved |
| *Nchare* | Documentation & DX | `technical-writing` | Every documented command was run |
| *Ndumbe* | Release & git | `git-workflow-release` | Green main, SemVer matches changes, rollback |

Each agent has a Cameroonian name and a persona drawn from the heritage it honours (traits, voice and a *blind spot* that peers challenge); the full profiles are in [docs/TEAM.md](docs/TEAM.md). Personas shape tone and working style only: technical standards and gates are identical for everyone, and they make no claim about real people. Edit `team/roster.json` to adjust any name or persona, then regenerate the docs.

Lifecycle: Ngono -> Njoya -> Kouam/Kamdem (or the specialist Njoya selects) -> Hayatou -> Lukong -> Endeley. Specialists (italic) are summoned only when the work calls for them. Full protocol: `skills/team-orchestration`.

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
```

The installer is **non-destructive**:
- validates the repo first (`scripts/validate.py`);
- backs up replaced folders to `<target>/.kuro-backup/<timestamp>` (last 3 kept);
- **never overwrites** `config.json`, `hooks.json`, `mcp_config.json` - it only creates them when missing;
- removes legacy duplicates from older versions, verifies every skill landed, and exits non-zero on failure.

Optional prompt firewall (blocks vague or runaway prompts before they burn tokens):
```powershell
.\install.ps1 -EnableInterceptor    # merges a PreInvocation hook into hooks.json, keeps existing hooks
```

### Automatic team start and per-instruction huddle
```powershell
.\install.ps1 -EnableTeamHook      # merges the "kuro-team-huddle" PreInvocation hook into hooks.json
```
Before every turn, `team/hooks/kuro_huddle.py` (pure Python, no model tokens, ~150 tokens injected) routes your instruction to roster members and installed skills and tells the orchestrator how to convene the team:

| Tier | When | Team behaviour |
| :-- | :-- | :-- |
| SOLO | chit-chat, trivial | one role answers, no subagents |
| FOCUSED | one domain | 1-2 relevant agents consulted as real subagents |
| FEATURE | several domains / new project | full deliberation, ADRs, gates |

On the first turn of a session it also triggers the bootstrap (roster + `PROJECT_STATE.md` + two-line greeting). Agents are instantiated lazily and reused, never all at once. If no installed skill matches, it flags a **coverage gap** and the team follows `skills/team-orchestration/references/capability-acquisition.md`: reuse, author a skill, acquire a vetted one (quarantine, scan, your approval, pinned SHA, `skills.lock.json`) or create a specialist agent.

Tune it in `team/config.json`: `concertation` (`always` | `auto` | `off`, or env `KURO_CONCERTATION`), `max_participants`, `max_rounds`, `skill_acquisition` (`ask` | `auto-if-scanned` | `off`), `agent_creation` (`ask` | `auto` | `off`), `skill_sources`, `allowed_licenses`. Defaults never download or create anything without asking.

### Reporter, progress files and handoff to other tools
**Mbarga** (reporter) keeps the project resumable and keeps you informed. State lives in the project, in `.kuro/`, written by `team/tools/kuro_ledger.py` (atomic, locked, secret-redacting, stdlib only), so a dead session or an empty token quota loses nothing:

| File | Purpose |
| :-- | :-- |
| `.kuro/tasks.json` | tasks with owner, status, dependencies, acceptance criteria, files, `portable` flag |
| `.kuro/STATUS.md` | dashboard: progress %, in progress, blocked, runnable now |
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
python scripts/validate.py               # frontmatter, name==dir, links, roster, JSON, counts, catalog
python scripts/validate.py --write-catalog   # regenerate docs/SKILLS.md after adding a skill
python scripts/validate.py --report          # token budget report
python scripts/split_skill.py <skill> --keep "Section A" --deep "Big section" [--dry-run]   # split an oversized SKILL.md
```
CI runs the same check on every push/PR (`.github/workflows/validate.yml`).

Adding a skill: create `skills/<name>/SKILL.md` with frontmatter `name` (equal to the folder), a routing-quality `description` (what it does and **when to use it**), then assign it to a member in `team/roster.json` and regenerate the catalog.

## Licensing

Most skills are third-party MIT works and keep their original notices; see [NOTICE](NOTICE). Content authored for this repo (rules, roster, scripts, installers and the skills listed as authored in `NOTICE`) is MIT, see [LICENSE](LICENSE).
