---
name: angular-structure
description: "Angular enterprise architecture: folder structure, feature slices, signals, standalone components, control flow, @defer, zoneless, NgRx SignalStore, httpResource, typed forms, SSR/hydration, Vitest/Playwright, Tailwind, Nx. Use when scaffolding an Angular project, reviewing its structure, choosing state management or data fetching, or making architectural decisions in an Angular/TypeScript codebase."
license: MIT
metadata:
  author: Marwen Amamou | amamoumarwen@gmail.com
  version: "1.0.0"
---

# Angular Enterprise Architecture Guidelines (2026)

Feature-first, enterprise-grade Angular architecture that scales across teams and codebases. Assumes **TypeScript strict**, modern tooling (**esbuild + Vite**, Angular 21+), and emphasizes **feature isolation**, **signals-first reactivity**, **performance**, and **operability**.

## Load on demand

The core rules in this file always apply. Read a reference below **only when the task needs it**:

| Topic | File |
| :-- | :-- |
| 3) Shared Layer (Stateless & Reusable) | [references/3-shared-layer-stateless-reusable.md](references/3-shared-layer-stateless-reusable.md) |
| 4) Feature Slices (DDD-style) | [references/4-feature-slices-ddd-style.md](references/4-feature-slices-ddd-style.md) |
| 5) Signals — Reactivity Model | [references/5-signals-reactivity-model.md](references/5-signals-reactivity-model.md) |
| 6) New Control Flow Syntax | [references/6-new-control-flow-syntax.md](references/6-new-control-flow-syntax.md) |
| 7) Deferrable Views (`@defer`) | [references/7-deferrable-views-defer.md](references/7-deferrable-views-defer.md) |
| 8) Data Fetching | [references/8-data-fetching.md](references/8-data-fetching.md) |
| 9) State Management Strategy | [references/9-state-management-strategy.md](references/9-state-management-strategy.md) |
| 10) Routing | [references/10-routing.md](references/10-routing.md) |
| 11) Forms | [references/11-forms.md](references/11-forms.md) |
| 12) Styling | [references/12-styling.md](references/12-styling.md) |
| 13) Performance | [references/13-performance.md](references/13-performance.md) |
| 14) Security & Compliance | [references/14-security-compliance.md](references/14-security-compliance.md) |
| 15) Server-Side Rendering & Hydration | [references/15-server-side-rendering-hydration.md](references/15-server-side-rendering-hydration.md) |
| 16) Testing | [references/16-testing.md](references/16-testing.md) |
| 17) Build Tools | [references/17-build-tools.md](references/17-build-tools.md) |
| 18) Tooling & Governance | [references/18-tooling-governance.md](references/18-tooling-governance.md) |
| 19) CI/CD & Quality Gates | [references/19-ci-cd-quality-gates.md](references/19-ci-cd-quality-gates.md) |
| 20) API Boundary & Models | [references/20-api-boundary-models.md](references/20-api-boundary-models.md) |
| 21) Example: Users Feature | [references/21-example-users-feature.md](references/21-example-users-feature.md) |
| 22) Layout Pattern | [references/22-layout-pattern.md](references/22-layout-pattern.md) |

---

## 1) High-Level Structure

```
src/
  app/
    app.component.ts              # root component (thin shell)
    app.config.ts                 # application providers
    app.routes.ts                 # top-level route definitions
    core/                         # singleton services, guards, interceptors
      auth/
        auth.service.ts
        auth.guard.ts
        auth.interceptor.ts
      error/
        global-error-handler.ts
      layout/
        header.component.ts
        sidebar.component.ts
        footer.component.ts
    shared/                       # reusable & stateless UI/utilities
      ui/                         # presentational components (buttons, cards, table)
      directives/                 # generic directives
      pipes/                      # generic pipes
      utils/                      # pure TS helpers
      styles/                     # design tokens, mixins, global CSS
    features/                     # domain-driven feature slices
      users/
        user-list/
          user-list.component.ts
        user-detail/
          user-detail.component.ts
        user-form/
          user-form.component.ts
        data-access/
          users.service.ts
          users.store.ts
          users.model.ts
        users.routes.ts
  environments/
    environment.ts
    environment.prod.ts
  assets/
  styles/
    tokens.css
    globals.css
  main.ts                         # app bootstrap
```

**Philosophy**
- Organize by **feature/domain**, not by technical layer.
- Keep **shared** stateless and UI-only; keep **data-access** inside the owning feature.
- Prefer **co-location**: tests, styles, stories next to implementation.
- **Standalone components** are the default — no `NgModule` for new code.

> **Nx Monorepo**: For large orgs, extract features into domain libraries (`packages/products/feat-product-list`, `packages/products/data-access`) and enforce module boundaries via tags (`type:feature`, `type:shared`, `scope:products`).

---

## 2) Core App Wiring

- **Bootstrap**: `app.config.ts` hosts all root providers (`provideRouter`, `provideHttpClient`, `provideZonelessChangeDetection`, etc.).
- **Routing**: Standalone routes in `app.routes.ts` with lazy-loaded feature routes.
- **Layout**: App chrome (header + sidebar + footer) lives in `core/layout/`, not in `shared` or features. Use `<router-outlet />` for content slots.
- **Errors**: Global `ErrorHandler` + error reporting (Sentry, etc.).
- **Runtime config**: Load from `/config.json` or environment files; expose via a typed service.

**Example**
```typescript
// app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(appRoutes, withComponentInputBinding()),
    provideHttpClient(
      withInterceptors([authInterceptor, errorInterceptor]),
      withFetch()
    ),
    provideZonelessChangeDetection(),
    provideClientHydration(withEventReplay(), withIncrementalHydration()),
  ],
};
```

```typescript
// main.ts
bootstrapApplication(AppComponent, appConfig);
```

---

## Summary Table

| Layer | Purpose | Rules |
|---|---|---|
| **core/** | Singletons (auth, layout, error handling, interceptors) | App-wide, instantiated once |
| **shared/** | Stateless UI + generic directives/pipes/utils | No data fetching/HTTP |
| **features/** | Domain UI + data-access + local store | Export minimally, isolate dependencies |
| **environments/** | Build-time config | Non-sensitive flags only |

## Recommended Stack (2026)

| Concern | Tool |
|---|---|
| Framework | **Angular 21+** (standalone, zoneless) |
| Language | **TypeScript 5.8+ strict** |
| Reactivity | **Signals** (`signal`, `computed`, `linkedSignal`, `effect`) |
| Routing | **Standalone routes** with `loadChildren` / `loadComponent` |
| Data fetching | **httpResource** (reads) + **HttpClient** (mutations) |
| Client state | **NgRx SignalStore** (complex) / plain signals (simple) |
| Forms | **Typed Reactive Forms** (`NonNullableFormBuilder`) |
| Styling | **Tailwind CSS v4** + **Angular CDK** |
| Unit testing | **Vitest** + **TestBed** |
| E2E testing | **Playwright** |
| API mocking | **MSW** or **HttpTestingController** |
| Build | **esbuild + Vite** (Angular CLI default) |
| Monorepo | **Nx** |
| SSR | **Angular SSR** with incremental hydration |
