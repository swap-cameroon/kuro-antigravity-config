---
name: security-audit
description: "Orchestrator for comprehensive security audits: auto-detects the stack, runs the applicable scanning skills and produces one unified report with remediation. Use for 'security audit', 'full security scan', 'comprehensive vulnerability assessment', 'run all security checks', or any broad multi-dimensional security review."
metadata:
  version: "1.0.0"
  domain: application-security
  type: orchestrator
  sub-skills:
    - llm-sast-scanner
    - dast-scanner
    - dependency-audit
    - security-config-review
    - api-contract-testing
    - secrets-scanner
    - compliance-mapper
---

# Security Audit — Smart Orchestrator

## Overview

This is the master orchestrator skill. It auto-detects the project's technology stack and selectively
invokes the appropriate security scanning skills. It produces a unified report with context-aware
remediation tailored to the project's language, framework, and existing code patterns.

The orchestrator is **language-agnostic** — it dynamically determines what to scan and how based on
what it finds in the project directory.

## Available Sub-Skills

| # | Skill | Description |
|---|-------|-------------|
| 1 | `llm-sast-scanner` | Static Application Security Testing — source code analysis for 34+ vulnerability classes using taint tracking and pattern matching |
| 2 | `dast-scanner` | Dynamic Application Security Testing — running endpoint probing, fuzzing, and runtime vulnerability detection against live services |
| 3 | `dependency-audit` | Dependency vulnerability scanning — identifies known CVEs in third-party packages and transitive dependencies |
| 4 | `security-config-review` | Infrastructure and configuration hardening review — Docker, CI/CD, cloud IaC, framework settings |
| 5 | `api-contract-testing` | API specification vs behavior validation — detects undocumented endpoints, schema mismatches, auth bypass |
| 6 | `secrets-scanner` | Hardcoded secrets detection — scans source code, config files, and git history for leaked credentials |
| 7 | `compliance-mapper` | Framework mapping — maps findings to OWASP Top 10, CWE Top 25, NIST 800-53, and PCI DSS requirements |

## Workflow

### Step 1: Project Context Detection

Scan the project directory to build a complete picture of the technology stack. Use the Read tool to load
`references/project_detection.md` for comprehensive detection patterns. Use the Glob tool to find manifest and config files.

**1a. Language and Runtime Detection**

Check for manifest files to identify the primary language(s):

