# Web Framework Security Configuration Hardening

This reference covers security configuration checks across major web frameworks. Each section lists what to check, default file locations, detection patterns, and fix examples.

---

## Express.js (Node.js)

**Default config locations:** `app.ts`, `app.js`, `index.ts`, `index.js`, `server.ts`, `server.js`, `src/app.ts`, `src/index.ts`, `package.json`

### 1. Missing Helmet Middleware

**What to check:** Whether the `helmet` package is installed and used as middleware.

**Detection pattern:**
- `package.json` does not include `helmet` in dependencies
- Main app file does not contain `app.use(helmet())`
- Helmet is imported but not applied to the app

**Why it matters:** Helmet sets critical HTTP security headers: `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `X-XSS-Protection`, and others. Without these headers, the application is vulnerable to clickjacking, MIME sniffing attacks, XSS, and protocol downgrade attacks.

**Severity:** Medium

**How to fix:**
```typescript
import helmet from 'helmet';

const app = express();
app.use(helmet());

// Or configure specific headers:
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
}));
```

---

### 2. CORS with Wildcard Origin and Credentials

**What to check:** CORS configuration that allows any origin (`*`) combined with credentials.

**Detection pattern:**
- `cors({ origin: '*', credentials: true })`
- `cors({ origin: true })` (reflects any origin)
- `res.setHeader('Access-Control-Allow-Origin', '*')` combined with `Access-Control-Allow-Credentials: true`
- `cors()` with no arguments (allows all origins)

**Why it matters:** If CORS allows any origin with credentials, a malicious site can make authenticated requests to the API on behalf of a logged-in user, stealing data or performing actions. This is a cross-origin data theft vulnerability.

**Severity:** High

**How to fix:**
```typescript
import cors from 'cors';

