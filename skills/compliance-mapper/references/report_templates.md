# Compliance Report Templates

Templates for generating structured compliance reports from mapped security findings.

---

## Executive Summary Template

```markdown
# Compliance Report -- Executive Summary

**Report Date:** [DATE]
**Scope:** [PROJECT NAME / REPOSITORY]
**Assessment Type:** [Automated Security Scan / Manual Review / Combined]
**Skills Used:** [List of security skills that produced findings]

## Overall Risk Rating: [CRITICAL / HIGH / MEDIUM / LOW]

| Severity | Count |
|----------|-------|
| Critical | [N]   |
| High     | [N]   |
| Medium   | [N]   |
| Low      | [N]   |
| Info     | [N]   |
| **Total**| **[N]**|

## Top Critical Findings

1. **[Finding Title]** (Severity: [X]) -- [One-sentence description]. Affects [OWASP category], [CWE-ID].
2. **[Finding Title]** (Severity: [X]) -- [One-sentence description]. Affects [OWASP category], [CWE-ID].
3. **[Finding Title]** (Severity: [X]) -- [One-sentence description]. Affects [OWASP category], [CWE-ID].

## Compliance Posture

| Framework          | Status                         | Score           |
|--------------------|--------------------------------|-----------------|
| OWASP Top 10       | [X]/10 categories with findings | [PASS/FAIL]    |
| CWE Top 25         | [X]/25 weaknesses found         | [PASS/FAIL]    |
| NIST SP 800-53     | [X] controls failing            | [Rating]       |
| PCI DSS v4.0       | [X] requirements non-compliant  | [Rating]       |
| ISO 27001:2022     | [X] controls with gaps          | [Rating]       |

## Key Recommendations

1. [Most urgent action item with expected impact]
2. [Second priority action item]
3. [Third priority action item]
4. [Fourth priority action item, if applicable]
5. [Fifth priority action item, if applicable]
```

---

## Detailed Findings Table Template

```markdown
# Detailed Findings

| ID | Title | Severity | Source | Location | OWASP | CWE | NIST | PCI DSS |
|----|-------|----------|--------|----------|-------|-----|------|---------|
| FINDING-001 | [Title] | Critical | [SAST/DAST/...] | [file:line or endpoint] | A0X | CWE-XXX | XX-X | Req X |
| FINDING-002 | [Title] | High | [Source] | [Location] | A0X | CWE-XXX | XX-X | Req X |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
```

---

## Individual Finding Template

```markdown
### FINDING-[NNN]: [Title]

| Attribute       | Value                                    |
|-----------------|------------------------------------------|
| **Severity**    | [Critical / High / Medium / Low / Info]  |
| **Source**       | [SAST / DAST / Dependency Audit / Config Review / Secrets Scanner / API Contract Testing / Manual] |
| **Location**    | [file:line or URL endpoint]              |

**Description:**
[Detailed description of the vulnerability, what it is, and why it matters.]

**Evidence:**
```
[Code snippet, request/response, or configuration excerpt demonstrating the issue]
```

**Impact:**
[What an attacker could achieve by exploiting this vulnerability. Include data at risk, potential business impact.]

**Framework References:**

| Framework     | Reference                              |
|---------------|----------------------------------------|
| OWASP Top 10  | A0X:2021 -- [Category Name]            |
| CWE           | CWE-XXX: [CWE Name]                   |
| NIST 800-53   | XX-X: [Control Name]                   |
| PCI DSS v4.0  | Req X.X.X: [Requirement Description]   |
| SANS Top 25   | #XX (if applicable, or N/A)            |
| ISO 27001     | A.X.XX: [Control Name]                 |

**Remediation:**
[Specific, actionable remediation advice. Use the project's actual technology stack and patterns when possible.]

```
[Example remediation code or configuration, if applicable]
```

**Effort Estimate:** [Low / Medium / High]
- Low: Simple configuration change or one-line fix
- Medium: Requires code changes across a few files
- High: Architectural change or significant refactoring required
```

---

## Compliance Scorecard Template

