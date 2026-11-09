# Security Configuration Testing Reference

Comprehensive testing methodology for security configuration issues detectable via HTTP requests. All techniques are backend-agnostic and operate at the HTTP level.

---

## Information Disclosure

### Debug Endpoints

```bash
# Common debug/diagnostic endpoints
DEBUG_PATHS=(
  "/debug"
  "/debug/vars"
  "/debug/pprof"
  "/_debug"
  "/api/debug"
  "/api/v1/debug"
  "/.env"
  "/env"
  "/api/env"
  "/config"
  "/api/config"
  "/info"
  "/api/info"
  "/status"
  "/api/status"
  "/health"
  "/api/health"
  "/healthcheck"
  "/metrics"
  "/api/metrics"
  "/prometheus"
  "/actuator"
  "/actuator/env"
  "/actuator/configprops"
  "/actuator/mappings"
  "/actuator/beans"
  "/actuator/heapdump"
  "/actuator/threaddump"
  "/__debug__"
  "/_profiler"
  "/elmah.axd"
  "/trace.axd"
  "/phpinfo.php"
  "/server-info"
  "/server-status"
  "/.git/config"
  "/.git/HEAD"
  "/.svn/entries"
  "/.DS_Store"
  "/wp-config.php.bak"
  "/web.config"
  "/crossdomain.xml"
  "/clientaccesspolicy.xml"
  "/robots.txt"
  "/sitemap.xml"
  "/.well-known/security.txt"
  "/swagger.json"
  "/openapi.json"
  "/api-docs"
  "/graphql"
  "/graphiql"
  "/altair"
  "/playground"
)

for path in "${DEBUG_PATHS[@]}"; do
  echo -n "$path: "
  curl -s -w "HTTP:%{http_code} SIZE:%{size_download}" -o /dev/null \
    "http://TARGET$path"
  echo
done
```

### Stack Trace / Error Message Disclosure

```bash
# Trigger errors with malformed input to check for stack traces
curl -s "http://TARGET/api/users/undefined"
curl -s "http://TARGET/api/users/-1"
curl -s "http://TARGET/api/users/9999999999999"
curl -s "http://TARGET/api/users/null"
curl -s "http://TARGET/api/users/../../etc/passwd"
curl -s "http://TARGET/api/users/%00"
curl -s "http://TARGET/api/users/{{7*7}}"

# Malformed JSON body
curl -s -X POST -H "Content-Type: application/json" \
  -d '{invalid json}' "http://TARGET/api/users"

# Malformed content type
curl -s -X POST -H "Content-Type: application/xml" \
  -d '{"username":"test"}' "http://TARGET/api/users"

# Empty body where body expected
curl -s -X POST -H "Content-Type: application/json" \
  "http://TARGET/api/login"

# Oversized input
curl -s -X POST -H "Content-Type: application/json" \
  -d "{\"username\":\"$(python3 -c 'print("A"*10000)')\"}" \
  "http://TARGET/api/login"

# Special characters
curl -s "http://TARGET/api/users/<script>"
curl -s "http://TARGET/api/users/'\";--"
```

### Stack Trace Detection Indicators

