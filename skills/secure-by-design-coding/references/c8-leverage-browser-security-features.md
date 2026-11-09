### C8 — Leverage Browser Security Features

*Use the browser's built-in security mechanisms — don't fight them.*

**Content Security Policy (CSP):**
- Start with `default-src 'self'` and add only what's needed
- Never use `'unsafe-inline'` or `'unsafe-eval'` — use nonces or hashes
- Use `report-uri` or `report-to` to monitor violations
- Deploy in `Content-Security-Policy-Report-Only` first, then enforce

**Cookie security attributes — always set all four:**

| Attribute | Value | Purpose |
|---|---|---|
| `Secure` | required | Only sent over HTTPS |
| `HttpOnly` | required | No JavaScript access (prevents XSS theft) |
| `SameSite` | `Lax` or `Strict` | CSRF protection |
| `__Host-` prefix | recommended | Enforces Secure + path=/ + no domain |

**Output encoding — encode for the output context:**

| Context | Encoding | Library |
|---|---|---|
| HTML body | HTML entity encoding | Framework auto-escaping |
| HTML attribute | Attribute encoding | Framework auto-escaping |
| JavaScript | JavaScript encoding | Never inject user data into JS |
| URL parameter | URL encoding | `encodeURIComponent()` |
| CSS | CSS encoding | Avoid user data in CSS |
| JSON API | JSON serialization | `JSON.stringify()` (auto-escapes) |

```typescript
// ❌ XSS — user data injected into HTML without encoding
element.innerHTML = userInput;

// ✅ Safe — use textContent or framework auto-escaping
element.textContent = userInput;
// Or with sanitization when HTML is required:
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

**Subresource Integrity (SRI):**
```html
<!-- ✅ Verify CDN scripts haven't been tampered with -->
<script src="https://cdn.example.com/lib.js"
        integrity="sha384-abc123..."
        crossorigin="anonymous"></script>
```