| Manifest File | Language/Runtime |
|---------------|-----------------|
| `package.json` | Node.js / TypeScript |
| `requirements.txt` / `pyproject.toml` / `Pipfile` / `setup.py` | Python |
| `pom.xml` / `build.gradle` / `build.gradle.kts` | Java / Kotlin |
| `Gemfile` | Ruby |
| `go.mod` | Go |
| `composer.json` | PHP |
| `Cargo.toml` | Rust |
| `*.csproj` / `*.fsproj` | .NET (C# / F#) |

If multiple manifest files exist, the project is polyglot — note all detected languages.

**1b. Framework Detection**

Read the manifest files and entry points to identify the framework(s) in use:

- **Node.js**: Express, Koa, Fastify, NestJS, Hapi, Restify
- **Python**: Flask, Django, FastAPI, Tornado, Sanic, Starlette
- **Java**: Spring Boot, Micronaut, Quarkus, Jakarta EE, Dropwizard
- **Ruby**: Rails, Sinatra, Hanami, Grape
- **Go**: Gin, Echo, Fiber, Chi, net/http (stdlib)
- **PHP**: Laravel, Symfony, Slim, Lumen, CodeIgniter
- **Rust**: Actix-web, Axum, Rocket, Warp, Tide
- **.NET**: ASP.NET Core, Blazor, Minimal APIs

**1c. Running Services Detection**

Use the Bash tool to probe common development ports for live HTTP services:

```
Ports to probe: 3000, 3001, 4000, 5000, 5173, 8000, 8080, 8443, 9000
Command: curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://localhost:PORT/
Running if: HTTP status is 200, 301, 302, 403, or 404
Not running if: connection refused or timeout
```

Also check for HTTPS on ports 443, 8443.

**1d. API Specification Detection**

Search the project for API specification files:
- OpenAPI: `openapi.yaml`, `openapi.json`, `openapi.yml`
- Swagger: `swagger.yaml`, `swagger.json`, `swagger.yml`
- GraphQL: `schema.graphql`, `*.graphql`, `*.gql`
- RAML: `*.raml`
- Postman: `*.postman_collection.json`

**1e. Configuration File Detection**

Scan for infrastructure and configuration files:
- **Containers**: `Dockerfile`, `docker-compose.yml`, `docker-compose.yaml`, `.dockerignore`
- **CI/CD**: `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/config.yml`, `.travis.yml`, `bitbucket-pipelines.yml`
- **Environment**: `.env`, `.env.*`, `.env.local`, `.env.production`
- **Cloud IaC**: `terraform/`, `*.tf`, `cloudformation/`, `pulumi/`, `cdk.json`, `serverless.yml`
- **Security**: `.helmet`, `cors.json`, `csp.json`, security middleware configs

**1f. Source Structure Analysis**

Identify the project's code organization:
- Route/controller files (where HTTP handlers are defined)
- Middleware files (authentication, authorization, validation)
- Model/schema files (data structures, database schemas)
- Configuration files (app settings, database connections)
- Test files (existing security tests)

### Step 2: Skill Selection

Based on the detection results from Step 1, determine which sub-skills are applicable:

| Skill | Condition | Category |
|-------|-----------|----------|
| `secrets-scanner` | Any text files exist in the project | Always |
| `llm-sast-scanner` | Source code files exist in a supported language | Always |
| `dependency-audit` | At least one manifest or lock file found | Conditional |
| `security-config-review` | Docker, CI/CD, cloud, or framework configuration files found | Conditional |
| `api-contract-testing` | API specification file found OR a live server detected | Conditional |
| `dast-scanner` | A live HTTP server detected on a probed port | Conditional |
| `compliance-mapper` | Any findings produced by the above skills | Always (runs last) |

**Before proceeding, display the detection results and selected skills to the user:**

```
## Project Detection Results

| Attribute | Detected |
|-----------|----------|
| Language(s) | {languages} |
| Framework(s) | {frameworks} |
| Package Manager | {package_manager} |
| Running Services | {ports or "None detected"} |
| API Specifications | {specs or "None found"} |
| Config Files | {list of config files found} |
| Source Structure | {summary of code organization} |

## Skills Selected for Execution

| # | Skill | Reason |
|---|-------|--------|
| 1 | secrets-scanner | Always runs |
| 2 | llm-sast-scanner | {language} source code detected |
| ... | ... | ... |

```

Use the AskUserQuestion tool to confirm the detection results and skill selection with the user before proceeding to Step 3.

### Step 3: Sequential Skill Execution

Run selected skills in this optimal order (fastest and most critical first):

1. **`secrets-scanner`** — Fast scan, catches critical credential leaks immediately
2. **`llm-sast-scanner`** — Comprehensive source code analysis across all vulnerability classes
3. **`dependency-audit`** — Check packages against CVE databases
4. **`security-config-review`** — Review infrastructure and framework configurations
5. **`api-contract-testing`** — Validate API behavior against specifications (if spec found or server running)
6. **`dast-scanner`** — Active probing against running endpoints (most time-intensive, requires live server)
7. **`compliance-mapper`** — Aggregate all findings and map to compliance frameworks (always runs last)

**Execution process for each skill:**

1. Use the Read tool to load the skill's `SKILL.md` file from `.claude/skills/{skill-name}/SKILL.md`
2. Follow the workflow defined in that skill's SKILL.md
3. Collect all findings in a structured format (ID, title, severity, location, evidence, remediation)
4. Track execution status: completed, skipped (condition not met), or failed (error during execution)
5. Note the finding count per severity level

**Between skills**, provide a brief progress update:

```
[2/7] SAST Scanner complete — found X findings (C critical, H high, M medium, L low)
[3/7] Starting Dependency Audit...
```

### Step 4: Findings Aggregation

After all skills have executed, aggregate and normalize the findings.

**4a. Deduplication**

Apply deduplication rules (see `references/report_format.md` for full logic):
- Same CWE + same file:line from different skills → merge into single finding, note all source skills
- Same vulnerability type at different locations → keep separate (each is independently exploitable)
- SAST finding + DAST confirmation of same issue → merge, mark confidence as "Confirmed"
- Dependency CVE + SAST confirming vulnerable function usage → merge, note "Vulnerable function confirmed in use"

**4b. Correlation and Confidence**

Boost confidence when multiple skills corroborate:
- Single skill finding → confidence: "Likely"
- Two skills confirming → confidence: "Confirmed"
- SAST + DAST confirming → confidence: "Confirmed (static + dynamic)"

**4c. Severity Normalization**

Ensure consistent severity across all skills:
- Use a unified Critical / High / Medium / Low / Info scale
- Apply severity escalation: if 3+ High findings exist, escalate overall risk to Critical
- Corroborated findings (multi-skill confirmation) → increase severity by one level (up to Critical)

**4d. Counting**

Tally final deduplicated findings by severity:
- Total Critical, High, Medium, Low, Informational
- Determine overall risk rating based on the highest individual finding severity (with escalation rules)

### Step 5: Unified Report Generation

Produce a single comprehensive report following the structure in `references/report_format.md`.

**Section 1: Executive Summary**

```
# Security Audit Report

## Executive Summary

| Attribute | Value |
|-----------|-------|
| **Project** | {name} |
| **Stack** | {language} / {framework} |
| **Scan Date** | {date} |
| **Skills Executed** | {count} of {total available} |
| **Overall Risk** | {Critical/High/Medium/Low} |

### Finding Totals

| Critical | High | Medium | Low | Info |
|----------|------|--------|-----|------|
| X | Y | Z | W | V |

### Top 3 Critical Issues

1. **SEQ-001**: {one-line description} — {location}
2. **SEQ-002**: {one-line description} — {location}
3. **SEQ-003**: {one-line description} — {location}
```

**Section 2: Detection Summary**

Table showing what was detected and which skills were run, including any skills that were skipped and why.

**Section 3: Findings (grouped by severity)**

For each finding, present:

- **ID**: SEQ-001, SEQ-002, etc. (sequential across all skills)
- **Title**: One-line vulnerability description
- **Severity**: Critical / High / Medium / Low / Info
- **Confidence**: Confirmed / Likely / Possible
- **Source**: Which skill(s) identified this finding
- **Location**: file:line for code issues, endpoint URL for runtime issues
- **Evidence**: Code snippet, request/response pair, or configuration excerpt
- **Impact**: What an attacker can achieve by exploiting this vulnerability
- **Framework References**:
  - OWASP Top 10 category (e.g., A03:2021 Injection)
  - CWE ID (e.g., CWE-89: SQL Injection)
  - NIST 800-53 control (e.g., SI-10: Information Input Validation)
  - PCI DSS requirement (e.g., 6.5.1: Injection Flaws)
- **Context-Aware Remediation**:
  - Reference the exact file and line where the fix should be applied
  - Use the project's detected language, framework, and library versions
  - Show before/after code using the project's actual patterns and imports
  - If the project contains secure counterparts (e.g., `// SECURE VERSION:`), reference them
  - Suggest framework-native solutions (e.g., `helmet()` for Express, `csrf_protect` for Django)
  - Start with the simplest fix, then mention more comprehensive alternatives
- **Effort Estimate**: Low / Medium / High

**Section 4: Compliance Scorecard**

```
### OWASP Top 10 (2021)

| Category | Status | Finding Count |
|----------|--------|---------------|
| A01: Broken Access Control | {PASS/FAIL/N/A} | X |
| A02: Cryptographic Failures | {PASS/FAIL/N/A} | X |
| ... | ... | ... |

### CWE Top 25

Matched: X of 25 most dangerous software weaknesses

### NIST 800-53

| Control Family | Findings |
|----------------|----------|
| AC (Access Control) | X |
| ... | ... |

### PCI DSS v4.0

| Requirement | Status |
|-------------|--------|
| 6.2.4: Software engineering techniques | {PASS/FAIL/N/A} |
| ... | ... |
```

**Section 5: Remediation Roadmap**

Prioritize fixes by impact and effort:

| Priority | Criteria | Action |
|----------|----------|--------|
| **P1 — Immediate** | Critical severity + Low effort | Fix now, these are quick wins with maximum impact |
| **P2 — Short-term** | High severity, or Critical + High effort | Schedule for current sprint |
| **P3 — Medium-term** | Medium severity | Plan for next sprint or release cycle |
| **P4 — Long-term** | Low severity, architectural changes | Add to backlog, address during refactoring |

List each finding under its priority tier with the specific remediation action.

**Section 6: Gap Analysis**

Document what was NOT tested and why:

- Skills that were skipped (e.g., "DAST scanner skipped — no running server detected on probed ports")
- Vulnerability classes not fully covered (e.g., "Business logic flaws require manual review")
- Recommended follow-up actions:
  - Start the application server and re-run with DAST enabled
  - Add API specification files for contract testing
  - Perform manual penetration testing for logic flaws
  - Review third-party integrations not covered by automated scanning
  - After applying fixes, run `/remediation-validator` to confirm vulnerabilities are resolved and detect regressions

