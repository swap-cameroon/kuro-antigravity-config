## 22) Layout Pattern

```
core/layout/
  layout.component.ts       # header + sidebar + <router-outlet />
  header.component.ts
  sidebar.component.ts
```

```typescript
// app.routes.ts
export const appRoutes: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [
      { path: 'users', loadChildren: () => import('./features/users/users.routes').then(m => m.USERS_ROUTES) },
      { path: 'dashboard', loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent) },
      { path: '', redirectTo: 'users', pathMatch: 'full' },
    ],
  },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login.component').then(m => m.LoginComponent),
  },
];
```
