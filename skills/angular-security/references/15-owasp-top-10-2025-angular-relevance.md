## 15. OWASP Top 10:2025 — Angular Relevance

| Rank    | Category                                     | Angular Relevance                                                          |
| ------- | -------------------------------------------- | -------------------------------------------------------------------------- |
| **A01** | Broken Access Control                        | **High** — route guards are client-side only; server must enforce          |
| **A02** | Security Misconfiguration                    | **High** — CSP, CORS, JIT in production, debug flags                       |
| **A03** | **Supply Chain Failures** (NEW)              | **Critical** — SVG-based XSS, esbuild CVE, npm attacks                     |
| **A04** | Cryptographic Failures                       | Medium — token handling, HTTPS                                             |
| **A05** | Injection                                    | **Angular-specific** — template injection (CSTI) if JIT; SVG/MathML bypass |
| **A06** | Insecure Design                              | High — SSR shared injector (CVE-2025-59052)                                |
| **A07** | Auth Failures                                | High — see Section 1                                                       |
| **A08** | Software & Data Integrity                    | High — CI/CD, ng add schematics                                            |
| **A09** | Logging & Alerting Failures                  | Medium — client-side error reporting                                       |
| **A10** | **Mishandling Exceptional Conditions** (NEW) | Medium — error handler, fail closed                                        |
