# API Authentication Enforcement Testing Reference

Comprehensive reference for testing authentication and authorization enforcement
on API endpoints. Use these techniques to verify that protected endpoints
correctly reject unauthorized access and that auth mechanisms are robust.

---

## Authentication Header Testing

### Missing Credentials

Send requests with no authentication at all. Every protected endpoint must reject these.

```bash
# No Authorization header
curl -s -o /dev/null -w "%{http_code}" http://target/api/protected

# Expected: 401 Unauthorized
# Finding if: 200 OK (auth bypass -- Critical)
```

### Empty Bearer Token

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer " \
  http://target/api/protected

# Expected: 401 Unauthorized
# Finding if: 200 OK (empty token accepted -- Critical)
```

### Malformed Token

```bash
# Random string
curl -s -H "Authorization: Bearer not-a-real-token" http://target/api/protected

# Truncated token (first half only)
curl -s -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9" http://target/api/protected

# Wrong auth scheme
curl -s -H "Authorization: Basic not-base64" http://target/api/protected

# Extra spaces
curl -s -H "Authorization:  Bearer  token" http://target/api/protected

# Expected: 401 Unauthorized for all
# Finding if: 200 OK or 500 Internal Server Error
```

### Expired Token

For JWT-based authentication, craft a token with an `exp` claim in the past:

```bash
# JWT with expired exp claim
# Header: {"alg":"HS256","typ":"JWT"}
# Payload: {"sub":"1","exp":1000000000}  (expired date)
curl -s -H "Authorization: Bearer <expired-jwt>" http://target/api/protected

# Expected: 401 Unauthorized
# Finding if: 200 OK (token expiration not enforced -- High)
```

### Valid Token for Wrong User

Test horizontal privilege escalation:

```bash
# User A's token accessing User B's resource
curl -s -H "Authorization: Bearer <user-a-token>" http://target/api/users/user-b-id/profile

# Expected: 403 Forbidden (not 200 with user B's data)
# Finding if: 200 OK with user B's data (IDOR -- Critical)
```

### Insufficient Role/Scope

Test vertical privilege escalation:

```bash
# Regular user token on admin endpoint
curl -s -H "Authorization: Bearer <regular-user-token>" http://target/api/admin/users

# Expected: 403 Forbidden
# Finding if: 200 OK (privilege escalation -- Critical)
```

---

## Token Validation Patterns

### JWT-Specific Tests

**Algorithm None Attack:**

Craft a JWT with `"alg": "none"` in the header. If accepted, the server is not
validating the signature at all.

```
Header: {"alg":"none","typ":"JWT"}
Payload: {"sub":"1","role":"admin"}
Signature: (empty)

Token: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0.
```

**Modified Claims:**

Take a valid JWT, decode the payload, modify claims (e.g., change `role` from
`user` to `admin`), re-encode without signing. If the server accepts this, it is
not verifying the signature.

**Algorithm Confusion:**

If the server uses RS256 (asymmetric), try sending a token signed with HS256
(symmetric) using the public key as the HMAC secret. This exploits CVE-2016-10555.

**Key ID (kid) Injection:**

If the JWT header contains a `kid` field, test for injection:
```json
{"alg":"HS256","kid":"../../etc/passwd"}
{"alg":"HS256","kid":"key' UNION SELECT 'secret'--"}
```

**JWK/JWKS Injection:**

Test if the server accepts a JWT with an embedded `jwk` header that contains
an attacker-controlled public key.

**Token Lifetime:**
- Check that `exp` claim is present and enforced
- Check that `iat` (issued at) is reasonable (not far in the future)
- Check that `nbf` (not before) is enforced if present
- Verify refresh tokens expire independently of access tokens

### API Key Tests

```bash
# Wrong API key
curl -s -H "X-API-Key: invalid-key-12345" http://target/api/resource

# API key in wrong location (header vs query)
curl -s "http://target/api/resource?api_key=valid-key"
# vs
curl -s -H "X-API-Key: valid-key" http://target/api/resource