app.use(cors({
  origin: ['https://myapp.example.com', 'https://admin.example.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
```

---

### 3. Excessive Body Parser Limits

**What to check:** `express.json()` or `body-parser` configured with no limit or an excessively large limit.

**Detection pattern:**
- `app.use(express.json())` with no options (default 100kb — acceptable)
- `app.use(express.json({ limit: '50mb' }))` or higher
- `app.use(bodyParser.json({ limit: '100mb' }))`
- No limit set on `express.urlencoded()`

**Why it matters:** An excessively large body limit allows attackers to send huge payloads that consume memory, causing denial-of-service. JSON parsing of large payloads is CPU-intensive and can block the event loop.

**Severity:** Medium

**How to fix:**
```typescript
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));
```

---

### 4. X-Powered-By Header Enabled

**What to check:** Whether the `X-Powered-By: Express` header is present.

**Detection pattern:**
- No `app.disable('x-powered-by')` call
- No helmet middleware (helmet disables it by default)
- `app.enable('x-powered-by')` explicitly

**Why it matters:** The `X-Powered-By` header reveals the server technology, allowing attackers to target Express-specific vulnerabilities. Information disclosure assists in reconnaissance.

**Severity:** Low

**How to fix:**
```typescript
app.disable('x-powered-by');
// Or use helmet which does this automatically
```

---

### 5. Static File Serving of Sensitive Directories

**What to check:** `express.static()` serving directories that contain uploads, source code, or configuration.

**Detection pattern:**
- `app.use(express.static('.'))` (serves entire project directory)
- `app.use(express.static('uploads'))` without access control
- `app.use('/static', express.static(path.join(__dirname, '..')))` (parent directory)
- Static serving of directories containing `.env`, `package.json`, source files

**Why it matters:** Serving the project root or parent directories exposes source code, configuration files, `.env` files, and `package.json` (which reveals dependencies and their versions). Upload directories may contain user-supplied malicious files.

**Severity:** High

**How to fix:**
```typescript
// Serve only a dedicated public directory
app.use(express.static('public', {
  dotfiles: 'deny',  // Block .env, .git, etc.
  index: false,       // Disable directory listing
}));
```

---

### 6. Global Error Handler Exposing Stack Traces

**What to check:** Error handling middleware that sends stack traces or internal error details in responses.

**Detection pattern:**
- `res.status(500).json({ error: err.message, stack: err.stack })`
- `res.send(err.toString())`
- No custom error handler (Express default shows stack in development)
- `NODE_ENV` not set to `production`

**Why it matters:** Stack traces reveal internal file paths, library versions, database connection details, and application architecture. This information helps attackers craft targeted exploits.

**Severity:** Medium

**How to fix:**
```typescript
// Production error handler — no stack traces
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack); // Log internally
  res.status(500).json({
    error: 'Internal server error',
    // Never include err.message or err.stack in production responses
    ...(process.env.NODE_ENV === 'development' && { details: err.message }),
  });
});
```

---

### 7. Missing Rate Limiting

**What to check:** Whether rate limiting middleware is applied, especially on authentication endpoints.

**Detection pattern:**
- No `express-rate-limit`, `rate-limiter-flexible`, or similar package in dependencies
- No rate limiting middleware on `/login`, `/api/auth`, `/register`, `/forgot-password`
- Rate limiter present but with very high limits (e.g., 10000 requests per minute)

**Why it matters:** Without rate limiting, attackers can brute-force credentials, enumerate users, abuse expensive operations, and perform denial-of-service attacks.

**Severity:** Medium

**How to fix:**
```typescript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// Stricter limit for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
});
app.use('/api/auth', authLimiter);
```

---

### 8. Insecure Session Cookie Configuration

**What to check:** Session cookies missing `secure`, `httpOnly`, or `sameSite` flags.

**Detection pattern:**
- `express-session` configured without `cookie.secure: true`
- `cookie.httpOnly` set to `false`
- `cookie.sameSite` not set or set to `'none'` without justification
- `cookie.maxAge` set to very long durations
- Using `MemoryStore` in production (also causes memory leaks)

**Why it matters:** Without `secure`, cookies are sent over HTTP and can be intercepted (MITM). Without `httpOnly`, JavaScript can read session cookies (XSS to session hijack). Without `sameSite`, cross-site requests include the cookie (CSRF).

**Severity:** High

**How to fix:**
```typescript
import session from 'express-session';

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,        // HTTPS only
    httpOnly: true,      // No JavaScript access
    sameSite: 'strict',  // No cross-site sending
    maxAge: 3600000,     // 1 hour
  },
  store: new RedisStore({ client: redisClient }), // Not MemoryStore
}));
```

---

### 9. Missing CSRF Protection

**What to check:** Whether CSRF protection is implemented for state-changing endpoints.

**Detection pattern:**
- No CSRF middleware (`csurf`, `csrf-csrf`, `lusca`)
- API endpoints accepting POST/PUT/DELETE without CSRF tokens
- SPA without double-submit cookie or custom header pattern

**Why it matters:** Without CSRF protection, a malicious website can trigger state-changing requests (transfers, password changes, data deletion) using an authenticated user's session.

**Severity:** High (for session-based auth), Low (for token-based auth with Authorization header)

**How to fix:**
```typescript
// For traditional apps with session cookies:
import { doubleCsrf } from 'csrf-csrf';

const { doubleCsrfProtection } = doubleCsrf({
  getSecret: () => process.env.CSRF_SECRET,
  cookieName: '_csrf',
  cookieOptions: { secure: true, sameSite: 'strict' },
});

app.use(doubleCsrfProtection);
```

---

## Flask (Python)

**Default config locations:** `app.py`, `config.py`, `wsgi.py`, `__init__.py`, `settings.py`, `instance/config.py`

### 10. DEBUG=True in Production

**What to check:** Flask debug mode enabled in production configuration.

**Detection pattern:**
- `app.debug = True`
- `app.run(debug=True)`
- `DEBUG = True` in config file
- `FLASK_DEBUG=1` in `.env` or environment
- Werkzeug debugger enabled (allows arbitrary code execution)

**Why it matters:** Flask's debug mode enables the Werkzeug interactive debugger, which allows arbitrary Python code execution in the browser. If exposed to the internet, this is a direct remote code execution vulnerability. Even with a debugger PIN, it can be brute-forced or derived.

**Severity:** Critical

**How to fix:**
```python
# config.py
class ProductionConfig:
    DEBUG = False
    TESTING = False

# app.py
app.config.from_object('config.ProductionConfig')

# Never use app.run() in production — use gunicorn or uwsgi
# gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

### 11. Hardcoded or Weak SECRET_KEY

**What to check:** Flask SECRET_KEY hardcoded in source code or using a weak/default value.

