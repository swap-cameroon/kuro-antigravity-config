# Team Kuro - Antigravity multi-agent configuration

A portable, versioned setup for **Google Antigravity (`agy`)**: a 13-agent engineering team (7 core roles + 6 on-demand specialists) with gated delivery, 50 skills loaded on demand, token discipline, and a handover protocol so any session (or colleague) resumes instantly.

## What you get

| Piece | Where | Purpose |
| :-- | :-- | :-- |
| Team rules (always on, 24 lines) | `plugins/team-kuro/` | Roles, routing, lifecycle gates, honesty rules |
| Token rules (always on, 11 lines) | `plugins/token-optimization/` | Output/read/command discipline |
| Skills (on demand) | `skills/` | 35 domain playbooks - see [docs/SKILLS.md](docs/SKILLS.md) |
| Team roster | `team/roster.json` | Single source of truth: who owns which skill, deliverable and gate |
| Handover | `skills/project-state/` | `PROJECT_STATE.md` template + resume/update protocol |

Design rule: **always-loaded files stay tiny; detail lives in skills** that are read only when the task needs them.

## Performance budget (measured, enforced in CI)

Estimated with 1 token ~ 4 characters (`python scripts/validate.py --report`):

| | Initial import | Now |
| :-- | --: | --: |
| Always-on rules (every turn) | ~2,250 | ~1,000 |
| Skill names + descriptions (every turn, if your host lists them) | ~3,880 | ~3,680 (50 skills instead of 35) |
| **Baseline per turn** | **~6,130** | **~4,680 (-24%, with 15 more skills)** |
| Heaviest SKILL.md on activation | ~8,070 | ~5,810 |
| Five heaviest SKILL.md combined | ~32,000 | ~20,600 |

How: oversized skills (`secure-by-design-coding`, `angular-structure`, `angular-security`, `security-auditor`, `perf`, `code-reviewer-angular`) keep their core rules in `SKILL.md` and expose the rest as `references/*.md` behind a "Load on demand" index; content is moved verbatim, never rewritten. Descriptions were tightened while keeping their routing triggers. CI fails if the always-on rules exceed 1,100 tokens, descriptions exceed 3,900 tokens in total, or a description exceeds 520 characters, and warns when a `SKILL.md` exceeds ~3,500 tokens.

## Team

| Member | Role | Core skills | Gate they enforce |
| :-- | :-- | :-- | :-- |
| **Sarah** | Product & domain strategy | `product-requirements`, `spec-miner` | Acceptance criteria exist and are testable |
| **Victor** | Architecture & critical review | `first-principles`, `system-design-architect` | ADRs with rejected alternatives |
| **Alex** | UI/UX engineering | `angular-*`, `react-nextjs`, `ui-design-a11y` | WCAG 2.2 AA, safe DOM |
| **Elena** | Backend & DBA | `spring-data-jpa`, `postgres`, `api-design`, `backend-performance-review` | Reversible migrations, explain plans |
| **Marcus** | Security | `security-auditor`, `threat-modeling`, `llm-sast-scanner`, `secure-by-design-coding`, `secrets-scanner` | No open critical/high, no secrets |
| **Lucas** | QA automation | `test-strategy`, `spring-testing`, `api-contract-testing`, `code-reviewer` | Every criterion has a test |
| **David** | DevOps, cloud, SRE | `devops-engineer`, `cloud-architect`, `sre-engineer`, `observability` | Green pipeline, rollback documented |
| *Theo* | Node/TS and Python backends | `node-typescript-backend`, `python-fastapi` | Strict typing, boundary validation |
| *Maya* | Mobile (Flutter, RN, native) | `mobile-engineering` | Keychain/Keystore, staged rollout |
| *Ines* | Data & AI | `data-engineering`, `llm-app-engineering` | Idempotent jobs, LLM regression evals |
| *Kai* | Debugging & refactoring | `systematic-debugging`, `refactoring-legacy` | Reproduce before fix, behaviour preserved |
| *Nora* | Documentation & DX | `technical-writing` | Every documented command was run |
| *Ravi* | Release & git | `git-workflow-release` | Green main, SemVer matches changes, rollback |

Lifecycle: Sarah -> Victor -> Alex/Elena (or the specialist Victor selects) -> Marcus -> Lucas -> David. Specialists (italic) are summoned only when the work calls for them. Full protocol: `skills/team-orchestration`.

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
