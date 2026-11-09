# Team Kuro - Antigravity multi-agent configuration

A portable, versioned setup for **Google Antigravity (`agy`)**: a 7-role engineering team with gated delivery, 35 skills loaded on demand, token discipline, and a handover protocol so any session (or colleague) resumes instantly.

## What you get

| Piece | Where | Purpose |
| :-- | :-- | :-- |
| Team rules (always on, ~35 lines) | `plugins/team-kuro/` | Roles, routing, lifecycle gates, honesty rules |
| Token rules (always on, ~15 lines) | `plugins/token-optimization/` | Output/read/command discipline |
| Skills (on demand) | `skills/` | 35 domain playbooks - see [docs/SKILLS.md](docs/SKILLS.md) |
| Team roster | `team/roster.json` | Single source of truth: who owns which skill, deliverable and gate |
| Handover | `skills/project-state/` | `PROJECT_STATE.md` template + resume/update protocol |

Design rule: **always-loaded files stay tiny; detail lives in skills** that are read only when the task needs them.

## Team

| Member | Role | Core skills | Gate they enforce |
| :-- | :-- | :-- | :-- |
| **Sarah** | Product & domain strategy | `spec-miner` | Acceptance criteria exist and are testable |
| **Victor** | Architecture & critical review | `first-principles`, `system-design-architect` | ADRs with rejected alternatives |
| **Alex** | UI/UX engineering | `angular-*`, `ui-design-a11y` | WCAG 2.2 AA, safe DOM |
| **Elena** | Backend & DBA | `spring-data-jpa`, `postgres`, `backend-performance-review` | Reversible migrations, explain plans |
| **Marcus** | Security | `security-auditor`, `llm-sast-scanner`, `secure-by-design-coding`, `secrets-scanner` | No open critical/high, no secrets |
| **Lucas** | QA automation | `spring-testing`, `api-contract-testing`, `code-reviewer` | Every criterion has a test |
| **David** | DevOps, cloud, SRE | `devops-engineer`, `cloud-architect`, `sre-engineer` | Green pipeline, rollback documented |

Lifecycle: Sarah -> Victor -> Alex/Elena -> Marcus -> Lucas -> David. Full protocol: `skills/team-orchestration`.

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
```
CI runs the same check on every push/PR (`.github/workflows/validate.yml`).

Adding a skill: create `skills/<name>/SKILL.md` with frontmatter `name` (equal to the folder), a routing-quality `description` (what it does and **when to use it**), then assign it to a member in `team/roster.json` and regenerate the catalog.

## Licensing

Most skills are third-party MIT works and keep their original notices; see [NOTICE](NOTICE). Skills authored for this repo (`team-orchestration`, `project-state`, `ui-design-a11y`) are MIT.
