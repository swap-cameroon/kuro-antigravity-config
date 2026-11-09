## 14) Security & Compliance

- Angular **auto-sanitizes** interpolated values in templates (HTML, styles, URLs).
- Avoid `innerHTML` with untrusted data; use `DomSanitizer.bypassSecurityTrustHtml()` only when absolutely necessary.
- Use `Renderer2` instead of direct DOM manipulation (`ElementRef.nativeElement`).
- Content Security Policy (CSP); avoid inline scripts/styles. Angular supports **Trusted Types** API.
- **CSRF**: `HttpClient` handles CSRF tokens via the double-submit cookie pattern.
- Auth tokens: use `Secure`, `HttpOnly`, `SameSite` cookies where possible.
- Use `withFetch()` in `provideHttpClient()` for modern fetch API.
- Functional route guards for authentication/authorization.
- Handle secrets on the server; never ship secrets to the client bundle.
