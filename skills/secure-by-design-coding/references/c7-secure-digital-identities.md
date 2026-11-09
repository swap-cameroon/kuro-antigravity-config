### C7 — Secure Digital Identities

*Authentication must be layered, sessions must be managed, and passwords must be stored correctly.*

**Authentication levels — choose based on risk:**

| Level | Method | Use when |
|---|---|---|
| Level 1 | Password + secure storage | Low-risk, no PII |
| Level 2 | MFA (password + TOTP/FIDO2) | PII handling, financial data |
| Level 3 | Cryptographic (WebAuthn/PassKeys) | High-impact, admin actions |

**Password policy — modern approach:**
- Minimum 8 characters (with MFA) or 12+ characters (without MFA)
- Accept all printable characters including spaces and Unicode
- Check against top 10,000 breached passwords (Have I Been Pwned API)
- No complexity requirements (uppercase + number + symbol) — favor length
- No mandatory rotation unless breach suspected
- Rate limit failed attempts (account lockout or exponential backoff)

**Session management:**

```typescript
// ✅ Secure session configuration
app.use(session({
  secret: process.env.SESSION_SECRET,       // long random string
  name: '__Host-sid',                        // __Host- prefix enforces secure + same-origin
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,                            // HTTPS only
    httpOnly: true,                          // no JS access
    sameSite: 'lax',                         // CSRF protection
    maxAge: 30 * 60 * 1000,                 // 30 min idle timeout
    domain: undefined,                       // current domain only
    path: '/',
  },
  store: new RedisStore({ client: redis }), // server-side storage
}));
```

**Session lifecycle rules:**
- Generate new session ID on login (prevent session fixation)
- Invalidate session on logout (server-side deletion, not just cookie removal)
- Set idle timeout (30min for sensitive apps) and absolute timeout (8–24h)
- Regenerate session ID on privilege change (role change, password reset)
- Implement concurrent session limits for sensitive applications

**Account enumeration prevention:**

```typescript
// ❌ Leaks whether email exists
if (!user) return res.status(404).json({ error: 'User not found' });
if (!validPassword) return res.status(401).json({ error: 'Wrong password' });

// ✅ Same response regardless
return res.status(401).json({ error: 'Invalid email or password' });
// Also: same response time (prevent timing-based enumeration)
```
