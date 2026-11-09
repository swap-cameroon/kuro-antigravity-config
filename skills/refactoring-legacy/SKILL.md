---
name: refactoring-legacy
description: "Refactor and modernize legacy code safely: characterization tests, small reversible steps, strangler pattern, dead-code removal. Use when cleaning up, restructuring, migrating or paying down technical debt."
license: MIT
metadata:
  version: "1.0.0"
---

# Refactoring & legacy modernization

Refactoring = changing structure without changing behavior. If behavior changes, it is a feature or a fix: separate commits, never mixed.

## Before touching code
1. **State the goal** and the pain it removes (cognitive load, change failure rate, perf, upgrade blocker). No goal, no refactor.
2. **Map**: use `spec-miner` for undocumented systems; find callers/usages by search, not memory; note public contracts (APIs, DB schema, events, files) that must not change.
3. **Safety net**: run existing tests and record baseline. Where coverage is missing, write **characterization tests** that pin *current* behavior (including odd behavior) via golden-master/snapshot of real inputs. Seam first (extract interface, inject dependency) if code is untestable.
4. Make the build and lint green on the starting commit.

## Execution rules
- Tiny steps, each compiling and green, each its own commit (`refactor:` prefix). Revert instead of debugging a step.
- Use the mechanical catalogue: rename, extract function/class, inline, move, replace conditional with polymorphism, introduce parameter object, replace magic values, remove duplication (rule of three), flatten nesting with guard clauses, separate query from command.
- Prefer IDE/tooling-driven refactors (rename, move, codemods like jscodeshift, OpenRewrite, `ruff --fix`, `ng update`) over hand edits for fidelity.
- Do not reformat whole files in the same commit as logic moves; formatting-only commits go first.
- Keep public interfaces stable; deprecate and route through adapters, remove later.

## Large-scale strategies
- **Strangler fig**: put a facade/router in front, move one capability at a time to the new implementation, keep both until traffic is shifted, then delete the old path.
- **Branch by abstraction** and **feature flags** for in-place swaps; **parallel run** (shadow traffic, compare outputs) for risky rewrites.
- **Expand/contract** for schema changes: add new, dual-write, backfill, switch reads, remove old (coordinate with `postgres`/`spring-data-jpa`).
- Rewrites from scratch are a last resort; require a written justification (Njoya) and an incremental cutover plan.

## Dead code & dependencies
Prove unused via search, coverage, logs/metrics over a full business cycle, then delete (Git keeps history). Upgrade dependencies one major at a time with changelog review and the test suite as the oracle.

## Done when
Behavior verified unchanged (tests, golden master, diff of outputs) - metrics for the stated goal improved (complexity, duplication, build time, coverage) - no public contract changed unintentionally - notes added to `PROJECT_STATE.md`.

## Report
What moved, how behavior was kept identical (evidence), residual risk, follow-ups. Say clearly what you did not verify.
