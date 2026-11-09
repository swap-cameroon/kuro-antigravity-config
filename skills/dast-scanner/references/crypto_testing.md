# Cryptographic Weakness Testing Reference

Comprehensive testing methodology for detecting cryptographic weaknesses and sensitive data exposure via HTTP responses. All techniques are backend-agnostic and operate at the HTTP level.

---

## Sensitive Data Exposure in Responses

### Plaintext Password Detection

```bash
# Check if passwords are returned in API responses
curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/profile"
curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/users"
curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/admin/users"
curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/users/1"
curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/account"
```

**Detection patterns** -- look for JSON fields like:
- `"password": "..."` (plaintext password returned)
- `"pass": "..."`, `"pwd": "..."`, `"passwd": "..."`
- `"secret": "..."`, `"api_key": "..."`, `"apiKey": "..."`
- `"token": "..."` (static API tokens in user records)
- `"private_key": "..."`, `"privateKey": "..."`

### SSN / National ID Detection

Look for patterns in API responses:

```
# US SSN pattern: XXX-XX-XXXX or XXXXXXXXX
# Regex: \b\d{3}-?\d{2}-?\d{4}\b

# UK National Insurance: AB 12 34 56 C
# Regex: \b[A-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-Z]\b
```

```bash
# Fetch endpoints likely to contain PII
curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/users" | \
  grep -oE '[0-9]{3}-[0-9]{2}-[0-9]{4}'

curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/users/1" | \
  grep -oE '[0-9]{3}-[0-9]{2}-[0-9]{4}'
```

### Credit Card Number Detection

```bash
# Check API responses for credit card patterns
# Visa: 4[0-9]{12}(?:[0-9]{3})?
# Mastercard: 5[1-5][0-9]{14} or 2[2-7][0-9]{14}
# Amex: 3[47][0-9]{13}
# Discover: 6(?:011|5[0-9]{2})[0-9]{12}

curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/payments" | \
  grep -oE '\b[0-9]{13,19}\b'

curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/orders" | \
  grep -oE '\b4[0-9]{12}([0-9]{3})?\b'
```

**Luhn validation**: After finding a potential card number, validate with the Luhn algorithm. A number passing Luhn in an API response is a critical finding.

### API Key / Secret Detection

```bash
# Check various endpoints for leaked credentials
ENDPOINTS=(
  "/api/config"
  "/api/settings"
  "/api/debug"
  "/api/env"
  "/api/admin/config"
  "/.env"
  "/config.json"
  "/api/keys"
)

for endpoint in "${ENDPOINTS[@]}"; do
  echo "=== $endpoint ==="
  curl -s "http://TARGET$endpoint" | \
    grep -iE 'api[_-]?key|api[_-]?secret|access[_-]?key|secret[_-]?key|private[_-]?key|aws[_-]?access|password|token|credential'
done
```

**Common API key patterns:**
- AWS Access Key: `AKIA[0-9A-Z]{16}`
- AWS Secret Key: 40-character base64 string
- Google API Key: `AIza[0-9A-Za-z_-]{35}`
- GitHub Token: `ghp_[0-9a-zA-Z]{36}` or `github_pat_[0-9a-zA-Z_]{82}`
- Slack Token: `xoxb-[0-9]{10,13}-[0-9a-zA-Z]{24}`
- Stripe Key: `sk_live_[0-9a-zA-Z]{24,}`
- JWT: `eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*`

---

## Weak Hashing Detection

### Identifying Hash Patterns in Responses

```bash
# Fetch user data and check for exposed hashes
curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/users" | python3 -c "
import sys, json, re
data = sys.stdin.read()

# MD5: 32 hex characters
md5_pattern = re.findall(r'\b[a-f0-9]{32}\b', data, re.I)
if md5_pattern:
    print(f'Potential MD5 hashes found: {md5_pattern[:5]}')

# SHA1: 40 hex characters
sha1_pattern = re.findall(r'\b[a-f0-9]{40}\b', data, re.I)
if sha1_pattern:
    print(f'Potential SHA1 hashes found: {sha1_pattern[:5]}')

# SHA256: 64 hex characters
sha256_pattern = re.findall(r'\b[a-f0-9]{64}\b', data, re.I)
if sha256_pattern:
    print(f'Potential SHA256 hashes found: {sha256_pattern[:5]}')

# bcrypt
bcrypt_pattern = re.findall(r'\\\$2[aby]?\\\$\d{2}\\\$.{53}', data)
if bcrypt_pattern:
    print(f'Bcrypt hashes found: {bcrypt_pattern[:5]}')
" 2>/dev/null
```

