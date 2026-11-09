### 🔐 Authentication (JWT / OAuth / Guards)

- **Route guards** — flag protected routes missing `canActivate` with an auth guard.
- **Token storage** — flag JWT stored in `localStorage`; prefer `httpOnly` cookies or `sessionStorage` with XSS mitigations.
- **Token refresh** — flag implementations that don't handle `401` responses with token refresh logic in an interceptor.
- **`isAuthenticated` as signal** — flag auth state exposed as Observable where `signal()` + `toSignal()` would be cleaner for template consumption.
- **Role-based access** — flag guards checking only authentication, not authorization (roles/permissions) for admin or privileged routes.
- **OAuth `state` parameter** — flag OAuth redirect flows missing CSRF state validation.