# Revoked API key (if revocation is supported)
curl -s -H "X-API-Key: previously-valid-revoked-key" http://target/api/resource

# Expected: 401 for all invalid cases
```

### Session-Based Auth Tests

```bash
# Invalid session ID
curl -s -b "session=invalid-session-id" http://target/api/resource

# Session after logout (session fixation test)
# 1. Login and get session
# 2. Logout
# 3. Reuse the old session
curl -s -b "session=logged-out-session-id" http://target/api/resource

# Session ID format testing
curl -s -b "session=0" http://target/api/resource
curl -s -b "session=1" http://target/api/resource
curl -s -b "session=null" http://target/api/resource
curl -s -b "session=undefined" http://target/api/resource
curl -s -b "session=true" http://target/api/resource

# Expected: 401 for all
# Finding if: any returns 200 (session validation bypass -- Critical)
```

---

## Scope and Permission Testing

### Horizontal Access Control (IDOR)

Test that users cannot access other users' resources by manipulating identifiers:

```bash
# Sequential ID enumeration
curl -s -H "Authorization: Bearer <user-1-token>" http://target/api/users/1/data  # own data
curl -s -H "Authorization: Bearer <user-1-token>" http://target/api/users/2/data  # other user
curl -s -H "Authorization: Bearer <user-1-token>" http://target/api/users/3/data  # other user

# UUID guessing (less likely but test anyway)
curl -s -H "Authorization: Bearer <token>" http://target/api/documents/<other-user-uuid>

# Indirect references
curl -s -H "Authorization: Bearer <token>" http://target/api/orders?user_id=other-user-id
```

For each resource endpoint, verify that the response only contains data belonging
to the authenticated user. Flag any case where user A can read, modify, or delete
user B's resources.

### Vertical Access Control

Test that lower-privilege users cannot access higher-privilege functionality:

```bash
# Regular user accessing admin endpoints
GET /api/admin/dashboard
GET /api/admin/users
POST /api/admin/users
DELETE /api/admin/users/123
GET /api/admin/settings
PUT /api/admin/settings
GET /api/admin/logs
GET /api/admin/audit

# Regular user performing privileged operations
PUT /api/users/self {"role": "admin"}
PATCH /api/users/self {"is_admin": true}
POST /api/users/self/permissions {"permissions": ["admin"]}
```

### Method-Level Permissions

Test that read-only users cannot perform write operations:

```bash
# User with read-only access
GET /api/resource/123     # Should succeed (200)
POST /api/resource        # Should fail (403)
PUT /api/resource/123     # Should fail (403)
PATCH /api/resource/123   # Should fail (403)
DELETE /api/resource/123  # Should fail (403)
```

### Field-Level Permissions

Test that responses filter sensitive fields based on the user's role:

```bash
# Regular user viewing a user profile
GET /api/users/123
# Should see: name, email, avatar
# Should NOT see: password_hash, ssn, internal_notes, admin_flags

# Admin viewing the same profile
GET /api/users/123 (with admin token)
# May see additional fields like internal_notes
```

Compare response fields between regular user and admin user requests. Flag any
sensitive field visible to regular users that should be admin-only.

---

## Common Auth Bypass Patterns

### Path Manipulation

```bash
# Trailing slash variation
curl -s http://target/admin
curl -s http://target/admin/

# Double slash
curl -s http://target//admin
curl -s http://target/./admin

# URL encoding
curl -s http://target/%61dmin
curl -s http://target/admin%00

# Case variation
curl -s http://target/Admin
curl -s http://target/ADMIN
curl -s http://target/aDmIn

# Path traversal to bypass prefix-based auth
curl -s http://target/public/../admin
curl -s http://target/api/public/../../admin

# Semicolon (Tomcat path parameter)
curl -s http://target/admin;.js
curl -s http://target/admin;param=value
```

If any variation returns 200 when the canonical path returns 401/403, flag as
an auth bypass (Critical severity).

### Parameter Override

```bash
# Query parameter injection
curl -s "http://target/api/data?admin=true"
curl -s "http://target/api/data?role=admin"
curl -s "http://target/api/data?debug=true"
curl -s "http://target/api/data?internal=true"
curl -s "http://target/api/data?test=true"

