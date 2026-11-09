## 8) Data Fetching

### httpResource (Reactive — Experimental)

```typescript
@Component({ ... })
export class ProductListComponent {
  private category = input<string>('all');

  // Auto re-fetches when category changes
  products = httpResource<Product[]>(() => `/api/products?category=${this.category()}`);
}
```

**Template usage**:
```html
@if (products.hasValue()) {
  @for (product of products.value(); track product.id) {
    <app-product-card [product]="product" />
  }
} @else if (products.isLoading()) {
  <app-spinner />
} @else if (products.error()) {
  <app-error [error]="products.error()" />
}
```

**Key points**
- `httpResource` is for **read operations only** (GET).
- For mutations (POST/PUT/DELETE), use `HttpClient` directly.
- Built on `HttpClient` — supports interceptors, testing with `HttpTestingController`.
- Cancels in-flight requests when dependencies change.

### HttpClient (Mutations & Legacy)

```typescript
@Injectable({ providedIn: 'root' })
export class UsersService {
  private http = inject(HttpClient);
  private baseUrl = '/api/users';

  getAll() {
    return this.http.get<UserDto[]>(this.baseUrl);
  }

  create(input: CreateUserInput) {
    return this.http.post<UserDto>(this.baseUrl, input);
  }

  update(id: string, input: UpdateUserInput) {
    return this.http.put<UserDto>(`${this.baseUrl}/${id}`, input);
  }

  delete(id: string) {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
```

### Functional Interceptors

```typescript
// auth.interceptor.ts
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(AuthService).getToken();
  if (token) {
    req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
  }
  return next(req);
};

// error.interceptor.ts
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    retry({ count: 2, delay: 1000 }),
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) inject(AuthService).logout();
      return throwError(() => error);
    })
  );
};
```
