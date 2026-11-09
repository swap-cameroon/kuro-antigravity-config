# Regression Detection Patterns

This reference catalogs patterns where security fixes introduce new vulnerabilities or where
code changes inadvertently weaken existing security controls. When validating a remediation,
always check for these regression patterns in the changed code.

---

## Refactoring Regressions

### Code moved to new file without security checks
During refactoring, a function is extracted to a utility module or moved to a different file.
The security checks (input validation, auth verification, output encoding) were in the calling
code, not in the function itself. The new location lacks these checks.

**Detection**: Compare the security-relevant code around the old location with the new location.
Look for middleware, decorators, wrapper functions, or inline checks that were not carried over.

### Function signature changed, now accepts unsanitized input
The refactored function has a different parameter signature. Previously, sanitized data was passed
in. Now, the function accepts raw input and no sanitization step exists in the new call chain.

**Detection**: Trace the data flow from the entry point (route handler, API endpoint) to the
refactored function. Verify sanitization still occurs somewhere in the chain.

### Middleware chain reordered
Auth or validation middleware runs after the handler instead of before, or a new middleware
is inserted between the auth check and the handler that modifies the request context.

**Detection**: Review the middleware registration order. In Express-style frameworks, check
`app.use()` ordering. In Django, check `MIDDLEWARE` list order. In Spring, check filter chains.

### Error handling refactored -- catch block drops security check
A try-catch block is restructured. The catch block previously applied a security fallback
(deny access, sanitize output) but the new error handling path does not.

**Detection**: Compare error handling paths before and after. Ensure security-critical operations
in catch/finally blocks are preserved.

### Database queries extracted to utility module
Queries are moved to a data access layer or repository pattern. The parameterization was done
inline in the route handler, not in the query itself. The new utility module uses string
concatenation because "it's an internal function."

**Detection**: Check every query in the new utility module for parameterization. Internal
functions must be as secure as public-facing ones.

### Shared validation function modified for new use case
A validation function is extended to handle a new input type. The modification weakens the
validation for existing use cases (e.g., adding a new allowed character that breaks existing
security assumptions).

**Detection**: Check all callers of the modified function, not just the new one. Verify the
change doesn't weaken validation for existing callers.

### Interface or type change removes security constraint
A type annotation or interface is changed in a way that removes a security constraint.
For example, changing a validated type to `any` or `string` or removing a max-length constraint.

**Detection**: Compare type definitions before and after. Check if any security-relevant
constraints (length limits, format validation, allowed values) were removed.

---

## Fix-Induced Vulnerabilities

### Added allowlist but the check is bypassable
File type allowlisting that checks the extension with simple string matching:
- Double extension: `malware.php.jpg` passes `.jpg` check but executes as PHP
- Null byte: `malware.php%00.jpg` may truncate at the null byte on some systems
- Case sensitivity: `.PHP` bypasses a check for `.php`
- Content-type mismatch: file has `.jpg` extension but contains PHP code

**Detection**: Check if the allowlist validation handles edge cases. Look for extension
extraction logic and verify it handles multiple dots, null bytes, and case.

### Added input validation but regex is vulnerable to ReDoS
The validation regex contains nested quantifiers or overlapping patterns that cause exponential
backtracking on crafted input:
- `/(a+)+$/` -- catastrophic backtracking on "aaa...!" 
- `/^(([a-z])+\.)+[A-Z]{2,}$/` -- email-like regex with nested groups
- `/(\w+\s?)*$/` -- word matching with optional spaces

**Detection**: Check for regex patterns with nested quantifiers `(a+)+`, `(a*)*`, `(a+)*`,
or alternation within repetition `(a|b|ab)*`. Test with long strings of near-matches.

### Added rate limiting but implementation leaks timing information
Rate limiting based on response time differences can leak whether a username exists
(faster rejection for nonexistent users). Or the rate limiter itself is vulnerable to
resource exhaustion.

**Detection**: Check if rate limiting returns different response times for different failure
modes. Verify the rate limiter doesn't consume excessive memory (e.g., storing every IP).

