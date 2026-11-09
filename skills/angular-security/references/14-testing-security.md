## 14. Testing Security

### Tools

| Layer             | Tool                                  |
| ----------------- | ------------------------------------- |
| Unit/Component    | **Vitest** or Karma + Jasmine         |
| Security scanning | **Socket.dev**, **Snyk**, `npm audit` |
| E2E               | **Playwright**                        |
| Accessibility     | **axe-core**                          |

### Security Test Examples

```typescript
describe("AuthGuard", () => {
  it("should redirect unauthenticated users to login", () => {
    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: { isAuthenticated: () => false } },
      ],
    });

    const guard = TestBed.runInInjectionContext(() =>
      authGuard({} as any, { url: "/dashboard" } as any),
    );

    expect(guard).toEqual(
      jasmine.objectContaining({ queryParams: { returnUrl: "/dashboard" } }),
    );
  });
});

describe("XSS Prevention", () => {
  it("should sanitize dangerous HTML", () => {
    const malicious = '<img src=x onerror=alert("XSS")>';
    const sanitized = DOMPurify.sanitize(malicious);
    expect(sanitized).not.toContain("onerror");
  });
});
```
