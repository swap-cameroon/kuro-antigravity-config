### 🌐 HttpClient & REST

- **Services, not components** — flag `HttpClient` injected directly in a component; all HTTP calls belong in services.

- **`httpResource()` (v19.2+)** — acceptable for component-level reactive data fetching. Flag it inside services (use `HttpClient` there).

- **Error handling** — flag HTTP calls without `catchError` or error state handling in the UI.

- **Typed HTTP responses** — flag `http.get('/api/users')` without a type parameter; always use `http.get<User[]>('/api/users')`.

- **Interceptors** — flag class-based `HttpInterceptor` in Angular 15+ projects; use functional interceptors:
  ```ts
  // ✅ Functional interceptor
  export const authInterceptor: HttpInterceptorFn = (req, next) => {
    const token = inject(AuthService).getToken();
    return next(req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }));
  };
  ```

- **Retry logic** — flag API calls that should retry on transient failures (network errors) without `retry()` or `retryWhen()`.