### Added CORS restrictions but origin reflection bug
The CORS implementation reads the Origin header and reflects it back if it's in the allowlist,
but the allowlist check is flawed:
- `origin.endsWith("example.com")` matches `evilexample.com`
- `origin.includes("example.com")` matches `example.com.evil.com`
- Allowlist includes `null` origin (bypassable via sandboxed iframes)

**Detection**: Check the origin validation logic for substring matching, endsWith, includes,
or regex patterns that could match unintended origins.

### Added CSP but with unsafe-inline or unsafe-eval
Content Security Policy that includes `unsafe-inline` in `script-src` does not prevent XSS.
`unsafe-eval` allows `eval()`, `Function()`, and `setTimeout("string")` which can execute
injected code.

**Detection**: Parse the CSP header value. Flag any directive containing `unsafe-inline` or
`unsafe-eval`. Also check for overly broad sources like `*` or `https:`.

### Added authentication but token in URL query parameters
Authentication tokens passed as query parameters appear in:
- Server access logs
- Browser history
- Referrer headers sent to external sites
- Proxy logs and CDN caches

**Detection**: Check if authentication tokens, API keys, or session IDs are passed as URL
query parameters instead of headers or cookies.

### Added encryption but using deprecated algorithm
The fix introduces encryption but uses a weak or deprecated algorithm:
- DES, 3DES, RC4, Blowfish for symmetric encryption
- MD5 or SHA-1 for integrity checking
- RSA with PKCS#1 v1.5 padding (vulnerable to Bleichenbacher)
- Any custom or "homegrown" encryption scheme

**Detection**: Check the algorithm specification in encryption function calls. Look for
algorithm name strings, constants, or enum values.

### Added logging but introduced log injection vulnerability
Log entries include unsanitized user input. An attacker can inject newlines and fake log
entries, manipulate log analysis, or exploit log viewing tools (ANSI escape codes in terminals,
HTML injection in web-based log viewers).

**Detection**: Check if user-controlled data is written to logs without sanitization.
Look for newline characters, ANSI escape sequences, or HTML that could be injected.

### Input validation added but only on one code path
Validation is added to the web form submission handler but the same data can be submitted
via API endpoint, file upload, import function, or admin interface without validation.

**Detection**: Identify all entry points that write to the same data store or call the same
processing function. Verify validation exists on every path.

---

## Dependency Update Regressions

### Major version upgrade breaks existing security measures
A major version change in a framework or library may change security defaults:
- Express 3 to 4: middleware changes
- Angular.js to Angular: different XSS protection model
- Django version upgrades: CSRF handling changes
- ORM upgrades: query building behavior changes

**Detection**: Check the changelog for the version range being upgraded. Look for
"BREAKING CHANGES" and "SECURITY" sections. Verify existing security code still works.

### Library changed default behavior
The updated library changed from opt-in to opt-out for a security feature, or vice versa:
- Template engine previously auto-escaped by default, now requires explicit escaping
- HTTP client previously verified TLS certificates, new version doesn't
- ORM previously parameterized by default, new version uses raw queries for performance

**Detection**: Check the library's migration guide for changed defaults. Test existing
security-sensitive code paths with the new version.

### New API surface with old security configuration
The library update introduces a new API. Existing security configuration (middleware,
interceptors, hooks) was written for the old API and doesn't apply to the new one.

**Detection**: Check if the application uses any deprecated API that has a new replacement.
Verify security configuration applies to both old and new API surfaces.

### Transitive dependency conflict
Updating package A pulls in a newer version of shared dependency C, but package B requires
an older version. The package manager resolves this by installing multiple versions, and
the application may use the vulnerable version at runtime.

**Detection**: Check for duplicate packages in the dependency tree with different versions.
Verify which version is actually used at runtime.

### Dependency removed but functionality reimplemented insecurely
A dependency is removed (to reduce attack surface) and its functionality is reimplemented
in application code. The reimplementation lacks the security hardening that the library
provided (e.g., reimplementing JWT parsing without signature verification).

**Detection**: If a security-relevant dependency was removed, check the replacement code
for common implementation mistakes.

---

## Configuration Change Regressions

