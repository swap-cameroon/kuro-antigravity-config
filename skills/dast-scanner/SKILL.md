---
name: dast-scanner
description: Dynamic Application Security Testing - sends crafted HTTP requests to running web server endpoints to detect vulnerabilities
trigger: When user asks to dynamically test, probe, scan, attack, or pentest a running web application's HTTP endpoints
---

# DAST Scanner Skill

Perform Dynamic Application Security Testing against a running web application. This skill is **language-agnostic** -- it tests HTTP endpoints regardless of backend technology (Node.js, Python, Java, PHP, Go, Ruby, .NET, etc.).

## Workflow

### Step 1: Endpoint Discovery

Identify all available endpoints through multiple strategies:

1. **Source code analysis**: Read route definition files to extract endpoints.
   - Look for framework-specific routing patterns (Express `app.get()`, Flask `@app.route()`, Spring `@RequestMapping`, Laravel `Route::get()`, Gin `r.GET()`, Rails `resources`, ASP.NET `[HttpGet]`, etc.)
   - Search for files: `routes/*.js`, `urls.py`, `*Controller.*`, `router.*`, `api.*`, `openapi.*`, `swagger.*`
2. **OpenAPI/Swagger specs**: Use the Bash tool to fetch `/swagger.json`, `/openapi.json`, `/api-docs`, `/swagger-ui` via curl if the server is running.
3. **Index endpoint probing**: `GET /` and parse response for links and API references.
4. **Common path fuzzing**: Try well-known paths (`/api`, `/admin`, `/login`, `/health`, `/debug`, `/status`, `/graphql`, `/metrics`, `/env`, `/.env`, `/config`, `/robots.txt`, `/sitemap.xml`).
5. **HTTP method fuzzing**: For each discovered endpoint, test OPTIONS to enumerate allowed methods, then try GET, POST, PUT, PATCH, DELETE, HEAD.

Compile a complete endpoint map with: path, supported methods, expected parameters (query, body, header), and authentication requirements.

### Step 2: Payload Selection

Based on endpoint characteristics, use the Read tool to load the appropriate testing references:

| Endpoint Characteristic | Reference to Load |
|---|---|
| Accepts user input (forms, query params, JSON body) | `references/injection_testing.md` |
| Login, signup, password reset, auth-related | `references/auth_testing.md` |
| Takes IDs, accesses user-specific data | `references/access_control_testing.md` |
| Accepts URLs, fetches remote resources, webhooks | `references/ssrf_testing.md` |
| Any endpoint (baseline testing) | `references/config_testing.md` |
| Returns tokens, hashes, or sensitive data | `references/crypto_testing.md` |
| File upload or file path parameters | `references/access_control_testing.md` (path traversal section) |

### Step 3: Attack Execution

For each endpoint, use the Bash tool to send crafted payloads via `curl`. Follow these principles:

- **Multiple injection points**: Test query parameters, request body (JSON and form-encoded), HTTP headers (Host, Referer, User-Agent, X-Forwarded-For), and cookies.
- **Timing-based detection**: For blind vulnerabilities, use time-delay payloads and measure response time differences (e.g., `time curl ...` or compare against baseline).
- **Authentication states**: Test each endpoint both unauthenticated and with valid credentials (if available). Test with other users' credentials for access control issues.
- **Encoding variations**: Try raw payloads, URL-encoded, double-encoded, and Unicode variations.
- **Safe testing**: Prefer read-only probes. Avoid destructive operations (DELETE on real data, DROP TABLE). Use conditional payloads that detect without destroying (e.g., `SELECT` not `DELETE`, `id` not `rm`).

Use the Bash tool to execute `curl` with these standard flags:
```bash
# Standard request with full response details
curl -s -w "\nHTTP_CODE:%{http_code}\nTIME_TOTAL:%{time_total}\n" -D - "http://TARGET/endpoint"

# POST with JSON body
curl -s -X POST -H "Content-Type: application/json" -d '{"key":"PAYLOAD"}' "http://TARGET/endpoint"

# With authentication
curl -s -H "Authorization: Bearer TOKEN" "http://TARGET/endpoint"

# Timing measurement for blind testing
curl -s -o /dev/null -w "%{time_total}" "http://TARGET/endpoint?param=PAYLOAD"
```

### Step 4: Response Analysis

Analyze HTTP responses for vulnerability indicators:

- **Error messages revealing internals**: Stack traces, SQL error messages, file paths, framework versions, debug output
- **Unexpected data in responses**: Database records from other users, internal IPs, configuration values
- **Status code anomalies**: 200 where 401/403 expected (broken access control), 500 with detailed errors (information disclosure)
- **Timing differences**: Significantly slower responses may indicate blind SQL injection or SSRF connecting to internal services
- **Payload reflection**: Input reflected in response without sanitization (XSS indicators, though DAST focuses on server-side)
- **Missing security headers**: Absence of CSP, HSTS, X-Frame-Options, etc.
- **Data leakage patterns**: Sensitive data (passwords, tokens, PII) in responses that should not contain them

### Step 5: Report Generation

Produce a structured report. For each finding include:

1. **Severity**: Critical / High / Medium / Low / Info
2. **Title**: Brief description of the vulnerability
3. **OWASP Category**: Map to OWASP Top 10 2021 (A01-A10)
4. **Endpoint**: Exact URL, HTTP method
5. **Payload**: The exact request that triggered the vulnerability
6. **Evidence**: The response (or relevant portion) proving the vulnerability exists
7. **Impact**: What an attacker could achieve by exploiting this
8. **Remediation**: Specific, actionable fix recommendations appropriate to the detected backend technology

Format the report as a markdown table summary followed by detailed findings sections.

### Severity Classification

| Severity | Criteria |
|---|---|
| Critical | Remote code execution, SQL injection with data access, authentication bypass, SSRF to cloud metadata |
| High | Stored XSS, IDOR with sensitive data, privilege escalation, path traversal with file read |
| Medium | Reflected XSS, CSRF, information disclosure of internal paths, missing security headers on sensitive endpoints |
| Low | Version disclosure, verbose error messages, missing optional security headers |
| Info | Informational findings, best practice recommendations |

## Key Principles

- **Evidence-driven**: Every finding MUST include the exact curl command used and the relevant response excerpt proving the vulnerability. No theoretical or assumed vulnerabilities.
- **False positive awareness**: Distinguish between actual vulnerabilities and expected error responses. A 400 Bad Request with a generic error message is NOT a vulnerability. Verify findings with multiple payloads when uncertain.
- **Safe testing**: Never execute destructive operations against production data. Prefer `SELECT` over `DELETE`, `id` over `rm -rf`, `sleep` over `shutdown`. Always consider the impact of test payloads.
- **Authentication-aware**: Test both unauthenticated and authenticated access patterns. When credentials are available, test horizontal and vertical privilege boundaries.
- **Language-agnostic**: All testing is performed at the HTTP level. Payloads and detection patterns cover multiple backend technologies. Do not assume any specific server-side language.
