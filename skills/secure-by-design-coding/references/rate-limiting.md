### Rate Limiting

```typescript
// ✅ Rate limit sensitive endpoints
import rateLimit from 'express-rate-limit';

// Strict limit on auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 10,                     // 10 attempts
  skipSuccessfulRequests: true, // only count failures
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many attempts. Try again later.' },
});
app.use('/api/auth/login', authLimiter);
app.use('/api/auth/register', authLimiter);
app.use('/api/auth/reset-password', authLimiter);

// General API limit
const apiLimiter = rateLimit({
  windowMs: 60 * 1000,        // 1 minute
  max: 100,                    // 100 requests
  standardHeaders: true,
});
app.use('/api/', apiLimiter);
```
