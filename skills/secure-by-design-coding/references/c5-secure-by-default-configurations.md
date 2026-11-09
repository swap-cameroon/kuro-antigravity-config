### C5 — Secure by Default Configurations

*The default state of every system must be secure. Security should not require configuration.*

**Principles:**
- Every setting starts at its most restrictive value
- Features are disabled until explicitly enabled
- New accounts get minimum permissions
- Production configs never inherit dev defaults

**Security headers — always set all of these:**

```typescript
// ✅ Express — use helmet with strict defaults
import helmet from 'helmet';
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],       // no 'unsafe-inline' or 'unsafe-eval'
      styleSrc: ["'self'"],
      imgSrc: ["'self'", "data:"],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      frameSrc: ["'none'"],
      upgradeInsecureRequests: [],
    },
  },
  crossOriginEmbedderPolicy: true,
  crossOriginOpenerPolicy: true,
  crossOriginResourcePolicy: { policy: "same-origin" },
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
  referrerPolicy: { policy: "strict-origin-when-cross-origin" },
}));
```

```python
# ✅ Django — production settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
```

**CORS — never use wildcard on authenticated endpoints:**

```typescript
// ❌ Open to any origin with credentials
app.use(cors({ origin: '*', credentials: true }));

// ✅ Explicit allowlist
const ALLOWED_ORIGINS = ['https://app.example.com', 'https://admin.example.com'];
app.use(cors({
  origin: (origin, cb) => {
    if (!origin || ALLOWED_ORIGINS.includes(origin)) cb(null, true);
    else cb(new Error('CORS blocked'));
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 86400,
}));
```

**Environment-specific configuration:**

```
# ✅ Separate config per environment — never mix
settings/
├── base.py          # shared defaults (secure)
├── development.py   # DEBUG=True, relaxed CORS (dev only)
├── production.py    # DEBUG=False, strict everything
└── testing.py       # test database, fast hashing
```

**Secret management:**
- Never hardcode secrets in code, config files, Dockerfiles, or CI logs
- Use environment variables validated at startup, or a secrets manager (Vault, AWS Secrets Manager, GCP Secret Manager)
- Rotate secrets on a schedule and on suspected compromise
- Validate all required secrets exist at application startup — fail fast if missing

```typescript
// ✅ Validate secrets at startup — fail fast
const REQUIRED_SECRETS = ['DATABASE_URL', 'JWT_SECRET', 'API_KEY'] as const;
for (const key of REQUIRED_SECRETS) {
  if (!process.env[key]) {
    throw new Error(`Missing required secret: ${key}`);
  }
}
```
