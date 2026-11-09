## 5. Angular SSR Security (@angular/ssr)

### Critical: CVE-2025-59052 — Cross-Request Data Leakage (CVSS 7.1)

Angular's SSR platform reused a shared global injector across concurrent requests. Under load, **User A's auth tokens, session data, or query results could leak to User B**.

**Fix**: Update to Angular 19.2.17+. `bootstrapApplication` now requires per-request `BootstrapContext`.

### SSRF via Header Injection

Angular's URL reconstruction trusted `Host`, `X-Forwarded-Host`, `X-Forwarded-Port`, `X-Forwarded-Proto`, `X-Forwarded-Prefix` headers without validation. Attackers could steer internal requests and steal Authorization headers.

**Fix**: Configure `allowedHosts` in `angular.json`:

```json
{
  "security": {
    "allowedHosts": ["example.com", "*.example.com"]
  }
}
```

Or via `NG_ALLOWED_HOSTS` environment variable.

### Open Redirect via X-Forwarded-Prefix

Enabled phishing and SEO hijacking. Patched in same advisory.

### SSR Security Rules

- Update to Angular 19.2.17+ (per-request isolation)
- Configure `allowedHosts` to prevent SSRF
- Ensure `ngJitMode: false` in server builds
- Use absolute URLs instead of `req.headers` for URL construction
- Never share state across requests — use per-request services
- If unable to upgrade: disable SSR via server routes or builder options
