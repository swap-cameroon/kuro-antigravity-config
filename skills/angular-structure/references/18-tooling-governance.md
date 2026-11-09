## 18) Tooling & Governance

- **TypeScript strict mode** — mandatory, no exceptions. TS 5.8+.
- **Path aliases** for `@app`, `@shared`, `@features/*`, `@core`.
- **ESLint** (`@angular-eslint`) + **Prettier**; add custom rules to forbid cross-feature imports.
- **`inject()` function** preferred over constructor injection — use Angular's migration schematic (`ng generate @angular/core:inject`).
- Consider **Nx** for monorepos: cached builds, affected tests, and **module boundary linting** via tags (`type:feature`, `type:shared`, `scope:users`).

```json
{
  "paths": {
    "@app/*": ["src/app/*"],
    "@core/*": ["src/app/core/*"],
    "@shared/*": ["src/app/shared/*"],
    "@features/*": ["src/app/features/*"]
  }
}
```
