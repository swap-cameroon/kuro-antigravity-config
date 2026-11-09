# Report Format Reference

Defines the structure, aggregation rules, and formatting standards for the unified security audit report.
Used by the security-audit orchestrator in Steps 4 and 5.

---

## 1. Severity Aggregation Rules

### Individual Finding Severity Scale

| Severity | Definition | Examples |
|----------|-----------|----------|
| **Critical** | Immediate exploitation possible, full system compromise | RCE, SQL injection with admin access, hardcoded production secrets, authentication bypass |
| **High** | Significant security impact, exploitation likely | Stored XSS, IDOR on sensitive data, weak crypto on passwords, privilege escalation |
| **Medium** | Moderate impact, exploitation requires specific conditions | Reflected XSS, missing rate limiting, verbose error messages, CSRF on state-changing actions |
| **Low** | Minor security concern, limited exploitability | Missing security headers, cookie without Secure flag, outdated dependency (no known exploit) |
| **Info** | Best practice recommendation, no direct vulnerability | Code quality suggestions, documentation gaps, deprecated API usage |

### Overall Risk Rating

The overall risk rating for the project is determined by:

1. **Base rule**: Overall risk equals the highest individual finding severity
2. **Escalation rule**: If 3 or more High findings exist, escalate overall risk to Critical
3. **Corroboration rule**: Findings confirmed by multiple skills (e.g., SAST + DAST) increase severity by one level, capped at Critical
4. **Mitigating factor**: If all Critical/High findings have existing mitigations noted in the code (e.g., commented-out but present secure alternatives), note this but do not downgrade

### Severity Escalation Matrix

| Original Severity | Corroborated (2+ skills) | Escalated Severity |
|-------------------|--------------------------|-------------------|
| Info | Info | Info |
| Low | Low | Low |
| Medium | Medium → High | High |
| High | High → Critical | Critical |
| Critical | Critical (already max) | Critical |

---

## 2. Deduplication Logic

### Same Issue from Multiple Skills

When different skills detect the same underlying vulnerability:

| Scenario | Action | Result |
|----------|--------|--------|
| Same CWE + same file:line | Merge into single finding | Keep the richest evidence from all skills, note all source skills |
| Same CWE + different file:line | Keep separate | Each location is independently exploitable |
| Same vulnerability type + different endpoints | Keep separate | Each endpoint is a distinct attack vector |
| SAST + DAST find same issue | Merge | Mark confidence as "Confirmed (static + dynamic analysis)" |
| Dependency CVE + SAST confirms usage | Merge | Note "Vulnerable function confirmed in use", escalate severity if applicable |
| Secrets scanner + SAST both flag hardcoded secret | Merge | Keep secrets scanner as primary source (more specific), note SAST corroboration |
| Config review + SAST flag same misconfiguration | Merge | Keep config review as primary (more context), note SAST corroboration |

### Deduplication Keys

To identify duplicates, compare:

1. **Primary key**: CWE ID + normalized file path + line number (within 5-line tolerance)
2. **Secondary key**: Vulnerability type + endpoint URL + HTTP method
3. **Tertiary key**: CVE ID (for dependency findings)

If any key matches between two findings, evaluate for merge.

### Merge Process

When merging two findings:
1. Keep the more specific title
2. Keep the higher severity (or escalate per corroboration rules)
3. Combine evidence from both skills
4. List all source skills in the "Source" field
5. Keep the more detailed remediation guidance
6. Set confidence to "Confirmed" if sources include both static and dynamic analysis

---

## 3. Context-Aware Remediation Guidelines

### Core Principles

1. **Reference exact locations**: Always cite the specific file path and line number where the fix should be applied
2. **Use project conventions**: Match the project's coding style, import patterns, and module structure
3. **Leverage existing patterns**: If the codebase already has secure implementations of similar functionality, reference them as examples
4. **Framework-native solutions**: Always prefer the framework's built-in security features over third-party additions
5. **Minimal change principle**: Suggest the smallest effective fix first, then mention more comprehensive alternatives
6. **Version-aware**: Reference package versions compatible with the project's current dependency tree

### Remediation Format

For each finding, structure the remediation as:

```
**Remediation:**

**Quick fix** (effort: Low):
In `{file}` at line {line}, replace:

\`\`\`{language}
// BEFORE (vulnerable)
{vulnerable code}
\`\`\`

with:

\`\`\`{language}
// AFTER (secure)
{fixed code}
\`\`\`

**Comprehensive fix** (effort: Medium/High):
{description of more thorough solution, e.g., adding middleware, refactoring to use parameterized queries globally}

**Reference**: See `{file_with_secure_pattern}` line {line} for an existing secure implementation in this codebase.
```

### Language-Specific Remediation Patterns

**Node.js/Express:**
- SQL Injection → use parameterized queries with the project's ORM (knex, sequelize, prisma)
- XSS → use the project's template engine auto-escaping, or add `helmet()` middleware
- CSRF → add `csurf` middleware or framework-native CSRF protection
- Auth → use the project's existing auth middleware pattern

