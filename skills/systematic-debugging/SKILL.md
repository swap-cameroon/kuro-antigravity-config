---
name: systematic-debugging
description: "Find root causes with evidence, not guesses: reproduce, isolate, hypothesize, test, fix, prevent. Use for bugs, flaky tests, regressions, crashes, wrong output, or 'it works on my machine'."
license: MIT
metadata:
  version: "1.0.0"
---

# Systematic debugging

Rule: **no fix without a reproduced failure and an explained cause.** A change that "seems to help" is a guess.

## Loop
1. **Define the failure**: expected vs actual, exact error text, where observed (env, version, input), since when. Get the stack trace/log instead of paraphrasing it.
2. **Reproduce** deterministically; shrink to a minimal failing case (smallest input, fewest dependencies). If intermittent, record frequency and conditions; add logging/seeds rather than retrying until green.
3. **Localize**: bisect the space.
   - `git bisect run <test>` to find the introducing commit.
   - Bisect inputs, config, data, time, dependencies (lockfile diff), environment.
   - Binary-search the call path with assertions/log points; compare a working run with a failing run (diff the traces).
4. **Hypothesize**: write 2-3 candidate causes ranked by likelihood and cost to check. Predict what each would make true that the others would not.
5. **Test the hypothesis** with the cheapest discriminating experiment (log, assert, debugger, unit test). Change one thing at a time. Record results; abandon refuted ideas explicitly.
6. **Fix the cause, not the symptom**: ask "why was this possible?" up to five times; fix at the layer where the invariant was broken.
7. **Prove**: the reproducer now passes; add it as a regression test (failing before, passing after); run the surrounding suite.
8. **Prevent**: add a guard, type, assertion, lint rule, alert or doc so the class of bug cannot return silently.

## Common root-cause classes (check early)
Off-by-one/boundaries - null/empty/unicode/timezone/locale - stale cache or state - race/ordering/async not awaited - shared mutable state - resource leak/pool exhaustion - config/env drift (flags, secrets, versions) - floating point/overflow/encoding - network timeouts/retries/partial failure - wrong assumption about a library's contract (read the source/docs).

## Flaky tests
Never add blind retries or sleeps. Look for: shared state between tests, time/random dependence, ordering, real network/IO, port collisions, async without proper awaiting, resource cleanup. Make it fail on demand (run in loop, shuffle order, constrain CPU) before fixing.

## Production incidents
Stabilize first (rollback, flag off, scale), preserve evidence (logs, heap/thread dumps, metrics window) then debug on a copy. Hand the timeline to `sre-engineer` for the post-mortem.

## Report format
`Symptom - Reproduction - Root cause (evidence) - Fix (diff) - Regression test - Prevention - Not verified`.
Be explicit about what you could not reproduce or confirm.
