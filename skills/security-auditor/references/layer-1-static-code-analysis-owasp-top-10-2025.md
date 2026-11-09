## Layer 1 — Static Code Analysis (OWASP Top 10:2025)

Work through each OWASP 2025 category systematically. Skip sections clearly out of scope.

### A01 — Broken Access Control (OWASP #1, most critical)
*This is the #1 web vulnerability. Scrutinize every data access point.*

#### IDOR (Insecure Direct Object Reference)
Flag any endpoint that retrieves or modifies a resource using a user-supplied ID
without verifying ownership:
```python
# ❌ IDOR — no ownership check
def get_order(request, order_id):
    order = Order.objects.get(id=order_id)  # attacker changes order_id
    return JsonResponse(order.data)

# ✅ Ownership enforced
def get_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return JsonResponse(order.data)
```
Check: API endpoints, ORM queries, database queries, file downloads, report generation.

#### Multi-Tenancy Isolation
Flag any query that doesn't filter by `tenant_id`, `organization_id`, or equivalent:
```python
# ❌ Tenant data leak — all tenants' data returned
users = User.objects.filter(active=True)

# ✅ Tenant-scoped
users = User.objects.filter(active=True, tenant=request.tenant)
```
Check: Every ORM query in multi-tenant systems. Flag any `get_all()`, `findAll()`,
`SELECT *` without a tenant/org scope. Flag shared caches (Redis, Memcached) missing
tenant-prefixed keys.

#### Horizontal Privilege Escalation
User A accesses User B's resource at the same permission level:
- Flag: missing ownership check on any mutable resource (update, delete, share)
- Flag: predictable resource IDs (sequential integers, guessable patterns)
- Flag: UUIDs that leak in responses and can be reused in direct requests

#### Vertical Privilege Escalation
Regular user accesses admin functionality:
- Flag: role checks done only on the frontend (UI hiding != authorization)
- Flag: missing `@permission_required` / `IsAdminUser` / equivalent on admin endpoints
- Flag: role stored in JWT payload without server-side verification
- Flag: parameter-based role escalation (`?role=admin`, `?isAdmin=true`)

#### SSRF (Server-Side Request Forgery) — now part of A01:2025
Flag any code that fetches a URL supplied (directly or indirectly) by user input:
```python
# ❌ SSRF — user controls the URL
url = request.data.get('webhook_url')
response = requests.get(url)  # attacker sends: http://169.254.169.254/latest/meta-data/

# ✅ Allowlist-based validation
ALLOWED_DOMAINS = {'api.trusted.com', 'cdn.yourapp.com'}
parsed = urlparse(url)
if parsed.hostname not in ALLOWED_DOMAINS:
    raise ValidationError("Domain not allowed")
```
Flag parameters named: `url`, `uri`, `path`, `dest`, `destination`, `redirect`,
`target`, `link`, `callback`, `webhook`, `fetch`, `endpoint`, `proxy`, `image`.
Flag cloud metadata endpoint access: `169.254.169.254` (AWS/Azure), `metadata.google.internal` (GCP).
Flag URL scheme bypass: only allow `http`/`https`, block `file://`, `gopher://`, `dict://`.

#### CORS Misconfiguration
- Flag `Access-Control-Allow-Origin: *` on authenticated endpoints
- Flag `origin` header reflected back without validation
- Flag `Access-Control-Allow-Credentials: true` combined with wildcard origin

### A02 — Security Misconfiguration (OWASP #2, biggest mover in 2025)
- Flag `DEBUG = True` / `NODE_ENV !== 'production'` in production config
- Flag `SECRET_KEY` / `JWT_SECRET` hardcoded or using weak defaults
- Flag `ALLOWED_HOSTS = ['*']` in production
- Flag default admin credentials not changed
- Flag directory listing enabled on static file servers
- Flag missing security headers — check for all of:
  ```
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Content-Security-Policy: default-src 'self'
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=()
  ```
- Flag `X-Powered-By` / `Server` headers exposing technology stack
- Flag verbose error messages / stack traces returned in API responses
- Flag open cloud storage buckets (S3, GCS, Azure Blob) — check bucket policy configs
- Flag admin interfaces (`/admin`, `/django-admin`, `/_debug`) exposed without IP restriction

