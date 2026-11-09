### 🗺️ Routing & Lazy Loading

- **Lazy loading** — flag `loadComponent` / `loadChildren` not used for feature routes. Every feature route should be lazy-loaded:
  ```ts
  // ❌ Eager — entire module loaded upfront
  { path: 'users', component: UsersComponent }

  // ✅ Lazy — loaded on demand
  { path: 'users', loadComponent: () => import('./users/users.component') }
  ```

- **Functional guards** — flag class-based `CanActivate` / `CanDeactivate` guards in Angular 15+ projects; use functional guards:
  ```ts
  // ❌ Class-based guard (legacy)
  @Injectable()
  export class AuthGuard implements CanActivate { ... }

  // ✅ Functional guard
  export const authGuard: CanActivateFn = (route, state) => {
    return inject(AuthService).isAuthenticated()
      ? true
      : inject(Router).createUrlTree(['/login']);
  };
  ```

- **`input.fromRoute()` (v17.1+)** — flag components using `ActivatedRoute.snapshot.params` or `paramMap` subscriptions; prefer `input.fromRoute()` where route inputs are enabled.

- **`withComponentInputBinding()`** — flag projects not enabling route component input binding in `provideRouter()` — required for `input.fromRoute()` to work.

- **Route prefetching** — flag critical user flows without `prefetch` strategy on lazy routes.
