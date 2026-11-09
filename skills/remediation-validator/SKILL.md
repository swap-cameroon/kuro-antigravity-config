---
name: remediation-validator
description: >
  Remediation validation skill that re-runs targeted scans after fixes to confirm vulnerabilities are resolved
  and detect regressions. Trigger when the user asks to: "verify a fix", "validate remediation", "confirm a
  vulnerability is resolved", "re-scan after fixing", "check if a patch works", "did my fix work",
  "validate the security fix", "re-test after remediation", or "check for regressions after the fix".
metadata:
  version: "1.0.0"
  domain: application-security
  references: validation_patterns.md, regression_detection.md
---

# Remediation Validator

## Purpose

Validate that security fixes actually resolve the reported vulnerabilities without introducing regressions.
Performs targeted, scoped re-scanning of only the affected files and endpoints rather than full project scans.
Language-agnostic -- works with any codebase, framework, or language.

---

## Workflow

### Step 1: Input Collection

Determine what is being validated. Accept one of the following inputs (ask if ambiguous):

1. **Previous audit report**: A security audit report from `/security-audit` or individual scanner skills (SAST, DAST, dependency audit, config review, secrets scanner). Extract finding IDs, descriptions, affected files, and line numbers.

2. **Specific findings**: A list of findings to re-check, identified by:
   - Finding ID (e.g., "SAST-003")
   - CWE number (e.g., "CWE-89")
   - Description (e.g., "SQL injection in login handler")

3. **File or commit reference**: The user states what they fixed (e.g., "I fixed the SQL injection in auth.py"). Identify the relevant file(s) and infer which vulnerability class to re-scan for.

4. **No specific input**: If the user simply says "validate my fix" or "did my fix work" without details:
   - Use the Bash tool to run `git diff HEAD~1` (or against the relevant base) to detect recent changes
   - Use the Bash tool to run `git log --oneline -5` to understand recent commit context
   - Infer which findings may be affected based on changed files and patterns
   - Use the AskUserQuestion tool to confirm before proceeding: "Based on recent changes to X and Y, I'll re-check findings A, B, and C. Proceed?"

### Step 2: Change Analysis

Determine exactly what was modified and map changes to findings.

**Parse the diff:**
- Use the Bash tool to run `git diff <base>...<head>` to identify changed files and line ranges
- For each changed file, extract added/removed/modified lines
- Identify the nature of the change (new code, refactored code, configuration change, dependency update)

**Match changes to findings:**
- Cross-reference changed files against the file paths in original findings
- Cross-reference changed line ranges against reported line numbers (with tolerance for line shifts)
- Identify which vulnerability class the changes address by recognizing fix patterns:
  - Parameterized queries, prepared statements, ORM usage --> SQL injection fix
  - Output encoding, DOMPurify, template auto-escaping --> XSS fix
  - `helmet()`, security headers, CSP directives --> Security headers fix
  - bcrypt/argon2, JWT changes, session config --> Authentication fix
  - Ownership checks, role validation, middleware additions --> Access control fix
  - URL validation, allowlists, SSRF protections --> SSRF fix
  - `crypto.randomBytes`, key rotation, algorithm changes --> Cryptography fix
  - `.gitignore` additions, secret removal, env var migration --> Secrets fix
  - `package.json` / lock file changes, version bumps --> Dependency fix
  - Rate limiting, CORS config, cookie flags --> Configuration fix

**Identify unaddressed findings:**
- List any original findings in changed files that the diff does NOT appear to address
- Flag findings in files that were NOT changed at all

### Step 3: Targeted Re-scan

For each finding being validated, run ONLY the relevant scan type. Do NOT run a full project scan.

**Source code fix** (injection, XSS, auth bypass, etc.):
- Use the Read tool to re-run SAST analysis on the specific changed file(s) only
- Focus on the specific vulnerability class identified in Step 2
- Check both the fixed location AND similar patterns elsewhere in the same file
- Use the Read tool to load the relevant reference from `../llm-sast-scanner/references/` for the vulnerability class

**Endpoint fix** (DAST-detected issues):
- If the server is running, re-run DAST checks on the specific endpoint(s) affected
- Test with the same payloads that triggered the original finding
- Check adjacent endpoints that share the same handler or middleware
- Use the Read tool to load the relevant reference from `../dast-scanner/references/`