# Body parameter injection (on POST/PUT)
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"role":"admin"}' http://target/api/profile
```

### HTTP Method Change

```bash
# If POST requires auth, does GET bypass it?
curl -s -X POST http://target/api/admin  # 401
curl -s -X GET http://target/api/admin   # 200? (bypass)

# HEAD may bypass body-based auth checks
curl -s -X HEAD http://target/api/admin

# OPTIONS may leak information
curl -s -X OPTIONS http://target/api/admin
```

### Header-Based Bypass

```bash
# IP spoofing headers (bypass IP allowlists)
curl -s -H "X-Forwarded-For: 127.0.0.1" http://target/admin
curl -s -H "X-Real-IP: 127.0.0.1" http://target/admin
curl -s -H "X-Original-URL: /admin" http://target/anything
curl -s -H "X-Rewrite-URL: /admin" http://target/anything
curl -s -H "X-Custom-IP-Authorization: 127.0.0.1" http://target/admin

# Referer-based bypass
curl -s -H "Referer: http://target/admin" http://target/api/admin/data
```

---

## Rate Limiting Verification

### Basic Rate Limit Testing

Send rapid requests to auth-related endpoints and check for rate limiting:

```bash
# Send 20 rapid requests to login endpoint
for i in $(seq 1 20); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST -H "Content-Type: application/json" \
    -d '{"username":"test","password":"wrong"}' \
    http://target/api/login)
  echo "Request $i: $STATUS"
done

# Expected: 429 Too Many Requests after some threshold
# Finding if: all return 200/401 (no rate limiting -- Medium)
```

### Rate Limit Header Verification

Check for standard rate limiting headers in responses:

```
X-RateLimit-Limit: 100          # Max requests per window
X-RateLimit-Remaining: 95       # Remaining requests
X-RateLimit-Reset: 1620000000   # Window reset timestamp
Retry-After: 60                 # Seconds until retry allowed
RateLimit-Limit: 100            # IETF draft standard
RateLimit-Remaining: 95
RateLimit-Reset: 60
```

### Rate Limit Scope Testing

Verify what the rate limit is scoped to:

```bash
# Per-IP: Change source IP, check if limit resets
# Per-user: Same IP, different user, check if limit is independent
# Per-endpoint: Hit different endpoints, check if limits are shared
# Global: Check if rate limit applies to all requests regardless

# Test if rate limit applies to successful auth too (not just failures)
# Test if rate limit persists after IP change (X-Forwarded-For bypass)
curl -s -H "X-Forwarded-For: 10.0.0.1" http://target/api/login
curl -s -H "X-Forwarded-For: 10.0.0.2" http://target/api/login
```

### Endpoints That Must Have Rate Limiting

These endpoints are high-value targets for brute force and must enforce rate limits:

- `/login`, `/auth/login`, `/signin` -- credential brute force
- `/register`, `/signup` -- account enumeration, spam
- `/forgot-password`, `/reset-password` -- account takeover
- `/token`, `/oauth/token` -- token brute force
- `/api/verify`, `/api/otp` -- OTP brute force
- `/api/search`, `/api/export` -- resource exhaustion

Flag any of these endpoints that lack rate limiting as a Medium severity finding.

---

## Test Execution Checklist

For each protected endpoint discovered during contract testing, run through
this sequence:

1. Request with no auth headers -- expect 401
2. Request with empty token -- expect 401
3. Request with malformed token -- expect 401
4. Request with expired token -- expect 401
5. Request with valid token, wrong user's resource -- expect 403
6. Request with valid token, insufficient role -- expect 403
7. Request with path variations (trailing slash, case change) -- expect same as canonical
8. Request with method override headers -- expect same enforcement
9. Check response for excessive data exposure
10. Check rate limiting on auth failure paths

Document every deviation from expected behavior as a finding with appropriate
severity level.
