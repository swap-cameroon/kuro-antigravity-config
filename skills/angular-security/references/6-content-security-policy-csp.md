## 6. Content Security Policy (CSP)

### AutoCSP (Angular 19 — Developer Preview)

Angular 19 introduced automatic hash-based Strict CSP generation. Enable in `angular.json`:

```json
{
  "projects": {
    "my-app": {
      "architect": {
        "build": {
          "options": {
            "security": {
              "autoCsp": true
            }
          }
        }
      }
    }
  }
}
```

This generates CSP hashes for inline scripts in `index.html`, preventing unauthorized script execution.

### Zone.js and CSP

Zone.js monkey-patches async APIs, which can conflict with strict CSP policies banning `unsafe-eval`.

**Solution: Go Zoneless**

```typescript
// Angular 19 (experimental)
provideExperimentalZonelessChangeDetection();

// Angular 20+ (stable)
provideZonelessChangeDetection();
```

Benefits:

- Eliminates `unsafe-eval` CSP conflict
- ~20% bundle size reduction
- Clean stack traces (no Zone-specific frames)
- Relies on Signals for change detection

Remove `zone.js` from `polyfills` in `angular.json` (both build and test targets).

### Trusted Types

Configure these policies in your CSP header:

- `angular` — core framework code
- `angular#bundler` — lazy-loaded chunk files
- `angular#unsafe-bypass` — DomSanitizer bypass calls (audit these!)
- `angular#unsafe-jit` — JIT compiler (should NOT appear in production)

### Minimum CSP for Angular

```
default-src 'self';
style-src 'self' 'nonce-{random}';
script-src 'self' 'nonce-{random}';
```

Security headers should be configured at the **server/CDN level**:

```
Content-Security-Policy: [see above]
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```
