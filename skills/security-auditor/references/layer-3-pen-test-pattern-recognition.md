## Layer 3 — Pen Test Pattern Recognition

*Approaching code from a bug hunter's perspective: how would an attacker abuse this system?*

### Mass Assignment
Flag ORM/model auto-binding where request body fields map directly to sensitive model attributes:
```python
# ❌ Mass assignment — attacker sends {"role": "admin", "is_staff": true}
user = User(**request.data)

# ✅ Explicit field allowlist
user = User(
    name=request.data['name'],
    email=request.data['email']
    # role is NOT taken from request
)
```
Flag: Django `ModelSerializer` without `read_only_fields` on sensitive fields. Flag: Express body spread into DB update without field filtering.

### Race Conditions
Flag check-then-act patterns in concurrent operations:
```python
# ❌ Race condition — two requests can pass the check simultaneously
if user.credits >= cost:
    time.sleep(0.1)  # network/DB latency window
    user.credits -= cost  # both requests deduct
    user.save()

# ✅ Atomic operation
User.objects.filter(id=user.id, credits__gte=cost).update(
    credits=F('credits') - cost
)
```
Flag: inventory deductions, balance transfers, quota enforcement, coupon redemption, vote counting — any "check balance → deduct" pattern without atomic transaction or DB-level locking.

### Timing Attacks
Flag non-constant-time comparisons for secrets:
```python
# ❌ Timing attack — string comparison leaks secret length
if user_token == stored_token:

# ✅ Constant-time comparison
import hmac
if hmac.compare_digest(user_token, stored_token):
```
Flag: password comparisons without bcrypt/Argon2, API key validation with `==`, HMAC verification with `==`.

### Path Traversal
Flag file operations with user-supplied paths:
```python
# ❌ Path traversal — attacker sends "../../etc/passwd"
filename = request.GET.get('file')
with open(f'/uploads/{filename}') as f:

# ✅ Sanitized path
import os
filename = os.path.basename(request.GET.get('file'))
safe_path = os.path.join('/uploads', filename)
if not safe_path.startswith('/uploads/'):
    raise PermissionDenied()
```

### HTTP Parameter Pollution
Flag endpoints that accept repeated parameters where the server picks a different value than expected:
- `?role=user&role=admin` — which value does the server use?
- `?id=1&id=2` — which record is fetched?

### Open Redirect
Flag redirect endpoints that don't validate the destination:
```python
# ❌ Open redirect — attacker sends ?next=https://evil.com
next_url = request.GET.get('next', '/')
return redirect(next_url)

# ✅ Relative URLs only
from urllib.parse import urlparse
next_url = request.GET.get('next', '/')
if urlparse(next_url).netloc:
    next_url = '/'  # reject absolute URLs
return redirect(next_url)
```

### Insecure File Upload
- Flag missing file type validation (magic bytes, not just extension)
- Flag uploaded files served from the same origin (XSS via SVG/HTML upload)
- Flag no file size limit
- Flag executable files storable in web-accessible directories

### Business Logic Vulnerabilities
These require understanding the domain — think like a fraudster:
- **Price manipulation**: Is the price taken from the client request instead of calculated server-side?
- **Quantity bypass**: Can `quantity=-1` result in a refund or credit?
- **Discount stacking**: Can the same promo code be applied multiple times?
- **State machine bypass**: Can a user skip required steps (e.g., pay → ship without verify)?
- **Feature flag bypass**: Are premium features gated only by frontend flags?

### Secrets & Credential Exposure
Run these scans:
```bash
# Scan for hardcoded secrets
grep -rn \
  -e "password\s*=\s*['\"]" \
  -e "secret\s*=\s*['\"]" \
  -e "api_key\s*=\s*['\"]" \
  -e "token\s*=\s*['\"]" \
  -e "-----BEGIN.*PRIVATE KEY-----" \
  --include="*.py" --include="*.ts" --include="*.js" --include="*.env" \
  --exclude-dir=node_modules --exclude-dir=.git .

# Check git history for secrets (last 50 commits)
git log --oneline -50 | while read hash msg; do
  git show "$hash" -- '*.env' '*.key' '*.pem' 2>/dev/null | grep -i "password\|secret\|token" | head -3
done
```
- Flag API keys, DB passwords, JWT secrets, private keys in code or committed `.env` files
- Flag secrets in Docker images (ENV instructions in Dockerfile)
- Flag secrets in CI/CD environment variables printed to logs
