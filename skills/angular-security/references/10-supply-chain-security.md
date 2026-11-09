## 10. Supply Chain Security

### Critical Angular CVEs (2025)

| CVE            | Package             | Impact                      | Fix      |
| -------------- | ------------------- | --------------------------- | -------- |
| CVE-2025-66412 | `@angular/compiler` | Stored XSS via SVG/MathML   | 19.2.17+ |
| CVE-2025-66035 | `@angular/common`   | XSRF token leakage          | 19.2.16+ |
| CVE-2025-59052 | `@angular/ssr`      | SSR cross-request data leak | 19.2.17+ |

### esbuild Vulnerability

CVE-2024-23334 affected esbuild <= 0.24.2 (dev server exposed files). Angular CLI uses esbuild internally. Force upgrade:

```json
// package.json
{
  "overrides": {
    "esbuild": ">=0.25.0"
  }
}
```

### Angular-Specific Risks

- **SVG-based XSS**: Malicious SVGs in dependency packages can trigger XSS through Angular's template compiler
- **ng add schematics**: Execute arbitrary code — audit all third-party schematics
- **ng update**: Does not perform security audits — always run `npm audit` after updates
- **Angular EOL**: Aggressive cycle — v18 already EOL. Unsupported versions get no security patches

### Defense Strategies

- Commit lockfiles; pin exact versions in production
- Run `npm audit` / `pnpm audit` in CI
- 7-14 day adoption delay for new packages
- Use Socket.dev, Snyk for real-time threat detection
- SRI for CDN resources