### A03 — Software Supply Chain Failures (NEW in 2025)
Run dependency audit:
```bash
npm audit --audit-level=high          # Node.js
pip-audit -r requirements.txt         # Python
safety check                          # Python alternative
```
- Flag: packages with known CVEs (Critical/High severity)
- Flag: packages not pinned to exact versions (floating `^` or `~` in production)
- Flag: packages with no recent maintenance (>2 years since last release)
- Flag: packages with very few downloads — supply chain substitution risk
- Flag: missing lockfile (`package-lock.json`, `yarn.lock`, `Pipfile.lock`)
- Flag: no SBOM (Software Bill of Materials) for production deployments
- Flag: CI/CD pipeline not verifying artifact integrity (checksums, signatures)
- Flag: `npm install` without `--ignore-scripts` in automated environments

### A04 — Cryptographic Failures
- Flag weak hashing algorithms for passwords: MD5, SHA1, SHA256 — use bcrypt/Argon2/scrypt
- Flag symmetric encryption with hardcoded IVs or reused nonces
- Flag weak random number generation (`Math.random()`, `random.random()`) for security tokens
- Flag short JWT secrets (< 256 bits)
- Flag JWT `algorithm: 'none'` — critical
- Flag JWT `alg` not explicitly verified on decode (algorithm confusion attack)
- Flag sensitive data (PII, passwords, tokens) stored in plaintext in DB, logs, or caches
- Flag HTTP used instead of HTTPS for any data transmission
- Flag weak TLS configuration (TLS 1.0/1.1 still enabled)
- Flag `SESSION_COOKIE_SECURE = False` / `httpOnly = false` on auth cookies

### A05 — Injection
#### SQL Injection
- Flag raw SQL with string concatenation or f-strings
- Flag ORM `raw()` / `execute()` with user input not parameterized
- Flag second-order injection: user data stored in DB, then used in a query later

#### Command Injection
- Flag `os.system()`, `subprocess.call()`, `exec()`, `eval()` with user input
- Flag shell=True in subprocess with user-controlled arguments

#### XSS (Cross-Site Scripting)
- Flag `innerHTML`, `dangerouslySetInnerHTML`, `document.write()` with user input
- Flag `|safe` template filter in Django/Jinja without explicit sanitization
- Flag `bypassSecurityTrustHtml()` in Angular without documented justification
- Flag reflected user input in HTML responses without encoding

#### Template Injection (SSTI)
- Flag user input rendered in Jinja2/Twig/Handlebars templates directly
- Flag dynamic template generation from user-supplied strings

#### LDAP / NoSQL / XML Injection
- Flag LDAP filter construction with user input
- Flag MongoDB `$where` with user data
- Flag XML parsers processing user-supplied XML without disabling external entities (XXE)

### A06 — Insecure Design
- Flag business logic that can be abused: price manipulation, discount stacking,
  quantity bypass, free trial abuse
- Flag password reset flows using predictable tokens or exposing user enumeration
- Flag missing rate limiting on sensitive operations (login, password reset, OTP)
- Flag race conditions in inventory/balance/quota operations (check-then-act patterns)
- Flag trust boundaries not defined (internal services assuming all callers are trusted)

### A07 — Authentication Failures
- Flag missing MFA for admin/privileged actions
- Flag session not invalidated on logout (token blacklisting missing)
- Flag session fixation (session ID not regenerated after login)
- Flag brute-force unprotected on login endpoints
- Flag "remember me" tokens with infinite expiry
- Flag credential stuffing protection missing (rate limiting + CAPTCHA)
- Flag account enumeration via different error messages (`"user not found"` vs `"wrong password"`)

### A08 — Data Integrity Failures
- Flag deserialization of untrusted data (pickle, Java ObjectInputStream, PHP unserialize)
- Flag unsigned software update mechanisms
- Flag integrity checks missing on plugin/extension loading
- Flag CI/CD pipelines pulling from mutable tags instead of pinned SHAs

### A09 — Security Logging & Alerting Failures
- Flag missing logs for: auth attempts, privilege escalations, data access, config changes
- Flag sensitive data (passwords, tokens, PII) logged in plaintext
- Flag logs not forwarded to a centralized system (SIEM)
- Flag no alerting configured on suspicious patterns
- Flag log injection: user input written to logs without sanitization

### A10 — Mishandling of Exceptional Conditions (NEW in 2025)
*Systems that break unsafely under stress or unexpected input.*
- Flag fail-open patterns: access control that defaults to ALLOW on exception
  ```python
  # ❌ Fail-open — exception bypasses the check
  try:
      if not user.has_permission('admin'):
          raise PermissionDenied()
  except Exception:
      pass  # continues without authorization
  ```
- Flag stack traces / internal paths / DB error messages returned to clients
- Flag missing input validation on edge cases (empty strings, null, negative numbers, boundary values)
- Flag missing timeouts on external calls (DB, HTTP, queue) — denial of service risk
- Flag null/undefined dereference that could bypass logic on error
