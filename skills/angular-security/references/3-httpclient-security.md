## 3. HttpClient Security

### XSRF Protection (Built-in)

Angular `HttpClient` automatically reads `XSRF-TOKEN` cookie and sets `X-XSRF-TOKEN` header on mutating requests (POST/PUT/DELETE).

```typescript
provideHttpClient(
  withXsrfConfiguration({
    cookieName: "CUSTOM_XSRF_TOKEN",
    headerName: "X-Custom-Xsrf-Header",
  }),
);
```

### Critical: CVE-2025-66035 — XSRF Token Leakage

Protocol-relative URLs (`//evil.com/api`) were incorrectly treated as same-origin, causing Angular to attach XSRF tokens to attacker-controlled domains.

**Fix**: Update to Angular 19.2.16+.

### withFetch() Implications

`withFetch()` switches from `XMLHttpRequest` to the Fetch API:

- Recommended for SSR applications (performance)
- Credentials handling differs: Fetch uses `credentials: "include"` vs XHR's `withCredentials: true`
- CORS behavior has subtle differences — may surface issues in SSR
- Test thoroughly when switching

### Functional vs Class-Based Interceptors

Class-based interceptors (`HttpInterceptor` interface) still work but **functional interceptors via `withInterceptors()` are the modern pattern**:

- More predictable ordering (array order)
- Better tree-shaking
- Security-relevant: interceptor order matters for auth, error handling, and retry logic

### XSSI Protection

Angular auto-strips the `)]}',\n` prefix from JSON responses (XSSI prevention).

### Request Configuration

```typescript
// Configure secure HTTP client
provideHttpClient(
  withInterceptors([authInterceptor, errorInterceptor]),
  withXsrfConfiguration({
    cookieName: "XSRF-TOKEN",
    headerName: "X-XSRF-TOKEN",
  }),
  withFetch(), // For SSR
);
```
