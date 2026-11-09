### C2 — Use Cryptography to Protect Data

*Never roll your own crypto. Use vetted libraries with secure defaults.*

**Password storage — always use adaptive hashing:**

| Algorithm | Status | Use when |
|---|---|---|
| Argon2id | ✅ Best choice | New projects, any language with library support |
| bcrypt | ✅ Good | Established projects, wide library support |
| scrypt | ✅ Good | When memory-hardness is important |
| PBKDF2-SHA256 | ⚠️ Acceptable | Only if above are unavailable (≥600,000 iterations) |
| SHA-256/SHA-1/MD5 | ❌ Never | Never for passwords, even with salt |

```python
# ✅ Python — Argon2id
from argon2 import PasswordHasher
ph = PasswordHasher()  # secure defaults: Argon2id, memory=65536, time=3
hash = ph.hash(password)
ph.verify(hash, password)  # raises on mismatch
```

```typescript
// ✅ Node.js — bcrypt
import bcrypt from 'bcrypt';
const hash = await bcrypt.hash(password, 12);  // cost factor 12+
const valid = await bcrypt.compare(password, hash);
```

**Encryption:**
- **At rest:** AES-256-GCM (authenticated encryption) with key management (Vault, KMS, AWS Secrets Manager)
- **In transit:** TLS 1.2+ mandatory, TLS 1.3 preferred. No HTTP for any data.
- **Keys:** Never hardcode. Rotate regularly. Store in vault/KMS, not environment variables.
- **Random generation:** Always use CSPRNG — `crypto.randomBytes()` (Node), `secrets.token_hex()` or `secrets.token_urlsafe()` (Python), `crypto/rand` (Go). Never `Math.random()` or `random.random()`.

**JWT security:**
- Algorithm: RS256 or ES256 for multi-service; HS256 only for single-service with long secret (≥256 bits)
- Always verify algorithm on decode (prevent `alg: none` attack)
- Short-lived access tokens (15min–1h), separate refresh tokens
- Store in httpOnly cookies, never localStorage
- Include `iss`, `aud`, `exp` claims and validate all three
- Prefer `jose` library over `jsonwebtoken` in Node 22+

**Constant-time comparison for secrets:**
```python
# ✅ Prevents timing attacks
import hmac
hmac.compare_digest(user_token, stored_token)
```

```typescript
// ✅ Node.js
import { timingSafeEqual } from 'crypto';
timingSafeEqual(Buffer.from(a), Buffer.from(b));
```
