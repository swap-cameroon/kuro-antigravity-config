### C9 — Implement Security Logging and Monitoring

*If you can't see it, you can't defend it.*

**What to always log (security events):**
- Authentication: login success/failure, logout, MFA events
- Authorization: access denied, privilege escalation attempts
- Input validation: rejected inputs (potential attack probing)
- Data access: reads/writes to sensitive resources
- Configuration changes: permission grants, setting modifications
- Account lifecycle: creation, deletion, role changes, password resets

**What to NEVER log:**
- Passwords (even hashed)
- Session tokens, API keys, JWTs
- Full credit card numbers, SSNs, PII beyond what's needed
- Request bodies containing sensitive fields

**Structured logging pattern:**

```typescript
// ✅ Structured security event log
logger.info({
  event: 'auth.login.success',
  userId: user.id,
  ip: req.ip,
  userAgent: req.headers['user-agent'],
  correlationId: req.id,
  timestamp: new Date().toISOString(),
});

logger.warn({
  event: 'auth.login.failure',
  email: maskEmail(email),          // mask PII in logs
  ip: req.ip,
  reason: 'invalid_password',
  attemptCount: failedAttempts,
  correlationId: req.id,
});
```

```python
# ✅ Python structured logging
import structlog
logger = structlog.get_logger()

logger.info("auth.login.success",
    user_id=user.id,
    ip=request.META.get('REMOTE_ADDR'),
    correlation_id=request.id,
)
```

**Log injection prevention:**
- Sanitize user input before writing to logs (strip newlines, control characters)
- Use structured logging (JSON format) — never string concatenation
- Restrict log file access (not world-readable)

**Alerting rules to implement:**
- N failed logins from same IP in T minutes
- Access denied spikes (potential enumeration)
- Admin actions from unexpected IPs/times
- Data export volume exceeding threshold