**Python/Flask/Django:**
- SQL Injection → use ORM queries or `db.execute()` with parameter binding
- XSS → ensure Jinja2 autoescaping is on, use `markupsafe.escape()`
- CSRF → enable `flask-wtf` CSRFProtect or Django's `{% csrf_token %}`
- Auth → use `@login_required` decorator or framework auth middleware

**Java/Spring:**
- SQL Injection → use JPA named parameters or `JdbcTemplate` with `?` placeholders
- XSS → use Thymeleaf auto-escaping, add `Content-Security-Policy` header
- CSRF → ensure Spring Security CSRF is not disabled
- Auth → use `@PreAuthorize` annotations with Spring Security

**Go:**
- SQL Injection → use `db.Query()` with `?` placeholders, never string concatenation
- XSS → use `html/template` (auto-escaping) instead of `text/template`
- Auth → use middleware pattern with context-based auth checks

---

## 4. Report Sections and Ordering

The unified report MUST follow this exact section ordering:

### Section 1: Executive Summary

Position: Always first. Provides at-a-glance risk assessment.

Contents:
- Project name, detected stack (language/framework)
- Scan date and timestamp
- List of skills executed (and count vs total available)
- Overall risk rating with justification
- Finding totals by severity (table format)
- Top 3 most critical findings with one-line summaries

Length: Keep to approximately 15-25 lines. This section is for executives and quick triage.

### Section 2: Detection Summary

Position: After executive summary. Documents what was detected and scanned.

Contents:
- Table of detected attributes (language, framework, running services, API specs, configs)
- Table of skills selected/skipped with reasoning
- Any detection ambiguities or assumptions noted

Length: Concise table format, typically 15-30 lines.

### Section 3: Critical Findings

Position: Immediately after detection summary. Most urgent issues first.

Contents: All findings with Critical severity, each with full detail block (ID, title, severity,
source, location, evidence, impact, framework references, remediation, effort).

### Section 4: High Findings

Same format as Critical findings, for High severity.

### Section 5: Medium Findings

Same format, for Medium severity.

### Section 6: Low Findings

Same format, for Low severity.

### Section 7: Informational Findings

Same format, for Info severity. May use abbreviated detail (skip evidence/impact if trivial).

### Section 8: Compliance Scorecard

Position: After all findings. Maps findings to compliance frameworks.

Contents:
- **OWASP Top 10 (2021)**: Table with each category (A01-A10), status (PASS/FAIL/N/A), and count of related findings
- **CWE Top 25**: Count of matched CWE IDs from findings, list the matched ones
- **NIST 800-53**: Summary by control family (AC, AU, CM, IA, SC, SI, etc.) with finding counts
- **PCI DSS v4.0**: Relevant requirements (primarily Req 6: Develop and Maintain Secure Systems) with status

### Section 9: Remediation Roadmap

Position: After compliance. Actionable prioritized fix plan.

Contents: Four priority tiers:

| Priority | Selection Criteria |
|----------|-------------------|
| P1 — Immediate | Critical severity AND Low/Medium effort |
| P2 — Short-term | High severity (any effort), OR Critical + High effort |
| P3 — Medium-term | Medium severity (any effort) |
| P4 — Long-term | Low severity, architectural improvements, defense-in-depth |

Each entry: Finding ID, one-line description, specific action to take, effort estimate.

### Section 10: Gap Analysis

Position: Last substantive section. Documents coverage limitations.

Contents:
- Skills that could not run and why (e.g., no live server for DAST, no API spec for contract testing)
- Vulnerability classes not fully covered by automated scanning
- Recommended manual testing areas (business logic, multi-step workflows, race conditions)
- Suggested next steps to improve coverage

### Section 11: Appendix — Raw Findings per Skill

Position: Very end. Optional, include only if findings were deduplicated/merged.

Contents:
- For each skill that produced findings, list the original finding IDs before deduplication
- Note which findings were merged and the merge rationale
- This provides traceability from the unified report back to individual skill outputs

---

## 5. Finding ID Schema

All findings in the unified report use a sequential ID with the prefix `SEQ-`:

- Format: `SEQ-{NNN}` where NNN is a zero-padded three-digit number
- Numbering: Sequential across all findings, ordered by severity (Critical first) then by skill execution order
- Example: SEQ-001 (first Critical), SEQ-002 (second Critical), ..., SEQ-015 (first Medium), etc.

When a finding is merged from multiple skills, assign a single SEQ ID and note the original skill-specific IDs in the evidence section.

---

## 6. Confidence Levels

Each finding includes a confidence level:

| Confidence | Definition | Typical Source |
|------------|-----------|---------------|
| **Confirmed** | Verified through multiple methods or demonstrated exploitation | SAST + DAST corroboration, or DAST with successful exploit |
| **Likely** | Strong evidence from single method, high-confidence pattern match | Single skill with clear evidence (e.g., obvious SQL concatenation) |
| **Possible** | Pattern match with some ambiguity, may be false positive | Complex data flow analysis, framework-specific edge cases |

Include confidence in the finding detail to help prioritize remediation effort and distinguish
between definite vulnerabilities and items that may need manual verification.