### Tightened one setting but loosened another
To make the application work with a tightened security setting, another setting was relaxed:
- Added CSP but set `X-Frame-Options` to `ALLOW-FROM` (weaker than CSP frame-ancestors)
- Restricted CORS but disabled CSRF protection ("CORS handles it")
- Added authentication but disabled rate limiting ("auth is enough")

**Detection**: Diff all configuration files, not just the one that was reported. Check for
compensating changes that weaken security.

### Security headers conflict between layers
The application sets a security header but a reverse proxy, CDN, or load balancer sets a
different value. Depending on the header, the last value wins or they're merged:
- Duplicate `Content-Security-Policy` headers may be merged or only one applied
- `X-Frame-Options` set in both nginx and application -- which wins depends on the browser
- `Strict-Transport-Security` set with different max-age values at different layers

**Detection**: If the infrastructure uses multiple layers (app, reverse proxy, CDN), check
for conflicting header values across layers. Test the actual response headers.

### Secrets moved to environment variables but .env committed
Secrets are moved from hardcoded values to environment variables (good), but the `.env`
file containing those variables is committed to the repository (bad). Or the `.env.example`
file contains actual secret values instead of placeholders.

**Detection**: Check if `.env`, `.env.local`, `.env.production`, or similar files are in the
repository. Check if `.env.example` contains real secrets instead of placeholder values.

### Docker USER directive caused permission issues, reverted entirely
The fix added a non-root USER directive to the Dockerfile, but the application needs write
access to certain directories. Instead of fixing the specific permission, the entire USER
directive was removed, running as root again.

**Detection**: Check Dockerfile for USER directives. If the fix involved container hardening,
verify the directive is still present and the permission issue was solved properly.

### Environment-specific configuration inconsistency
The fix is applied in the development configuration but not in production, or vice versa.
Or staging has a different configuration that doesn't include the fix.

**Detection**: Check all environment-specific config files (production, staging, development).
Verify the security fix is applied consistently across all environments.

---

## Detection Techniques

### Total finding count comparison
Run the same scan before and after the fix. If the total count increases, new findings were
introduced. If it stays the same but individual findings changed, a fix may have been offset
by a new issue.

### New findings in modified files
Run a targeted scan on all files touched by the fix. Any finding that wasn't in the original
report is a potential regression, even if it's a different vulnerability class.

### Security configuration diff
Diff all configuration files (not just the ones explicitly changed). Look for:
- Weakened security headers
- Removed middleware or decorators
- Changed authentication/authorization settings
- Modified CORS, CSP, or cookie settings
- Changed logging levels or destinations

### Adjacent code path testing
The fix modifies function A. Functions B and C call A or share code with A. Test B and C
to verify the fix didn't break their security properties:
- Shared utility functions that now behave differently
- Middleware that function A relied on but is no longer in the chain
- Database queries that function A's changes affect

### Dependency tree verification
After a dependency update:
1. Verify the lock file was regenerated
2. Check for new dependencies introduced transitively
3. Run a vulnerability scan on the new dependency tree
4. Check for duplicate package versions that could cause version confusion

### Git history analysis for secret removal
When a secret is removed from code:
1. Check `git log --all -p -S '<secret_value>'` to find all commits containing the secret
2. Verify the secret doesn't exist in any branch, tag, or stash
3. Confirm the secret has been rotated (new value generated and deployed)
4. Check if the secret appears in CI/CD logs, error logs, or monitoring systems

### Middleware and filter chain verification
After changes to middleware, filters, or interceptors:
1. Map the complete chain for affected routes
2. Verify auth middleware still precedes handler functions
3. Check that new middleware doesn't short-circuit before security checks
4. Verify error handlers still apply security responses (e.g., generic error messages)

### Cross-endpoint consistency check
When a fix is applied to one endpoint:
1. Identify all endpoints that handle the same resource type
2. Verify the same fix is applied to all CRUD operations (GET, POST, PUT, DELETE)
3. Check related endpoints (e.g., fixing /api/users should also check /api/users/export)
4. Verify batch/bulk endpoints apply the same controls as single-resource endpoints
