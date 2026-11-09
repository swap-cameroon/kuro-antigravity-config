---
name: code-reviewer-angular
description: "Angular/TypeScript review overlay extending code-reviewer with version-aware rules. Use when reviewing Angular components, services, directives, pipes, guards, resolvers, NgRx, RxJS, HttpClient, SSR or any .ts/.html file in an Angular project. Not for Node.js backend code or plain TypeScript utilities."
license: MIT
metadata:
  author: Marwen Amamou | amamoumarwen@gmail.com
  version: "1.0.0"
---

# Code Reviewer — Angular Overlay

This skill extends `code-reviewer` (the universal skill). Always apply the universal
skill's full checklist first, then apply the Angular-specific rules in this file on top.

**Composition order:**
1. Run `code-reviewer` (universal pillars: correctness, security, performance, DRY, tests, docs)
2. Run this overlay (Angular/TypeScript-specific rules below)
3. Report findings from both in a single unified output

## Load on demand

The core rules in this file always apply. Read a reference below **only when the task needs it**:

| Topic | File |
| :-- | :-- |
| Angular-Specific Review Checklist - 🏗️ Components | [references/components.md](references/components.md) |
| Angular-Specific Review Checklist - ⚡ Signals | [references/signals.md](references/signals.md) |
| Angular-Specific Review Checklist - 🔁 RxJS | [references/rxjs.md](references/rxjs.md) |
| Angular-Specific Review Checklist - 🗺️ Routing & Lazy Loading | [references/routing-lazy-loading.md](references/routing-lazy-loading.md) |
| Angular-Specific Review Checklist - 🌐 HttpClient & REST | [references/httpclient-rest.md](references/httpclient-rest.md) |
| Angular-Specific Review Checklist - 🔐 Authentication (JWT / OAuth / Guards) | [references/authentication-jwt-oauth-guards.md](references/authentication-jwt-oauth-guards.md) |
| Angular-Specific Review Checklist - 📦 NgRx | [references/ngrx.md](references/ngrx.md) |
| Angular-Specific Review Checklist - 🎨 Angular Material | [references/angular-material.md](references/angular-material.md) |
| Angular-Specific Review Checklist - 🖥️ Angular Universal / SSR | [references/angular-universal-ssr.md](references/angular-universal-ssr.md) |
| Angular-Specific Review Checklist - 🔵 GraphQL / Apollo Angular (if present) | [references/graphql-apollo-angular-if-present.md](references/graphql-apollo-angular-if-present.md) |

---

## Step 0 — Detect Versions First (always, before reviewing anything)

Run these commands before touching any code. Version determines which rules apply.

```bash
# Angular and CLI version
cat package.json | grep -E '"(@angular/core|@angular/cli|@angular/material|@ngrx|@apollo/client|apollo-angular|typescript|rxjs)"' | head -20

# Check if zoneless is configured
grep -r "provideZoneless\|provideExperimentalZoneless\|zone.js" src/ --include="*.ts" -l 2>/dev/null | head -5

# Check standalone vs module-based
grep -r "NgModule\|standalone:" src/ --include="*.ts" -l 2>/dev/null | head -10

# Check for legacy structural directives still in use
grep -r "\*ngIf\|\*ngFor\|\*ngSwitch" src/ --include="*.html" -l 2>/dev/null | head -5
```

Report at the top of your review:
```
🔍 Environment: Angular vX.Y | TypeScript X.Y | RxJS X.Y
    NgRx: X.Y (if present) | Apollo Angular: X.Y (if present)
    Mode: Standalone / Module-based / Mixed | Zoneless: Yes / No / Not yet
```

Then apply the version-specific rules below.

---

## Angular Version Rules

### Angular 17
- New control flow (`@if`, `@for`, `@switch`) introduced — flag new code still using `*ngIf`/`*ngFor`; suggest migration.
- `standalone: true` is now the default recommended approach — flag new `NgModule`-based components without justification.
- `@for` **requires `track`** — flag any `@for` loop missing `track user.id` (or equivalent stable key). Never `track $index` on mutable lists.
- Deferrable views (`@defer`) available — flag large components that could benefit from deferred loading.
- TypeScript 5.2+ required — flag `tsconfig` targeting lower versions.

### Angular 18
- Signals API **stable** — flag `BehaviorSubject` used for simple local/component state; suggest `signal()`.
- Zoneless change detection available as experimental (`provideExperimentalZonelessChangeDetection`) — don't flag usage, but flag missing `OnPush` on new components regardless.
- esbuild + Vite is the default builder — flag `angular.json` still using webpack (`@angular-devkit/build-angular:browser`) for new projects.
- Angular Material 3 stable — flag Material 2 component APIs that were renamed.

