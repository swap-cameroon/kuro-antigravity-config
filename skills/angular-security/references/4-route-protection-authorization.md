## 4. Route Protection & Authorization

### Functional Guards (Angular 17+ — class-based deprecated)

```typescript
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticated()) {
    return router.createUrlTree(["/login"], {
      queryParams: { returnUrl: state.url },
    });
  }

  const requiredRole = route.data["role"];
  if (requiredRole && !authService.hasRole(requiredRole)) {
    return router.createUrlTree(["/unauthorized"]);
  }

  return true;
};

// Route configuration
{
  path: "admin",
  canActivate: [authGuard],
  data: { role: "admin" },
  loadComponent: () => import("./admin.component"),
}
```

### Important

- Guards are **client-side only** — they are a UX mechanism, NOT a security boundary
- Server-side authorization is mandatory
- Lazy-loaded modules can be fetched by any client regardless of guards
- Put guards at **layout routes** to protect entire sections
- `CanLoad` is deprecated — use `CanMatch` instead