### Hash Type Identification

| Pattern | Length | Algorithm | Security |
|---|---|---|---|
| `[a-f0-9]{32}` | 32 hex chars | MD5 | Weak -- easily crackable |
| `[a-f0-9]{40}` | 40 hex chars | SHA-1 | Weak -- collision-prone |
| `[a-f0-9]{64}` | 64 hex chars | SHA-256 | OK for data integrity, weak for passwords (no salt) |
| `$2a$`, `$2b$`, `$2y$` | 60 chars | bcrypt | Strong (but should not be in responses) |
| `$argon2i$`, `$argon2id$` | Variable | Argon2 | Strong (but should not be in responses) |
| `$5$` | Variable | SHA-256 crypt | Acceptable |
| `$6$` | Variable | SHA-512 crypt | Acceptable |
| `{SSHA}` | Variable | Salted SHA | Weak for modern use |
| `pbkdf2:sha256:` | Variable | PBKDF2 | Acceptable |

### Hash Exposure Assessment

Any password hash exposed in an API response is a finding:
- **Critical**: MD5 or unsalted SHA hashes of passwords in responses
- **High**: Bcrypt/Argon2 hashes in responses (even strong hashes should not be exposed)
- **Medium**: Hash-like patterns in responses where the field purpose is unclear

---

## Predictable Token Analysis

### Collecting Multiple Tokens

```bash
# Generate multiple tokens/sessions and analyze for patterns
TOKENS=()
for i in $(seq 1 10); do
  TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"password"}' \
    "http://TARGET/api/login" | jq -r '.token // .session // .sessionId // .access_token')
  TOKENS+=("$TOKEN")
  echo "Token $i: $TOKEN"
  sleep 1
done
```

### Pattern Detection

**Sequential tokens:**
```bash
# Check if tokens increment sequentially
# If tokens are numeric or have numeric components, check deltas
# Tokens like: 1001, 1002, 1003 = sequential = critical vulnerability
```

**Timestamp-based tokens:**
```bash
# Check if token contains or is derived from timestamp
# Convert token to decimal and compare with epoch time
# If token = base64(timestamp) or hex(timestamp), it is predictable
```

**Low entropy detection:**
```bash
# Check character distribution
echo "$TOKEN" | fold -w1 | sort | uniq -c | sort -rn
# If very few unique characters or obvious patterns, entropy is low
```

### Token Analysis Criteria

| Property | Secure | Insecure |
|---|---|---|
| Length | 32+ characters | Less than 16 characters |
| Character set | Alphanumeric + symbols | Numeric only |
| Predictability | No pattern across tokens | Sequential, timestamp-based |
| Entropy | High (random) | Low (patterned) |
| Uniqueness | Never repeated | Collisions observed |

---

## Session Token Strength

### Entropy Measurement

```bash
# Collect multiple session tokens
for i in $(seq 1 20); do
  curl -s -c - "http://TARGET/" 2>/dev/null | grep -i session
done

# Analyze entropy using Python
python3 -c "
import math, collections
tokens = '''PASTE_TOKENS_HERE'''.strip().split('\n')
for token in tokens:
    if not token: continue
    freq = collections.Counter(token)
    length = len(token)
    entropy = -sum((count/length) * math.log2(count/length) for count in freq.values())
    print(f'Token: {token[:20]}... Length: {length} Entropy: {entropy:.2f} bits/char')
" 2>/dev/null
```

### Session Token Requirements

- Minimum 128 bits of entropy (16 bytes of randomness)
- Generated by cryptographically secure PRNG
- No user-controllable components
- Changes after authentication
- Invalidated after logout
- Reasonable expiration time

---

## Data-in-Transit Testing

### HTTP vs HTTPS Availability

```bash
# Check if sensitive operations are available over HTTP
# Login over HTTP (credentials in plaintext)
curl -s -w "HTTP:%{http_code}" -o /dev/null -X POST \
  -d '{"username":"test","password":"test"}' \
  "http://TARGET/api/login"

# Check if HTTP redirects to HTTPS
curl -s -D - -o /dev/null "http://TARGET/api/login" | grep -i location

# Check HSTS header on HTTPS
curl -s -D - -o /dev/null "https://TARGET/" | grep -i strict-transport-security
```

### Sensitive Operations Over HTTP

