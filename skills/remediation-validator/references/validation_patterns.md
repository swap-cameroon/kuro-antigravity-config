# Common Incomplete Fix Patterns

This reference catalogs patterns where a security fix appears correct but leaves the vulnerability partially
or fully exploitable. When validating a remediation, check the fix against these patterns to catch common
mistakes.

---

## SQL Injection Partial Fixes

### Parameterized main query but string-concatenated ORDER BY
The developer parameterizes the WHERE clause but dynamically builds ORDER BY using string concatenation.
ORDER BY does not accept parameters in most databases, so developers often skip it. The fix must use an
allowlist of valid column names instead.
```
-- Looks fixed but isn't:
query = "SELECT * FROM users WHERE id = ? ORDER BY " + sortColumn
-- Correct approach:
ALLOWED_SORTS = {"name", "email", "created_at"}
if sortColumn not in ALLOWED_SORTS: sortColumn = "id"
query = "SELECT * FROM users WHERE id = ? ORDER BY " + sortColumn
```

### Parameterized one handler but not similar handlers in same file
A file with multiple route handlers may have the fix applied to the reported handler but identical
vulnerable patterns in adjacent handlers. Always check every query in the same file.

### Used ORM but bypassed with raw query in edge case
The developer migrated to an ORM for standard queries but kept a raw query for a "complex" query,
search, or reporting feature. The raw query often lacks parameterization.

### Escaped input instead of parameterizing
Using escape functions (e.g., `mysql_real_escape_string`, `escapeSingleQuotes`) instead of parameterized
queries. Escaping can be bypassed with character set tricks, encoding attacks, or future changes that
remove the escaping step. Parameterized queries are the only reliable fix.

### Fixed SELECT but not INSERT/UPDATE/DELETE in same endpoint
The same endpoint or handler may perform multiple query types. A fix applied to the SELECT query may
leave INSERT, UPDATE, or DELETE queries in the same function vulnerable.

### Allowlisted some inputs but not all injection points
The developer validates or sanitizes one parameter but the same endpoint accepts other parameters that
are also injected into queries. Check all parameters flowing into SQL context, not just the one reported.

### Used LIKE with parameterized value but no wildcard escaping
Even with parameterized LIKE queries, user input containing `%` or `_` can manipulate query behavior.
While not classic SQLi, it can cause information disclosure or denial of service.

---

## XSS Partial Fixes

### Escaped in HTML context but not in JavaScript context
HTML entity encoding (`&lt;`, `&gt;`) prevents XSS in HTML body but not inside `<script>` tags,
event handlers (`onclick`), or JavaScript template literals. Each context requires its own encoding.

### Used HTML encoding but not URL encoding for href attributes
Values placed in `href` or `src` attributes need URL encoding in addition to HTML encoding.
A value like `javascript:alert(1)` is not prevented by HTML entity encoding alone.

### Fixed server-rendered XSS but not DOM-based XSS
The server-side template is now safe, but client-side JavaScript reads from `location.hash`,
`document.referrer`, or URL parameters and inserts into the DOM without sanitization.

### Applied DOMPurify but configured with dangerous allowlisted tags
DOMPurify or similar sanitizers can be configured to allow tags like `<iframe>`, `<object>`,
`<embed>`, `<svg>`, or `<math>` which can execute JavaScript. Check the sanitizer configuration.

### Escaped in one template but not in another rendering the same data
The same data may be rendered in multiple templates or views. The fix applied to one template
does not protect other templates that render the same data.

### Fixed reflected XSS but not stored XSS (or vice versa)
The same input may be both reflected immediately and stored for later display. Fixing the
reflection point does not fix the stored variant. Check the full data flow.

### Added CSP but with unsafe-inline
Content Security Policy with `unsafe-inline` does not prevent inline script injection.
The CSP must use nonces or hashes for inline scripts to be effective.

### Sanitized on input but not on output
Input sanitization can be bypassed by data that enters through other channels (APIs, database
imports, admin interfaces). Output encoding at render time is the reliable defense.

---

## Authentication Partial Fixes

### Added rate limiting to login but not to password reset
Password reset, account recovery, MFA verification, and API token endpoints are all authentication
surfaces that need rate limiting. Protecting only the login endpoint leaves other vectors open.

### Added bcrypt but didn't migrate existing passwords
New passwords are hashed with bcrypt but existing users still have MD5/SHA-1/plaintext passwords
in the database. A migration strategy is needed: either force password resets or re-hash on next login.

### Added JWT expiry but didn't implement token rotation
JWTs now expire, but there's no refresh token mechanism. Users are forced to re-authenticate
frequently, or the expiry is set very long (days/weeks) making it nearly useless.

