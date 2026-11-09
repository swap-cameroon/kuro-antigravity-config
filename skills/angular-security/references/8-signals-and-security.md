## 8. Signals and Security

Angular Signals (stable in v19) do not introduce new security vulnerabilities:

- **No XSS vector**: Signal values pass through Angular's template sanitization. `{{ mySignal() }}` is sanitized like `{{ myProperty }}`.
- **State exposure risk**: Signals are synchronous. If a `signal()` holds sensitive data (tokens, PII), it's accessible to any code with a reference. Follow principle of least privilege.
- **`computed()` signals**: Lazily evaluated — no stale security state leaking.
- **`effect()` timing**: Runs after change detection. Be cautious about effects that write sensitive data to localStorage.
- **`linkedSignal()`**: Derived writable signals — ensure they don't expose source data to broader scopes.