```markdown
# Compliance Scorecard

## OWASP Top 10 (2021)

| Category | Name | Status | Findings | Severity |
|----------|------|--------|----------|----------|
| A01 | Broken Access Control | [PASS/FAIL/PARTIAL/NOT TESTED] | [N] | [Highest severity] |
| A02 | Cryptographic Failures | [PASS/FAIL/PARTIAL/NOT TESTED] | [N] | [Highest severity] |
| A03 | Injection | [PASS/FAIL/PARTIAL/NOT TESTED] | [N] | [Highest severity] |
| A04 | Insecure Design | [PASS/FAIL/PARTIAL/NOT TESTED] | [N] | [Highest severity] |
| A05 | Security Misconfiguration | [PASS/FAIL/PARTIAL/NOT TESTED] | [N] | [Highest severity] |
| A06 | Vulnerable Components | [PASS/FAIL/PARTIAL/NOT TESTED] | [N] | [Highest severity] |
| A07 | Auth Failures | [PASS/FAIL/PARTIAL/NOT TESTED] | [N] | [Highest severity] |
| A08 | Integrity Failures | [PASS/FAIL/PARTIAL/NOT TESTED] | [N] | [Highest severity] |
| A09 | Logging Failures | [PASS/FAIL/PARTIAL/NOT TESTED] | [N] | [Highest severity] |
| A10 | SSRF | [PASS/FAIL/PARTIAL/NOT TESTED] | [N] | [Highest severity] |

Status definitions:
- **PASS**: Category was tested and no findings were identified
- **FAIL**: One or more findings mapped to this category
- **PARTIAL**: Some aspects tested with findings, others not tested
- **NOT TESTED**: No testing coverage for this category

## CWE/SANS Top 25 (2023)

| Rank | CWE | Name | Status |
|------|-----|------|--------|
| 1 | CWE-787 | Out-of-bounds Write | [FOUND/NOT FOUND/NOT TESTED] |
| 2 | CWE-79 | Cross-site Scripting | [FOUND/NOT FOUND/NOT TESTED] |
| 3 | CWE-89 | SQL Injection | [FOUND/NOT FOUND/NOT TESTED] |
| 4 | CWE-416 | Use After Free | [FOUND/NOT FOUND/NOT TESTED] |
| 5 | CWE-78 | OS Command Injection | [FOUND/NOT FOUND/NOT TESTED] |
| 6 | CWE-20 | Improper Input Validation | [FOUND/NOT FOUND/NOT TESTED] |
| 7 | CWE-125 | Out-of-bounds Read | [FOUND/NOT FOUND/NOT TESTED] |
| 8 | CWE-22 | Path Traversal | [FOUND/NOT FOUND/NOT TESTED] |
| 9 | CWE-352 | CSRF | [FOUND/NOT FOUND/NOT TESTED] |
| 10 | CWE-434 | Unrestricted Upload | [FOUND/NOT FOUND/NOT TESTED] |
| 11 | CWE-862 | Missing Authorization | [FOUND/NOT FOUND/NOT TESTED] |
| 12 | CWE-476 | NULL Pointer Dereference | [FOUND/NOT FOUND/NOT TESTED] |
| 13 | CWE-287 | Improper Authentication | [FOUND/NOT FOUND/NOT TESTED] |
| 14 | CWE-190 | Integer Overflow | [FOUND/NOT FOUND/NOT TESTED] |
| 15 | CWE-502 | Deserialization of Untrusted Data | [FOUND/NOT FOUND/NOT TESTED] |
| 16 | CWE-77 | Command Injection | [FOUND/NOT FOUND/NOT TESTED] |
| 17 | CWE-119 | Buffer Overflow | [FOUND/NOT FOUND/NOT TESTED] |
| 18 | CWE-798 | Hard-coded Credentials | [FOUND/NOT FOUND/NOT TESTED] |
| 19 | CWE-918 | SSRF | [FOUND/NOT FOUND/NOT TESTED] |
| 20 | CWE-306 | Missing Authentication | [FOUND/NOT FOUND/NOT TESTED] |
| 21 | CWE-362 | Race Condition | [FOUND/NOT FOUND/NOT TESTED] |
| 22 | CWE-269 | Improper Privilege Management | [FOUND/NOT FOUND/NOT TESTED] |
| 23 | CWE-94 | Code Injection | [FOUND/NOT FOUND/NOT TESTED] |
| 24 | CWE-863 | Incorrect Authorization | [FOUND/NOT FOUND/NOT TESTED] |
| 25 | CWE-276 | Incorrect Default Permissions | [FOUND/NOT FOUND/NOT TESTED] |

## NIST SP 800-53 Rev 5

| Control Family | Description | Status | Failing Controls | Not Tested |
|----------------|-------------|--------|-----------------|------------|
| AC | Access Control | [Satisfactory/Needs Improvement/Failing/Not Tested] | [list] | [list] |
| AU | Audit & Accountability | [Status] | [list] | [list] |
| CA | Assessment & Authorization | [Status] | [list] | [list] |
| CM | Configuration Management | [Status] | [list] | [list] |
| IA | Identification & Auth | [Status] | [list] | [list] |
| IR | Incident Response | [Status] | [list] | [list] |
| SC | System & Communications | [Status] | [list] | [list] |
| SI | System & Info Integrity | [Status] | [list] | [list] |

Status definitions:
- **Satisfactory**: All assessed controls passing
- **Needs Improvement**: Some controls failing but no critical gaps
- **Failing**: Critical controls failing
- **Not Tested**: No assessment data for this control family

## PCI DSS v4.0

| Requirement | Description | Status | Findings |
|-------------|-------------|--------|----------|
| 1 | Network Security Controls | [Compliant/Non-Compliant/N/A] | [N] |
| 2 | Secure Configurations | [Compliant/Non-Compliant/N/A] | [N] |
| 3 | Protect Stored Data | [Compliant/Non-Compliant/N/A] | [N] |
| 4 | Protect Data in Transit | [Compliant/Non-Compliant/N/A] | [N] |
| 5 | Malware Protection | [Compliant/Non-Compliant/N/A] | [N] |
| 6 | Secure Software | [Compliant/Non-Compliant/N/A] | [N] |
| 7 | Restrict Access | [Compliant/Non-Compliant/N/A] | [N] |
| 8 | Identify & Authenticate | [Compliant/Non-Compliant/N/A] | [N] |
| 9 | Physical Access | N/A (code review) | 0 |
| 10 | Log & Monitor | [Compliant/Non-Compliant/N/A] | [N] |
| 11 | Test Security | [Compliant/Non-Compliant/N/A] | [N] |
| 12 | Security Policies | [Compliant/Non-Compliant/N/A] | [N] |

Status definitions:
- **Compliant**: All sub-requirements assessed and passing
- **Non-Compliant**: One or more sub-requirements failing
- **N/A**: Requirement not applicable to code-level assessment
```