### Added auth middleware but missed some routes
Auth middleware is applied to most routes but specific routes (often admin, debug, healthcheck,
or API documentation endpoints) are excluded. Check every route registration.

### Strengthened password policy for new users but not existing
Password complexity requirements only apply at registration. Existing users with weak passwords
are not prompted to update. Add enforcement at login time for existing users.

### Added session invalidation on logout but not on password change
When a user changes their password, all existing sessions should be invalidated. Otherwise,
a compromised session remains valid after the user "secures" their account.

### Added MFA but the enrollment flow is bypassable
MFA is required but the enrollment step can be skipped by directly navigating to the
post-authentication URL or by manipulating the enrollment state.

### Token stored in localStorage instead of httpOnly cookie
Moving from no auth to token-based auth is good, but storing the token in localStorage
makes it accessible to XSS. Use httpOnly cookies for token storage.

---

## Access Control Partial Fixes

### Added ownership check but used client-supplied user ID
The check compares `request.body.userId === resource.ownerId` instead of extracting the user ID
from the authenticated session/token. Attackers can supply any user ID in the request body.

### Added role check but case-sensitive comparison
Comparing `user.role === "Admin"` when the database stores `"admin"`. Or using string comparison
when roles are stored as integers. Always normalize before comparing.

### Fixed IDOR on GET but not on PUT/DELETE for same resource
The GET endpoint checks ownership but the PUT or DELETE endpoint for the same resource does not.
All CRUD operations on a resource must enforce the same access control.

### Added auth to /admin/users but not to /admin/users/:id
Route-level access control must cover all sub-routes. A wildcard or middleware approach is more
reliable than per-route decoration.

### Fixed path traversal with string replacement but not normalization
Replacing `../` with empty string can be bypassed: `....//` becomes `../` after replacement.
Use path normalization (`path.resolve`, `realpath`) and verify the result is within the allowed directory.

### Added file extension check but allowed double extensions
Checking for `.jpg` allows `.php.jpg` if the server processes by first extension. Check the
full filename and use allowlists rather than denylists.

### Authorization check in frontend only
Added role/permission checks in the UI (hiding buttons, disabling fields) but the API endpoint
still allows unauthorized access. Authorization must be enforced server-side.

### Horizontal privilege escalation still possible
Added vertical access control (role-based) but users with the same role can still access each
other's resources. Both horizontal and vertical controls are needed.

---

## SSRF Partial Fixes

### Blocklisted 127.0.0.1 but not other loopback representations
`localhost`, `0.0.0.0`, `::1`, `0x7f000001`, `2130706433`, `017700000001`, `127.1`, and
`127.0.0.1.nip.io` all resolve to loopback. The fix must resolve the hostname and check the
IP address, not match against a string list.

### Checked hostname at validation time but not at fetch time (DNS rebinding)
The hostname resolves to a safe IP during validation, then the DNS record is changed to an
internal IP before the actual request. The fix must pin the resolved IP or re-validate after resolution.

### Blocked http:// but not other schemes
`gopher://`, `file://`, `dict://`, `ftp://`, `ldap://`, and `tftp://` can all be used for SSRF.
Use an allowlist of permitted schemes rather than blocking known-bad ones.

### Used regex to check domain but regex is bypassable
`/^https:\/\/example\.com/` matches `https://example.com.attacker.com`. Domain validation
must parse the URL properly and compare the exact hostname, not use regex prefix matching.

### Blocked internal IPs but not cloud metadata
`169.254.169.254` (AWS/GCP/Azure metadata), `100.100.100.200` (Alibaba), and
`fd00:ec2::254` (AWS IMDSv2) are not in RFC 1918 ranges but provide internal-only services.

### Added URL validation but followed redirects to blocked destinations
The initial URL passes validation but the server follows a 301/302 redirect to an internal IP.
Either disable redirects or re-validate each redirect destination.

### Used DNS resolution check but vulnerable to TOCTOU
Time-of-check vs time-of-use: DNS resolves to a safe IP, then between check and fetch, the
attacker changes the DNS record. Use connection-level IP pinning.

---

## Cryptographic Partial Fixes

### Upgraded to SHA-256 but still no salt
SHA-256 without a salt is still vulnerable to rainbow table attacks. Password hashing must use
bcrypt, scrypt, or argon2 which include salting automatically.

### Added encryption but stored the key alongside the data
The encryption key is in the same file, same database table, same environment, or same
repository as the encrypted data. Key management must separate keys from data.

### Used AES but with ECB mode
ECB mode encrypts identical plaintext blocks to identical ciphertext blocks, leaking patterns.
Use GCM (preferred) or CBC with HMAC for authenticated encryption.

