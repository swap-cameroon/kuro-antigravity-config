## 17) Build Tools

| Tool | Use case |
|---|---|
| **esbuild + Vite** | Default Angular CLI builder. Fastest builds, zero config. |
| **Nx** | Enterprise monorepos. Cached builds, affected tests, module boundary linting. |

Angular CLI uses esbuild for compilation and Vite for the dev server by default since Angular 17. No `vite.config.ts` needed.

```json
{
  "build": { "builder": "@angular-devkit/build-angular:application" },
  "serve": { "builder": "@angular-devkit/build-angular:dev-server" },
  "test":  { "builder": "@angular/build:unit-test" }
}
```