**Dependency upgrade:**
- Re-run dependency audit on the updated package(s)
- Check if the specific CVE is addressed by the new version
- Verify the lock file matches package.json
- Check for new vulnerabilities introduced by the upgrade
- Use the Read tool to load references from `../dependency-audit/references/`

**Configuration change:**
- Re-run config review on the specific configuration file
- Verify the setting change achieves the intended effect
- Check for conflicting settings elsewhere
- Use the Read tool to load references from `../security-config-review/references/`

**Secret removed:**
- Re-scan the specific file for remaining secrets
- CRITICAL: Use the Bash tool to check git history -- `git log -p --all -S '<pattern>'` -- to verify the secret is not still in history
- Verify the secret was rotated (check for new secret format/value)
- Use the Read tool to load references from `../secrets-scanner/references/`

### Step 4: Comparison

Compare re-scan results against each original finding. Classify into exactly one of five categories:

**RESOLVED**: The finding no longer appears in re-scan results. The vulnerability is fixed.
- Evidence: show the new code and explain why it addresses the vulnerability
- Confidence: HIGH if the fix follows established best practices, MEDIUM if it uses a less common approach

**PARTIALLY FIXED**: The finding still appears but with reduced severity or scope.
- Examples: parameterized one query but not another in the same file; fixed reflected XSS but stored XSS remains
- Evidence: show what was fixed and what remains
- Remaining work: describe exactly what else needs to change

**NOT FIXED**: The finding appears unchanged. The attempted fix did not address the vulnerability.
- Evidence: show the current code and explain why the vulnerability persists
- Common causes: fix was applied to wrong location, fix pattern doesn't address this variant, fix has a bypass
- Use the Read tool to load `references/validation_patterns.md` to check for known incomplete fix patterns

**REGRESSION**: New findings appeared in the changed code that were not present before.
- Evidence: show the new vulnerability with full details (file, line, severity, CWE)
- Use the Read tool to load `references/regression_detection.md` to check for known regression patterns
- Classify whether the regression is directly caused by the fix or coincidental

**SHIFTED**: The same vulnerability moved to a different location.
- Examples: code refactored to another file but same vulnerable pattern kept; vulnerability moved from frontend to backend
- Evidence: show the old location and new location
- Note: this counts as NOT FIXED for remediation tracking purposes

### Step 5: Validation Report

Produce a structured report in the following format:

```
# Remediation Validation Report

**Date**: [date]
**Scope**: [files/endpoints validated]
**Base**: [original report or findings being validated]
**Changes analyzed**: [git ref range or description]

## Summary

| Status | Count |
|--------|-------|
| Resolved | X |
| Partially Fixed | Y |
| Not Fixed | Z |
| Regression | W |
| Shifted | S |

**Remediation Progress**: [resolved / total original findings]%

## Detailed Results

### [Finding ID]: [Finding Title]
- **Original**: [brief description of original finding, file, line]
- **Fix Applied**: [what the developer changed]
- **Status**: [RESOLVED / PARTIALLY FIXED / NOT FIXED / REGRESSION / SHIFTED]
- **Evidence**: [code snippet or scan output showing result]
- **Notes**: [additional context, confidence level, or remaining work]

[Repeat for each finding]

## Regressions

[If any regressions were found, detail each one with the same format as
original scan findings: description, severity, CWE, affected file/line,
evidence, and remediation guidance]

## Remaining Items

[List any findings that are not yet resolved, grouped by priority]
[Include specific remediation guidance for each remaining item]
```

---

## Key Principles

- **Scoped scanning**: Only re-scan what was changed, not the entire project. This is faster and reduces noise.
- **Git-aware**: Use `git diff` to understand what changed. Never guess -- always verify against the actual diff.
- **Pattern-aware**: Check `references/validation_patterns.md` for common incomplete fix patterns. Many fixes look correct but miss edge cases.
- **Regression-conscious**: Always check for regressions. Fixes frequently introduce new issues. See `references/regression_detection.md`.
- **Non-judgmental**: Report facts, not blame. Say "finding persists" not "fix is wrong". Say "additional changes needed" not "incomplete work".
- **Language-agnostic**: Do not assume any specific language, framework, or toolchain. Analyze the code as-is using the patterns and techniques applicable to whatever language is present.
- **Evidence-based**: Every classification must include concrete evidence -- code snippets, scan output, or diff excerpts. Never classify a finding without showing why.
- **Conservative**: When uncertain whether a fix is complete, classify as PARTIALLY FIXED rather than RESOLVED. False negatives (missing a still-present vulnerability) are worse than false positives.