### Used Math.random() for security-sensitive tokens
`Math.random()` (JavaScript), `random.random()` (Python), `rand()` (PHP/C) are not
cryptographically secure. Use `crypto.randomBytes()`, `secrets.token_hex()`, or equivalent.

### Added HTTPS but no HTTP redirect
The application supports HTTPS but still serves HTTP. Without a redirect (and HSTS header),
users connecting via HTTP are vulnerable to MITM attacks.

### Encrypted data at rest but logged plaintext
Data is encrypted in the database but debug/audit logs, error messages, or monitoring systems
capture the plaintext. Check all logging paths for sensitive data exposure.

### Used proper algorithm but with insufficient key size
AES-128 when AES-256 is required by policy, RSA-1024 instead of RSA-2048+, or ECDSA with
a curve smaller than P-256. Check key sizes against current recommendations.

### Hardcoded initialization vector (IV) or nonce
Using a static IV with CBC mode or reusing a nonce with GCM mode breaks the security guarantees.
IVs must be random and nonces must never repeat for the same key.

---

## Configuration Partial Fixes

### Added helmet but disabled key protections
`helmet({ contentSecurityPolicy: false })` or `helmet({ xssFilter: false })` negates the
protection those features provide. Check which helmet options are disabled and why.

### Restricted CORS origin but kept credentials with wildcard
`Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true` is invalid per
spec, but some browsers handle it inconsistently. An explicit origin with credentials is required.

### Removed debug endpoint but left similar endpoints accessible
Removed `/debug` but `/info`, `/config`, `/status`, `/healthz`, `/metrics`, or `/swagger`
may still expose sensitive information without authentication.

### Set secure cookie flags on session cookie but not auth cookie
Multiple cookies may be in use. All cookies containing sensitive data need `Secure`, `HttpOnly`,
and `SameSite` flags, not just the primary session cookie.

### Added .gitignore but didn't rotate committed secrets
Adding `.env` to `.gitignore` prevents future commits but the secret is still in git history.
The secret must be rotated (new value generated) and git history optionally cleaned.

### Added error handler but leaks info in development mode
The error handler returns generic messages in production but `NODE_ENV=development` (or
equivalent) causes stack traces, query details, or internal paths to be returned.

### Set security headers in app but reverse proxy overrides them
The application sets `X-Frame-Options` but nginx/Apache/CDN sends a different value. The
last header wins in most browsers. Check the full response chain.

### CORS allows all subdomains
`*.example.com` allows any subdomain including potentially compromised or user-controlled
subdomains. Restrict to specific trusted subdomains.

---

## Dependency Partial Fixes

### Upgraded package but pinned to still-vulnerable version
Updated from 2.0.0 to 2.0.5 when the fix is in 2.1.0. Always verify the specific version
that patches the CVE, not just "a newer version".

### Updated direct dependency but transitive dependency still vulnerable
The direct dependency is updated but it still depends on a vulnerable version of a transitive
dependency. Check `npm ls <package>`, `pip show`, or equivalent to verify the entire tree.

### Removed vulnerable package but replaced with equally vulnerable alternative
Swapped one XML parser for another that has the same XXE vulnerability, or replaced one
HTTP client with another that has the same SSRF characteristics.

### Updated package.json but didn't regenerate lock file
The manifest declares a safe version but the lock file still resolves to the old vulnerable
version. Run the package manager's install/update command and verify the lock file.

### Fixed one CVE but package has other unpatched CVEs
A package may have multiple CVEs. Fixing one does not fix the others. Check the full
vulnerability list for the package, not just the one that was reported.

### Upgraded to a version with breaking security changes
The new version changed security defaults (e.g., auto-escaping became opt-in instead of
default). The upgrade "fixes" the reported CVE but the application code assumes the old behavior.

---

## Logging and Monitoring Partial Fixes

### Added logging for failed logins but not successful ones
Cannot detect account takeover if only failed attempts are logged. Successful authentications,
especially from new IPs or devices, must also be logged.

### Added audit log but logs are world-readable
Audit logs contain sensitive information (usernames, actions, IP addresses) and must have
restricted access. Check file permissions and log storage access controls.

### Added logging but included sensitive data in entries
Log entries contain passwords, API keys, session tokens, or PII. This creates a new
vulnerability (CWE-532: Information Exposure Through Log Files).

### Added event logging but without user/session context
Logs record "record deleted" but not "who deleted it". Security logs must include the
authenticated user, session ID, source IP, and timestamp.

### Added logging but no log integrity protection
Logs can be modified or deleted by an attacker who gains access. Consider append-only storage,
log signing, or shipping logs to a separate system.

### Added monitoring alerts but only for known attack patterns
Signature-based detection misses novel attacks. Include anomaly-based alerts for unusual
patterns (e.g., sudden increase in 403 responses, unusual data access volumes).
