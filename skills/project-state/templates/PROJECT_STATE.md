# PROJECT_STATE

> Handover file for humans and AI agents. Keep under ~200 lines. Never put secrets here.

## 1. Active context
- **Project**: <name> - <one-line purpose>
- **Branch**: <branch> | **Target version**: <x.y.z> | **Last verified commit**: <short-sha> on <YYYY-MM-DD>
- **Stack**: <languages, frameworks, datastores> (rationale: <ADR link>)
- **Environments**: <local / staging / prod: URLs or "none yet">
- **Docs**: PRD.md, ARCHITECTURE.md, docs/adr/

## 2. Run it (verified commands)
```
<install>
<run dev>
<test>
<build>
```
Required env vars (names only): `<VAR_A>`, `<VAR_B>` - obtained from <where>.

## 3. Completed milestones
- [x] <milestone> - <commit/PR> - <date>

## 4. Current in-flight task
- **Task**: <what>
- **Owner role**: <Alex/Elena/...>
- **Where**: `<file>` / `<symbol>`
- **Done so far**: <state>
- **To continue**: <exact next step>

## 5. Next 3 actions
1. <action>
2. <action>
3. <action>

## 6. Critical path (P0)
- [ ] **P0** <blocking item: auth layer / schema migration / API contract / security finding> - unblocks: <items>

## 7. Roadmap by domain
| Domain | P1 | P2 |
| :-- | :-- | :-- |
| Product | | |
| UI | | |
| Backend/Data | | |
| Security | | |
| QA | | |
| DevOps | | |

## 8. Invariants & gotchas
- <non-obvious decision and why>

## 9. Gate status
| Gate | Status | Evidence / waiver |
| :-- | :-- | :-- |
| Spec (Sarah) | | |
| Architecture (Victor) | | |
| Security (Marcus) | | |
| Tests (Lucas) | | |
| Deploy (David) | | |