**Detection pattern:**
- `app.secret_key = 'dev'` or `app.secret_key = 'changeme'`
- `SECRET_KEY = 'some-string-here'` in config.py
- Short SECRET_KEY (less than 24 characters)
- SECRET_KEY committed to version control
- `os.urandom(16)` called at startup (changes on restart, invalidating sessions)

**Why it matters:** The SECRET_KEY is used to sign session cookies and CSRF tokens. If it is known or guessable, an attacker can forge sessions, impersonate any user, and bypass CSRF protection.

**Severity:** Critical

**How to fix:**
```python
import os

# Generate a strong key: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")
```

---

### 12. Missing CSRF Protection (Flask-WTF)

**What to check:** Whether Flask-WTF or equivalent CSRF protection is enabled.

**Detection pattern:**
- No `flask-wtf` or `flask-seasurf` in requirements
- `CSRFProtect(app)` not called
- `WTF_CSRF_ENABLED = False` in config
- Forms without `{{ form.hidden_tag() }}` or `{{ csrf_token() }}`

**Why it matters:** Without CSRF protection, attackers can trick authenticated users into performing unintended actions (changing passwords, making purchases, deleting data) by luring them to a malicious page.

**Severity:** High

**How to fix:**
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# In templates:
# <form method="post">
#   {{ csrf_token() }}
#   ...
# </form>
```

---

### 13. Jinja2 Autoescape Disabled

**What to check:** Jinja2 template engine with autoescaping turned off.

**Detection pattern:**
- `Jinja2` environment created with `autoescape=False`
- Using `Markup()` or `| safe` filter excessively
- Templates rendering user input without escaping
- `app.jinja_env.autoescape = False`

**Why it matters:** Without autoescaping, any user input rendered in templates can inject HTML and JavaScript, leading to cross-site scripting (XSS). Flask enables autoescape for `.html` templates by default, but not for `.txt`, `.xml`, or other extensions.

**Severity:** High

**How to fix:**
```python
from jinja2 import select_autoescape

app.jinja_env.autoescape = select_autoescape(
    enabled_extensions=('html', 'htm', 'xml', 'svg'),
    default_for_string=True,
)
```

---

### 14. Missing Rate Limiting

**What to check:** No rate limiting on Flask routes.

**Detection pattern:**
- No `flask-limiter` in requirements
- Auth endpoints without rate decorators
- API endpoints with no throttling

**Severity:** Medium

**How to fix:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    pass
```

---

### 15. CORS Misconfiguration

**What to check:** Flask-CORS with overly permissive settings.

**Detection pattern:**
- `CORS(app)` with no arguments (allows all origins)
- `CORS(app, origins="*", supports_credentials=True)`
- `@cross_origin()` on sensitive endpoints

**Severity:** High

**How to fix:**
```python
from flask_cors import CORS

CORS(app, origins=["https://myapp.example.com"], supports_credentials=True)
```

---

## Django (Python)

**Default config locations:** `settings.py`, `<project>/settings.py`, `settings/base.py`, `settings/production.py`, `.env`

### 16. DEBUG=True and SECRET_KEY in settings.py

**What to check:** Debug mode and secret key configuration.

**Detection pattern:**
- `DEBUG = True` in any settings file not clearly marked as development-only
- `SECRET_KEY = '...'` hardcoded in settings.py (especially if committed to VCS)
- `SECRET_KEY` shorter than 50 characters

**Why it matters:** Django's DEBUG mode exposes detailed error pages with local variables, SQL queries, settings values, and full stack traces. The SECRET_KEY is used for cryptographic signing of sessions, CSRF tokens, and password reset tokens.

**Severity:** Critical

**How to fix:**
```python
import os

DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']  # Fail if not set
```

---

### 17. ALLOWED_HOSTS=['*']

**What to check:** ALLOWED_HOSTS set to wildcard.

**Detection pattern:**
- `ALLOWED_HOSTS = ['*']`
- `ALLOWED_HOSTS = []` (with DEBUG=True, allows all)

**Why it matters:** ALLOWED_HOSTS validates the Host header to prevent HTTP Host header attacks, which can be used for cache poisoning, password reset poisoning, and SSRF.

**Severity:** High

**How to fix:**
```python
ALLOWED_HOSTS = ['myapp.example.com', 'www.myapp.example.com']
```

---

### 18. Missing SecurityMiddleware