- File paths in response (`/home/user/app/`, `/var/www/`, `C:\Users\`)
- Line numbers and function names
- Framework-specific errors:
  - Node.js: `at Object.<anonymous>`, `node_modules/`, `Error: `
  - Python: `Traceback (most recent call last)`, `File "`, `.py", line`
  - Java: `at com.`, `java.lang.`, `javax.`, `.java:`
  - PHP: `Fatal error:`, `Warning:`, `in /var/www/`
  - Ruby: `from /`, `.rb:`, `ActionController::`
  - .NET: `System.`, `at `, `.cs:line`
  - Go: `goroutine`, `panic:`, `.go:`

### Server Version Headers

```bash
# Check response headers for version information
curl -s -D - -o /dev/null "http://TARGET/" | grep -iE 'server:|x-powered-by:|x-aspnet-version:|x-runtime:|x-version:|x-generator:'
```

**Check for:**
- `Server: Apache/2.4.41` (version disclosure)
- `X-Powered-By: Express` or `PHP/7.4` (framework/language disclosure)
- `X-AspNet-Version: 4.0.30319` (.NET version)
- `X-Generator: Drupal 9` (CMS disclosure)

### Directory Listing

```bash
# Check for directory listing on common paths
for dir in / /static/ /public/ /uploads/ /images/ /assets/ /files/ /media/ /css/ /js/ /backup/ /backups/; do
  echo -n "$dir: "
  RESP=$(curl -s "http://TARGET$dir")
  if echo "$RESP" | grep -qiE 'index of|directory listing|parent directory|<dir>'; then
    echo "DIRECTORY LISTING ENABLED"
  else
    echo "OK"
  fi
done
```

---

## Security Header Analysis

### Comprehensive Header Check

```bash
# Fetch headers from main page and key API endpoints
curl -s -D - -o /dev/null "http://TARGET/" 2>/dev/null
```

### Required Security Headers

| Header | Expected Value | Severity if Missing |
|---|---|---|
| `Content-Security-Policy` | Restrictive policy (no `unsafe-inline`, no `unsafe-eval`) | Medium |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` (min 1 year) | Medium |
| `X-Frame-Options` | `DENY` or `SAMEORIGIN` | Medium |
| `X-Content-Type-Options` | `nosniff` | Low |
| `Referrer-Policy` | `strict-origin-when-cross-origin` or stricter | Low |
| `Permissions-Policy` | Restrictive feature policy | Low |
| `X-XSS-Protection` | `0` (deprecated, CSP preferred) or absent | Info |
| `Cache-Control` | `no-store` on sensitive responses | Medium |

### Header Analysis Curl Example

```bash
echo "=== Security Headers Analysis ==="
HEADERS=$(curl -s -D - -o /dev/null "http://TARGET/")

check_header() {
  HEADER_NAME=$1
  if echo "$HEADERS" | grep -qi "$HEADER_NAME"; then
    echo "[PRESENT] $HEADER_NAME: $(echo "$HEADERS" | grep -i "$HEADER_NAME" | head -1)"
  else
    echo "[MISSING] $HEADER_NAME"
  fi
}

check_header "Content-Security-Policy"
check_header "Strict-Transport-Security"
check_header "X-Frame-Options"
check_header "X-Content-Type-Options"
check_header "Referrer-Policy"
check_header "Permissions-Policy"
check_header "Cache-Control"
```

### CSP Analysis

If CSP is present, check for weaknesses:

- `unsafe-inline` -- allows inline scripts (XSS risk)
- `unsafe-eval` -- allows eval() (code injection risk)
- `*` -- wildcard source (defeats purpose of CSP)
- `data:` -- allows data URIs (can be abused)
- `http:` -- allows HTTP sources on HTTPS page (mixed content)
- Missing `frame-ancestors` -- clickjacking possible
- Missing `default-src` -- no fallback policy

---

## CORS Testing

### Basic CORS Check

```bash
# Test with arbitrary origin
curl -s -D - -o /dev/null -H "Origin: https://evil.com" "http://TARGET/api/users"

# Check preflight
curl -s -D - -o /dev/null -X OPTIONS \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization" \
  "http://TARGET/api/users"
```

### Wildcard Origin with Credentials

```bash
# This combination is a vulnerability
curl -s -D - -o /dev/null -H "Origin: https://evil.com" \
  "http://TARGET/api/sensitive-data"
# Check for: Access-Control-Allow-Origin: * AND Access-Control-Allow-Credentials: true
# (Browsers block this, but misconfigured servers may reflect the origin instead)
```

### Null Origin

```bash
curl -s -D - -o /dev/null -H "Origin: null" "http://TARGET/api/users"
# If Access-Control-Allow-Origin: null -- exploitable via sandboxed iframes
```

### Origin Reflection

```bash
# Check if server reflects any origin
for origin in "https://evil.com" "https://subdomain.TARGET.com" "https://TARGETevil.com" "null"; do
  echo -n "Origin=$origin: "
  curl -s -D - -o /dev/null -H "Origin: $origin" "http://TARGET/api/users" 2>/dev/null | grep -i "access-control-allow-origin"
done
```

### CORS Vulnerability Matrix

| Allow-Origin | Allow-Credentials | Severity |
|---|---|---|
| Reflects attacker origin | true | Critical |
| Reflects attacker origin | false/absent | Medium |
| `*` | false/absent | Low (data exposure) |
| `*` | true | N/A (browsers reject) |
| `null` | true | High |
| Specific trusted origin | true | OK (if origin is trusted) |

---

## Error Handling Testing

### Trigger Various Error Conditions

```bash
# 404 - Non-existent endpoint
curl -s -w "\nHTTP:%{http_code}" "http://TARGET/nonexistent-endpoint-12345"

# 405 - Wrong method
curl -s -w "\nHTTP:%{http_code}" -X DELETE "http://TARGET/"

# 400 - Malformed request
curl -s -w "\nHTTP:%{http_code}" -X POST \
  -H "Content-Type: application/json" -d '{bad' "http://TARGET/api/login"

# 413 - Oversized payload
curl -s -w "\nHTTP:%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$(head -c 1000000 /dev/urandom | base64 | head -c 1000000)\"}" \
  "http://TARGET/api/upload" 2>/dev/null

# 415 - Unsupported media type
curl -s -w "\nHTTP:%{http_code}" -X POST \
  -H "Content-Type: application/x-protobuf" -d 'test' "http://TARGET/api/users"

# 500 - Server error via special characters
curl -s -w "\nHTTP:%{http_code}" "http://TARGET/api/users/%ff"
```

### Error Handling Assessment Criteria

- **Good**: Generic error messages ("An error occurred", "Not found")
- **Bad**: Stack traces, file paths, SQL queries, internal IPs, framework details
- Custom error pages vs default framework error pages

---

## HTTP Method Testing

### OPTIONS Enumeration

```bash
# Check what methods are advertised
curl -s -D - -o /dev/null -X OPTIONS "http://TARGET/"
curl -s -D - -o /dev/null -X OPTIONS "http://TARGET/api/users"
# Look for Allow: header listing supported methods
```

### Unexpected Method Support

```bash
# Test potentially dangerous methods
curl -s -w "HTTP:%{http_code}" -X TRACE "http://TARGET/"
curl -s -w "HTTP:%{http_code}" -X TRACK "http://TARGET/"
curl -s -w "HTTP:%{http_code}" -X CONNECT "http://TARGET/"
curl -s -w "HTTP:%{http_code}" -X PROPFIND "http://TARGET/"
curl -s -w "HTTP:%{http_code}" -X MOVE "http://TARGET/"
curl -s -w "HTTP:%{http_code}" -X COPY "http://TARGET/"
curl -s -w "HTTP:%{http_code}" -X MKCOL "http://TARGET/"
```

**TRACE/TRACK**: If response reflects the request (including headers), Cross-Site Tracing (XST) is possible -- attackers can steal cookies/auth headers.

---

## TLS Configuration Testing

### HTTP vs HTTPS Availability

```bash
# Check if HTTP is available when HTTPS is expected
curl -s -w "HTTP:%{http_code}" -o /dev/null "http://TARGET/"
curl -s -w "HTTP:%{http_code}" -o /dev/null "https://TARGET/"

# Check for redirect from HTTP to HTTPS
curl -s -D - -o /dev/null "http://TARGET/" | grep -i location

# Check HSTS header
curl -s -D - -o /dev/null "https://TARGET/" | grep -i strict-transport-security
```

### Mixed Content

```bash
# If HTTPS is used, check if HTTP resources are loaded
curl -s "https://TARGET/" | grep -i 'http://'
```

---

## Cookie Security Assessment

### Cookie Flag Analysis

```bash
# Login and examine all set-cookie headers
curl -s -D - -o /dev/null -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  "http://TARGET/api/login" | grep -i 'set-cookie'
```

### Cookie Security Checklist

| Flag | Purpose | Severity if Missing |
|---|---|---|
| `Secure` | Only sent over HTTPS | Medium |
| `HttpOnly` | Not accessible via JavaScript | Medium |
| `SameSite=Strict` or `Lax` | CSRF protection | Medium |
| `Path=/` (appropriate scope) | Limit cookie scope | Low |
| Reasonable `Max-Age`/`Expires` | Session duration | Low |
| `__Secure-` prefix | Requires Secure flag | Info |
| `__Host-` prefix | Requires Secure, Path=/, no Domain | Info |

### Session Cookie Naming

Common session cookie names to look for:
- `JSESSIONID` (Java)
- `PHPSESSID` (PHP)
- `ASP.NET_SessionId` (.NET)
- `connect.sid` (Express/Node.js)
- `session` (generic)
- `_session_id` (Rails)
- `ci_session` (CodeIgniter)
- `laravel_session` (Laravel)

---

## Additional Configuration Tests

### Clickjacking Protection

```bash
# Check X-Frame-Options and CSP frame-ancestors
curl -s -D - -o /dev/null "http://TARGET/" | grep -iE 'x-frame-options|frame-ancestors'
```

### Content Type Sniffing

```bash
# Check X-Content-Type-Options
curl -s -D - -o /dev/null "http://TARGET/" | grep -i 'x-content-type-options'

# Test if browser might sniff content type
curl -s -D - "http://TARGET/api/users" | head -5
# Check if Content-Type matches actual response content
```

### Cache Control on Sensitive Data

```bash
# Check caching headers on sensitive endpoints
curl -s -D - -o /dev/null "http://TARGET/api/profile"
curl -s -D - -o /dev/null "http://TARGET/api/account"
# Look for: Cache-Control: no-store, no-cache, must-revalidate
# Bad: no cache control or public caching on sensitive data
```

### HTTP Request Smuggling Indicators

```bash
# Test for ambiguous Content-Length and Transfer-Encoding handling
curl -s -D - -H "Transfer-Encoding: chunked" -H "Content-Length: 0" \
  -X POST -d "0\r\n\r\n" "http://TARGET/"

# Check for duplicate header handling
curl -s -D - -H "Host: TARGET" -H "Host: evil.com" "http://TARGET/"
```

---

## General Configuration Testing Checklist

1. **Remove debug endpoints** from production
2. **Suppress version headers** (Server, X-Powered-By)
3. **Implement all security headers** (CSP, HSTS, X-Frame-Options, etc.)
4. **Configure CORS** restrictively (no wildcard with credentials)
5. **Use custom error pages** that do not leak internals
6. **Disable unnecessary HTTP methods** (TRACE, TRACK)
7. **Enforce HTTPS** with proper redirects and HSTS
8. **Set secure cookie flags** on all session/auth cookies
9. **Disable directory listing**
10. **Remove backup files** and development artifacts from production