```bash
# These should ONLY be available over HTTPS
SENSITIVE_ENDPOINTS=(
  "/api/login"
  "/api/register"
  "/api/change-password"
  "/api/forgot-password"
  "/api/profile"
  "/api/payment"
  "/api/checkout"
  "/api/admin"
)

for endpoint in "${SENSITIVE_ENDPOINTS[@]}"; do
  echo -n "HTTP $endpoint: "
  curl -s -w "HTTP:%{http_code}" -o /dev/null "http://TARGET$endpoint"
  echo
done
```

### Mixed Content Detection

```bash
# On HTTPS pages, check for HTTP resource loading
curl -s "https://TARGET/" | grep -oiE 'src="http://[^"]*"|href="http://[^"]*"' | head -20
```

---

## Response Data Minimization

### Excessive PII in API Responses

```bash
# Check if API returns more data than necessary
# User listing should not include passwords, full SSN, full credit cards
curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/users" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        records = data.get('users', data.get('data', data.get('results', [data])))
    else:
        records = []
    
    if isinstance(records, list) and len(records) > 0:
        sample = records[0] if isinstance(records[0], dict) else {}
        sensitive_fields = [k for k in sample.keys() if any(s in k.lower() for s in [
            'password', 'pass', 'pwd', 'secret', 'ssn', 'social_security',
            'credit_card', 'card_number', 'cvv', 'private_key', 'api_key',
            'token', 'hash', 'salt'
        ])]
        if sensitive_fields:
            print(f'SENSITIVE FIELDS IN RESPONSE: {sensitive_fields}')
        print(f'Total fields returned: {list(sample.keys())}')
    else:
        print('Could not parse response as record list')
except:
    print('Response is not JSON')
" 2>/dev/null
```

### Data Minimization Checklist

- **User listings**: Should not include password hashes, full SSN, full credit card numbers
- **Profile endpoints**: Should only return the authenticated user's own data
- **Search results**: Should not include internal IDs, database keys, or sensitive metadata
- **Error responses**: Should not include stack traces, SQL queries, or internal paths
- **Admin endpoints**: Should be restricted and return only necessary administrative data

---

## Weak Cryptographic Storage Indicators

### Password Storage Assessment

```bash
# Check if the application stores passwords in a weak format
# Try to trigger password-related error messages
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong"}' \
  "http://TARGET/api/login"
# Look for error messages that hint at storage method

# Check password reset -- does it send the old password? (plaintext storage)
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com"}' \
  "http://TARGET/api/forgot-password"
# If response or email contains the current password, it is stored in plaintext/reversible encryption
```

### Symmetric Encryption in Responses

```bash
# Look for base64-encoded encrypted data that might be using weak encryption
curl -s -H "Authorization: Bearer $TOKEN" "http://TARGET/api/users/1" | \
  grep -oE '[A-Za-z0-9+/]{20,}={0,2}' | while read b64; do
    DECODED=$(echo "$b64" | base64 -d 2>/dev/null | xxd -p | head -c 20)
    echo "Base64: ${b64:0:30}... Hex start: $DECODED"
done
```

---

## Randomness Testing

### Reset Token Predictability

```bash
# Request multiple password reset tokens
for i in $(seq 1 5); do
  echo "=== Request $i ($(date +%s)) ==="
  curl -s -X POST -H "Content-Type: application/json" \
    -d '{"email":"test@example.com"}' \
    "http://TARGET/api/forgot-password"
  sleep 1
done
# Compare tokens for:
# - Sequential patterns (token1=100, token2=101)
# - Timestamp embedding (token contains unix epoch)
# - Short tokens (less than 20 chars = low entropy)
# - Numeric-only tokens (brute-forceable)
```

### CSRF Token Analysis

```bash
# Collect multiple CSRF tokens
for i in $(seq 1 5); do
  curl -s "http://TARGET/login" | grep -ioE 'csrf[^"]*"[^"]*"' | head -1
  sleep 1
done
# Same analysis as reset tokens
```

---

## General Cryptographic Testing Checklist

1. **No plaintext passwords** in any API response
2. **No weak hashes** (MD5, SHA1) for password storage
3. **No sensitive data** (SSN, CC numbers, API keys) in responses unless strictly necessary
4. **Strong session tokens** (128+ bits of entropy, CSPRNG)
5. **Unpredictable reset tokens** (not sequential, not timestamp-based)
6. **HTTPS enforced** for all sensitive operations
7. **HSTS enabled** with appropriate max-age
8. **No mixed content** on HTTPS pages
9. **Proper data minimization** in API responses
10. **No hash/salt exposure** even for strong algorithms