**What to check:** Whether `django.middleware.security.SecurityMiddleware` is in MIDDLEWARE.

**Detection pattern:**
- `SecurityMiddleware` not in `MIDDLEWARE` list
- `SECURE_SSL_REDIRECT = False`
- `SECURE_HSTS_SECONDS = 0`
- `SECURE_BROWSER_XSS_FILTER = False`
- `SECURE_CONTENT_TYPE_NOSNIFF = False`

**Severity:** Medium

**How to fix:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ... other middleware
]

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

---

### 19. Insecure Cookie Settings

**What to check:** CSRF and session cookie flags.

**Detection pattern:**
- `CSRF_COOKIE_SECURE = False`
- `SESSION_COOKIE_SECURE = False`
- `SESSION_COOKIE_HTTPONLY = False`
- `CSRF_COOKIE_HTTPONLY = False`
- `SESSION_COOKIE_SAMESITE` not set or `None`

**Severity:** High

**How to fix:**
```python
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
```

---

### 20. Missing Content-Security-Policy

**What to check:** Whether CSP header is configured (Django does not set it by default).

**Detection pattern:**
- No `django-csp` in requirements
- No CSP middleware
- No CSP header set in web server config

**Severity:** Medium

**How to fix:**
```python
# pip install django-csp
MIDDLEWARE = [
    'csp.middleware.CSPMiddleware',
    # ...
]

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:")
```

---

### 21. Database Passwords in settings.py

**What to check:** Database credentials hardcoded in settings.

**Detection pattern:**
- `'PASSWORD': 'mypassword'` in DATABASES config
- Database connection strings with embedded passwords
- Any credential in settings.py committed to VCS

**Severity:** Critical

**How to fix:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

---

## Spring Boot (Java)

**Default config locations:** `application.yml`, `application.properties`, `application-*.yml`, `application-*.properties`, `src/main/resources/`, `SecurityConfig.java`, `WebSecurityConfig.java`, `pom.xml`, `build.gradle`

### 22. Actuator Endpoints Exposed Without Authentication

**What to check:** Spring Boot Actuator endpoints accessible without authentication.

**Detection pattern:**
- `management.endpoints.web.exposure.include=*` in application.properties
- `management.endpoints.web.exposure.include: "*"` in application.yml
- Actuator dependency present without Spring Security configured
- `/actuator/env`, `/actuator/configprops`, `/actuator/heapdump` accessible

**Why it matters:** Actuator endpoints expose environment variables (including secrets), heap dumps (containing in-memory secrets), configuration properties, thread dumps, and application metrics. The `/actuator/env` endpoint has been used to achieve RCE in some configurations.

**Severity:** Critical

**How to fix:**
```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: when-authorized
```

```java
@Configuration
public class ActuatorSecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.requestMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeRequests()
            .anyRequest().hasRole("ADMIN")
            .and().httpBasic();
    }
}
```

---

### 23. CORS Misconfiguration in WebMvcConfigurer

**What to check:** Overly permissive CORS configuration.

**Detection pattern:**
- `.allowedOrigins("*")` combined with `.allowCredentials(true)`
- `@CrossOrigin` annotation without specifying origins
- `CorsConfiguration.setAllowedOrigins(Arrays.asList("*"))`

**Severity:** High

**How to fix:**
```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://myapp.example.com")
            .allowedMethods("GET", "POST", "PUT", "DELETE")
            .allowCredentials(true);
    }
}
```

---

### 24. CSRF Disabled Globally

**What to check:** CSRF protection disabled in Spring Security config.

**Detection pattern:**
- `http.csrf().disable()` or `http.csrf(csrf -> csrf.disable())`
- CSRF disabled without being a pure REST API using token-based auth

**Why it matters:** Disabling CSRF globally removes protection for all endpoints. While pure stateless REST APIs with token-based auth (Authorization header) do not need CSRF, applications with session-based auth or cookies do.

**Severity:** High (session-based auth), Low (stateless token auth only)

**How to fix:**
```java
http.csrf(csrf -> csrf
    .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
    .ignoringRequestMatchers("/api/webhook/**")  // Only exclude specific endpoints
);
```

---

### 25. Missing Security Headers

**What to check:** Security headers not configured in SecurityFilterChain.

