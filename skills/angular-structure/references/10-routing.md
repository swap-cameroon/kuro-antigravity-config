## 10) Routing

### Standalone Route Configuration

```typescript
// app.routes.ts
export const appRoutes: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [
      {
        path: 'users',
        loadChildren: () => import('./features/users/users.routes')
          .then(m => m.USERS_ROUTES),
        canMatch: [() => inject(AuthService).isAuthenticated()],
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard.component')
          .then(m => m.DashboardComponent),
        canActivate: [authGuard],
        resolve: { stats: statsResolver },
      },
    ],
  },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login.component')
      .then(m => m.LoginComponent),
  },
];
```

### Feature Routes

```typescript
// features/users/users.routes.ts
export const USERS_ROUTES: Routes = [
  { path: '', component: UserListComponent },
  { path: 'new', component: UserFormComponent },
  { path: ':id', component: UserDetailComponent },
  { path: ':id/edit', component: UserFormComponent },
];
```

### Functional Guards & Resolvers

```typescript
// core/auth/auth.guard.ts
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  return authService.isAuthenticated()
    ? true
    : router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
};

// Functional resolver
export const userResolver: ResolveFn<User> = (route) => {
  return inject(UsersService).getById(route.paramMap.get('id')!);
};
```

**Key patterns**
- **Functional guards and resolvers** — class-based are deprecated.
- Use `canMatch` instead of `canLoad` (deprecated) — prevents lazy loading code user cannot access.
- `loadChildren` for feature route files; `loadComponent` for single-component routes.
- Scoped providers via `providers` array on route config.