### Angular 19
- **`standalone: true` is the default** — flag `@Component({ standalone: false })` unless the component is intentionally module-based for a documented reason. Flag components declared in `NgModule.declarations` — Angular 19 will throw `NG2007`.
- `httpResource()` available (experimental, 19.2+) — acceptable for component-level data fetching; flag it being used in service layers (keep services using `HttpClient`).
- ⚠️ **EOL May 19, 2026** — flag projects pinned to Angular 19 as High priority. Suggest immediate migration to Angular 20.
- XSS CVE fixed in 19.2.18 (SVG `href`/`xlink:href` bypass) — flag projects on Angular 19 < 19.2.18 as Critical.

### Angular 20+ ✅ Current recommended
- Signals fully stable — `effect()`, `linkedSignal()`, `input()`, `output()`, `model()` all stable.
- **`ngIf`, `ngFor`, `ngSwitch` are deprecated** — flag any new code using structural directives; flag existing code as Medium priority for migration.
- `provideZonelessChangeDetection` (renamed from `provideExperimentalZonelessChangeDetection`) — flag old name as breaking in 20.
- TypeScript 5.8+ required, Node 20+ required — flag `package.json` engines or `tsconfig.json` targeting lower versions.
- View Engine metadata completely removed — flag any library dependency still referencing View Engine.

**Upcoming (Angular 21):**
- Signal Forms expected — once available, flag `FormGroup`/`FormControl` in new Angular 21+ projects; suggest Signal Forms.

---

## Angular-Specific Review Checklist

## Anti-Patterns Quick Reference

Flag these immediately when spotted:

| Anti-pattern | Severity | Fix |
|---|---|---|
| `*ngIf` / `*ngFor` in new code (v17+) | Medium | Use `@if` / `@for` |
| `@for` without `track` | High | Add `track item.id` |
| `subscribe()` in component body | High | Use `toSignal()` or `async` pipe |
| Constructor injection | Low | Use `inject()` |
| `@Input()` / `@Output()` in new code (v17.1+) | Low | Use `input()` / `output()` |
| `BehaviorSubject` for local state | Medium | Use `signal()` |
| `effect()` for state derivation | High | Use `computed()` |
| Writable `signal` exposed from service | Medium | Use `.asReadonly()` |
| `NgModule` for new features (v17+) | Medium | Use standalone components |
| `CommonModule` in standalone imports | Low | Import specific directives |
| Direct `window`/`document` in SSR app | Critical | Use `isPlatformBrowser()` |
| HTTP call in component | Medium | Move to service |
| `[innerHTML]` without sanitizer | Critical | Use `DomSanitizer` or restructure |
| Missing `OnPush` | Medium | Add `ChangeDetectionStrategy.OnPush` |
| Nested `.subscribe()` | High | Use `switchMap`/`combineLatest` |
| Unsubscribed observable | High | Use `takeUntilDestroyed()` |
| Angular 19 < 19.2.18 | Critical | Update — XSS CVE |
| Angular 19 (EOL May 2026) | High | Migrate to Angular 20 |

---

## Unified Output Format

Use the same format as `code-reviewer` (universal). Add an Angular context line:

```
🔍 Environment: Angular v20.x | TypeScript 5.8 | RxJS 7.x
    NgRx Signal Store: v19.x | Apollo Angular: N/A
    Mode: Standalone | Zoneless: Developer Preview enabled

## Code Review Summary
[... standard universal format ...]

### 🅰️ Angular-Specific Issues
[Issues found by this overlay, using the same severity/format as universal]
```

---

## Behavior Rules (Angular-specific additions)

- **Version first, always** — never apply version rules without detecting Angular version. Angular 19 EOL and XSS CVE are Critical-level findings.
- **Signals-first mindset for state, RxJS for streams** — don't flag RxJS in service layers; do flag RxJS `BehaviorSubject` replacing `signal()` in component state.
- **`OnPush` is always required** — no exceptions for new components regardless of version.
- **SSR is high-risk** — `window`/`document`/`localStorage` without platform guard is always Critical in SSR projects.
- **Don't refactor working NgRx to Signals** — if existing class-based NgRx works, flag as Low/suggestion only; don't gate a PR on it.
- **Delegate deep security audits** → `security-auditor` skill if available.