---

## Remediation Roadmap Template

```markdown
# Remediation Roadmap

## Priority 1 -- Immediate (fix within 1-7 days)
Criteria: Critical severity AND Low/Medium remediation effort

| Finding ID | Title | Severity | Effort | Framework Impact |
|-----------|-------|----------|--------|-----------------|
| FINDING-XXX | [Title] | Critical | Low | [Frameworks affected] |
| ... | ... | ... | ... | ... |

**Rationale:** These findings represent the highest risk with the lowest effort to resolve. They should be addressed immediately to reduce the most significant attack surface.

## Priority 2 -- Short-term (fix within 1-4 weeks)
Criteria: High severity, OR Critical severity with High effort

| Finding ID | Title | Severity | Effort | Framework Impact |
|-----------|-------|----------|--------|-----------------|
| FINDING-XXX | [Title] | High | Medium | [Frameworks affected] |
| ... | ... | ... | ... | ... |

**Rationale:** These findings represent significant risk but may require more effort or coordination to resolve. Plan these into the next sprint or release cycle.

## Priority 3 -- Medium-term (fix within 1-3 months)
Criteria: Medium severity

| Finding ID | Title | Severity | Effort | Framework Impact |
|-----------|-------|----------|--------|-----------------|
| FINDING-XXX | [Title] | Medium | [Effort] | [Frameworks affected] |
| ... | ... | ... | ... | ... |

**Rationale:** These findings represent moderate risk. Schedule remediation as part of regular development work.

## Priority 4 -- Long-term (fix within 3-6 months)
Criteria: Low severity, OR findings requiring architectural changes

| Finding ID | Title | Severity | Effort | Framework Impact |
|-----------|-------|----------|--------|-----------------|
| FINDING-XXX | [Title] | Low | High | [Frameworks affected] |
| ... | ... | ... | ... | ... |

**Rationale:** These findings represent lower immediate risk or require significant architectural changes. Include in long-term planning and design reviews.
```

---

## Gap Analysis Template

```markdown
# Gap Analysis

## Testing Coverage Summary

| Security Skill | Was Run | Findings Produced | Coverage Areas |
|---------------|---------|-------------------|----------------|
| SAST Scanner | [Yes/No] | [N] | Code-level vulnerabilities, injection, crypto |
| DAST Scanner | [Yes/No] | [N] | Runtime vulnerabilities, headers, auth |
| Dependency Audit | [Yes/No] | [N] | Known CVEs, outdated components |
| Config Review | [Yes/No] | [N] | Security headers, TLS, server config |
| Secrets Scanner | [Yes/No] | [N] | Hardcoded credentials, API keys, tokens |
| API Contract Testing | [Yes/No] | [N] | API security, auth, input validation |

## Framework Coverage Gaps

### OWASP Top 10
Categories with NO testing coverage:
- [A0X: Category Name] -- Reason: [which skill would cover this]

### NIST SP 800-53
Control families with NO testing coverage:
- [XX: Family Name] -- Reason: [requires manual review / different tool]

### PCI DSS v4.0
Requirements with NO testing coverage:
- [Req X: Description] -- Reason: [out of scope / requires organizational assessment]

## Recommendations for Additional Testing

1. **[Gap Area]**: Run [specific skill or tool] to cover [framework categories]
2. **[Gap Area]**: Perform [manual review type] to assess [specific controls]
3. **[Gap Area]**: Consider [additional tool or process] for [coverage area]
```