**Detection pattern:**
- No `http.headers()` configuration
- `http.headers().disable()`
- Missing CSP, HSTS, X-Frame-Options configuration

**Severity:** Medium

**How to fix:**
```java
http.headers(headers -> headers
    .contentSecurityPolicy(csp -> csp.policyDirectives("default-src 'self'"))
    .httpStrictTransportSecurity(hsts -> hsts.maxAgeInSeconds(31536000).includeSubDomains(true))
    .frameOptions(frame -> frame.deny())
    .contentTypeOptions(Customizer.withDefaults())
);
```

---

### 26. Default Credentials in application.properties

**What to check:** Passwords, keys, and credentials hardcoded in config files.

**Detection pattern:**
- `spring.datasource.password=...`
- `spring.security.user.password=...`
- `spring.mail.password=...`
- `spring.redis.password=...`
- Any property containing `password`, `secret`, `key`, `token` with a literal value

**Severity:** Critical

**How to fix:**
```yaml
spring:
  datasource:
    password: ${DB_PASSWORD}  # Reference environment variable
```

---

### 27. H2 Console Enabled in Production

**What to check:** H2 in-memory database console enabled and accessible.

**Detection pattern:**
- `spring.h2.console.enabled=true`
- `spring.h2.console.settings.web-allow-others=true`

**Why it matters:** The H2 console provides a web-based SQL interface. If accessible, it allows arbitrary SQL execution and in some configurations can lead to RCE via JNDI injection or Java code execution through SQL functions.

**Severity:** Critical

**How to fix:**
```yaml
# Disable H2 console in production
spring:
  h2:
    console:
      enabled: false
```

---

## Laravel (PHP)

**Default config locations:** `.env`, `config/app.php`, `config/auth.php`, `config/cors.php`, `config/session.php`, `config/database.php`

### 28. APP_DEBUG=true in Production

**What to check:** Debug mode enabled in production.

**Detection pattern:**
- `APP_DEBUG=true` in `.env`
- `'debug' => true` in `config/app.php`
- Ignition error page visible (shows source code, environment variables, database queries)

**Why it matters:** Laravel's debug mode (powered by Ignition) exposes full stack traces, source code, environment variables (including secrets), database queries, and request details. Ignition has had RCE vulnerabilities (CVE-2021-3129).

**Severity:** Critical

**How to fix:**
```
# .env
APP_DEBUG=false
APP_ENV=production
```

---

### 29. APP_KEY Exposed or Default

**What to check:** Application encryption key misconfiguration.

**Detection pattern:**
- `APP_KEY=` (empty)
- `APP_KEY=base64:SomeObviousTestKey...`
- APP_KEY committed to version control
- Same APP_KEY used across environments

**Why it matters:** APP_KEY is used for encrypting cookies, sessions, CSRF tokens, and any encrypted data. If known, an attacker can decrypt sensitive data and forge sessions. In some Laravel versions, knowledge of APP_KEY enables remote code execution via deserialization.

**Severity:** Critical

**How to fix:**
```bash
# Generate a new key
php artisan key:generate

# Store in environment, not in committed .env
# Use different keys per environment
```

---

### 30. CORS Misconfiguration

**What to check:** `config/cors.php` with overly permissive settings.

**Detection pattern:**
- `'allowed_origins' => ['*']` with `'supports_credentials' => true`
- `'allowed_methods' => ['*']`
- `'allowed_headers' => ['*']`

**Severity:** High

**How to fix:**
```php
// config/cors.php
return [
    'allowed_origins' => ['https://myapp.example.com'],
    'allowed_methods' => ['GET', 'POST', 'PUT', 'DELETE'],
    'supports_credentials' => true,
];
```

---

### 31. Missing CSRF Verification

**What to check:** CSRF middleware disabled or excessively bypassed.

**Detection pattern:**
- `VerifyCsrfToken` middleware removed from `Kernel.php`
- Large `$except` array in `VerifyCsrfToken.php`
- `@csrf` directive missing from forms

**Severity:** High

**How to fix:**
```php
// app/Http/Middleware/VerifyCsrfToken.php
protected $except = [
    'api/webhook/*',  // Only exclude webhook endpoints
];
```

---

### 32. Debug Bar Enabled in Production

**What to check:** Laravel Debugbar package enabled in production.

