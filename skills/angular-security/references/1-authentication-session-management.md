## 1. Authentication & Session Management

### Requirements

- **Token storage**: Store access tokens in memory (Angular service), NEVER in localStorage/sessionStorage
- **Refresh tokens**: Store in HttpOnly, Secure, SameSite cookies
- **Token expiration**: Implement automatic server-side refresh before expiration
- **Logout**: Clear all tokens, call backend invalidation, redirect to login
- **Session timeout**: Implement inactivity timeout with warning before logout
- **Multi-tab sync**: Synchronize auth state across browser tabs (BroadcastChannel API)
- **Token injection**: Automatically inject tokens via HttpClient interceptors
- **Secure redirects**: Validate redirect URLs to prevent open redirect vulnerabilities

### Angular Pattern

```typescript
// Store tokens in memory only — never localStorage
@Injectable({ providedIn: "root" })
export class AuthService {
  private accessToken: string | null = null;

  setToken(token: string) {
    this.accessToken = token; // Memory only
  }

  getToken(): string | null {
    return this.accessToken;
  }

  clearToken() {
    this.accessToken = null;
  }
}

// Functional interceptor for token injection (Angular 17+)
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getToken();

  if (token) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        return inject(AuthService)
          .refresh()
          .pipe(switchMap(() => next(req)));
      }
      return throwError(() => error);
    }),
  );
};

// Register in app config
provideHttpClient(withInterceptors([authInterceptor]));
```

### What NOT to Do

- Store tokens in localStorage or sessionStorage (vulnerable to XSS)
- Store sensitive data in cookies without HttpOnly flag
- Include tokens in URL parameters
- Keep users logged in indefinitely without re-authentication
- Use class-based `HttpInterceptor` (deprecated — use functional interceptors)
