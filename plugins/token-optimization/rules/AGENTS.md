# Token discipline (always on)

Goal: spend tokens on reasoning and code, not on noise. Never trade correctness for brevity.

1. **Output**: no greetings, apologies, filler or restating the request. Lead with the answer or the diff. Code, commands, paths, error text and security warnings are always written in full.
2. **Search before read**: locate with grep/glob/symbol search, then read only the needed line range. Whole-file reads are fine for files under ~150 lines and for `SKILL.md` files; never for lockfiles, bundles, generated or minified output.
3. **Bound command output**: use `--stat`, `-n`, `head`, `Select-Object -First`, filters. Never dump unbounded logs or `tree` of dependency folders.
4. **Reuse before spawning**: message an existing subagent instead of creating another with the same prompt. Hand subagents a precise brief (goal, files, constraints, expected output), not the whole conversation.
5. **Hygiene**: suggest `/compact` or `/new` when a sub-task ends or context is bloated; keep `.antigravityignore` current (see skill `token-saver`).
6. **Model routing**: Flash-class models for lookups, formatting, boilerplate and tests; Pro-class for architecture, security review and multi-file debugging.
7. **Keep this file small**: always-loaded rules cost tokens every turn. Put detail in a skill, not here.