**Detection pattern:**
- `barryvdh/laravel-debugbar` in `require` (not `require-dev`) in `composer.json`
- `DEBUGBAR_ENABLED=true` in production `.env`
- Debugbar assets visible in page source

**Why it matters:** Debugbar shows SQL queries, request data, session contents, and other sensitive internal information. It can leak database structure, credentials passed in queries, and session tokens.

**Severity:** High

**How to fix:**
```json
// composer.json — move to require-dev
"require-dev": {
    "barryvdh/laravel-debugbar": "^3.0"
}
```
```
# .env
DEBUGBAR_ENABLED=false
```

---

## ASP.NET

**Default config locations:** `appsettings.json`, `appsettings.*.json`, `Startup.cs`, `Program.cs`, `web.config`, `Properties/launchSettings.json`

### 33. Custom Errors Off (Exposing Stack Traces)

**What to check:** Detailed error pages enabled in production.

**Detection pattern:**
- `app.UseDeveloperExceptionPage()` without environment check
- `<customErrors mode="Off" />` in web.config
- `ASPNETCORE_ENVIRONMENT=Development` in production

**Why it matters:** Developer exception pages show full stack traces, source code snippets, request details, and configuration values. This reveals internal architecture, file paths, library versions, and potentially sensitive data.

**Severity:** Medium

**How to fix:**
```csharp
// Program.cs
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}
else
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}
```

---

### 34. Missing HTTPS Redirection

**What to check:** Whether HTTP to HTTPS redirection is configured.

**Detection pattern:**
- No `app.UseHttpsRedirection()` in middleware pipeline
- No `app.UseHsts()` call
- `RequireHttpsAttribute` not applied globally

**Why it matters:** Without HTTPS redirection, users may access the application over HTTP, exposing session cookies, credentials, and all data to network sniffers (MITM attacks). HSTS ensures browsers always use HTTPS.

**Severity:** High

**How to fix:**
```csharp
app.UseHttpsRedirection();
app.UseHsts();

// In Program.cs or Startup.cs:
builder.Services.AddHsts(options =>
{
    options.MaxAge = TimeSpan.FromDays(365);
    options.IncludeSubDomains = true;
    options.Preload = true;
});
```

---

### 35. CORS AllowAnyOrigin with AllowCredentials

**What to check:** Overly permissive CORS policy.

**Detection pattern:**
- `.AllowAnyOrigin().AllowCredentials()` (throws at runtime in newer versions)
- `.SetIsOriginAllowed(_ => true).AllowCredentials()`
- `.WithOrigins("*")`

**Severity:** High

**How to fix:**
```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("Production", policy =>
    {
        policy.WithOrigins("https://myapp.example.com")
              .AllowCredentials()
              .WithMethods("GET", "POST", "PUT", "DELETE")
              .WithHeaders("Content-Type", "Authorization");
    });
});
```

---

### 36. Missing Anti-Forgery Tokens

**What to check:** CSRF protection not configured for form submissions.

**Detection pattern:**
- No `[ValidateAntiForgeryToken]` on POST actions
- No `[AutoValidateAntiforgeryToken]` at controller or global level
- No `@Html.AntiForgeryToken()` or `asp-antiforgery="true"` in forms
- Anti-forgery globally disabled

**Severity:** High

**How to fix:**
```csharp
// Apply globally in Program.cs:
builder.Services.AddControllersWithViews(options =>
{
    options.Filters.Add(new AutoValidateAntiforgeryTokenAttribute());
});

// Or per-controller:
[AutoValidateAntiforgeryToken]
public class AccountController : Controller { }
```

---

### 37. Connection Strings in appsettings.json

**What to check:** Database connection strings with credentials in configuration files.

**Detection pattern:**
- `"ConnectionStrings"` section with `Password=` or `Pwd=`
- Connection strings committed to VCS
- Sensitive data in `appsettings.json` (not `appsettings.Development.json`)

**Severity:** Critical

**How to fix:**
```csharp
// Use User Secrets in development:
// dotnet user-secrets set "ConnectionStrings:Default" "Server=...;Password=..."

// Use environment variables in production:
// ConnectionStrings__Default=Server=...;Password=...

// Or use Azure Key Vault / AWS Secrets Manager:
builder.Configuration.AddAzureKeyVault(
    new Uri("https://myvault.vault.azure.net/"),
    new DefaultAzureCredential());
```
