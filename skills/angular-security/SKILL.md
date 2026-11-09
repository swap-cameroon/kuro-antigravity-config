---
name: angular-security
description: "Angular frontend security: XSS and DomSanitizer, CSRF/XSRF, CSP and Trusted Types, auth and session handling, route guards, HttpClient and SSR hardening, NgRx and supply-chain risks, deployment hardening (OWASP 2025). Use when writing or reviewing security-sensitive Angular code, handling user input, configuring auth or CSP, or securing Angular SSR."
license: MIT
metadata:
  author: Marwen Amamou | amamoumarwen@gmail.com
  version: "1.0.0"
---

# Angular Frontend Security Best Practices (2026)

A comprehensive guide for building secure, production-grade Angular applications. Covers **Angular 19+**, **@angular/ssr**, and aligns with **OWASP Top 10:2025**.

## Load on demand

The core rules in this file always apply. Read a reference below **only when the task needs it**:

| Topic | File |
| :-- | :-- |
| 1. Authentication & Session Management | [references/1-authentication-session-management.md](references/1-authentication-session-management.md) |
| 3. HttpClient Security | [references/3-httpclient-security.md](references/3-httpclient-security.md) |
| 4. Route Protection & Authorization | [references/4-route-protection-authorization.md](references/4-route-protection-authorization.md) |
| 5. Angular SSR Security (@angular/ssr) | [references/5-angular-ssr-security-angular-ssr.md](references/5-angular-ssr-security-angular-ssr.md) |
| 6. Content Security Policy (CSP) | [references/6-content-security-policy-csp.md](references/6-content-security-policy-csp.md) |
| 7. Input Validation & Sanitization | [references/7-input-validation-sanitization.md](references/7-input-validation-sanitization.md) |
| 8. Signals and Security | [references/8-signals-and-security.md](references/8-signals-and-security.md) |
| 9. State Management Security (NgRx) | [references/9-state-management-security-ngrx.md](references/9-state-management-security-ngrx.md) |
| 10. Supply Chain Security | [references/10-supply-chain-security.md](references/10-supply-chain-security.md) |
| 11. Secure Build & Deployment | [references/11-secure-build-deployment.md](references/11-secure-build-deployment.md) |
| 12. Secure Data Handling | [references/12-secure-data-handling.md](references/12-secure-data-handling.md) |
| 13. Error Handling & Logging | [references/13-error-handling-logging.md](references/13-error-handling-logging.md) |
| 14. Testing Security | [references/14-testing-security.md](references/14-testing-security.md) |
| 15. OWASP Top 10:2025 — Angular Relevance | [references/15-owasp-top-10-2025-angular-relevance.md](references/15-owasp-top-10-2025-angular-relevance.md) |
| 16. Monitoring & Compliance | [references/16-monitoring-compliance.md](references/16-monitoring-compliance.md) |

---

## 2. Template Security & XSS Prevention

### Angular's Built-in Sanitization

Angular automatically sanitizes values in templates across **five security contexts**: HTML, Style, URL, Resource URL, and Script. This is the primary XSS defense.

### Critical: AOT vs JIT

- **AOT (default)**: Prevents template injection entirely. Templates compile at build time — user input cannot become template syntax.
- **JIT**: Trusts template code at runtime. If templates are dynamically generated with user input, full XSS is possible.
- **Rule**: NEVER use JIT in production. Ensure `ngJitMode` is `false` in server builds.

### Template Injection Test

If `{{ 7*7 }}` entered as user input renders as `49`, Client-Side Template Injection (CSTI) is present. AOT prevents this; JIT does not.

### DomSanitizer Bypass Methods

Each bypass creates a potential XSS vector. Audit every usage:

```typescript
// ❌ DANGEROUS — bypasses all sanitization
this.sanitizer.bypassSecurityTrustHtml(userInput);

// ✅ SAFE — sanitize first, then bypass
const sanitized = DOMPurify.sanitize(userInput);
this.sanitizer.bypassSecurityTrustHtml(sanitized);

// ✅ BEST — use Angular's auto-sanitization
{
  {
    userInput;
  }
} // Angular auto-escapes in templates
```

When Trusted Types are enforced, bypass calls use the `angular#unsafe-bypass` policy, making them auditable.

### CVE-2025-66412 — Stored XSS via SVG/MathML

Angular's template compiler had an incomplete security schema for SVG animation attributes (`animate`, `set`, `animateMotion`, `animateTransform`) and MathML attributes. Malicious `javascript:` URLs in these attributes bypassed sanitization.

**Fix**: Update to Angular 19.2.17+.

### Rules

- Never concatenate user input into Angular template strings
- Audit all `bypassSecurityTrust*` calls — each is a potential XSS vector
- Use DOMPurify before any bypass call
- Keep Angular patched for SVG/MathML sanitization fixes
- Prefer `[innerHTML]="userContent"` (auto-sanitized) over bypass methods

---

## Security Checklist

Before deploying to production:

### Authentication & Authorization

- [ ] Tokens stored in service (memory) or HttpOnly cookies, not localStorage
- [ ] Refresh tokens in HttpOnly, Secure, SameSite cookies
- [ ] Functional route guards + server-side authorization enforcement
- [ ] Session timeout with inactivity detection
- [ ] Functional interceptors for token injection (not class-based)

### Template & XSS

- [ ] AOT compilation (JIT disabled in production)
- [ ] All `bypassSecurityTrust*` calls audited and paired with DOMPurify
- [ ] No user input concatenated into template strings
- [ ] Angular 19.2.17+ (SVG/MathML XSS fix)

### HttpClient & CSRF

- [ ] XSRF configuration set up
- [ ] Angular 19.2.16+ (XSRF token leakage fix)
- [ ] No protocol-relative URLs in API calls
- [ ] Custom headers on requests

### SSR

- [ ] Angular 19.2.17+ (cross-request data leak fix)
- [ ] `allowedHosts` configured
- [ ] Per-request isolation verified
- [ ] `ngJitMode: false` in server builds

### CSP & Trusted Types

- [ ] AutoCSP enabled (Angular 19+)
- [ ] Zoneless change detection (no `unsafe-eval` needed)
- [ ] Trusted Types policies configured
- [ ] Security headers at server/CDN level

### Supply Chain

- [ ] Lockfiles committed
- [ ] Dependencies audited (`npm audit` in CI)
- [ ] esbuild >= 0.25.0
- [ ] Third-party schematics audited before `ng add`

### Build & Deploy

- [ ] Source maps disabled in production
- [ ] No secrets in environment files
- [ ] console.log stripped in production
- [ ] AutoCSP enabled

### State & Data

- [ ] NgRx DevTools disabled in production
- [ ] No sensitive data in localStorage
- [ ] Persisted state encrypted and cleared on logout

### Monitoring

- [ ] Error monitoring configured (Sentry)
- [ ] Security events tracked
- [ ] Alerts for critical errors
- [ ] Incident response plan documented
